import type * as THREE from 'three';
import type {EngineLike} from 'types/game.js';

/** `?shaderAudit` on the dev server (2026-10-24): which materials and objects produce each distinct fragment shader, and
 * what building them costs, for keeping the shader count small (ShaderSharing.ts). Wraps three's per-object node build,
 * shader module and pipeline creation before the first frame. Read it from the console: `__shaderAudit()`. */
interface Use {count:number;examples:string[];code:string}
interface Cost {count:number;ms:number}
export function installShaderAudit(engine:EngineLike):void {
    if(typeof location==='undefined'||!['localhost','127.0.0.1'].includes(location.hostname)||!new URLSearchParams(location.search).has('shaderAudit'))return;
    const renderer=engine.renderer as unknown as {
        _nodes?:{nodeBuilderCache:Map<unknown,unknown>;getForRender:(ro:unknown,...rest:unknown[])=>{fragmentShader?:string}};
        backend:{createProgram:(p:unknown)=>void;createRenderPipeline:(ro:unknown,promises:unknown)=>void};
    };
    const nodes=renderer._nodes;
    if(!nodes)return;
    const programs=new Map<string,Use>(),builds=new Map<string,Cost>();
    // per build: the parts of three's cache key (RenderObject.getMaterialCacheKey) and the program it made
    const keys:{parts:Record<string,string>;code:string}[]=[];
    const protoKeys=(m:object)=>{const out:string[]=[];let p=Object.getPrototypeOf(m);while(p){for(const [k,d] of Object.entries(Object.getOwnPropertyDescriptors(p)))if(typeof d.get==='function')out.push(k);p=Object.getPrototypeOf(p);}return out;};
    const keyParts=(ro:Record<string,unknown>&{material:Record<string,unknown>&{customProgramCacheKey:()=>string};object:Record<string,unknown>;context:{id:number}})=>{
        const m=ro.material,parts:Record<string,string>={};
        parts['@type']=String(m.type);parts['@custom']=m.customProgramCacheKey();parts['@name']=String(m.name);
        for(const k of [...Object.keys(m),...protoKeys(m)]){
            if(/^(is[A-Z]|_)|^(visible|version|uuid|name|opacity|userData)$/.test(k))continue;
            const v=m[k] as unknown;let s:string;
            if(v===null||v===undefined)s=String(v);
            else if(typeof v==='number')s=k==='side'?String(v):v!==0?'1':'0';
            else if(typeof v==='object')s=(v as {isTexture?:boolean}).isTexture?(()=>{const t=v as THREE.Texture;return `tex${t.mapping}/${t.magFilter}/${t.minFilter}/${t.wrapS}/${t.wrapT}`;})():(v as {isNode?:boolean}).isNode?'node':'{}';
            else if(typeof v==='function')s='fn';
            else s=String(v);
            parts[k]=s;
        }
        const o=ro.object as {receiveShadow?:boolean;geometry?:{attributes:Record<string,{itemSize:number;normalized?:boolean;data?:{stride:number}}>;index:unknown}};
        if(o.geometry)parts['@geometry']=Object.keys(o.geometry.attributes).sort().map(n=>{const a=o.geometry!.attributes[n]!;return n+(a.data?'/'+a.data.stride:'')+'/'+a.itemSize+(a.normalized?'n':'');}).join(' ');
        parts['@context']=String(ro.context.id);parts['@receiveShadow']=String(o.receiveShadow);
        const own=(m as {lightsNode?:{id?:number;getLights?:()=>THREE.Light[]}}).lightsNode;
        const ln=own??ro.lightsNode as {id?:number;getLights?:()=>THREE.Light[]}|undefined;parts['@lights']=(own?'own ':'scene ')+String(ln?.id);
        if(ln?.id!==undefined&&!lightLists[ln.id]){const all=ln.getLights?.()??[];const types:Record<string,number>={};for(const l of all)types[l.type]=(types[l.type]??0)+1;
            lightLists[ln.id]=`${all.length} lights ${JSON.stringify(types)} shadows: ${all.filter(l=>l.castShadow).map(l=>`${l.type}:${l.name||'?'}`).join(', ')}`;}
        parts['@dynamic']=String((ro as unknown as {getDynamicCacheKey:()=>number}).getDynamicCacheKey());
        parts['@clipping']=String(ro.clippingContextCacheKey);
        return parts;
    };
    const totals={builds:0,buildMs:0,programs:0,programMs:0,pipelines:0,pipelineMs:0};
    // main-thread freezes over 200 ms, and the engine's warm-up compile calls, by time since navigation
    const freezes:string[]=[],compiles:string[]=[],timeline:Record<number,number>={},stacks:Record<number,string>={},recent:string[]=[],lightLists:Record<number,string>={};
    try{new PerformanceObserver(list=>{for(const e of list.getEntries())if(e.duration>200)freezes.push(`${Math.round(e.startTime)}+${Math.round(e.duration)}`);}).observe({type:'longtask',buffered:true});}catch{/* no long-task timing */}
    const timedRenderer=engine.renderer as unknown as {compileAsync:(...a:unknown[])=>Promise<unknown>};
    const compile=timedRenderer.compileAsync.bind(timedRenderer);
    timedRenderer.compileAsync=(...a)=>{const t=performance.now(),b=totals.builds;return compile(...a).finally(()=>compiles.push(`${Math.round(t)}+${Math.round(performance.now()-t)} builds ${totals.builds-b}`));};
    const owner=(o:THREE.Object3D|null)=>{let p=o;let name='';while(p&&p.parent){if(p.name)name=p.name;p=p.parent;}return name.replace(/[0-9]+/g,'#').slice(0,40);};
    const getForRender=nodes.getForRender.bind(nodes);
    nodes.getForRender=(ro:unknown,...rest:unknown[])=>{
        const before=nodes.nodeBuilderCache.size,t=performance.now();
        const state=getForRender(ro,...rest);
        const r=ro as {material:THREE.Material&{lightsNode?:{id:number}};object:THREE.Object3D&{receiveShadow:boolean;isInstancedMesh?:boolean;count?:number}};
        if(nodes.nodeBuilderCache.size>before){
            const dt=performance.now()-t;totals.builds++;totals.buildMs+=dt;
            const second=Math.floor(t/1000);timeline[second]=(timeline[second]??0)+dt;
            const o=r.object,m=r.material;
            const kind=`${m.type}${o.isInstancedMesh||(o.count??1)>1?' instanced':''} @${owner(o)}`;
            recent.push(`${Math.round(t)} ctx${(ro as {context:{id:number}}).context.id} ${m.type}:${m.name} ${o.name} @${owner(o)} ${dt.toFixed(1)}ms`);
            let c=builds.get(kind);if(!c)builds.set(kind,c={count:0,ms:0});
            c.count++;c.ms+=dt;
            const ctx=(ro as {context:{id:number}}).context.id;if(!stacks[ctx])stacks[ctx]=(new Error().stack??'').split('\n').slice(2,22).map(l=>l.trim().replace(/https?:\/\/[^/]+/,'')).join('\n');
            if(state?.fragmentShader)keys.push({parts:keyParts(ro as Parameters<typeof keyParts>[0]),code:state.fragmentShader});
        }
        const code=state?.fragmentShader;
        if(code){
            let use=programs.get(code);if(!use)programs.set(code,use={count:0,examples:[],code});
            use.count++;
            if(use.examples.length<6){
                const m=r.material;
                use.examples.push(`${m.type}:${(m.name||'?').slice(0,28)}${m.lightsNode?' L'+m.lightsNode.id:''}${r.object.receiveShadow?' rs':''} @${owner(r.object)}`);
            }
        }
        return state;
    };
    // every render object, for checking what its bindings hold (atlasCheck)
    const renderObjects=new Set<{object:THREE.Object3D;material:THREE.Material&{atlasMap?:THREE.Texture};context:{id:number};_bindings?:{bindings:{isSampledTexture?:boolean;texture?:THREE.Texture}[]}[]|null}>();
    const objects=(engine.renderer as unknown as {_objects:{get:(...a:unknown[])=>unknown}})._objects;
    const objectsGet=objects.get.bind(objects);
    // the textures each GPU bind group was made with (three rebuilds a bind group only when a texture's generation changes)
    const utils=(engine.renderer as unknown as {backend:{bindingUtils?:{createBindGroup:(g:{bindings:{isSampledTexture?:boolean;texture?:THREE.Texture}[]},l:unknown)=>unknown}}}).backend.bindingUtils;
    const made=new WeakMap<object,THREE.Texture[]>();
    if(utils){const create=utils.createBindGroup.bind(utils);utils.createBindGroup=(g,l)=>{made.set(g,g.bindings.filter(b=>b.isSampledTexture&&b.texture).map(b=>b.texture!));return create(g,l);};}
    objects.get=(...a:unknown[])=>{const ro=objectsGet(...a) as never;renderObjects.add(ro);return ro;};
    const atlasCheck=()=>{
        let total=0,wrong=0;const examples:string[]=[],atlases=new Set<THREE.Texture>();
        for(const ro of renderObjects)if(ro.material?.atlasMap)atlases.add(ro.material.atlasMap);
        for(const ro of renderObjects){
            const want=ro.material?.atlasMap;if(!want||!ro._bindings)continue;
            for(const g of ro._bindings)for(const b of g.bindings){
                if(!b.isSampledTexture||!b.texture||!atlases.has(b.texture))continue;
                total++;const gpu=made.get(g)?.find(t=>atlases.has(t));
                if(b.texture!==want||gpu!==want){wrong++;if(examples.length<10)examples.push(`${ro.object.name} ctx${ro.context.id}: binding #${b.texture.id} gpu #${gpu?.id} want #${want.id}`);}
            }
        }
        return {total,wrong,examples,atlases:atlases.size};
    };
    const backend=renderer.backend;
    const createProgram=backend.createProgram.bind(backend);
    backend.createProgram=p=>{const t=performance.now();createProgram(p);totals.programs++;totals.programMs+=performance.now()-t;};
    const createRenderPipeline=backend.createRenderPipeline.bind(backend);
    backend.createRenderPipeline=(ro,promises)=>{const t=performance.now();createRenderPipeline(ro,promises);totals.pipelines++;totals.pipelineMs+=performance.now()-t;};
    (window as unknown as {__shaderAudit:()=>unknown}).__shaderAudit=()=>({
        totals,
        builds:[...builds.entries()].map(([kind,c])=>({kind,...c})).sort((a,b)=>b.ms-a.ms),
        programs:[...programs.values()].sort((a,b)=>b.count-a.count),
        keys,freezes,compiles,timeline,stacks,recent,lightLists,atlas:atlasCheck(),
        lightsNow:(()=>{const out:string[]=[];engine.scene?.traverse(o=>{const l=o as THREE.Light;if(l.isLight&&l.castShadow)out.push(`${l.type}:${l.name||'?'} visible=${l.visible} intensity=${l.intensity.toFixed(2)}`);});return out;})(),
        contexts:Object.entries((engine.renderer as unknown as {_renderContexts:{_renderContexts:Record<string,{id:number}>}})._renderContexts._renderContexts).map(([k,v])=>`${v.id} ${k}`),
    });
    console.info('[ShaderAudit] recording node builds, programs and pipelines');
}
