import type * as THREE from 'three';

/** An attribute's components as plain floats (2026-10-26): `fromBufferAttribute`/`getX` per vertex was most of the
 * batching time on the quantized (meshopt) sources, and one generic reader over every array type stays polymorphic, so
 * V8 never inlines it. Each source is converted once, by a loop for its own array type, into a reused buffer of doubles:
 * exactly the values three's accessors return (three's `denormalize`: unsigned types divide by their maximum, signed ones
 * also clamp at -1, in double precision), packed `itemSize` a vertex. Always a Float64Array, so the loops reading it see
 * one array type. Buffers belong to a `Scratch` that each build owns (builds run as generators that yield mid-mesh and
 * interleave, so a shared buffer could change under a suspended one); a result is valid until that scratch's next call
 * with the same slot. */
export class Scratch {readonly buffers:Float64Array[]=[];}
export function floats(a:THREE.BufferAttribute|THREE.InterleavedBufferAttribute,scratch:Scratch,slot:number):Float64Array{
    const interleaved='isInterleavedBufferAttribute' in a&&a.isInterleavedBufferAttribute;
    const array=interleaved?(a as THREE.InterleavedBufferAttribute).data.array:(a as THREE.BufferAttribute).array;
    const stride=interleaved?(a as THREE.InterleavedBufferAttribute).data.stride:a.itemSize,offset=interleaved?(a as THREE.InterleavedBufferAttribute).offset:0;
    const size=a.itemSize,count=a.count,n=count*size;
    let out=scratch.buffers[slot];if(!out||out.length<n){out=new Float64Array(Math.max(n,(out?.length??0)*2,4096));scratch.buffers[slot]=out;}
    const norm=a.normalized;
    if(array instanceof Float32Array){for(let i=0,k=0;i<count;i++)for(let c=0;c<size;c++)out[k++]=array[i*stride+offset+c]!;}
    else if(array instanceof Int16Array){const s=norm?32767:1;for(let i=0,k=0;i<count;i++)for(let c=0;c<size;c++){const v=array[i*stride+offset+c]!;out[k++]=norm?Math.max(v/s,-1):v;}}
    else if(array instanceof Uint16Array){const s=norm?65535:1;for(let i=0,k=0;i<count;i++)for(let c=0;c<size;c++)out[k++]=array[i*stride+offset+c]!/s;}
    else if(array instanceof Int8Array){const s=norm?127:1;for(let i=0,k=0;i<count;i++)for(let c=0;c<size;c++){const v=array[i*stride+offset+c]!;out[k++]=norm?Math.max(v/s,-1):v;}}
    else if(array instanceof Uint8Array){const s=norm?255:1;for(let i=0,k=0;i<count;i++)for(let c=0;c<size;c++)out[k++]=array[i*stride+offset+c]!/s;}
    else if(array instanceof Int32Array){const s=norm?2147483647:1;for(let i=0,k=0;i<count;i++)for(let c=0;c<size;c++){const v=array[i*stride+offset+c]!;out[k++]=norm?Math.max(v/s,-1):v;}}
    else if(array instanceof Uint32Array){const s=norm?4294967295:1;for(let i=0,k=0;i<count;i++)for(let c=0;c<size;c++)out[k++]=array[i*stride+offset+c]!/s;}
    else throw new Error(`AttributeReader: unsupported array ${array.constructor.name}`);
    return out.subarray(0,n);
}
