import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {runtimeUrl} from './RuntimeAssets.js';
import {bakeMode} from './CityBake.js';
import {cityCellsEnabled} from './CityCells.js';

/** The baked distant LODs (build/baked/city-lod.bin, VLOD, written by tools/bake/bake-city.mjs; the format is described
 * there). Per near batch: which of its vertices the LOD keeps and the LOD's triangles over them, ~2.7 MB for the city
 * (brotli). CityLod gathers those vertices from the batch it built instead of clustering it (2026-10-26). A batch whose
 * vertex count, index count or sampled positions differ from the baked one is clustered as before. */
export interface BakedLod {
    /** the near batch it was made from */
    vertices:number;indices:number;hash:number;
    /** the LOD's vertex count and index count */
    count:number;indexCount:number;
    subset:Uint8Array;index:Uint8Array;
}
export class LodBake {
    constructor(private readonly parts:Map<string,Map<string,BakedLod[]>>){}
    batch(part:string,key:string,k:number):BakedLod|undefined{return this.parts.get(part)?.get(key)?.[k];}
    get partCount():number{return this.parts.size;}
    static combine(files:readonly LodBake[]):LodBake {
        const parts=new Map<string,Map<string,BakedLod[]>>();
        for(const file of files)for(const [id,blocks] of file.parts){
            let target=parts.get(id);if(!target){target=new Map();parts.set(id,target);}
            for(const [key,batches] of blocks){
                if(target.has(key))throw new Error(`Duplicate LOD block ${id}/${key}`);
                target.set(key,batches);
            }
        }
        return new LodBake(parts);
    }
}

let bake:LodBake|null=null,loading:Promise<LodBake|null>|null=null;
/** The bake once it has loaded (null before, without one, or with `?bake=off`/`capture`). */
export function cityLodBake():LodBake|null{return bake;}
/** Use this bake (tests, tools). */
export function useCityLodBake(lods:LodBake|null):void{bake=lods;}
/** Load the bake (once). */
export function loadCityLodBake():Promise<LodBake|null>{
    if(bakeMode!=='use')return Promise.resolve(null);
    return loading??=(async()=>{
        try{
            if(cityCellsEnabled){
                const directory='/build/baked/cells';
                const response=await fetch(runtimeUrl(directory+'/manifest.json'));
                if(!response.ok)throw new Error('City LOD cell manifest unavailable');
                const manifest=await response.json() as {version:number;cellSize:number;cells:{file:string}[]};
                if(manifest.version!==1||manifest.cellSize!==800)throw new Error('Unsupported LOD cell manifest');
                await MeshoptDecoder.ready;
                const files:LodBake[]=[];
                // Bound simultaneous requests without changing any part or batch identity.
                for(let i=0;i<manifest.cells.length;i+=4){
                    files.push(...await Promise.all(manifest.cells.slice(i,i+4).map(async cell=>{
                        const r=await fetch(runtimeUrl(directory+'/'+cell.file));
                        if(!r.ok)throw new Error(`City LOD cell unavailable: ${cell.file}`);
                        return parse(new Uint8Array(await r.arrayBuffer()));
                    })));
                }
                return bake=LodBake.combine(files);
            }
            const [response]=await Promise.all([fetch(runtimeUrl('/build/baked/city-lod.bin')),MeshoptDecoder.ready]);
            if(!response.ok){console.warn(`[CityBake] no baked LODs (${response.status}): run node tools/bake/bake-city.mjs; clustering in the browser`);return null;}
            bake=parse(new Uint8Array(await response.arrayBuffer()));
            return bake;
        }catch(error){console.warn('[CityBake] baked LODs unusable; clustering in the browser',error);return null;}
    })();
}

export function parse(bytes:Uint8Array):LodBake{
    const dv=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
    if(dv.getUint32(0,true)!==0x444f4c56||dv.getUint16(4,true)!==1)throw new Error('Not a baked LOD file (VLOD 1)');
    let at=8;
    const varint=()=>{let v=0,shift=0,b=0;do{b=bytes[at++]!;v+=(b&127)*2**shift;shift+=7;}while(b&128);return v;};
    const utf8=new TextDecoder(),text=()=>{const n=varint(),s=utf8.decode(bytes.subarray(at,at+n));at+=n;return s;};
    const chunk=()=>{const n=varint(),b=bytes.subarray(at,at+n);at+=n;return b;};
    const parts=new Map<string,Map<string,BakedLod[]>>();
    for(let p=varint();p>0;p--){
        const id=text(),blocks=new Map<string,BakedLod[]>();parts.set(id,blocks);
        for(let b=varint();b>0;b--){
            const key=text(),list:BakedLod[]=[];blocks.set(key,list);
            for(let k=varint();k>0;k--){
                const vertices=varint(),indices=varint(),hash=dv.getUint32(at,true);at+=4;
                const count=varint(),indexCount=varint();
                list.push({vertices,indices,hash,count,indexCount,subset:chunk(),index:chunk()});
            }
        }
    }
    return new LodBake(parts);
}

/** The same sample hash as the bake tool: FNV-1a over the float bits of 64 evenly spaced positions. */
export function sampleHash(positions:Float32Array,vertices:number):number{
    const bits=new Uint32Array(positions.buffer,positions.byteOffset,vertices*3);
    let h=0x811c9dc5;
    for(let s=0;s<64;s++){const v=Math.floor(s*vertices/64)*3;for(let c=0;c<3;c++){h^=bits[v+c]??0;h=Math.imul(h,0x01000193);}}
    return h>>>0;
}

/** The LOD's batch vertex ids (in its own vertex order) and its index list. */
export function decodeLod(b:BakedLod):{subset:Uint32Array;index:Uint16Array|Uint32Array}{
    const subset=new Uint32Array(b.count);
    for(let i=0,at=0,prev=0;i<b.count;i++){let z=0,shift=0,byte=0;do{byte=b.subset[at++]!;z+=(byte&127)*2**shift;shift+=7;}while(byte&128);prev+=z%2?-(z+1)/2:z/2;subset[i]=prev;}
    const wide=b.count>=65536,index=wide?new Uint32Array(b.indexCount):new Uint16Array(b.indexCount);
    if(b.indexCount)MeshoptDecoder.decodeIndexBuffer(new Uint8Array(index.buffer),b.indexCount,wide?4:2,b.index);
    return {subset,index};
}
