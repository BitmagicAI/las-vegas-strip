import {WebGPURenderer} from 'three/webgpu';
import type {EngineLike} from 'types/game.js';
import {EngineLighting,DEFAULT_ENGINE_LIGHTING_OPTIONS,rendererBatchesLights} from 'engine/lighting/EngineLighting.js';

/** Engine 3.1337 batches the scene's lights into one shader loop per type, capped at 64 point and 16 spot lights; a
 * light past the cap silently goes dark. The city outgrows that: the engine's own light manager parks 40 point and 8
 * spot slots, the city adds its venue and nearby lights, and the film looks add 8 street lamps and 12 architectural
 * floods (film/SceneAtmosphere.ts). On 2026-10-24 a night take lost its lamp pools and lit a different facade.
 * Before the first frame, while no material is compiled (the set of lights never changes during play), give the
 * batched lighting room for all of them. The loops run over the lights present, so a higher cap costs nothing. */
const MAX_POINT_LIGHTS = 128;
const MAX_SPOT_LIGHTS = 32;

export function configureLightCaps(engine:EngineLike):void {
    const renderer=engine.renderer;
    if(!(renderer instanceof WebGPURenderer) || !rendererBatchesLights(renderer))return;
    const info=renderer.info.render;
    if(info.frame>0||info.calls>0)throw new Error('Light caps must be configured before the first frame');
    const lighting=new EngineLighting({...DEFAULT_ENGINE_LIGHTING_OPTIONS,maxPointLights:MAX_POINT_LIGHTS,maxSpotLights:MAX_SPOT_LIGHTS});
    renderer.lighting=lighting;
    // (three r185 builds its render lists in init(), with the lighting of that moment)
    const lists=(renderer as unknown as {_renderLists?:{lighting:unknown}|null})._renderLists;
    if(lists)lists.lighting=lighting;
    console.info(`[LightCaps] batched lighting: ${MAX_POINT_LIGHTS} point, ${MAX_SPOT_LIGHTS} spot lights`);
}
