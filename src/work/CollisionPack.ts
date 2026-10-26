import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {runtimeUrl} from './RuntimeAssets.js';

/** Collision meshes as tools/optimize/pack-data.mjs writes them (VCOL, 2026-10-25; the format is described there): no
 * JSON, no JS arrays. Positions stay as 16-bit grid values and indices as 16-bit wherever a mesh allows, decoded by the
 * meshopt workers (GltfDecoders.ts); a mesh becomes the Float32Array and Uint32Array physics wants only when its
 * collider is built (Rapier keeps both, so each collider owns its pair). */
export class CollisionPack {
    private constructor(
        readonly count:number,
        /** the mapped city's cell per mesh (160 m squares), or null */
        readonly cellX:Int16Array|null,readonly cellZ:Int16Array|null,
        private readonly origin:Int32Array,private readonly exponent:Uint8Array,
        private readonly vertexStart:Uint32Array,private readonly triangles:Uint32Array,private readonly indexStart:Uint32Array,private readonly wide:Uint8Array,
        private readonly positions:Uint16Array,private readonly narrowIndices:Uint16Array,private readonly wideIndices:Uint32Array){}

    static async decode(buffer:ArrayBuffer):Promise<CollisionPack>{
        const dv=new DataView(buffer);
        if(dv.getUint32(0,true)!==0x4c4f4356||dv.getUint16(4,true)!==1)throw new Error('Not a collision pack (VCOL 1)');
        const flags=dv.getUint16(6,true),n=dv.getUint32(8,true);
        let at=12;
        const align=()=>{at=(at+3)&~3;};
        const i16=()=>{const a=new Int16Array(buffer,at,n);at+=n*2;align();return a;};
        const cellX=flags&1?i16():null,cellZ=flags&1?i16():null;
        const origin=new Int32Array(buffer,at,n*3);at+=n*12;
        const exponent=new Uint8Array(buffer,at,n);at+=n;align();
        const vertexCount=new Uint32Array(buffer,at,n);at+=n*4;
        const triangleCount=new Uint32Array(buffer,at,n);at+=n*4;
        const section=()=>{const length=dv.getUint32(at,true),bytes=new Uint8Array(buffer,at+4,length);at+=4+length;align();return bytes;};
        const coded=[section(),section(),section()] as const;
        // offsets: vertices in one list; indices in two (16-bit meshes, then the few 32-bit ones)
        const vertexStart=new Uint32Array(n+1),indexStart=new Uint32Array(n+1),wide=new Uint8Array(n);
        let narrowTotal=0,wideTotal=0;
        for(let i=0;i<n;i++){
            vertexStart[i+1]=vertexStart[i]!+vertexCount[i]!;
            wide[i]=vertexCount[i]!>65536?1:0;
            if(wide[i]){indexStart[i]=wideTotal;wideTotal+=triangleCount[i]!*3;}else{indexStart[i]=narrowTotal;narrowTotal+=triangleCount[i]!*3;}
        }
        const total=vertexStart[n]!;
        const decode=(count:number,size:number,source:Uint8Array,mode:'ATTRIBUTES'|'TRIANGLES')=>count?MeshoptDecoder.decodeGltfBufferAsync(count,size,source,mode,'NONE'):Promise.resolve(new Uint8Array(0));
        const [p,a,b]=await Promise.all([decode(total,8,coded[0],'ATTRIBUTES'),decode(narrowTotal,2,coded[1],'TRIANGLES'),decode(wideTotal,4,coded[2],'TRIANGLES')]);
        return new CollisionPack(n,cellX,cellZ,origin,exponent,vertexStart,triangleCount,indexStart,wide,
            new Uint16Array(p.buffer,p.byteOffset,total*4),new Uint16Array(a.buffer,a.byteOffset,narrowTotal),new Uint32Array(b.buffer,b.byteOffset,wideTotal));
    }

    /** Mesh `i`'s vertices in metres (a new array, for its collider). */
    vertices(i:number):Float32Array{
        const from=this.vertexStart[i]!,n=this.vertexStart[i+1]!-from,out=new Float32Array(n*3),q=this.positions;
        const s=2**-this.exponent[i]!,ox=this.origin[i*3]!,oy=this.origin[i*3+1]!,oz=this.origin[i*3+2]!;
        for(let v=0,k=from*4;v<n;v++,k+=4){out[v*3]=(ox+q[k]!)*s;out[v*3+1]=(oy+q[k+1]!)*s;out[v*3+2]=(oz+q[k+2]!)*s;}
        return out;
    }
    /** Mesh `i`'s triangle indices (a new array, or a view for the few 32-bit meshes). */
    indices(i:number):Uint32Array{
        const n=this.triangles[i]!*3,from=this.indexStart[i]!;
        if(this.wide[i])return this.wideIndices.subarray(from,from+n);
        const out=new Uint32Array(n);out.set(this.narrowIndices.subarray(from,from+n));return out;
    }
    triangleCount(i:number):number{return this.triangles[i]!;}
    /** Mesh `i`'s grid step in metres (positions are within half a step of the source). */
    gridStep(i:number):number{return 2**-this.exponent[i]!;}
    /** Mesh `i` as a trimesh collider record (engine MeshLevelTrimeshCollider). */
    trimesh(i:number,name:string):{name:string;shape:'trimesh';vertices:Float32Array;indices:Uint32Array}{
        return {name,shape:'trimesh',vertices:this.vertices(i),indices:this.indices(i)};
    }
}

/** Fetch and decode a .bin collision pack (the URL as the dev server serves it; runtimeUrl maps it to the CDN). */
export async function loadCollisionPack(url:string):Promise<CollisionPack>{
    const response=await fetch(runtimeUrl(url));
    if(!response.ok)throw new Error(`Collision data unavailable: ${url} (${response.status}; run node tools/optimize/pack-data.mjs)`);
    return CollisionPack.decode(await response.arrayBuffer());
}
