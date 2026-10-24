import cdn from './runtime-cdn.json';

/** Where a runtime file loads from (2026-10-24). On the dev server: `/build/...` and `/foliage/...` as always. In a
 * published game, which is one file in object storage with nothing beside it, the Bitmagic CDN copy of the runtime set
 * that tools/release/cdn-upload.mjs made (`runtime-cdn.json`: request path → URL; the files are content-addressed, so
 * a revision query is dropped). `?assets=cdn` uses the CDN on localhost too, to try a publish before making it. */
const files=(cdn as {files:Record<string,{url:string}>}).files;
const local=typeof location!=='undefined'&&['localhost','127.0.0.1'].includes(location.hostname)
    &&new URLSearchParams(location.search).get('assets')!=='cdn';

/** True when runtime files come from the CDN (a published game, or `?assets=cdn`). */
export const runtimeOnCdn=!local;

export function runtimeUrl(path:string):string {
    if(local)return path;
    const q=path.indexOf('?'),key=(q<0?path:path.slice(0,q)).replace(/^\//,'');
    const entry=files[key];
    if(!entry){console.warn(`[RuntimeAssets] not on the CDN: ${key}`);return path;}
    return entry.url;
}
