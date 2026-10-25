import {runtimeOnCdn} from './RuntimeAssets.js';

/** Download runtime files before their loaders ask for them (2026-10-25). The start-up loaders take their files one
 * after another, with parsing and batching in between (StripLandmarks keeps parsing serial so every asset's memory is
 * not doubled at once), so a first visit from the CDN spent ~70 s receiving 373 MB that arrives at ~20 MB/s. Here the
 * bytes come down early, a few at a time and at low priority, into the browser's HTTP cache (CDN files are immutable,
 * cached for a year); the loaders then read them from the cache. Nothing is parsed or kept here. Only on the CDN: the
 * dev server's files are already local. */
const MAX_IN_FLIGHT=4;
const queue:string[]=[];
const started=new Set<string>();
let inFlight=0;

export function prefetch(urls:readonly string[]):void{
    if(!runtimeOnCdn)return;
    for(const url of urls)if(!started.has(url)){started.add(url);queue.push(url);}
    pump();
}

function pump():void{
    while(inFlight<MAX_IN_FLIGHT&&queue.length){
        const url=queue.shift()!;inFlight++;
        fetch(url,{priority:'low'} as RequestInit).then(r=>r.ok?r.arrayBuffer():null).catch(()=>null).finally(()=>{inFlight--;pump();});
    }
}
