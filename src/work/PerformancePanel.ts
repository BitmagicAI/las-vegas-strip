import {GameState,getGameStateManager} from 'engine/core/GameStateManager.js';
import {foliageSettings} from './FoliageSettings.js';
import {shadowSettings,SHADOW_DISTANCE_MIN,SHADOW_DISTANCE_MAX} from './ShadowSettings.js';
import {cityLodStats} from './CityLod.js';
import {getActiveBackend} from 'engine/render/backend/RendererType.js';
import {getActiveQualityController} from 'engine/quality/QualityController.js';
import type {EngineLike} from 'types/game.js';
import {SceneMetrics} from './SceneMetrics.js';
import {cpuReleaseStats} from './CpuGeometryRelease.js';

export interface StreamingMetrics {publicInteriors:string[];guest:{stairs:number;corridors:number;rooms:number};cityCells:number;loading:boolean;legacyInteriorBatches:number}
const compact=new Intl.NumberFormat('en-US',{notation:'compact',maximumFractionDigits:2}),standard=new Intl.NumberFormat('en-US');
const count=(n:number)=>(n>=100000?compact:standard).format(n);
const average=(a:number[])=>a.length?a.reduce((sum,v)=>sum+v,0)/a.length:0;
/** Chrome's JS heap plus typed-array memory; V8 collects hard above ~8 GB of it. */
const jsMemory=()=>{const m=(performance as unknown as {memory?:{usedJSHeapSize:number}}).memory;return m?`${Math.round(m.usedJSHeapSize/1048576)} MB`:'n/a';};
const percentile=(a:number[],p:number)=>{const s=[...a].sort((a,b)=>a-b);return s[Math.min(s.length-1,Math.floor(s.length*p))]??0;};

/** B opens a cursor-driven statistics panel; metrics use the existing render loop. */
export class PerformancePanel {
    readonly metrics:SceneMetrics;
    private shown=false;
    private onKeyDown=(event:KeyboardEvent):void=>{
        if(event.code!=='KeyB'||event.ctrlKey||event.metaKey||event.altKey)return;
        const target=event.target;
        if(target instanceof HTMLElement&&(target.isContentEditable||target.matches('input:not([type=checkbox]):not([type=range]),textarea,select')))return;
        if(!this.shown&&!getGameStateManager().isState(GameState.PLAYING))return;
        event.preventDefault();event.stopImmediatePropagation();
        if(!event.repeat)this.setShown(!this.shown);
    };
    private setShown(shown:boolean):void {
        this.shown=shown;this.root.hidden=!shown;this.metrics.detailed=shown;
        if(shown){this.setExpanded(true);this.engine.enterInteractiveUI?.();this.metrics.requestAudit();}
        else {if(this.root.contains(document.activeElement))(document.activeElement as HTMLElement).blur();this.engine.exitInteractiveUI?.();}
    }
    private unsubscribeFoliage:(()=>void)|null=null;private unsubscribeShadows:(()=>void)|null=null;
    private root=document.createElement('section');private toggle=document.createElement('button');
    private body=document.createElement('div');private numbers=document.createElement('pre');private table=document.createElement('tbody');
    private lastInventory:SceneMetrics['inventory']=null;
    private more=document.createElement('details');private note=document.createElement('p');private lastUi=0;private expanded=true;
    constructor(private engine:EngineLike,private streaming:()=>StreamingMetrics,loadingBetween:(from:number,to:number)=>string|null=()=>null){
        this.root.id='scene-performance';this.root.setAttribute('aria-label','Scene performance');
        this.root.style.cssText='position:fixed;left:18px;top:82px;z-index:85;width:min(375px,calc(100vw - 36px));max-height:calc(100vh - 190px);overflow:auto;background:#10222df2;color:#e8f2f3;border:1px solid #527578;border-radius:6px;font:12px/1.4 system-ui;box-shadow:0 5px 20px #0005;font-variant-numeric:tabular-nums';
        this.toggle.type='button';this.toggle.setAttribute('aria-expanded','true');this.toggle.setAttribute('aria-controls','scene-performance-body');
        this.toggle.style.cssText='width:100%;text-align:left;border:0;background:#19313c;color:#e8f2f3;padding:10px;cursor:pointer;font:600 12px system-ui';
        this.toggle.textContent='Performance · B to close';this.toggle.onclick=()=>this.setExpanded(!this.expanded);this.root.append(this.toggle);
        this.body.id='scene-performance-body';this.body.style.padding='10px';this.numbers.style.cssText='margin:0;font:12px/1.5 ui-monospace,monospace;white-space:pre-wrap';this.body.append(this.numbers);
        this.addShadowControls();
        this.addFoliageControls();
        const summary=document.createElement('summary');summary.textContent='Main-view draw breakdown';summary.style.cursor='pointer';this.more.append(summary);this.more.open=true;
        const table=document.createElement('table');table.style.cssText='width:100%;font:11px/1.5 system-ui;border-collapse:collapse;margin:6px 0';
        const head=document.createElement('thead');head.innerHTML='<tr><th style="text-align:left">Component</th><th>Draws</th><th>Triangles</th><th title="Meshes with fewer than 100 base triangles">Small</th></tr>';table.append(head,this.table);this.more.append(table);this.body.append(this.more);
        this.note.style.cssText='font:10px/1.4 system-ui;color:#b1c9ce;margin:8px 0';this.body.append(this.note);
        const refresh=document.createElement('button');refresh.type='button';refresh.textContent='Refresh scene breakdown';refresh.onclick=()=>this.metrics.requestAudit();this.body.append(refresh);
        const save=document.createElement('button');save.type='button';save.textContent='Save metrics snapshot';save.onclick=()=>this.save();this.body.append(save);
        this.root.append(this.body);document.body.append(this.root);
        this.metrics=new SceneMetrics(engine,()=>this.refresh(),loadingBetween);
        this.root.hidden=true;this.metrics.detailed=false;
        window.addEventListener('keydown',this.onKeyDown,true);
    }
    private addFoliageControls():void {
        const controls=document.createElement('fieldset');controls.style.cssText='margin:0 0 10px;padding:8px;border:1px solid #527578';
        const legend=document.createElement('legend');legend.textContent='Foliage';controls.append(legend);
        const enabled=document.createElement('input');enabled.type='checkbox';enabled.id='foliage-enabled';
        const label=document.createElement('label');label.htmlFor=enabled.id;label.append(enabled,document.createTextNode(' Show trees and grass'));controls.append(label);
        const range=document.createElement('input');range.type='range';range.id='foliage-distance';range.min='25';range.max='200';range.step='5';range.style.width='100%';
        const distance=document.createElement('label');distance.htmlFor=range.id;distance.textContent='Foliage distance';distance.style.display='block';
        const value=document.createElement('output');value.setAttribute('for',range.id);value.style.display='block';
        controls.append(distance,range,value);
        const note=document.createElement('small');note.textContent='Applies to managed foliage. Ground and colliders stay in place. Saved on this browser.';note.style.display='block';controls.append(note);
        enabled.onchange=()=>{foliageSettings.set({enabled:enabled.checked});this.metrics.requestAudit();};
        range.oninput=()=>{foliageSettings.set({distanceScale:Number(range.value)/100});};
        range.onchange=()=>this.metrics.requestAudit();
        this.unsubscribeFoliage=foliageSettings.subscribe(settings=>{enabled.checked=settings.enabled;range.value=String(Math.round(settings.distanceScale*100));range.disabled=!settings.enabled;value.textContent=`${Math.round(settings.distanceScale*100)}% · Grass ${Math.round(36*settings.distanceScale)} m · Trees ${Math.round(650*settings.distanceScale)} m`;range.setAttribute('aria-valuetext',value.textContent);});
        this.body.prepend(controls);
    }
    private addShadowControls():void {
        const controls=document.createElement('fieldset');controls.style.cssText='margin:0 0 10px;padding:8px;border:1px solid #527578';
        const legend=document.createElement('legend');legend.textContent='Sun shadows';controls.append(legend);
        const range=document.createElement('input');range.type='range';range.id='shadow-distance';range.min=String(SHADOW_DISTANCE_MIN);range.max=String(SHADOW_DISTANCE_MAX);range.step='8';range.style.width='100%';
        const label=document.createElement('label');label.htmlFor=range.id;label.textContent='Shadow distance';label.style.display='block';
        const value=document.createElement('output');value.setAttribute('for',range.id);value.style.display='block';
        const note=document.createElement('small');note.textContent='Wider regions use a larger shadow map (more GPU work). Saved on this browser.';note.style.display='block';
        controls.append(label,range,value,note);
        range.oninput=()=>shadowSettings.set({distance:Number(range.value)});
        this.unsubscribeShadows=shadowSettings.subscribe(settings=>{range.value=String(settings.distance);value.textContent=`${settings.distance} m around you`;range.setAttribute('aria-valuetext',value.textContent);});
        this.body.prepend(controls);
    }
    private setExpanded(value:boolean):void {this.expanded=value;this.body.hidden=!value;this.toggle.setAttribute('aria-expanded',String(value));if(this.metrics){this.metrics.detailed=value;if(value)this.metrics.requestAudit();}try{localStorage.setItem('afterlight:performance-expanded',String(value));}catch{}}
    recordUpdate(ms:number):void {this.metrics.recordUpdate(ms);}
    private snapshot(){return {foliage:foliageSettings.get(),shadows:shadowSettings.get(),stalls:this.metrics.stalls.history,lod:cityLodStats(this.engine.scene!),at:new Date().toISOString(),camera:this.engine.camera?.position.toArray(),backend:getActiveBackend(this.engine.renderer),quality:getActiveQualityController()?.debugInfo(),drawingBuffer:{width:this.engine.renderer?.domElement.width,height:this.engine.renderer?.domElement.height},renderCounters:this.metrics.frame,fps:average(this.metrics.frameTimes)?1000/average(this.metrics.frameTimes):0,frameSamples:this.metrics.frameTimes.length,frameMs:{mean:average(this.metrics.frameTimes),p50:percentile(this.metrics.frameTimes,.5),p95:percentile(this.metrics.frameTimes,.95)},cpuMs:{gameUpdateP50:percentile(this.metrics.updateTimes,.5),renderSubmissionP50:percentile(this.metrics.renderTimes,.5),gameUpdateP95:percentile(this.metrics.updateTimes,.95),renderSubmissionP95:percentile(this.metrics.renderTimes,.95)},scene:this.metrics.inventory,submittedMeshes:this.metrics.submitted,physics:this.engine.physicsWorld?.getStats(),streaming:this.streaming(),sampledAt:this.metrics.sampledAt,scanMs:this.metrics.scanMs,scope:'Renderer counters at main-scene end; component draws count actual main-camera mesh submissions. Enabled is not occlusion-tested. CPU spans are not GPU timing. Resident interior assets can be hidden. Physics totals cover the entire world.'};}
    private refresh():void {
        const now=performance.now();if(now-this.lastUi<500)return;this.lastUi=now;
        const m=this.metrics,p50=percentile(m.frameTimes,.5),p95=percentile(m.frameTimes,.95),mean=average(m.frameTimes),fps=mean?1000/mean:0;
        this.toggle.textContent=`${this.expanded?'▾':'▸'} Performance · ${fps.toFixed(0)} fps · ${count(m.frame.calls)} draws · B to close`;
        if(!this.shown||!this.expanded)return;
        const s=this.snapshot(),i=m.inventory,rows=i?.components??[],interior=rows.filter(r=>r.kind==='interior');
        const drawn=rows.reduce((n,r)=>n+r.drawn,0),small=rows.reduce((n,r)=>n+r.smallDrawn,0);
        const memory=this.engine.renderer?.info.memory;
        this.numbers.textContent=[
            `Frame ms       ${p50.toFixed(1)} median / ${p95.toFixed(1)} p95`,
            `Last stall     ${m.stalls.description}` ,
            `Draw calls     ${count(m.frame.calls)}`,
            `Render size    ${s.drawingBuffer.width} × ${s.drawingBuffer.height} · ${s.quality?.tier??'unknown'}`,
            `Triangles      ${count(m.frame.triangles)}`,
            `City LOD       ${s.lod.full} full / ${s.lod.coarse} coarse / ${s.lod.culled} culled blocks`,
            `Objects loaded ${count(i?.objects??0)} · meshes ${count(i?.meshes??0)}`,
            `Meshes         ${count(i?.enabled??0)} enabled / ${count(drawn)} drawn`,
            `Small drawn    ${count(small)} meshes (<100 base triangles)`,
            `Resources      ${count(i?.geometries??0)} geom / ${count(i?.materials??0)} materials`,
            `GPU resources  ${count(memory?.geometries??0)} geom / ${count(memory?.textures??0)} textures`,
            `Lights         ${i?.activeLights??0} active / ${i?.lights??0} loaded`,
            `JS memory      ${jsMemory()} · city CPU copies freed ${cpuReleaseStats().releasedMB} MB`,
            `Physics world  ${count(s.physics?.rigidBodyCount??0)} bodies / ${count(s.physics?.colliderCount??0)} colliders`,
            `Interior draws ${count(interior.reduce((n,r)=>n+r.calls,0))} · ${count(interior.reduce((n,r)=>n+r.triangles,0))} triangles`,
            `Legacy inside  ${s.streaming.legacyInteriorBatches} enabled batches`,
            `Public loaded  ${s.streaming.publicInteriors.length} · guest ${s.streaming.guest.stairs} stairs / ${s.streaming.guest.corridors} halls / ${s.streaming.guest.rooms} rooms`,
            `Collision cells ${s.streaming.cityCells} · ${s.streaming.loading?'LOADING':'idle'}`,
            `CPU ms         update ${s.cpuMs.gameUpdateP50.toFixed(2)} / render ${s.cpuMs.renderSubmissionP50.toFixed(2)}`,
        ].join('\n');
        if(i!==this.lastInventory){
        this.lastInventory=i;this.table.replaceChildren();
        for(const row of [...rows].sort((a,b)=>b.calls-a.calls).filter(r=>r.calls>0).slice(0,8)){
            const tr=document.createElement('tr');tr.title=`${row.kind}; ${row.drawn}/${row.meshes} meshes drawn/loaded; ${row.materials} materials`;
            for(const [index,value] of [row.name,count(row.calls),count(row.triangles),count(row.smallDrawn)].entries()){const td=document.createElement('td');td.textContent=value;td.style.cssText=`padding:2px 0;border-top:1px solid #33505a;text-align:${index?'right':'left'}`;tr.append(td);}this.table.append(tr);
        }
        }
        this.note.textContent=`Scene breakdown refreshed on demand (scan ${m.scanMs.toFixed(1)} ms; ${m.sampledAt?Math.floor((Date.now()-m.sampledAt)/1000):0}s ago). Renderer totals can include shadows/other passes. Enabled ≠ drawn; triangles include instances. CPU ≠ GPU time. Public loaded: ${s.streaming.publicInteriors.join(', ')||'none'}.`;
    }
    private save():void {const url=URL.createObjectURL(new Blob([JSON.stringify(this.snapshot(),null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download='afterlight-performance.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
    dispose():void {window.removeEventListener('keydown',this.onKeyDown,true);if(this.shown)this.setShown(false);this.unsubscribeFoliage?.();this.unsubscribeShadows?.();this.metrics.dispose();this.root.remove();}
}
