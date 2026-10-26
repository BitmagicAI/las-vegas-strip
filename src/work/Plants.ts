import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {runtimeUrl} from './RuntimeAssets.js';

/** One list of plants from a VPLT file (tools/optimize/pack-data.mjs, 2026-10-25): 8 bytes a plant, x, y, z on a 16-bit
 * grid over the list's bounds, yaw in 1/256 turns, scale in 1/255 of its range. Read with the accessors; nothing is
 * expanded into JS numbers ahead of use. */
export class PlantList {
    private readonly grid:Uint16Array;
    constructor(readonly count:number,private readonly origin:Float32Array,private readonly step:Float32Array,
        private readonly scaleMin:number,private readonly scaleStep:number,private readonly data:Uint8Array){
        this.grid=new Uint16Array(data.buffer,data.byteOffset,count*4);
    }
    x(i:number):number{return this.origin[0]!+this.grid[i*4]!*this.step[0]!;}
    y(i:number):number{return this.origin[1]!+this.grid[i*4+1]!*this.step[1]!;}
    z(i:number):number{return this.origin[2]!+this.grid[i*4+2]!*this.step[2]!;}
    yaw(i:number):number{return this.data[i*8+6]!*(Math.PI/128);}
    scale(i:number):number{return this.scaleMin+this.data[i*8+7]!*this.scaleStep;}
}

export async function loadPlants(url:string):Promise<{trees:PlantList;grass:PlantList}>{
    const response=await fetch(runtimeUrl(url));
    if(!response.ok)throw new Error(`Plant placements unavailable: ${url} (${response.status}; run node tools/optimize/pack-data.mjs)`);
    const buffer=await response.arrayBuffer(),dv=new DataView(buffer);
    if(dv.getUint32(0,true)!==0x544c5056||dv.getUint16(4,true)!==1)throw new Error('Not a plant list (VPLT 1)');
    let at=8;
    const list=async()=>{
        const count=dv.getUint32(at,true),header=new Float32Array(buffer.slice(at+4,at+36));at+=36;
        const length=dv.getUint32(at,true),coded=new Uint8Array(buffer,at+4,length);at=(at+4+length+3)&~3;
        const data=count?await MeshoptDecoder.decodeGltfBufferAsync(count,8,coded,'ATTRIBUTES','NONE'):new Uint8Array(0);
        return new PlantList(count,header.subarray(0,3),header.subarray(3,6),header[6]!,header[7]!,data);
    };
    const trees=await list(),grass=await list();
    return {trees,grass};
}
