import type * as THREE from 'three';
import type {Camera,Object3D,Scene,Texture} from 'three';
import {FloatType} from 'three';
import {float} from 'three/tsl';
import {NodeMaterial,NodeUpdateType,TextureNode,WebGPURenderer,type MRTNode,type Node,type NodeFrame,type PassNode,type RenderTarget} from 'three/webgpu';
import type {EngineLike} from 'types/game.js';

/** Fewer shaders (2026-10-24: the owner asked for very few shaders,
 * and no new compile when only vertex buffers and textures differ).
 *
 * three r185 gives every InstancedMesh with up to ~1,000 instances its own uniform buffer for the matrices, named after
 * the buffer node's id (`NodeBuffer_850160`), so each instanced mesh compiles its own vertex shader and pipeline even
 * when everything else is identical: 626 of the city's 1,122 vertex shaders on 2026-10-24. Above the uniform limit
 * three reads the matrices from instanced vertex attributes instead, which is the same shader for every mesh. The
 * limit is read only there (nodes/accessors/Instance.js: matrices and instance colours) and by RangeNode, which the
 * city does not use, so reporting 0 sends every instanced mesh down the shared path. Set before the first frame. */
export function configureShaderSharing(engine:EngineLike):void {
    const renderer=engine.renderer;
    if(!(renderer instanceof WebGPURenderer))return;
    const capabilities=(renderer.backend as unknown as {capabilities?:{getUniformBufferLimit?:()=>number}}).capabilities;
    if(!capabilities?.getUniformBufferLimit)throw new Error('Unsupported three backend: no uniform buffer limit to override');
    capabilities.getUniformBufferLimit=()=>0;
}

type Contexts={_renderContexts:Record<string,{id:number}>;get:(target:RenderTarget|null,mrt:MRTNode|null,depth?:number)=>unknown};
/** The engine's start-up warm-up (2026-10-24) pre-compiles every material with `compileAsync`, which renders into the
 * renderer's own HDR target at call depth 0. The game draws its scene inside the post chain's scene pass, into that
 * pass's multi-target buffer at call depth 1, and three keys node builds, shaders and pipelines by that render context:
 * every pre-compiled shader was a throwaway (the engine's WarmupController calls it a known limit) and the warm frame
 * then built the real ones in one blocking burst, 1,122 node builds and ~11 s of main thread with half of them unused.
 * Here each pre-compile renders into a small throwaway target with the scene pass's attachments and MRT, at the depth the
 * pass renders at (the engine's own suggestion), so it builds exactly what the frame draws with, off the frame.
 * three's compileAsync then waits for each object's pipeline before starting the next object's (2026-10-25: ~190
 * pipelines one after another, 16 s), so their promises are collected instead and awaited together at the end of the
 * call: the GPU process compiles them side by side, and the engine still holds its render loop until all are ready. */
export function compileForScenePass(engine:EngineLike):void {
    const renderer=engine.renderer;
    if(!(renderer instanceof WebGPURenderer))return;
    const contexts=(renderer as unknown as {_renderContexts?:Contexts})._renderContexts;
    if(!contexts?.get||!contexts._renderContexts)throw new Error('Unsupported three renderer: no render contexts to compile against');
    type Compile=(scene:Object3D,camera:Camera,target?:Scene|null)=>Promise<unknown>;
    type ForRender=(renderObject:unknown,promises?:Promise<unknown>[]|null)=>unknown;
    const pipelines=(renderer as unknown as {_pipelines?:{getForRender:ForRender}})._pipelines;
    if(!pipelines?.getForRender)throw new Error('Unsupported three renderer: no pipeline cache to compile into');
    const original=renderer.compileAsync.bind(renderer) as Compile,forRender=pipelines.getForRender;
    // `?precompile=serial|plain` on localhost: three's own waiting, or no redirect at all (A/B)
    const mode=typeof location!=='undefined'&&['localhost','127.0.0.1'].includes(location.hostname)?new URLSearchParams(location.search).get('precompile'):null;
    if(mode==='plain')return;
    const compileAsync:Compile=(scene,camera,target)=>{
        if(mode==='serial')return original(scene,camera,target);
        const pending:Promise<unknown>[]=[];
        pipelines.getForRender=function(this:unknown,renderObject,promises=null){
            if(!promises)return forRender.call(this,renderObject,promises);
            const mine:Promise<unknown>[]=[],pipeline=forRender.call(this,renderObject,mine);
            for(const p of mine)pending.push(p);
            return pipeline;
        };
        return original(scene,camera,target).then(()=>Promise.all(pending)).finally(()=>{pipelines.getForRender=forRender;});
    };
    /** Compile into `into` with `mrt`, as if rendered at call depth `depth`. compileAsync picks its render context
     * synchronously, before its first await, so everything is restored right after the call. */
    const compileInto=(into:RenderTarget,mrt:MRTNode|null,depth:number,scene:Object3D,camera:Camera,target?:Scene|null)=>{
        const previousTarget=renderer.getRenderTarget(),previousMrt=renderer.getMRT(),get=contexts.get;
        renderer.setRenderTarget(into);renderer.setMRT(mrt);
        contexts.get=(rt,m,d=0)=>get.call(contexts,rt,m,rt===into&&m===mrt?depth:d);
        let compiling:Promise<unknown>;
        try{compiling=compileAsync(scene,camera,target);}
        finally{contexts.get=get;renderer.setRenderTarget(previousTarget);renderer.setMRT(previousMrt);}
        return compiling.finally(()=>into.dispose());
    };
    (renderer as unknown as {compileAsync:Compile}).compileAsync=(scene,camera,target)=>{
        const pass=scenePass(engine),mrt=pass?.getMRT()??null;
        if(!pass||!mrt)return compileAsync(scene,camera,target);
        const live=pass.renderTarget,texture=live.texture,samples=(pass as unknown as {options:{samples?:number}}).options.samples??renderer.samples;
        // the depth the pass rendered at (three's render-context key), once it has rendered
        const prefix=`${live.textures.length}:${texture.format}:${renderer.getOutputBufferType()}:${samples}:${live.depthBuffer}:${live.stencilBuffer}-${mrt.id}-`;
        const used=Object.keys(contexts._renderContexts).find(key=>key.startsWith(prefix));
        const depth=used?Number(used.slice(prefix.length)):1;
        // as the pass sets its target up when it renders (PassNode.setup): samples, colour type, reversed-depth type
        const throwaway=live.clone();throwaway.setSize(16,16);
        throwaway.samples=samples;
        throwaway.texture.type=renderer.getOutputBufferType();
        if(renderer.reversedDepthBuffer&&throwaway.depthTexture)throwaway.depthTexture.type=FloatType;
        return compileInto(throwaway,mrt,depth,scene,camera,target);
    };
}

// Not pre-compiled: the lake mirrors' own pass (renderMirror: a half-float 4-sample target at call depth 2, ~90 builds,
// 0.9 s of the warm frame). Compiling it the same way (a 16 px throwaway target, depth forced to 2) made door frames from
// somewhere below the street show through the road at the Paris view (2026-10-25, found with ?precompile=serial|scene;
// not traced further).

/** The post chain's scene pass: the pass node that renders the engine's scene with an MRT. */
function scenePass(engine:EngineLike):PassNode|null {
    const output=(engine as unknown as {postFx?:{bloomPipeline?:{outputNode?:Node}|null}}).postFx?.bloomPipeline?.outputNode;
    if(!output)return null;
    const seen=new Set<Node>(),stack:Node[]=[output];
    while(stack.length){
        const node=stack.pop()!;if(seen.has(node))continue;seen.add(node);
        const pass=node as unknown as PassNode&{isPassNode?:boolean};
        if(pass.isPassNode&&pass.scene===engine.scene&&pass.getMRT())return pass;
        for(const child of node.getChildren())stack.push(child as Node);
    }
    return null;
}

/** A texture node whose texture is the drawn material's `property`, looked up at draw time. three shares one node build
 * between materials whose cache keys match, so a family of materials that differ only in a texture can share one
 * shader when the texture comes from here rather than from a `texture(map)` captured in each material's node graph
 * (each such graph is its own build). The family's materials must also share a `customProgramCacheKey`. */
class DrawnTextureNode extends TextureNode {
    property='';
    constructor(value?:Texture,uvNode?:Node|null,levelNode?:Node|null,biasNode?:Node|null){
        super(value,uvNode as never,levelNode as never,biasNode as never);
        // updated for every drawn object (three's texture setup would reset a plain field to NONE)
        Object.defineProperty(this,'updateType',{configurable:true,get:()=>NodeUpdateType.OBJECT,set:()=>{}});
    }
    override update(frame:NodeFrame):boolean|undefined{
        const texture=(frame.material as unknown as Record<string,unknown>|null)?.[this.property];
        if(texture)this.value=texture as Texture;
        return super.update(frame);
    }
    override clone():this{const node=super.clone() as this;node.property=this.property;return node;}
}
export function drawnTexture(property:string,placeholder:Texture):TextureNode{
    const node=new DrawnTextureNode(placeholder);node.property=property;return node;
}

/** Inputs read only by the shadow pass, which renders with three's shadow material and keys its own shader. */
const SHADOW_ONLY=new Set(['maskShadowNode','castShadowNode','castShadowPositionNode']);
/** Key a node material's shader by the node inputs its own passes read. three's default hashes every node input, and a
 * node's key is its object id, so a per-material shadow mask (an interior's ceiling cut, a cut-out's `map` reference)
 * gave each material its own build of an identical shader. Keeps a key the material already chose. */
export function keyWithoutShadowNodes(material:THREE.Material):void{
    const m=material as unknown as {isNodeMaterial?:boolean;customProgramCacheKey:()=>string};
    if(!m.isNodeMaterial||m.customProgramCacheKey!==NodeMaterial.prototype.customProgramCacheKey)return;
    m.customProgramCacheKey=function(this:Record<string,unknown>&{type:string}){
        let key=this.type;
        for(const property of Object.getOwnPropertyNames(this)){
            if(property.startsWith('_')||SHADOW_ONLY.has(property))continue;
            const node=this[property] as {isNode?:boolean;getCacheKey():number}|null;
            if(node?.isNode)key+=`|${property}:${node.getCacheKey()}`;
        }
        return key;
    };
}

const cutoffs=new Map<number,Node>();
/** One alpha cut-off node per value, shared by every material that uses it (a node per material is a build each). */
export function sharedAlphaCutoff(value:number):Node{
    let node=cutoffs.get(value);if(!node){node=float(value) as unknown as Node;cutoffs.set(value,node);}
    return node;
}

/** Compile a root that is not shown yet (city geometry loading behind play), off the frame: every object in it, hidden
 * levels of detail and objects behind the camera included, so it draws without building anything when it appears.
 * The flags are changed only for compileAsync's synchronous part, so nothing is drawn early. */
export function compileSubtree(engine:EngineLike,root:Object3D):Promise<unknown>{
    const renderer=engine.renderer as unknown as {compileAsync?:(root:Object3D,camera:Camera,scene:Scene)=>Promise<unknown>},camera=engine.camera,scene=engine.scene;
    if(!renderer.compileAsync||!camera||!scene)return Promise.resolve();
    const saved:{o:Object3D;visible:boolean;culled:boolean}[]=[];
    root.traverse(o=>{saved.push({o,visible:o.visible,culled:o.frustumCulled});o.visible=true;o.frustumCulled=false;});
    try{return renderer.compileAsync(root,camera,scene);}
    finally{for(const s of saved){s.o.visible=s.visible;s.o.frustumCulled=s.culled;}}
}
