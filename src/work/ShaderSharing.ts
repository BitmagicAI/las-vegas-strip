import type {Camera,Object3D,Scene,Texture} from 'three';
import {FloatType} from 'three';
import {NodeUpdateType,TextureNode,WebGPURenderer,type MRTNode,type Node,type NodeFrame,type PassNode,type RenderTarget} from 'three/webgpu';
import type {EngineLike} from 'types/game.js';

/** Fewer shaders (2026-10-24, the owner: "Ideally we would have a very small number of shaders ... If the only
 * difference is vertex buffer and textures, we should not have any recompiling").
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
 * pass renders at (the engine's own suggestion), so it builds exactly what the frame draws with, off the frame. */
export function compileForScenePass(engine:EngineLike):void {
    const renderer=engine.renderer;
    if(!(renderer instanceof WebGPURenderer))return;
    const contexts=(renderer as unknown as {_renderContexts?:Contexts})._renderContexts;
    if(!contexts?.get||!contexts._renderContexts)throw new Error('Unsupported three renderer: no render contexts to compile against');
    type Compile=(scene:Object3D,camera:Camera,target?:Scene|null)=>Promise<unknown>;
    const compileAsync=renderer.compileAsync.bind(renderer) as Compile;
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
        const previousTarget=renderer.getRenderTarget(),previousMrt=renderer.getMRT(),get=contexts.get;
        renderer.setRenderTarget(throwaway);renderer.setMRT(mrt);
        contexts.get=(rt,m,d=0)=>get.call(contexts,rt,m,rt===throwaway&&m===mrt?depth:d);
        // compileAsync picks its render context synchronously, before its first await: restore right after
        let compiling:Promise<unknown>;
        try{compiling=compileAsync(scene,camera,target);}
        finally{contexts.get=get;renderer.setRenderTarget(previousTarget);renderer.setMRT(previousMrt);}
        return compiling.finally(()=>throwaway.dispose());
    };
}

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
