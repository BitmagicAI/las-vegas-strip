import * as THREE from 'three';
import type {EngineLike} from 'types/game.js';
import {activeDeviceQualityTier} from 'engine/quality/DeviceQuality.js';
import {RealisticWater} from './RealisticWater.js';

/** `?stalls`, on any host, the published game included (2026-10-25: the owner sees a long stall on the first camera turn
 * and a flickering lake in Chrome that headless Chrome does not reproduce). Lists every frame longer than 200 ms in a
 * corner of the screen (and the console) with what happened in it: shader builds and GPU pipelines, new render
 * contexts, a post-processing rebuild, a quality-tier or resolution change, a lake-mirror resize, streaming. Off
 * without the flag: nothing is wrapped and nothing runs. */
const STALL_MS=200,LINES=14;
export function installStallReport(engine:EngineLike,streamingBusy:()=>boolean):void{
    if(typeof location==='undefined'||!new URLSearchParams(location.search).has('stalls'))return;
    const renderer=engine.renderer as unknown as {
        _nodes?:{nodeBuilderCache:Map<unknown,unknown>};
        _renderContexts?:{get:(...a:unknown[])=>object};
        backend:{createProgram:(p:unknown)=>void;createRenderPipeline:(ro:unknown,promises:unknown)=>void};
        getDrawingBufferSize(v:THREE.Vector2):THREE.Vector2;
    };
    let pipelines=0,programs=0,contexts=0;
    const createProgram=renderer.backend.createProgram.bind(renderer.backend);
    renderer.backend.createProgram=p=>{programs++;createProgram(p);};
    const createRenderPipeline=renderer.backend.createRenderPipeline.bind(renderer.backend);
    renderer.backend.createRenderPipeline=(ro,promises)=>{pipelines++;createRenderPipeline(ro,promises);};
    const seen=new WeakSet<object>(),rc=renderer._renderContexts;
    if(rc){const get=rc.get.bind(rc);rc.get=(...a:unknown[])=>{const c=get(...a);if(!seen.has(c)){seen.add(c);contexts++;}return c;};}

    const box=document.createElement('div');
    box.style.cssText='position:fixed;right:8px;top:8px;z-index:2147483647;max-width:46ch;padding:6px 8px;border-radius:6px;'
        +'background:rgba(0,0,0,.72);color:#e8f0ff;font:11px/1.35 ui-monospace,Menlo,monospace;white-space:pre-wrap;pointer-events:none';
    document.body.appendChild(box);
    const lines:string[]=[];
    const size=new THREE.Vector2();
    let last=0,frames=0,fpsAt=0,fps=0;
    let builds=renderer._nodes?.nodeBuilderCache.size??0,pipes=0,progs=0,ctxs=0;
    let tier=activeDeviceQualityTier(),bw=0,bh=0,signature='',mirror='',busy=false;
    const postFx=()=>String((engine as unknown as {postFx?:{build?:{signature?:string|null}}}).postFx?.build?.signature??'');
    const mirrors=()=>{let s='';for(const m of RealisticWater.mirrors)s+=m.target?`${m.target.width}x${m.target.height} `:'- ';return s;};
    const header=()=>`[stalls] ${activeDeviceQualityTier()} · ${bw}x${bh} · ${fps} fps · lake mirror ${mirror||'off'}`;
    const frame=(t:number)=>{
        requestAnimationFrame(frame);
        frames++;if(t-fpsAt>=1000){fps=Math.round(frames*1000/(t-fpsAt));frames=0;fpsAt=t;}
        renderer.getDrawingBufferSize(size);
        const nowBuilds=renderer._nodes?.nodeBuilderCache.size??0,nowTier=activeDeviceQualityTier(),nowSig=postFx(),nowMirror=mirrors(),nowBusy=streamingBusy();
        const gap=last?t-last:0;last=t;
        if(gap>STALL_MS){
            const what:string[]=[];
            if(nowBuilds!==builds)what.push(`${nowBuilds-builds} shader builds`);
            if(pipelines!==pipes)what.push(`${pipelines-pipes} pipelines`);
            if(programs!==progs)what.push(`${programs-progs} shaders`);
            if(contexts!==ctxs)what.push(`${contexts-ctxs} new render contexts`);
            if(nowSig!==signature)what.push('post-processing rebuilt');
            if(nowTier!==tier)what.push(`tier ${tier}→${nowTier}`);
            if(size.x!==bw||size.y!==bh)what.push(`resolution ${bw}x${bh}→${size.x}x${size.y}`);
            if(nowMirror!==mirror)what.push(`mirror ${mirror||'-'}→${nowMirror}`);
            if(nowBusy||busy)what.push('streaming');
            const line=`${(t/1000).toFixed(1)}s  ${Math.round(gap)} ms  ${what.join(', ')||'(nothing counted: GPU or main thread)'}`;
            lines.unshift(line);if(lines.length>LINES)lines.length=LINES;
            console.info('[stalls] '+line);
        }else if(nowTier!==tier||size.x!==bw||size.y!==bh||nowSig!==signature||nowMirror!==mirror){
            // changes without a stall are worth a line too (a resized mirror can flicker without stalling)
            const line=`${(t/1000).toFixed(1)}s  change: ${nowTier!==tier?`tier ${tier}→${nowTier} `:''}${size.x!==bw||size.y!==bh?`resolution ${bw}x${bh}→${size.x}x${size.y} `:''}${nowSig!==signature?'post-processing rebuilt ':''}${nowMirror!==mirror?`mirror ${mirror||'-'}→${nowMirror}`:''}`;
            if(bw)lines.unshift(line);if(lines.length>LINES)lines.length=LINES;
            if(bw)console.info('[stalls] '+line);
        }
        builds=nowBuilds;pipes=pipelines;progs=programs;ctxs=contexts;tier=nowTier;bw=size.x;bh=size.y;signature=nowSig;mirror=nowMirror;busy=nowBusy;
        box.textContent=header()+'\n'+lines.join('\n');
    };
    requestAnimationFrame(frame);
    console.info('[stalls] reporting frames over '+STALL_MS+' ms');
}
