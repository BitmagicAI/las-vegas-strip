import {runtimeUrl} from './RuntimeAssets.js';

/** Metadata records as tools/optimize/pack-data.mjs writes them (VDAT, 2026-10-25; the format is described there): the
 * game's venue lists, the Sphere, the coaster's route, the PBR sets, hotel module levels and bridge concourses, without
 * JSON. Objects come back as plain objects; every number list is a typed array (a view of the file, or a Float32Array for
 * lists stored on a grid); lists of number lists are flat (stride known to the reader); long lists of numeric records come
 * back as columns: `{length, <field>: typed array}`. */
export type Numbers=Uint8Array|Int8Array|Uint16Array|Int16Array|Uint32Array|Int32Array|Float32Array|Float64Array;

export function decodeRecords(buffer:ArrayBuffer):unknown{
    const dv=new DataView(buffer),bytes=new Uint8Array(buffer);
    if(dv.getUint32(0,true)!==0x54414456||dv.getUint16(4,true)!==1)throw new Error('Not a record file (VDAT 1)');
    const blob=(12+dv.getUint32(8,true)+7)&~7;
    let at=12;
    const varint=()=>{let v=0,shift=0,b=0;do{b=bytes[at++]!;v+=(b&127)*2**shift;shift+=7;}while(b&128);return v;};
    const utf8=new TextDecoder(),count=varint(),strings=new Array<string>(count);
    for(let i=0;i<count;i++){const n=varint();strings[i]=utf8.decode(bytes.subarray(at,at+n));at+=n;}
    const f64=()=>{const v=dv.getFloat64(at,true);at+=8;return v;};
    const numbers=():Numbers=>{
        const kind=bytes[at++]!,stride=varint(),n=varint(),offset=blob+varint();
        switch(kind){
            case 1:return new Uint8Array(buffer,offset,n);
            case 2:return new Int8Array(buffer,offset,n);
            case 3:return new Uint16Array(buffer,offset,n);
            case 4:return new Int16Array(buffer,offset,n);
            case 5:return new Uint32Array(buffer,offset,n);
            case 6:return new Int32Array(buffer,offset,n);
            case 7:return new Float32Array(buffer,offset,n);
            case 8:return new Float64Array(buffer,offset,n);
        }
        const step=f64(),origin=new Float64Array(stride);for(let c=0;c<stride;c++)origin[c]=f64();
        const q=kind===9?new Uint16Array(buffer,offset,n):new Uint32Array(buffer,offset,n),out=new Float32Array(n);
        for(let i=0,c=0;i<n;i++){out[i]=origin[c]!+q[i]!*step;if(++c===stride)c=0;}
        return out;
    };
    const value=():unknown=>{
        const tag=bytes[at++]!;
        switch(tag){
            case 0:return null;
            case 1:return false;
            case 2:return true;
            case 3:{const z=varint();return z%2?-(z+1)/2:z/2;}
            case 4:{const v=dv.getFloat32(at,true);at+=4;return v;}
            case 5:return f64();
            case 6:return strings[varint()];
            case 7:{const n=varint(),list=new Array<unknown>(n);for(let i=0;i<n;i++)list[i]=value();return list;}
            case 8:{const n=varint(),o:Record<string,unknown>={};for(let i=0;i<n;i++){const k=strings[varint()]!;o[k]=value();}return o;}
            case 9:return numbers();
            case 10:{const rows=varint(),n=varint(),o:Record<string,unknown>={length:rows};for(let i=0;i<n;i++){const k=strings[varint()]!;at++;o[k]=numbers();}return o;}
        }
        throw new Error(`Record file: unknown tag ${tag}`);
    };
    return value();
}

/** Fetch and decode a .bin record file (the URL as the dev server serves it; runtimeUrl maps it to the CDN). */
export async function loadRecords<T>(url:string):Promise<T>{
    const response=await fetch(runtimeUrl(url));
    if(!response.ok)throw new Error(`Data unavailable: ${url} (${response.status}; run node tools/optimize/pack-data.mjs)`);
    return decodeRecords(await response.arrayBuffer()) as T;
}
