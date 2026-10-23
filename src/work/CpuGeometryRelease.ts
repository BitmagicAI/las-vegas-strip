import * as THREE from 'three';
import {isGeometryReleaseSuspended} from 'engine/GeometryCpuRelease.js';

/** CPU copies of geometry this game builds itself (city batches, coarse LODs,
 * shadow batches) are dropped once the GPU holds them.
 *
 * Three keeps every attribute's typed array for the life of the geometry. The
 * city's were ~3 GB, which kept the renderer above V8's 8 GB global-memory mark:
 * every few MB allocated then forced a full mark-compact (30-125 ms, 6-8 a second
 * standing still). The rules are the engine's (engine/GeometryCpuRelease.ts):
 *  - an attribute is released only when the backend already has its GPU buffer,
 *    checked per attribute, so a shadow pass that uploaded `position` alone frees
 *    `position` alone and the rest waits for its own first draw;
 *  - the index is never released (WebGPU re-creates it when a geometry is bound
 *    again, and a 0-byte index blanks the frame);
 *  - bounds are computed first: culling and raycasts read them lazily;
 *  - nothing runs during the engine's warm-up render.
 * Only register geometry that is never disposed while still drawn and never
 * re-bound to a new mesh after release; nothing may read its arrays afterwards.
 */
const pending=new Set<THREE.BufferGeometry>();
let lastSweep=0;
let released=0;

export function releaseAfterUpload(geometry:THREE.BufferGeometry):void {
    if(geometry.boundingBox===null)geometry.computeBoundingBox();
    if(geometry.boundingSphere===null)geometry.computeBoundingSphere();
    pending.add(geometry);
}
export function forgetGeometry(geometry:THREE.BufferGeometry):void {pending.delete(geometry);}

type Backend={get(o:object):{buffer?:unknown;bufferGPU?:unknown}};
function uploaded(backend:Backend,attribute:THREE.BufferAttribute|THREE.InterleavedBufferAttribute):boolean {
    const data=backend.get('isInterleavedBufferAttribute' in attribute&&attribute.isInterleavedBufferAttribute?attribute.data:attribute);
    return data.buffer!==undefined||data.bufferGPU!==undefined;
}

/** Call every frame; it does real work at most twice a second. */
export function sweepUploadedGeometry(renderer:{backend:unknown}|null|undefined,now=performance.now()):void {
    if(!renderer||now-lastSweep<500||!pending.size||isGeometryReleaseSuspended())return;
    lastSweep=now;const backend=renderer.backend as Backend;
    for(const geometry of pending){
        let remaining=0;
        for(const attribute of Object.values(geometry.attributes)){
            const holder=('isInterleavedBufferAttribute' in attribute&&attribute.isInterleavedBufferAttribute)?attribute.data:attribute as THREE.BufferAttribute;
            if(!holder.array.length)continue;
            if(!uploaded(backend,attribute)){remaining++;continue;}
            released+=holder.array.byteLength;
            holder.array=new (holder.array.constructor as new(n:number)=>THREE.TypedArray)(0);
        }
        if(!remaining)pending.delete(geometry);
    }
}
export function cpuReleaseStats():{pendingGeometries:number;releasedMB:number}{return {pendingGeometries:pending.size,releasedMB:Math.round(released/1048576)};}
