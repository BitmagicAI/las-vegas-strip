// Standing-still frame-rate probe: boots the game in headless Chrome (WebGPU, this Mac's GPU), leaves the
// player at the spawn point with no input, and measures a series of scenarios one after another in the same
// session — foliage on/off, trees only, grass only, tree shadows, half resolution, frozen shadow map.
// For every scenario it records, per rendered frame: the frame interval, main-thread CPU time spent in
// requestAnimationFrame callbacks, GPU time of every render pass (WebGPU timestamp queries, grouped by
// render target) and the renderer's draw/triangle counters. With --profile it also samples the main thread.
//
//   node tools/probe-idle.mjs [--name idle] [--viewport 1505x772] [--dpr 2] [--seconds 8]
//        [--scenarios foliage-on,no-trees,...] [--profile] [--max-seconds 600]
//
// Output: build/probe/idle/<name>/{report.json,summary.txt,console.log}. Local only (dev server port from
// .bitmagic/dev.json); never publishes or uploads. One headless Chrome, always closed in `finally`.
import fs from 'node:fs';
import path from 'node:path';
import {launchSystemChrome} from './lib/bitmagic-cli.mjs';
import {browserRendererArgs} from './lib/bitmagic-cli.mjs';

const argv=process.argv.slice(2);
const opt=(name,fallback)=>{const i=argv.indexOf('--'+name);return i<0?fallback:(argv[i+1]===undefined||argv[i+1].startsWith('--')?true:argv[i+1]);};
const name=String(opt('name','idle')),seconds=Number(opt('seconds',8)),dpr=Number(opt('dpr',2)),profile=opt('profile',false)===true,maxSeconds=Number(opt('max-seconds',600));
const [vw,vh]=String(opt('viewport','1505x772')).split('x').map(Number);
const traceScenarios=String(opt('trace','')).split(',').filter(Boolean);
// Main-thread view of a Chrome trace: every top-level task over 30 ms with what it spent its time on, and GC totals.
function summarizeTrace(trace){
  const ev=trace.traceEvents||trace;const names=new Map();
  for(const e of ev)if(e.ph==='M'&&e.name==='thread_name')names.set(e.pid+':'+e.tid,e.args.name);
  const main=[...names.entries()].filter(([,n])=>n==='CrRendererMain').map(([k])=>k);
  // The game page's renderer main thread is the one with the most FireAnimationFrame events.
  const counts=new Map();for(const e of ev){const k=e.pid+':'+e.tid;if(main.includes(k)&&e.name==='FireAnimationFrame')counts.set(k,(counts.get(k)||0)+1);}
  const mainKey=[...counts.entries()].sort((a,b)=>b[1]-a[1])[0]?.[0];
  const onMain=ev.filter(e=>e.pid+':'+e.tid===mainKey&&e.ph==='X'&&e.dur!==undefined).sort((a,b)=>a.ts-b.ts);
  const top=onMain.filter(e=>e.name==='RunTask'||e.name==='ThreadControllerImpl::RunTask');
  const gcNames=/^(MajorGC|MinorGC|V8\.GC_|GCEvent|BlinkGC|V8\.GCScavenger|V8\.GCFinalizeMC|V8\.GCIncrementalMarking|V8\.GCMarkCompactor|CppGC)/;
  const gc=onMain.filter(e=>gcNames.test(e.name));
  const gcBy={};for(const e of gc){gcBy[e.name]=gcBy[e.name]||{n:0,ms:0,max:0};gcBy[e.name].n++;gcBy[e.name].ms+=e.dur/1000;gcBy[e.name].max=Math.max(gcBy[e.name].max,e.dur/1000);}
  const t0=onMain[0]?.ts??0,span=((onMain.at(-1)?.ts??0)-t0)/1e6;
  const long=top.filter(e=>e.dur>30000).map(e=>{const inside=onMain.filter(c=>c!==e&&c.ts>=e.ts&&c.ts+c.dur<=e.ts+e.dur);const by={};
    for(const c of inside){if(c.name==='RunTask'||c.name==='ThreadControllerImpl::RunTask')continue;by[c.name]=(by[c.name]||0)+c.dur/1000;}
    const fns=inside.filter(c=>c.name==='FunctionCall'||c.name==='TimerFire'||c.name==='EventDispatch'||c.name==='FireAnimationFrame'||c.name==='v8.callFunction').map(c=>[c.name,Math.round(c.dur/1000),c.args?.data?.functionName||c.args?.data?.url?.split('/').slice(-1)[0]||c.args?.data?.type||'',c.args?.data?.lineNumber]).filter(x=>x[1]>=5).slice(0,8);
    return {atMs:Math.round((e.ts-t0)/1000),ms:Math.round(e.dur/1000),breakdown:Object.entries(by).filter(([,v])=>v>=3).sort((a,b)=>b[1]-a[1]).slice(0,10).map(([k,v])=>[k,Math.round(v)]),calls:fns};});
  const busy=top.reduce((n,e)=>n+e.dur/1000,0);
  // GPU process main thread busy time, for comparison.
  const gpuKey=[...names.entries()].find(([,n])=>n==='CrGpuMain')?.[0];const gpuTop=gpuKey?ev.filter(e=>e.pid+':'+e.tid===gpuKey&&e.ph==='X'&&(e.name==='RunTask'||e.name==='ThreadControllerImpl::RunTask')):[];
  return {seconds:+span.toFixed(1),mainBusyMsPerSecond:Math.round(busy/Math.max(.1,span)),gcMsPerSecond:Math.round(gc.reduce((n,e)=>n+e.dur/1000,0)/Math.max(.1,span)),gc:Object.fromEntries(Object.entries(gcBy).map(([k,v])=>[k,{n:v.n,ms:Math.round(v.ms),maxMs:Math.round(v.max)}])),
    gpuMainBusyMsPerSecond:Math.round(gpuTop.reduce((n,e)=>n+e.dur/1000,0)/Math.max(.1,span)),gpuLongTasks:gpuTop.filter(e=>e.dur>30000).map(e=>[Math.round((e.ts-t0)/1000),Math.round(e.dur/1000)]).slice(0,30),longMainTasks:long};
}
const ALL=['foliage-on','tree-shadows-off','no-trees','no-grass','foliage-off','foliage-off-half-res','foliage-off-frozen-shadow','foliage-off-long'];
const scenarios=String(opt('scenarios',ALL.join(','))).split(',');
const port=JSON.parse(fs.readFileSync('.bitmagic/dev.json','utf8')).gamePort;
const out=path.join('build/probe/idle',name);fs.mkdirSync(out,{recursive:true});

const browser=await launchSystemChrome({headless:true,args:[...browserRendererArgs(process.env,'webgpu'),'--mute-audio'],command:'local idle probe'});
const watchdog=setTimeout(()=>{console.error('probe watchdog: closing the browser');browser.close().finally(()=>process.exit(2));},maxSeconds*1000);
const logs=[],errors=[];
try {
  const context=await browser.newContext({viewport:{width:vw,height:vh},deviceScaleFactor:dpr});
  const page=await context.newPage();
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{const s=m.text();logs.push(s);if(m.type()==='error')errors.push(s);});
  await page.addInitScript(()=>{
    Object.defineProperty(Element.prototype,'requestPointerLock',{configurable:true,writable:true,value:()=>Promise.resolve()});
    // Every rAF callback is timed; a tick's CPU is the sum of the callbacks that ran for that timestamp.
    const raf=window.requestAnimationFrame.bind(window);
    const F=window.__ticks={cpu:new Map(),submits:0};
    window.requestAnimationFrame=cb=>raf(t=>{const s=performance.now();try{cb(t);}finally{F.cpu.set(t,(F.cpu.get(t)||0)+performance.now()-s);}});
    const submit=window.GPUQueue?.prototype.submit;
    if(submit)window.GPUQueue.prototype.submit=function(...a){F.submits++;return submit.apply(this,a);};
  });
  await page.goto(`http://localhost:${port}/?probe&quality=${process.env.PROBE_QUALITY??"ultra"}`,{waitUntil:'domcontentloaded',timeout:60000});await page.bringToFront();
  const bootDeadline=Date.now()+180000;
  let trapped=false;
  const trapFoliage=()=>page.evaluate(()=>{
    // From the moment the game exists: who changes a foliage group's visibility, with a short stack.
    const pr=window.__afterlightProbe;if(!pr)return false;const planting=pr.engine().scene.getObjectByName('Bellagio botanical planting');if(!planting)return false;
    const log=window.__foliageLog=[];const snap=()=>{let n=0;planting.children.forEach(g=>{if(g.visible)n++;});return n;};
    window.__foliageVisibleAtTrap=snap();
    for(const g of planting.children){let v=g.visible;Object.defineProperty(g,'visible',{configurable:true,get:()=>v,set(x){if(x!==v&&log.length<400)log.push({t:Math.round(performance.now()),group:g.name,to:x,stack:String(new Error().stack).split('\n').slice(2,9).map(l=>l.trim().replace(/https?:\/\/[^/]+/,'').replace(/\?[^:]*/,'')).join(' <- ')});v=x;}});}
    let rv=planting.visible;Object.defineProperty(planting,'visible',{configurable:true,get:()=>rv,set(x){if(x!==rv&&log.length<400)log.push({t:Math.round(performance.now()),group:'ROOT',to:x,stack:String(new Error().stack).split('\n').slice(2,9).map(l=>l.trim().replace(/https?:\/\/[^/]+/,'').replace(/\?[^:]*/,'')).join(' <- ')});rv=x;}});
    return true;});
  while(Date.now()<bootDeadline&&!logs.some(s=>s.includes('🎮 Starting game...'))){
    if(!trapped&&opt('trace-foliage',false)===true)trapped=await trapFoliage().catch(()=>false);
    if(errors.some(e=>/Failed to load|SchemaError/.test(e)))throw Error(errors.join('\n'));
    const choice=page.locator('.start-screen-selection__option').first(),play=page.locator('#play-button, .hud-play-button').first();
    if(await choice.isVisible())await choice.click();
    else if(await play.isVisible()){await page.waitForTimeout(500);if(await play.isVisible())await play.click();}
    await page.waitForTimeout(500);
  }
  if(!logs.some(s=>s.includes('🎮 Starting game...')))throw Error('Game did not start');
  await page.waitForFunction(()=>!!window.__afterlightProbe,{timeout:120000});
  const idle=async(quietPolls=6)=>{let quiet=0;const end=Date.now()+120000;while(quiet<quietPolls&&Date.now()<end){quiet=(await page.evaluate(()=>window.__afterlightProbe.streaming().busy))?0:quiet+1;await page.waitForTimeout(500);}};
  await idle(8);

  // Instrument once the renderer exists: GPU timestamps per render pass, labelled by render target.
  const setup=await page.evaluate((noTimestamps)=>{
    const pr=window.__afterlightProbe,R=pr.renderer(),E=pr.engine(),B=R.backend;
    const hasTimestamps=!noTimestamps&&!!B.device?.features?.has('timestamp-query');
    if(hasTimestamps)B.trackTimestamp=true;
    const labels=window.__ctxLabels=new Map();
    const rc=R._renderContexts,get=rc.get.bind(rc);
    rc.get=(rt=null,...rest)=>{const c=get(rt,...rest);if(!labels.has(c.id)){const tex=rt?.texture,name=rt?(rt.name||tex?.name||(rt.depthTexture&&!rt.texture?'depth':'')||'target'):'screen';labels.set(c.id,rt?`${name} ${rt.width}x${rt.height}${rt.samples?' msaa'+rt.samples:''}`:'screen');}return c;};
    // Per-tick record: [t, interval, cpuMs, submits, gpuMs|null, drawCalls, triangles].
    const T=window.__idle={rows:[],gpu:[],passes:new Map(),last:performance.now(),lastSubmits:0,on:false,lastTs:0};
    const pool=()=>B.timestampQueryPool?.render;
    let seen=0;
    const loop=t=>{
      const now=performance.now();
      // CPU of the PREVIOUS tick is complete now.
      const prevT=T.lastTs,cpu=window.__ticks.cpu.get(prevT)||0;window.__ticks.cpu.delete(prevT);
      const submits=window.__ticks.submits-T.lastSubmits;T.lastSubmits=window.__ticks.submits;
      if(T.on&&prevT)T.rows.push([Math.round(prevT*10)/10,Math.round((t-prevT)*100)/100,Math.round(cpu*100)/100,submits,R.info.render.drawCalls,R.info.render.triangles]);
      T.lastTs=t;
      if(hasTimestamps&&pool()){
        R.resolveTimestampsAsync('render').then(()=>{
          const p=pool();if(!p)return;const entries=[...p.timestamps.entries()];
          // The pool keeps every uid it has ever resolved; only the new ones are this resolve's frames.
          const fresh=entries.slice(seen);seen=entries.length;
          const byFrame=new Map();
          for(const [uid,ms] of fresh){const m=uid.match(/^.*?:(\d+):f(\d+)$/);if(!m)continue;const f=+m[2],label=labels.get(+m[1])||('ctx '+m[1]);
            const e=byFrame.get(f)||{ms:0,passes:{}};e.ms+=ms;e.passes[label]=(e.passes[label]||0)+ms;byFrame.set(f,e);}
          if(T.on)for(const [f,e] of byFrame){T.gpu.push([f,Math.round(e.ms*100)/100]);for(const [k,v] of Object.entries(e.passes)){const a=T.passes.get(k)||{n:0,ms:0,frames:new Set()};a.n++;a.ms+=v;a.frames.add(f);T.passes.set(k,a);}}
          if(entries.length>200000){p.timestamps.clear();seen=0;}
        }).catch(()=>{});
      }
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
    // Where the managed foliage is relative to the player, and how much of it is switched on.
    const planting=E.scene.getObjectByName('Bellagio botanical planting');let foliageInfo=null;
    if(planting){planting.updateMatrixWorld(true);const box=new planting.position.constructor();const groups={};let min=[1e9,1e9,1e9],max=[-1e9,-1e9,-1e9];
      planting.children.forEach(g=>{const k=g.name.replace(/ -?\d+,-?\d+ /,' ');const e=groups[k]||(groups[k]={groups:0,visible:0,instances:0,tris:0});e.groups++;if(g.visible){e.visible++;g.traverse(m=>{if(m.isInstancedMesh||m.geometry?.isInstancedBufferGeometry){const t=(m.geometry.index?m.geometry.index.count:m.geometry.attributes.position.count)/3,n=m.isInstancedMesh?m.count:m.geometry.instanceCount;e.instances+=n;e.tris+=t*n;}});}
        g.traverse(m=>{if(m.isInstancedMesh||m.geometry?.isInstancedBufferGeometry){if(m.isInstancedMesh)m.computeBoundingBox();const b=(m.isInstancedMesh?m.boundingBox:m.geometry.boundingBox).clone().applyMatrix4(m.matrixWorld);min=min.map((v,i)=>Math.min(v,b.min.getComponent(i)));max=max.map((v,i)=>Math.max(v,b.max.getComponent(i)));}});});
      box.set(0,0,0);foliageInfo={rootVisible:planting.visible,parentChainVisible:(()=>{let o=planting;while(o){if(!o.visible)return false;o=o.parent;}return true;})(),worldMin:min.map(Math.round),worldMax:max.map(Math.round),groups,settings:JSON.parse(localStorage.getItem('afterlight:foliage:v1')||'null')};}
    const cam=E.camera;
    // Which cameras the scene's onBeforeRender hooks see, in order (foliage/grove LOD selection reads args[2]).
    const S=E.scene,orig=S.onBeforeRender,calls=window.__sceneCameras=[];
    S.onBeforeRender=function(...a){const c=a[2];if(calls.length<400)calls.push([Math.round(performance.now()),c===cam?'MAIN':`${c.type}:${c.name||''}`,Math.round(c.getWorldPosition(c.position.clone()).distanceTo(cam.position))]);return orig.apply(this,a);};
    return {hasTimestamps,backend:R.backend?.constructor?.name,pixelRatio:R.getPixelRatio(),canvas:[R.domElement.width,R.domElement.height],targetFps:E.getTargetFps?.(),position:pr.position(),camera:cam?{pos:cam.position.toArray().map(v=>+v.toFixed(1)),dir:cam.getWorldDirection(cam.position.clone()).toArray().map(v=>+v.toFixed(2))}:null,foliage:foliageInfo,videos:[...document.querySelectorAll('video')].map(v=>({src:v.currentSrc.split('/').pop(),paused:v.paused,size:v.videoWidth+'x'+v.videoHeight}))};
  },opt('no-timestamps',false)===true);
  console.log('setup',JSON.stringify(setup));
  await page.waitForTimeout(1500);
  const sceneCameras=await page.evaluate(()=>window.__sceneCameras.slice(0,60));
  console.log('scene.onBeforeRender cameras (ms, camera, metres from main camera):',JSON.stringify(sceneCameras.slice(0,8)));
  if(opt('trace-foliage',false)===true){
    // Who switches foliage LOD groups, and with which camera position: trap every group's visible setter,
    // then toggle foliage off and on (which re-selects every cell) and keep watching for a few seconds.
    const trace=await page.evaluate(async()=>{
      const E=window.__afterlightProbe.engine(),planting=E.scene.getObjectByName('Bellagio botanical planting'),log=[];
      for(const g of planting.children){let v=g.visible;Object.defineProperty(g,'visible',{configurable:true,get:()=>v,set(x){if(x!==v&&log.length<60)log.push({t:Math.round(performance.now()),group:g.name,to:x,stack:String(new Error().stack).split('\n').slice(2,7).map(l=>l.trim().replace(/https?:\/\/[^/]+/,'').replace(/\?[^:]*/,'')).join(' <- ')});v=x;}});}
      const count=()=>{const vis={};planting.children.forEach(g=>{const k=g.name.split(' ')[0]+' '+g.name.split(' ').pop();vis[k]=(vis[k]||0)+(g.visible?1:0);});return vis;};
      const wait=ms=>new Promise(r=>setTimeout(r,ms)),pr=window.__afterlightProbe,home=pr.position(),steps=[];
      steps.push(['boot log',window.__foliageVisibleAtTrap,(window.__foliageLog||[]).map(l=>[l.t,l.group,l.to,l.stack.slice(0,400)])]);
      await wait(2000);steps.push(['idle 2 s at spawn',count(),log.length]);
      pr.teleport(home.x+700,home.y+40,home.z);await wait(2500);steps.push(['teleported 700 m east',count(),log.length,pr.position()]);
      pr.teleport(home.x,home.y+.2,home.z);await wait(2500);steps.push(['back at spawn',count(),log.length,pr.position()]);
      const box=document.getElementById('foliage-enabled');box.click();await wait(500);box.click();await wait(2500);steps.push(['after toggling foliage off and on',count(),log.length]);
      return {steps,log,rootVisible:planting.visible,settings:localStorage.getItem('afterlight:foliage:v1')};
    });
    fs.writeFileSync(path.join(out,'foliage-trace.json'),JSON.stringify(trace,null,1));console.log('foliage trace: '+trace.log.length+' switches; steps',JSON.stringify(trace.steps),'last',JSON.stringify(trace.log.slice(-3).map(l=>[l.t,l.group,l.to,l.stack.slice(0,160)])));
  }

  // Scenario switches. Each returns the page to the default state when it is undone.
  const scenarioCode={
    'foliage-on':'',
    'tree-shadows-off':`each('Trees',m=>{m.castShadow=false;});`,
    'no-trees':`each('Trees',m=>{m.visible=false;});`,
    'no-grass':`each('Lawn',m=>{m.visible=false;});`,
    'foliage-off':`foliage(false);`,
    'foliage-off-half-res':`foliage(false);R.setPixelRatio(R.getPixelRatio()/2);`,
    'foliage-off-frozen-shadow':`foliage(false);freezeShadow();`,
    'foliage-off-long':`foliage(false);`,
    // What makes the lawn expensive: its lit/shadowed shader, or rasterizing many thin overlapping blades.
    'grass-near-hidden':`each('Lawn',m=>{if(m.parent.name.endsWith('LOD0'))m.visible=false;});`,
    'grass-far-hidden':`each('Lawn',m=>{if(m.parent.name.endsWith('LOD1'))m.visible=false;});`,
    'grass-unlit':`let Basic=null;S.traverse(o=>{for(const m of [o.material].flat())if(m?.isMeshBasicMaterial&&!Basic)Basic=m.constructor;});const saved=window.__grassMats=new Map();each('Lawn',m=>{saved.set(m,m.material);m.material=new Basic({map:m.material.map,color:m.material.color,side:m.material.side});});`,
    'foliage-off-videos-paused':`foliage(false);for(const v of document.querySelectorAll('video'))v.pause();`,
    // Experiment only (irreversible, run it last): drop the CPU copy of every geometry attribute that already has a
    // GPU buffer, so the ArrayBuffers can be collected. Shows what the resident CPU geometry costs in GC.
    'release-cpu-geometry':`foliage(false);const B=R.backend;let freed=0,n=0;const done=new Set();S.traverse(o=>{const g=o.geometry;if(!g)return;for(const a of [...Object.values(g.attributes||{}),g.index].filter(Boolean)){const t=a.isInterleavedBufferAttribute?a.data:a;if(done.has(t)||!t.array||!B.get(t).buffer)continue;done.add(t);freed+=t.array.byteLength;n++;t.array=new t.array.constructor(0);}});window.__released={MB:Math.round(freed/1048576),attributes:n};`,
  };
  const apply=async(code,undo)=>page.evaluate(({code,undo})=>{
    const pr=window.__afterlightProbe,R=pr.renderer(),E=pr.engine(),S=E.scene;
    const planting=S.getObjectByName('Bellagio botanical planting');
    const each=(prefix,fn)=>{if(!planting)throw Error('no foliage root');planting.traverse(o=>{if((o.isInstancedMesh||o.geometry?.isInstancedBufferGeometry)&&o.parent?.name?.startsWith(prefix))fn(o);});};
    const foliage=on=>{const box=document.getElementById('foliage-enabled');if(box.checked!==on)box.click();};
    let sun=null;S.traverse(o=>{if(o.isDirectionalLight&&o.name==='Afterlight focused sun')sun=o;});
    const freezeShadow=()=>{for(const k of ['needsUpdate','autoUpdate'])Object.defineProperty(sun.shadow,k,{configurable:true,get:()=>false,set(){}});};
    if(undo){
      if(planting)planting.traverse(o=>{if(o.isInstancedMesh||o.geometry?.isInstancedBufferGeometry){o.visible=true;o.castShadow=!!o.parent?.name?.startsWith('Trees');}});
      foliage(true);
      if(window.__grassMats){for(const [m,mat] of window.__grassMats)m.material=mat;window.__grassMats=null;}
      if(window.__basePixelRatio)R.setPixelRatio(window.__basePixelRatio);
      if(sun){delete sun.shadow.needsUpdate;delete sun.shadow.autoUpdate;sun.shadow.autoUpdate=true;sun.shadow.needsUpdate=true;}
      return null;
    }
    window.__basePixelRatio=window.__basePixelRatio||R.getPixelRatio();
    // The engine's start-up warm-up can leave foliage groups hidden behind a LOD cache that thinks they are
    // shown (they reappear once the player moves). Toggling the setting re-selects every cell, as the panel does.
    if(!code.includes('foliage(false)')){foliage(false);foliage(true);}
    new Function('R','E','S','each','foliage','freezeShadow',code)(R,E,S,each,foliage,freezeShadow);
    const vis={};if(planting)planting.children.forEach(g=>{const k=g.name.split(' ')[0]+' '+g.name.split(' ').pop();vis[k]=(vis[k]||0)+(g.visible?1:0);});
    return {pixelRatio:R.getPixelRatio(),canvas:[R.domElement.width,R.domElement.height],plantingVisible:planting?.visible,visibleGroups:vis,released:window.__released??null};
  },{code,undo});
  const settle=async()=>{ // until no new pipelines for 2 s (shader builds after a switch are not the steady state)
    const end=Date.now()+30000;let last=-1,stable=0;
    while(Date.now()<end&&stable<4){const n=await page.evaluate(()=>{const R=window.__afterlightProbe.renderer();return (R._pipelines?.caches?.size??0)+(R.info.memory.programs??0);});stable=n===last?stable+1:0;last=n;await page.waitForTimeout(500);}
    await page.waitForTimeout(1500);
  };
  const stats=a=>{if(!a.length)return null;const s=[...a].sort((x,y)=>x-y),q=p=>s[Math.min(s.length-1,Math.floor(s.length*p))];return {mean:+(a.reduce((x,y)=>x+y,0)/a.length).toFixed(2),p50:q(.5),p90:q(.9),p99:q(.99),max:s[s.length-1],n:a.length};};
  const results=[];
  let cdp=null;if(profile){cdp=await context.newCDPSession(page);await cdp.send('Profiler.enable');await cdp.send('Profiler.setSamplingInterval',{interval:500});}
  for(const scenario of scenarios){
    const code=scenarioCode[scenario];if(code===undefined)throw Error('unknown scenario '+scenario);
    const applied=await apply(code,false);
    if(scenario==='release-cpu-geometry'){const c=await context.newCDPSession(page);await c.send('HeapProfiler.enable');await c.send('HeapProfiler.collectGarbage');await c.detach();console.log('released',JSON.stringify(applied.released));}
    await settle();
    const dur=scenario.endsWith('-long')?seconds*3:seconds;
    await page.evaluate(()=>{const T=window.__idle;T.rows=[];T.gpu=[];T.passes=new Map();T.on=true;});
    let profileStart=0;if(cdp){profileStart=await page.evaluate(()=>performance.now());await cdp.send('Profiler.start');}
    const tracing=traceScenarios.includes(scenario);let tcdp=null;
    const heapBefore=await page.evaluate(()=>performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize}:null);
    if(tracing){tcdp=await context.newCDPSession(page);await tcdp.send('Tracing.start',{transferMode:'ReturnAsStream',traceConfig:{recordMode:'recordContinuously',includedCategories:['devtools.timeline','v8','v8.gc','disabled-by-default-devtools.timeline','disabled-by-default-v8.gc','blink','gpu','viz','toplevel','disabled-by-default-devtools.timeline.frame']}});}
    await page.waitForTimeout(dur*1000);
    const prof=cdp?(await cdp.send('Profiler.stop')).profile:null;
    const heapAfter=await page.evaluate(()=>performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize}:null);
    let traceSummary=null;
    if(tcdp){
      const done=new Promise(r=>tcdp.once('Tracing.tracingComplete',r));await tcdp.send('Tracing.end');const {stream}=await done;
      let text='';for(;;){const c=await tcdp.send('IO.read',{handle:stream,size:4<<20});text+=c.base64Encoded?Buffer.from(c.data,'base64').toString('utf8'):c.data;if(c.eof)break;}await tcdp.send('IO.close',{handle:stream});
      const tracePath=path.join(out,scenario+'.trace.json');fs.writeFileSync(tracePath,text);
      traceSummary=summarizeTrace(JSON.parse(text));
    }
    const data=await page.evaluate(()=>{const T=window.__idle;T.on=false;return {rows:T.rows,gpu:T.gpu,passes:[...T.passes.entries()].map(([k,v])=>[k,v.n,v.ms,v.frames.size])};});
    await page.waitForTimeout(400);
    await page.screenshot({path:path.join(out,scenario+'.png')});
    await apply('',true);
    const rendered=[];let lastRendered=null;
    for(const r of data.rows){if(r[3]>0){if(lastRendered!==null)rendered.push({interval:r[0]-lastRendered,cpu:r[2],draws:r[4],tris:r[5]});lastRendered=r[0];}}
    const gpuFrames=data.gpu.length;
    const passes=data.passes.map(([k,n,ms,frames])=>({pass:k,perFrameMs:+(ms/Math.max(1,gpuFrames)).toFixed(2),passesPerFrame:+(n/Math.max(1,gpuFrames)).toFixed(2)})).sort((a,b)=>b.perFrameMs-a.perFrameMs);
    let cpuTop=null;
    if(prof){
      const nodes=new Map(prof.nodes.map(n=>[n.id,n])),parent=new Map();for(const n of prof.nodes)for(const c of n.children||[])parent.set(c,n.id);
      const label=n=>{const f=n.callFrame;const file=String(f.url||'').replace(/^https?:\/\/[^/]+/,'').split('?')[0].split('/').slice(-2).join('/');return `${f.functionName||'(anon)'} ${file}:${f.lineNumber+1}`;};
      const self=new Map(),incl=new Map();let total=0;
      for(let i=0;i<prof.samples.length;i++){const dt=(prof.timeDeltas[i+1]??500)/1000;total+=dt;let id=prof.samples[i];self.set(label(nodes.get(id)),(self.get(label(nodes.get(id)))||0)+dt);const seen=new Set();while(id!==undefined){const l=label(nodes.get(id));if(!seen.has(l)){seen.add(l);incl.set(l,(incl.get(l)||0)+dt);}id=parent.get(id);}}
      const top=(m,k)=>[...m.entries()].filter(([l])=>!/^\((root|program|anon)\)/.test(l)).sort((a,b)=>b[1]-a[1]).slice(0,k).map(([l,v])=>[l,+(v/Math.max(1,rendered.length)).toFixed(2)]);
      cpuTop={sampledMs:Math.round(total),idleMsPerFrame:+((self.get('(idle) :0')||self.get('(idle) :1')||0)/Math.max(1,rendered.length)).toFixed(2),gcMsPerFrame:+((self.get('(garbage collector) :0')||self.get('(garbage collector) :1')||0)/Math.max(1,rendered.length)).toFixed(2),selfMsPerFrame:top(self,25),inclusiveMsPerFrame:top(incl,40)};
    }
    const interval=stats(rendered.map(r=>r.interval));
    const result={scenario,applied,seconds:dur,renderedFrames:rendered.length,fps:interval?+(1000/interval.mean).toFixed(1):0,
      frameIntervalMs:interval,cpuMs:stats(rendered.map(r=>r.cpu)),gpuMs:stats(data.gpu.map(g=>g[1])),
      heapMB:heapBefore&&heapAfter?{before:Math.round(heapBefore.used/1048576),after:Math.round(heapAfter.used/1048576),total:Math.round(heapAfter.total/1048576)}:null,trace:traceSummary,
      drawCalls:stats(rendered.map(r=>r.draws)),triangles:stats(rendered.map(r=>r.tris)),gpuPasses:passes.slice(0,14),cpuProfile:cpuTop,
      series:rendered.map(r=>[+r.interval.toFixed(1),+r.cpu.toFixed(1)]),gpuSeries:data.gpu.map(g=>g[1])};
    results.push(result);
    console.log(`${scenario.padEnd(26)} ${String(result.fps).padStart(5)} fps  interval p50 ${interval?.p50?.toFixed(1)} p90 ${interval?.p90?.toFixed(1)} max ${interval?.max?.toFixed(1)}  cpu p50 ${result.cpuMs?.p50?.toFixed(1)}  gpu p50 ${result.gpuMs?.p50?.toFixed(1)} p90 ${result.gpuMs?.p90?.toFixed(1)}  draws ${result.drawCalls?.p50}  tris ${result.triangles?.p50}`);
    for(const p of passes.slice(0,6))console.log(`     gpu ${String(p.perFrameMs).padStart(7)} ms  x${p.passesPerFrame}  ${p.pass}`);
  }
  const quality=await page.evaluate(()=>{try{return window.__bmDebug?.getQuality?.()??null;}catch{return null;}});
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({setup,sceneCameras,viewport:[vw,vh],dpr,quality,results,errors:errors.slice(0,20)},null,1));
  const lines=[`IDLE PROBE ${name} viewport ${vw}x${vh} @${dpr} canvas ${setup.canvas.join('x')} timestamps=${setup.hasTimestamps}`];
  for(const r of results){lines.push(`${r.scenario.padEnd(26)} ${r.fps} fps | interval ms p50 ${r.frameIntervalMs?.p50?.toFixed(1)} p90 ${r.frameIntervalMs?.p90?.toFixed(1)} max ${r.frameIntervalMs?.max?.toFixed(1)} | cpu ms p50 ${r.cpuMs?.p50?.toFixed(1)} p90 ${r.cpuMs?.p90?.toFixed(1)} | gpu ms p50 ${r.gpuMs?.p50?.toFixed(1)} p90 ${r.gpuMs?.p90?.toFixed(1)} max ${r.gpuMs?.max?.toFixed(1)} | draws ${r.drawCalls?.p50} tris ${r.triangles?.p50}`);
    for(const p of r.gpuPasses.slice(0,8))lines.push(`      gpu ${p.perFrameMs} ms x${p.passesPerFrame} ${p.pass}`);
    if(r.heapMB)lines.push(`      JS heap ${r.heapMB.before} -> ${r.heapMB.after} MB (total ${r.heapMB.total} MB)`);
    if(r.trace){lines.push(`      trace: main thread busy ${r.trace.mainBusyMsPerSecond} ms/s, GC ${r.trace.gcMsPerSecond} ms/s, GPU process main ${r.trace.gpuMainBusyMsPerSecond} ms/s; GC ${JSON.stringify(r.trace.gc)}`);for(const t of r.trace.longMainTasks.slice(0,12))lines.push(`        long task at ${t.atMs} ms: ${t.ms} ms  ${JSON.stringify(t.breakdown)} ${JSON.stringify(t.calls)}`);}
    if(r.cpuProfile){lines.push(`      cpu profile per frame: idle ${r.cpuProfile.idleMsPerFrame} gc ${r.cpuProfile.gcMsPerFrame}`);for(const [l,v] of r.cpuProfile.selfMsPerFrame.slice(0,10))lines.push(`        self ${v} ms ${l}`);}}
  fs.writeFileSync(path.join(out,'summary.txt'),lines.join('\n'));
  console.log(lines.join('\n'));
} finally {
  clearTimeout(watchdog);
  try{fs.writeFileSync(path.join(out,'console.log'),logs.join('\n'));}catch{}
  await browser.close();
}
