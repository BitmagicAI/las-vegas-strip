import type {GLTF,GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {LoaderUtils} from 'three';
import cdn from './runtime-cdn.json';
import {gltfUrlHooks} from './GltfDecoders.js';
import {runtimeOnCdn} from './RuntimeAssets.js';

/** Download runtime files before their loaders ask for them (2026-10-25). The start-up loaders take their files one
 * after another, with parsing and batching in between (StripLandmarks keeps parsing serial so every asset's memory is
 * not doubled at once), so a first visit from the CDN spent ~70 s receiving 373 MB that arrives at ~20 MB/s.
 *
 * The bytes are kept here until their loader takes them (`takePrefetched`, `loadGltf`): the browser's HTTP cache did
 * not keep them (a first try fetched 35 files, 253 MB, twice: large entries are not cached in every profile). A budget
 * of bytes downloaded but not yet taken holds the queue back, so at most ~200 MB wait in memory; sizes come from the
 * CDN map. Only on the CDN: the dev server's files are already local. */
const BUDGET=200*1048576,MAX_IN_FLIGHT=4,UNKNOWN_SIZE=8*1048576;
const sizes=new Map<string,number>();
for(const f of Object.values((cdn as {files:Record<string,{url:string;bytes:number}>}).files))sizes.set(f.url,f.bytes);
const queue:string[]=[];
const pending=new Map<string,Promise<ArrayBuffer|null>>();
let inFlight=0,held=0;

export function prefetch(urls:readonly string[]):void{
    if(!runtimeOnCdn)return;
    for(const url of urls)if(!pending.has(url)&&!queue.includes(url))queue.push(url);
    pump();
}

function pump():void{
    while(inFlight<MAX_IN_FLIGHT&&queue.length){
        const size=sizes.get(queue[0]!)??UNKNOWN_SIZE;
        // always let one file through, so a file over the whole budget still comes down
        if(held>0&&held+size>BUDGET)return;
        const url=queue.shift()!;inFlight++;held+=size;
        pending.set(url,fetch(url).then(r=>r.ok?r.arrayBuffer():null).catch(()=>null).finally(()=>{inFlight--;pump();}));
    }
}

/** The prefetched bytes of `url` (and their budget released), or null when it was never prefetched. */
export function takePrefetched(url:string):Promise<ArrayBuffer|null>|null{
    const bytes=pending.get(url);
    if(bytes){pending.delete(url);held-=sizes.get(url)??UNKNOWN_SIZE;pump();return bytes;}
    const queued=queue.indexOf(url);if(queued>=0)queue.splice(queued,1);
    return null;
}

/** `loader.loadAsync(url)`, from prefetched bytes when there are any (the URL hooks run as for a loaded URL). */
export async function loadGltf(loader:GLTFLoader,url:string):Promise<GLTF>{
    const bytes=await takePrefetched(url);
    if(!bytes)return loader.loadAsync(url);
    const gltf=await loader.parseAsync(bytes,LoaderUtils.extractUrlBase(url));
    for(const hook of gltfUrlHooks){try{hook(gltf.scene,url);}catch(e){console.warn('[Prefetch] url hook failed',e);}}
    return gltf;
}
