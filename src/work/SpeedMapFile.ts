import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {runtimeUrl} from './RuntimeAssets.js';
import type {SpeedMap} from './DrivingSpeedAssist.js';

/** speed-map.bin (VSPD, tools/optimize/pack-data.mjs, 2026-10-25): u32 magic, u16 version 1, u16 0, u32 roads, points,
 * cells, segments; u16 points per road, u16 reach per road (cm), u8 limit per road, varint-coded deltas of the cell keys,
 * varint segments per cell, varint-coded ascending segments within each cell, then the points (i32 cm x 3, meshopt). */
export async function loadSpeedMap(url:string):Promise<SpeedMap>{
    const response=await fetch(runtimeUrl(url));
    if(!response.ok)throw new Error(`Road speed map unavailable: ${url} (${response.status}; run node tools/optimize/pack-data.mjs)`);
    const buffer=await response.arrayBuffer(),dv=new DataView(buffer),bytes=new Uint8Array(buffer);
    if(dv.getUint32(0,true)!==0x44505356||dv.getUint16(4,true)!==1)throw new Error('Not a speed map (VSPD 1)');
    const roads=dv.getUint32(8,true),points=dv.getUint32(12,true),cells=dv.getUint32(16,true),segments=dv.getUint32(20,true);
    let at=24;
    const align=()=>{at=(at+3)&~3;};
    const counts=new Uint16Array(buffer,at,roads);at+=roads*2;align();
    const reach=new Uint16Array(buffer,at,roads);at+=roads*2;align();
    const limit=new Uint8Array(buffer,at,roads);at+=roads;
    const varint=()=>{let v=0,shift=0,b=0;do{b=bytes[at++]!;v+=(b&127)*2**shift;shift+=7;}while(b&128);return v;};
    const cellKeys=new Uint32Array(cells),cellStart=new Uint32Array(cells+1),list=new Uint32Array(segments),roadStart=new Uint32Array(roads+1);
    for(let c=0,k=0;c<cells;c++){k+=varint();cellKeys[c]=k;}
    for(let c=0;c<cells;c++)cellStart[c+1]=cellStart[c]!+varint();
    for(let c=0,s=0;c<cells;c++){let v=0;for(const end=cellStart[c+1]!;s<end;s++){v+=varint();list[s]=v;}}
    for(let r=0;r<roads;r++)roadStart[r+1]=roadStart[r]!+counts[r]!;
    align();
    const length=dv.getUint32(at,true),coded=new Uint8Array(buffer,at+4,length);
    const decoded=points?await MeshoptDecoder.decodeGltfBufferAsync(points,12,coded,'ATTRIBUTES','NONE'):new Uint8Array(0);
    return {points:new Int32Array(decoded.buffer,decoded.byteOffset,points*3),roadStart,limit,reach,cellKeys,cellStart,segments:list};
}
