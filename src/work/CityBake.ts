import * as THREE from 'three';

/** The city bake (2026-10-26, the owner: "add a build step so that when any new geometry is updated, we bake the city so
 * that it's only done once and not in the client at every load").
 *
 * The city's static geometry used to be assembled in every visitor's browser: source meshes merged into batches, texture
 * atlases drawn, facade and silhouette LODs and per-cell shadow casters built (15-20 s of main thread). tools/bake/
 * bake-city.mjs now runs that same code once, in headless Chrome with `?bake=capture`, and this module records what it
 * builds. The tool writes the result as files (src/work/CityBakeLoad.ts reads them): the client loads ready-made buffers.
 *
 * Modes: `capture` (`?bake=capture&bakeServer=...`, localhost: build and record), `off` (`?bake=off`, localhost: build in
 * the browser as before, for A/B), otherwise `use` (load the bake; a part without one is built as before). */
export type BakeMode='capture'|'use'|'off';
const query=typeof location==='undefined'?null:new URLSearchParams(location.search);
const local=typeof location!=='undefined'&&['localhost','127.0.0.1'].includes(location.hostname);
export const bakeMode:BakeMode=!query?'off':local&&query.get('bake')==='capture'?'capture':local&&query.get('bake')==='off'?'off':'use';

type Associations=Map<object,{nodes?:number;meshes?:number;primitives?:number}>;
interface Part {id:string;url:string;root:THREE.Object3D;associations:Associations;blocks:CapturedBlock[];shadows:THREE.Mesh[];extras:Record<string,number|string>}
interface CapturedBlock {key:string;box:THREE.Box3;near:number;far:number;facade:boolean;
    /** the spacing today's LOD clusters at (CityLod; null: none) */spacing:number|null;userData:Record<string,unknown>;
    high:THREE.Mesh[];low:THREE.Mesh[];retained:THREE.Mesh[];merged:THREE.Mesh[]}

class Capture {
    private parts=new Map<THREE.Object3D,Part>();
    /** CityBatches.silhouetteColors, set by that module (so this one imports nothing of the city). */
    silhouette:((batch:THREE.BufferGeometry)=>Uint8Array)|null=null;
    /** A loader's GLB that the bake covers (call before anything moves its meshes). */
    begin(id:string,url:string,root:THREE.Object3D,associations:Associations):void{
        this.parts.set(root,{id,url,root,associations,blocks:[],shadows:[],extras:{}});
    }
    block(owner:THREE.Object3D,block:CapturedBlock):void{this.part(owner).blocks.push(block);}
    private part(owner:THREE.Object3D):Part{
        let part=this.parts.get(owner);
        if(!part){part={id:owner.name,url:'',root:owner,associations:new Map(),blocks:[],shadows:[],extras:{}};this.parts.set(owner,part);}
        return part;
    }
    /** One FNV-1a hash over every built batch and LOD array, in build order (comparing two implementations). */
    checksum():Record<string,string>{
        const hashes:Record<string,number>={};
        const feed=(key:string,array:ArrayBufferView)=>{let h=hashes[key]??0x811c9dc5;const u=new Uint8Array(array.buffer,array.byteOffset,array.byteLength);for(let i=0;i<u.length;i++){h^=u[i]!;h=Math.imul(h,0x01000193);}hashes[key]=h;};
        const parts=[...this.parts.values()].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
        for(const p of parts)for(const b of p.blocks)for(const [level,list] of [['high',b.high],['low',b.low]] as const)for(const m of list){
            const g=m.geometry;
            for(const name of ['position','normal','uv','color']){const a=g.getAttribute(name);if(a)feed(level+'.'+name,a.array);}
            if(g.index)feed(level+'.index',g.index.array);
        }
        for(const p of parts)for(const s of p.shadows){feed('shadow.position',s.geometry.getAttribute('position').array);if(s.geometry.index)feed('shadow.index',s.geometry.index.array);}
        return Object.fromEntries(Object.entries(hashes).map(([k,h])=>[k,(h>>>0).toString(16)]));
    }
    /** Vertex and triangle counts of what was built, per part (for sizing the bake). */
    stats():unknown{
        const out:unknown[]=[];
        const count=(meshes:THREE.Mesh[])=>{let v=0,t=0;for(const m of meshes){v+=m.geometry.getAttribute('position')?.count??0;t+=(m.geometry.index?.count??0)/3;}return {v,t};};
        for(const p of this.parts.values()){
            const high=count(p.blocks.flatMap(b=>b.high)),low=count(p.blocks.flatMap(b=>b.low)),merged=count(p.blocks.flatMap(b=>b.merged));
            out.push({id:p.id,blocks:p.blocks.length,highVertices:high.v,highTriangles:high.t,lowVertices:low.v,lowTriangles:low.t,mergedSourceVertices:merged.v,
                retained:p.blocks.reduce((n,b)=>n+b.retained.length,0),facade:p.blocks.filter(b=>b.facade).length});
        }
        return out;
    }
    shadows(owner:THREE.Object3D,meshes:THREE.Mesh[]):void{this.part(owner).shadows.push(...meshes);}
    extra(owner:THREE.Object3D,key:string,value:number|string):void{const p=this.parts.get(owner);if(p)p.extras[key]=value;}
    get partCount():number{return this.parts.size;}

    /** The near batches, sent to the bake tool (tools/bake/bake-city.mjs): one request per part, then `done`. */
    async export(server:string):Promise<{parts:number;batches:number}>{
        const ids=new Set<string>();let batches=0;
        for(const part of this.parts.values()){
            if(!part.blocks.length)continue;
            if(ids.has(part.id))throw new Error(`City bake: two parts are called "${part.id}"`);ids.add(part.id);
            const blobs:Uint8Array[]=[];let offset=0;
            const blob=(array:ArrayBufferView)=>{const bytes=new Uint8Array(array.buffer,array.byteOffset,array.byteLength).slice();blobs.push(bytes);const at=offset;offset+=bytes.length;return {at,bytes:bytes.length,type:array.constructor.name};};
            const head={id:part.id,blocks:part.blocks.map(b=>({key:b.key,facade:b.facade,spacing:b.spacing,near:b.near,box:[...b.box.min.toArray(),...b.box.max.toArray()],
                batches:b.high.map(m=>{batches++;const g=m.geometry,a=(n:string)=>g.getAttribute(n) as THREE.BufferAttribute;
                    if(!a('position').array.length)throw new Error('City bake: a batch was released before capture');
                    // the normal and the surface row, decoded from the batch's snorm16 x 4 (xyz normal, w row; CityBatches.ts)
                    const packed=a('normal').array as Int16Array,n=a('position').count,normal=new Float32Array(n*3),row=new Float32Array(n);
                    for(let i=0;i<n;i++){for(let c=0;c<3;c++)normal[i*3+c]=Math.max(packed[i*4+c]!/32767,-1);row[i]=packed[i*4+3]!;}
                    return {vertices:n,indices:g.index!.count,position:blob(a('position').array),normal:blob(normal),
                        uv:blob(a('uv').array),color:blob(a('color').array),silhouette:blob(this.silhouette!(g)),row:blob(row),index:blob(g.index!.array)};})}))};
            const json=new TextEncoder().encode(JSON.stringify(head));
            // in 16 MB requests: the browser reports request bodies to the automation pipe, which cannot take half a gigabyte
            const body=concat([u32(json.length),json,...blobs]),chunk=16<<20,count=Math.ceil(body.length/chunk);
            for(let i=0;i<count;i++)await post(`${server}/part?n=${ids.size}&chunk=${i}&of=${count}`,body.subarray(i*chunk,Math.min(body.length,(i+1)*chunk)));
        }
        await post(`${server}/done`,new Uint8Array(0));
        return {parts:ids.size,batches};
    }
}

const u32=(n:number)=>new Uint8Array(new Uint32Array([n]).buffer);
function concat(parts:Uint8Array[]):Uint8Array{let n=0;for(const p of parts)n+=p.length;const out=new Uint8Array(n);let o=0;for(const p of parts){out.set(p,o);o+=p.length;}return out;}
async function post(url:string,body:Uint8Array):Promise<void>{
    const r=await fetch(url,{method:'POST',body:body as unknown as BodyInit});
    if(!r.ok)throw new Error(`City bake: ${url} answered ${r.status}`);
}

/** Recording, while the page runs with `?bake=capture`; null otherwise. */
export const bakeCapture=bakeMode==='capture'?new Capture():null;
if(bakeCapture)(window as unknown as {__cityBake:Capture}).__cityBake=bakeCapture;
/** The tool's server, from `?bakeServer=`. */
export const bakeServer=query?.get('bakeServer')??'';
