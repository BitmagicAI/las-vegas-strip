import {runtimeOnCdn,runtimeUrl} from './RuntimeAssets.js';
/** Where a runtime GLB is loaded from: its optimized copy when one is current.
 *
 * tools/optimize/install-optimized.mjs writes meshopt-compressed copies (float positions, 8-bit
 * normals, 16-bit UVs where they fit; the optimizing-assets skill's presets) to build/optimized/
 * and records each source's size and modification time in build/optimized/manifest.json.
 * The originals stay where they are: Blender and the resort pipelines read and patch them
 * byte by byte, and cannot read meshopt.
 *
 * A copy is used only while its source on disk is the one it was made from (HEAD request:
 * Content-Length and Last-Modified). A pipeline that regenerates a source therefore gets its
 * new geometry immediately, from the original, with a console note to re-run the optimizer;
 * a stale copy can never hide an edit. `?glb=original` loads every original (for A/B). Local
 * development only: a published game (or `?assets=cdn`) gets the runtime set's CDN URL (RuntimeAssets.ts).
 */
interface Entry {size:number;modified:number;optimized:string}
let manifest:Promise<Record<string,Entry>>|null=null;
const local=typeof location!=='undefined'&&['localhost','127.0.0.1'].includes(location.hostname);
const originals=typeof location!=='undefined'&&new URLSearchParams(location.search).get('glb')==='original';

function load():Promise<Record<string,Entry>> {
    manifest??=fetch('/build/optimized/manifest.json',{cache:'no-store'}).then(r=>r.ok?r.json() as Promise<{files:Record<string,Entry>}>:{files:{}}).then(m=>m.files??{}).catch(()=>({}));
    return manifest;
}

export async function glbUrl(url:string):Promise<string> {
    if(runtimeOnCdn)return runtimeUrl(url);
    if(!local||originals)return url;
    const parsed=new URL(url,location.origin),key=parsed.pathname.replace(/^\//,''),entry=(await load())[key];
    if(!entry)return url;
    try{
        const head=await fetch(parsed.pathname,{method:'HEAD',cache:'no-store'});
        const size=Number(head.headers.get('content-length')),modified=Date.parse(head.headers.get('last-modified')??'');
        if(size===entry.size&&Math.floor(modified/1000)===Math.floor(entry.modified/1000))return '/'+entry.optimized+parsed.search;
        console.warn(`[OptimizedGlb] ${key} changed since it was optimized; loading the original. Re-run: node tools/optimize/optimize-runtime-glbs.mjs && node tools/optimize/optimize-runtime-glbs.mjs --variant=webp-textures && node tools/optimize/install-optimized.mjs`);
    }catch{}
    return url;
}
