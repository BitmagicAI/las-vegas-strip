import {WebGPURenderer} from 'three/webgpu';
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
