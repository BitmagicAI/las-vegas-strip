import {WebGPURenderer} from 'three/webgpu';
import type {EngineLike} from 'types/game.js';

/** The vendored engine's renderer factory doesn't yet expose Three's depth
 * options. Recreate through its public lifecycle hook, then configure the fresh
 * renderer before its asynchronous GPU initialization and first scene compile.
 * This is deliberately a Three r185 compatibility adapter: changing only the
 * renderer flag would leave the backend using the opposite depth comparison.
 * Reversed floating-point depth preserves close indoor clipping AND centimetre
 * facade layers kilometres away. No logarithmic fragment-depth/post-FX mismatch.
 */
export function configureSkylineDepth(engine:EngineLike):void {
    if(!(engine.renderer instanceof WebGPURenderer) || engine.renderer.reversedDepthBuffer)return;
    if(!engine.recreateRenderer){
        // Engine 3.1337 keeps one renderer per page (recreateRenderer is gone) and starts its init() at once. r185
        // reads the flag only when it builds pipelines, depth textures and render passes (WebGPUPipelineUtils,
        // WebGPUTextureUtils, WebGPUUtils), for the clear depth and camera._reversedDepth: never inside init(). So
        // the live renderer takes it in place, as long as it has not drawn or compiled anything yet.
        const renderer=engine.renderer,info=renderer.info.render;
        if(info.frame>0||info.calls>0)throw new Error('Skyline depth must be configured before the first frame');
        enableReversedDepth(renderer);
        return;
    }
    engine.recreateRenderer(engine.renderer.samples>0,'webgpu');
    const renderer=engine.renderer;
    if(!(renderer instanceof WebGPURenderer) || renderer.initialized)
        throw new Error('Skyline depth must be configured before renderer initialization');
    enableReversedDepth(renderer);
}

function enableReversedDepth(renderer:WebGPURenderer):void {
    // These are real, writable own properties in r185, although Three marks
    // constructor options readonly in its public types. Keep the workaround
    // here (never on a live renderer), until Bitmagic exposes creation options.
    const flag=Object.getOwnPropertyDescriptor(renderer,'reversedDepthBuffer');
    if(!flag?.writable)throw new Error('Unsupported Three renderer depth configuration');
    Reflect.set(renderer,'reversedDepthBuffer',true);
    const parameters:unknown=Reflect.get(renderer.backend,'parameters');
    if(!parameters || typeof parameters!=='object')throw new Error('Unsupported Three backend parameters');
    Object.assign(parameters,{reversedDepthBuffer:true});
    configureReversedDepthSorting(renderer);
    console.info(`[SkylineDepth] Reversed floating-point depth enabled before the ${renderer.initialized?'first frame':'GPU initialization'}`);
}

/** r185 reverses the entire render list for reversed depth, including explicit
 * renderOrder. Compensate the non-depth keys so the sky stays before the world,
 * and transparent UI/decals retain their intended order. Leave the depth key
 * reversed: larger reversed-Z is nearer. Also works if WebGL fallback declines
 * reversed depth because EXT_clip_control is unavailable. */
export function configureReversedDepthSorting(renderer:WebGPURenderer):void {
    // Comparators return -1/0/1 only: a fractional depth difference handed back to the
    // built-in sort is boxed as a heap number on every comparison (~2 MB/s standing still).
    const cmp=(x:number,y:number)=>x<y?-1:x>y?1:0;
    renderer.setOpaqueSort((a,b)=>{
        const direction=renderer.reversedDepthBuffer?-1:1;
        return (cmp(a.groupOrder!,b.groupOrder!)||cmp(a.renderOrder!,b.renderOrder!))*direction || cmp(a.z!,b.z!) || cmp(a.id!,b.id!)*direction;
    });
    renderer.setTransparentSort((a,b)=>{
        const direction=renderer.reversedDepthBuffer?-1:1;
        return (cmp(a.groupOrder!,b.groupOrder!)||cmp(a.renderOrder!,b.renderOrder!))*direction || cmp(b.z!,a.z!) || cmp(a.id!,b.id!)*direction;
    });
}
