// Local driving probe: moves the player along the Strip at driving speed in headless Chrome and
// records every long frame, which streaming job (if any) was running at the time, what the renderer
// was creating during it (shader builds, pipelines, GPU buffers/textures, GPU API time) and, with
// --profile, what the main thread was doing. A stall with no overlapping "Loading…" job is a stall the
// player sees without a message.
//
//   node tools/probe-streaming.mjs [--name base] [--speed 20] [--from-z -240] [--to-z 1240] [--laps 1]
//        [--lightweight] (skip renderer/GPU method instrumentation)
//        [--reverse] [--profile] [--viewport 960x540] [--query probe] [--max-seconds 240]
//
// A lap is one pass of the route; --laps 2 drives there and back, which is the case that matters most:
// everything the first pass loaded has been unloaded or hidden again by the time you return.
// Output: build/probe/streaming/<name>/{report.json,summary.txt,console.log}. Local only: it loads the
// dev server (port from .bitmagic/dev.json) and never publishes or uploads anything. One headless
// Chrome at a time, always closed in `finally`; keep the load bounded (small viewport, capped length).
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {execSync} from 'node:child_process';
import {launchSystemChrome} from './lib/bitmagic-cli.mjs';
import {browserRendererArgs} from './lib/bitmagic-cli.mjs';

const argv=process.argv.slice(2);
const opt=(name,fallback)=>{const i=argv.indexOf('--'+name);return i<0?fallback:(argv[i+1]===undefined||argv[i+1].startsWith('--')?true:argv[i+1]);};
const name=String(opt('name','run')),speed=Number(opt('speed',20)),fromZ=Number(opt('from-z',-240)),toZ=Number(opt('to-z',1240));
const jeepMode=opt('jeep',false)===true,laps=jeepMode?1:Number(opt('laps',1)),reverse=opt('reverse',false)===true,profile=opt('profile',false)===true,maxSeconds=Number(opt('max-seconds',240));
const [vw,vh]=String(opt('viewport','960x540')).split('x').map(Number);
const lightweight=opt('lightweight',false)===true;
const query=String(opt('query','probe')),traceGc=opt('trace-gc',false)===true;
const port=JSON.parse(fs.readFileSync('.bitmagic/dev.json','utf8')).gamePort;
const out=path.join('build/probe/streaming',name);fs.mkdirSync(out,{recursive:true});

// The Strip road line from the generated road graph (game metres, x east, z south), always south to north.
const road=JSON.parse(fs.readFileSync('build/geographic-strip/road-network.json','utf8')).stripRoute
  .filter(p=>p[2]>=fromZ-30&&p[2]<=toZ+30).sort((a,b)=>a[2]-b[2]);
const route=road.map(p=>[p[0],p[1],p[2]]);
const cumulative=[0];for(let i=1;i<route.length;i++)cumulative.push(cumulative[i-1]+Math.hypot(route[i][0]-route[i-1][0],route[i][2]-route[i-1][2]));

const browser=await launchSystemChrome({headless:true,args:[...browserRendererArgs(process.env,'webgpu'),'--mute-audio',...(traceGc?['--js-flags=--trace-gc --expose-gc']:[])],command:'local streaming probe'});
const logs=[],errors=[];
let cdp=null,profileStartPage=0,profileData=null;
const deadline=Date.now()+maxSeconds*1000+240000;
try {
  const context=await browser.newContext({viewport:{width:vw,height:vh},deviceScaleFactor:1});
  const page=await context.newPage();
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{const s=m.text();logs.push(s);if(m.type()==='error')errors.push(s);});
  await page.addInitScript((lightweight)=>{
    Object.defineProperty(Element.prototype,'requestPointerLock',{configurable:true,writable:true,value:()=>Promise.resolve()});
    const P=window.__probe={gaps:[],longtasks:[],loaf:[],logs:[],frames:0,last:performance.now(),maxGap:0,sum:0};
    const loop=t=>{const gap=t-P.last;P.last=t;P.frames++;P.sum+=gap;if(gap>P.maxGap)P.maxGap=gap;if(gap>50)P.gaps.push({t:Math.round(t),gap:Math.round(gap)});requestAnimationFrame(loop);};
    requestAnimationFrame(loop);
    try{new PerformanceObserver(l=>{for(const e of l.getEntries())P.longtasks.push({t:Math.round(e.startTime),dur:Math.round(e.duration)});}).observe({type:'longtask',buffered:true});}catch{}
    try{
      const short=s=>({fn:s.sourceFunctionName||s.invoker,src:String(s.sourceURL||'').split('/').slice(-2).join('/').split('?')[0],dur:Math.round(s.duration),pause:Math.round(s.pauseDuration||0)});
      new PerformanceObserver(l=>{for(const e of l.getEntries()){
        P.loaf.push({t:Math.round(e.startTime),dur:Math.round(e.duration),block:Math.round(e.blockingDuration||0),
          render:Math.round(e.renderStart?e.startTime+e.duration-e.renderStart:0),style:Math.round(e.styleAndLayoutStart?e.startTime+e.duration-e.styleAndLayoutStart:0),
          scripts:(e.scripts||[]).map(short)});
        if(P.loaf.length>400)P.loaf.shift();
      }}).observe({type:'long-animation-frame',buffered:true});
    }catch{}
    for(const level of ['info','log','warn','error']){const original=console[level].bind(console);console[level]=(...a)=>{try{if(P.logs.length<4000)P.logs.push({t:Math.round(performance.now()),level,text:a.map(String).join(' ').slice(0,300)});}catch{}original(...a);};}
    // A heartbeat worker: it runs on its own thread, so if the main thread is merely busy it keeps ticking on time,
    // and if the machine is starved (CPU contention, throttling) it stalls too. That separates the two explanations.
    try{
      const code='let last=performance.now();const gaps=[];const origin=performance.timeOrigin;setInterval(()=>{const n=performance.now(),g=n-last;last=n;if(g>40&&gaps.length<2000)gaps.push([Math.round(origin+n-g),Math.round(g)]);},5);onmessage=()=>postMessage({gaps});';
      window.__hb=new Worker(URL.createObjectURL(new Blob([code])));
    }catch{}
    // Time every GPU API call the renderer makes, so a stall can be split into JS work and GPU-object work.
    const G=window.__gpu={};
    if(lightweight)return;
    const wrap=(proto,names)=>{if(!proto)return;for(const n of names){const f=proto[n];if(typeof f!=='function')continue;proto[n]=function(...a){const t=performance.now();try{return f.apply(this,a);}finally{const d=performance.now()-t,e=G[n]||(G[n]={n:0,ms:0});e.n++;e.ms+=d;}};}};
    wrap(window.GPUDevice?.prototype,['createRenderPipeline','createShaderModule','createBindGroup','createBindGroupLayout','createPipelineLayout','createTexture','createBuffer','createSampler']);
    wrap(window.GPUQueue?.prototype,['writeBuffer','writeTexture','copyExternalImageToTexture','submit']);
  },lightweight);
  const url=`http://localhost:${port}/?${query}`;
  await page.goto(url,{waitUntil:'domcontentloaded',timeout:60000});await page.bringToFront();
  const bootDeadline=Date.now()+180000;
  while(Date.now()<bootDeadline && !logs.some(s=>s.includes('🎮 Starting game...'))){
    if(errors.length&&errors.some(e=>/Failed to load|SchemaError/.test(e)))throw Error(errors.join('\n'));
    const choice=page.locator('.start-screen-selection__option').first();
    const play=page.locator('#play-button, .hud-play-button').first();
    if(await choice.isVisible())await choice.click();
    else if(await play.isVisible()){await page.waitForTimeout(500);if(await play.isVisible())await play.click();}
    await page.waitForTimeout(500);
  }
  if(!logs.some(s=>s.includes('🎮 Starting game...')))throw Error('Game did not start');
  await page.waitForFunction(()=>!!window.__afterlightProbe,{timeout:120000});
  const idle=async(label,quietPolls=6)=>{let quiet=0;const end=Date.now()+120000;while(quiet<quietPolls&&Date.now()<end){const busy=await page.evaluate(()=>window.__afterlightProbe.streaming().busy);quiet=busy?0:quiet+1;await page.waitForTimeout(500);}console.log('idle after',label,quiet>=quietPolls);};
  await idle('boot');
  // Move to the start of the route and let everything around it finish loading (boot cost, not drive-by cost).
  const startPoint=reverse?route[route.length-1]:route[0];
  await page.evaluate(([x,y,z])=>window.__afterlightProbe.teleport(x,y+.2,z),startPoint);
  await page.waitForTimeout(1500);await idle('route start',8);await page.waitForTimeout(3000);
  const bootJobs=await page.evaluate(()=>window.__afterlightProbe.streaming().history.length);
  await page.evaluate(()=>{const P=window.__probe;P.gaps.length=0;P.longtasks.length=0;P.loaf.length=0;P.frames=0;P.sum=0;P.maxGap=0;});
  if(profile){cdp=await context.newCDPSession(page);await cdp.send('Profiler.enable');await cdp.send('Profiler.setSamplingInterval',{interval:1000});profileStartPage=await page.evaluate(()=>performance.now());await cdp.send('Profiler.start');}
  // The drive runs inside the page so that every frame sees a fresh position; it holds still while the
  // game itself is held by a streaming job, exactly as the real vehicle is.
  // With --trace-gc (run with DEBUG=pw:browser to see V8's lines) two forced collections with reason "testing" mark page time.
  const gcMark=traceGc?await page.evaluate(()=>{const a=performance.now();window.gc();const b=performance.now();window.gc();return {before:a,afterFirst:b,after:performance.now()};}):null;
  if(jeepMode){
    // The real vehicle: the jeep is set down on the road facing along the route and the player seated in it.
    const a=route[reverse?route.length-1:0],b=route[reverse?route.length-4:3],heading=Math.atan2(b[0]-a[0],b[2]-a[2]);
    const seated=await page.evaluate(([x,y,z,h])=>window.__afterlightProbe.seatJeep(x,y+.6,z,h),[a[0],a[1],a[2],heading]);
    await page.waitForTimeout(2500);
    const state=await page.evaluate(()=>window.__afterlightProbe.jeep());
    console.log('jeep seated',seated,JSON.stringify(state));
    if(!state)throw Error('the player is not in the jeep');
    await idle('jeep placed',8);await page.waitForTimeout(2000);
  }
  const loadSamples=[],busy=[];
  const loadTimer=setInterval(()=>{loadSamples.push([Date.now(),+os.loadavg()[0].toFixed(2)]);},2000);
  const psTimer=setInterval(()=>{try{busy.push(execSync("ps -Ao pcpu,rss,comm -r | head -7 | tail -6",{encoding:'utf8'}).trim().split('\n').map(l=>l.trim().replace(/\s+/g,' ').slice(0,90)));}catch{}},4000);
  const driveStarted=Date.now();
  await page.evaluate((lightweight)=>{
    window.__builds=[];window.__rt={};
    if(lightweight)return;
    // Time the renderer's own stages (inclusive times; they nest) so a long frame can be split into
    // shader building, geometry/texture upload, pipeline lookup and drawing.
    const R=window.__afterlightProbe.renderer(),T=window.__rt={};
    const wrap=(obj,name,label)=>{const f=obj&&obj[name];if(typeof f!=='function'||f.__wrapped)return;const w=function(...a){const t=performance.now();try{return f.apply(this,a);}finally{const d=performance.now()-t,e=T[label]||(T[label]={n:0,ms:0});e.n++;e.ms+=d;}};w.__wrapped=true;obj[name]=w;};
    // Every method of the renderer and of the managers it owns, so whatever blocks shows up by name.
    const wrapAll=(obj,prefix)=>{if(!obj||typeof obj!=='object')return;const seen=new Set();for(let p=obj;p&&p!==Object.prototype;p=Object.getPrototypeOf(p))for(const n of Object.getOwnPropertyNames(p)){if(n==='constructor'||seen.has(n))continue;seen.add(n);const d=Object.getOwnPropertyDescriptor(p,n);if(d&&typeof d.value==='function'&&!/^(get|has|is|set)[A-Z]?.{0,3}$/.test(n))wrap(obj,n,prefix+'.'+n);}};
    wrapAll(R,'R');
    for(const k of Object.keys(R))if(/^_(nodes|geometries|bindings|pipelines|textures|attributes|objects|renderLists|renderContexts|background|animation|info|bundles|lighting|sceneRef)$/.test(k))wrapAll(R[k],k.slice(1));
    wrapAll(R.backend,'backend');
    const E=window.__afterlightProbe.engine();for(const k of ['bloomPipeline','composer','waterFeatures'])if(E[k])wrapAll(E[k],k);
    for(const k of Object.keys(R.backend))if(/Utils$|Pool$|^(utils)$/.test(k))wrapAll(R.backend[k],'backend.'+k);
    window.__builds=[];
    const sigOf=b=>{const o=b.object,m=b.material,g=o&&o.geometry;const attrs=g&&g.attributes?Object.keys(g.attributes).join('+'):'';
      return [o&&(o.isInstancedMesh?'inst':o.isBatchedMesh?'batch':o.isSkinnedMesh?'skin':o.isMesh?'mesh':o.type),m&&m.type,m&&m.transparent?'T':'',m&&(m.side===2?'DS':m.side===1?'BS':'FS'),m&&m.alphaTest?'AT':'',m&&m.map?'map':'',m&&m.normalMap?'nrm':'',m&&m.roughnessMap?'rgh':'',m&&m.metalnessMap?'mtl':'',m&&m.emissiveMap?'ems':'',m&&m.aoMap?'ao':'',m&&m.vertexColors?'vc':'',o&&o.receiveShadow?'rs':'',o&&o.castShadow?'cs':'','a:'+attrs].filter(Boolean).join('|');};
    const cnb=R.backend.createNodeBuilder;
    if(typeof cnb==='function')R.backend.createNodeBuilder=function(...a){const b=cnb.apply(this,a);const ob=b.build;b.build=function(...x){const t=performance.now();try{return ob.apply(this,x);}finally{const d=performance.now()-t,e=T['nodeBuilder.build']||(T['nodeBuilder.build']={n:0,ms:0});e.n++;e.ms+=d;if(window.__builds.length<3000)window.__builds.push({t:Math.round(t),ms:Math.round(d),sig:sigOf(this),name:String(this.object&&this.object.name||'').slice(0,40),src:String(this.object&&this.object.userData&&this.object.userData.source||'').slice(0,40),mat:String(this.material&&this.material.name||'').slice(0,40),lights:this.lightsNode&&this.lightsNode.getLights?this.lightsNode.getLights().length:-1,override:!!(this.scene&&this.scene.overrideMaterial)});}};return b;};
  },lightweight);
  await page.evaluate(({route,cumulative,speed,laps,reverse,jeepMode,lightweight})=>{
    const P=window.__probe;P.gaps=[];P.longtasks=[];P.loaf=[];P.frames=0;P.sum=0;P.maxGap=0;P.last=performance.now();
    const total=cumulative[cumulative.length-1];
    const D=window.__drive={done:false,s:reverse?total:0,dir:reverse?-1:1,lap:0,lapStarts:[performance.now()],samples:[],long:[],heap:[],total};
    const pr=window.__afterlightProbe,R=pr.renderer();let last=performance.now(),i=0,lastHeap=0;
    const counters=()=>{const m=R.info.memory,n=R._nodes?.nodeBuilderCache?.size??0,p=R._pipelines?.caches?.size??0;return {geo:m.geometries,tex:m.textures,prog:m.programs??0,builders:n,pipes:p};};
    const gpuNow=()=>{const o={};for(const k in window.__gpu)o[k]=[window.__gpu[k].n,window.__gpu[k].ms];return o;};
    const rtNow=()=>{const o={};for(const k in window.__rt)o[k]=[window.__rt[k].n,window.__rt[k].ms];return o;};
    // The lights the last render actually used: their ids are part of every lit material's shader cache key.
    const E=pr.engine();let lightSig='',lightSet=new Set();D.lightChanges=[];
    // Sampled at 4 Hz: the lights that are visible all the way up the scene graph (a traversal of the whole scene is too heavy per frame).
    let lastLightScan=0,lastLights=[];
    const lightsNow=()=>{if(lightweight)return [];const t=performance.now();if(t-lastLightScan<250)return lastLights;lastLightScan=t;const out=[];try{E.scene.traverseVisible(o=>{if(o.isLight)out.push(o);});}catch{}lastLights=out;return out;};
    const down=new Set();let stuckSince=0;
    const press=(code,on)=>{if(on===down.has(code))return;if(on)down.add(code);else down.delete(code);document.dispatchEvent(new KeyboardEvent(on?'keydown':'keyup',{code,key:code.replace('Key','').toLowerCase(),bubbles:true,cancelable:true}));};
    const releaseAll=()=>{for(const c of [...down])press(c,false);};
    let prevC=counters(),prevG=gpuNow(),prevR=rtNow(),lastDelta=null;
    const step=now=>{
      const gap=now-last;const dt=Math.min(gap/1000,1/20);last=now;
      const busy=pr.streaming().busy;
      let x,y,z;
      if(jeepMode){
        // Pure pursuit: aim at a point ahead on the route; A turns toward +X (yaw up), D toward -X.
        const st=pr.jeep();
        if(!st){D.error='the player left the jeep';releaseAll();D.done=true;return;}
        x=st.x;y=st.y;z=st.z;
        const forward=D.dir>0;
        let best=Infinity,bj=i,bt=0;
        for(let j=Math.max(0,i-3);j<Math.min(route.length-1,i+12);j++){const a=route[j],b=route[j+1],vx=b[0]-a[0],vz=b[2]-a[2],L=vx*vx+vz*vz||1e-6;let t=((x-a[0])*vx+(z-a[2])*vz)/L;t=Math.max(0,Math.min(1,t));const dx=x-(a[0]+vx*t),dz=z-(a[2]+vz*t),d=dx*dx+dz*dz;if(d<best){best=d;bj=j;bt=t;}}
        i=bj;D.s=cumulative[bj]+bt*(cumulative[bj+1]-cumulative[bj]);
        const ahead=Math.max(14,st.speed*1.2),targetS=forward?Math.min(total,D.s+ahead):Math.max(0,D.s-ahead);
        let k=0;while(k<cumulative.length-2&&cumulative[k+1]<targetS)k++;
        const ta=route[k],tb=route[k+1],tf=(targetS-cumulative[k])/Math.max(1e-6,cumulative[k+1]-cumulative[k]);
        const tx=ta[0]+(tb[0]-ta[0])*tf,tz=ta[2]+(tb[2]-ta[2])*tf;
        const yaw=Math.atan2(st.fx,st.fz),want=Math.atan2(tx-x,tz-z);let err=want-yaw;while(err>Math.PI)err-=2*Math.PI;while(err<-Math.PI)err+=2*Math.PI;
        press('KeyA',err>0.05);press('KeyD',err<-0.05);press('KeyW',st.speed<speed);press('KeyS',false);
        if(st.speed<0.5&&!busy){if(!stuckSince)stuckSince=now;else if(now-stuckSince>9000){D.error='stuck at z='+Math.round(z);releaseAll();D.done=true;return;}}else stuckSince=0;
        if(forward?D.s>=total-12:D.s<=12){releaseAll();D.done=true;return;}
      }else{
        if(!busy)D.s+=D.dir*speed*dt;
        if(D.s>=total&&D.dir>0||D.s<=0&&D.dir<0){D.lap++;D.s=Math.min(total,Math.max(0,D.s));if(D.lap>=laps){D.done=true;return;}D.dir=-D.dir;D.lapStarts.push(now);}
        while(i<cumulative.length-2&&cumulative[i+1]<D.s)i++;while(i>0&&cumulative[i]>D.s)i--;
        const a=route[i],b=route[i+1],span=Math.max(1e-6,cumulative[i+1]-cumulative[i]),f=Math.min(1,Math.max(0,(D.s-cumulative[i])/span));
        x=a[0]+(b[0]-a[0])*f;y=a[1]+(b[1]-a[1])*f+.2;z=a[2]+(b[2]-a[2])*f;
        pr.teleport(x,y,z);
      }
      D.samples.push([Math.round(now),Math.round(D.s),Math.round(x),Math.round(z),busy?1:0,D.lap,jeepMode?Math.round((pr.jeep()?.speed??0)*10)/10:0]);if(D.samples.length>40000)D.samples.shift();
      // A frame's work runs AFTER its rAF timestamp, so a long frame shows up as a long gap one callback later.
      // Depending on whether the engine's callback runs before or after this one, the stall is in the window that
      // ended at the previous callback or in the one that ends now: keep both and report the heavier.
      {const ls=lightsNow(),sig=ls.map(l=>l.id).sort((a,b)=>a-b).join(',');if(sig!==lightSig){const cur=new Set(ls.map(l=>l.id));const added=[],removed=[];for(const l of ls)if(!lightSet.has(l.id))added.push(l.id+':'+(l.type||'')+':'+(l.name||'').slice(0,24));for(const id of lightSet)if(!cur.has(id))removed.push(id);D.lightChanges.push({t:Math.round(now),n:ls.length,types:ls.reduce((m,l)=>(m[l.type]=(m[l.type]||0)+1,m),{}),added:added.slice(0,6),addedN:added.length,removedN:removed.length});lightSig=sig;lightSet=cur;}}
      const c=counters(),g=gpuNow(),rt=rtNow();
      const dc={};for(const k in c)dc[k]=c[k]-prevC[k];
      const dg={};for(const k in g){const dn=g[k][0]-(prevG[k]?.[0]??0),dm=g[k][1]-(prevG[k]?.[1]??0);if(dn>0)dg[k]=[dn,Math.round(dm)];}
      const rows=[];for(const k in rt){const dn=rt[k][0]-(prevR[k]?.[0]??0),dm=rt[k][1]-(prevR[k]?.[1]??0);if(dn>0&&dm>=5)rows.push([k,dn,Math.round(dm)]);}rows.sort((x,y)=>y[2]-x[2]);
      const dr={};for(const [k,dn,dm] of rows.slice(0,16))dr[k]=[dn,dm];
      const curDelta={d:dc,gpu:dg,stages:dr,heavy:rows.length?rows[0][2]:0};
      if(gap>100){const pick=lastDelta&&lastDelta.heavy>curDelta.heavy?lastDelta:curDelta;D.long.push({t:Math.round(now),gap:Math.round(gap),lap:D.lap,z:Math.round(z),busy,d:pick.d,gpu:pick.gpu,stages:pick.stages});}
      lastDelta=curDelta;
      prevC=c;prevG=g;prevR=rt;
      if(now-lastHeap>500){lastHeap=now;const m=performance.memory;if(m)D.heap.push([Math.round(now),Math.round(m.usedJSHeapSize/1048576)]);}
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  },{route,cumulative,speed,laps,reverse,jeepMode,lightweight});
  const driveEnd=Date.now()+maxSeconds*1000;
  while(Date.now()<driveEnd){
    if(await page.evaluate(()=>window.__drive?window.__drive.done:'reloaded')==='reloaded')throw Error('the page reloaded during the run (the dev server hot-reloads every open page when a project file changes)');
    if(await page.evaluate(()=>window.__drive.done))break;
    if(Date.now()>deadline)throw Error('probe deadline');
    await page.waitForTimeout(500);
  }
  clearInterval(loadTimer);clearInterval(psTimer);
  await page.waitForTimeout(2500);
  if(cdp){const r=await cdp.send('Profiler.stop');profileData=r.profile;}
  const data=await page.evaluate(()=>{const P=window.__probe,D=window.__drive;return {
    frames:P.frames,sumMs:P.sum,maxGap:P.maxGap,gaps:P.gaps,longtasks:P.longtasks,loaf:P.loaf,logs:P.logs,
    done:D.done,samples:D.samples,error:D.error||null,long:D.long,heap:D.heap,builds:window.__builds,lightChanges:window.__drive.lightChanges,lapStarts:D.lapStarts,distance:D.s,total:D.total,
    streaming:window.__afterlightProbe.streaming(),resident:window.__afterlightProbe.resident(),timeOrigin:performance.timeOrigin};});
  const heartbeat=await page.evaluate(()=>new Promise(r=>{if(!window.__hb)return r(null);window.__hb.onmessage=e=>r(e.data.gaps);window.__hb.postMessage(0);setTimeout(()=>r(null),3000);}));
  const wall=(Date.now()-driveStarted)/1000;
  const history=data.streaming.history;
  const lapOf=t=>{let l=0;data.lapStarts.forEach((s,i)=>{if(t>=s)l=i;});return l;};
  const posAt=t=>{let best=null;for(const s of data.samples){if(s[0]>t)break;best=s;}return best?{s:best[1],x:best[2],z:best[3]}:null;};
  const longGaps=data.gaps.filter(g=>g.gap>=120).map(g=>{const start=g.t-g.gap;const job=history.filter(h=>h.at<=g.t&&h.at+h.heldMs>=start-5).map(h=>h.key);
    const tasks=data.longtasks.filter(l=>l.t<=g.t&&l.t+l.dur>=start).map(l=>l.dur);
    const loaf=data.loaf.filter(l=>l.t<=g.t&&l.t+l.dur>=start);
    const detail=data.long.find(l=>Math.abs(l.t-g.t)<=3)??null;
    return {lap:lapOf(start),at:start,gap:g.gap,pos:posAt(start),coveredByLoadingJobs:job,longTasksMs:tasks,renderer:detail?{created:detail.d,gpuCalls:detail.gpu,stagesMs:detail.stages}:null,
      loaf:loaf.map(l=>({dur:l.dur,block:l.block,render:l.render,style:l.style,scripts:l.scripts.filter(s=>s.dur>=20).slice(0,6)}))};});
  let attribution=null;
  if(profileData){
    const nodes=new Map(profileData.nodes.map(n=>[n.id,n])),parent=new Map();
    for(const n of profileData.nodes)for(const c of n.children||[])parent.set(c,n.id);
    const label=n=>{const f=n.callFrame;const file=String(f.url||'').replace(/^https?:\/\/[^/]+/,'').split('?')[0].split('/').slice(-3).join('/');return `${f.functionName||'(anonymous)'} ${file}:${f.lineNumber+1}`;};
    const times=[];let tt=profileData.startTime;for(const d of profileData.timeDeltas){tt+=d;times.push(tt);}
    const toPage=us=>profileStartPage+(us-profileData.startTime)/1000;
    attribution=longGaps.filter(g=>g.gap>=250).map(g=>{
      const incl=new Map(),self=new Map();let total=0;
      for(let i=0;i<profileData.samples.length;i++){const pt=toPage(times[i]);if(pt<g.at||pt>g.at+g.gap)continue;
        const dt=(profileData.timeDeltas[i+1]??1000)/1000;total+=dt;
        const seen=new Set();let id=profileData.samples[i];const selfLabel=label(nodes.get(id));self.set(selfLabel,(self.get(selfLabel)||0)+dt);
        while(id!==undefined){const l=label(nodes.get(id));if(!seen.has(l)){seen.add(l);incl.set(l,(incl.get(l)||0)+dt);}id=parent.get(id);}}
      const top=m=>[...m.entries()].filter(([k])=>!/^\((root|program)\)|^\(anonymous\)/.test(k)).sort((a,b)=>b[1]-a[1]).slice(0,14).map(([k,v])=>[k,Math.round(v)]);
      return {at:g.at,gap:g.gap,sampledMs:Math.round(total),idleMs:Math.round(self.get('(idle) :1')||0),gcMs:Math.round(self.get('(garbage collector) :0')||0),topInclusive:top(incl),topSelf:top(self)};
    });
  }
  for(const g of longGaps){const inGap=data.builds.filter(b=>b.t>=g.at-20&&b.t<=g.at+g.gap+20);const by=new Map();for(const b of inGap){const e=by.get(b.sig)||{n:0,ms:0,example:b.name||b.src||b.mat,override:b.override,lights:b.lights};e.n++;e.ms+=b.ms;by.set(b.sig,e);}g.builds={n:inGap.length,ms:inGap.reduce((a,b)=>a+b.ms,0),overridePass:inGap.filter(b=>b.override).length,bySignature:[...by.entries()].sort((a,b)=>b[1].ms-a[1].ms).slice(0,12).map(([sig,e])=>({sig,...e,ms:Math.round(e.ms)}))};}
  for(const g of longGaps){g.lightChangesNearby=data.lightChanges.filter(c=>c.t>=g.at-120&&c.t<=g.at+g.gap+120).map(c=>({dt:c.t-g.at,n:c.n,addedN:c.addedN,removedN:c.removedN,added:c.added}));}
  for(const g of longGaps){const a=data.timeOrigin+g.at,b=a+g.gap;const hb=(heartbeat||[]).filter(h=>h[0]<=b&&h[0]+h[1]>=a);g.workerThreadStalls=heartbeat?{n:hb.length,maxMs:Math.max(0,...hb.map(h=>h[1]))}:null;}
  const mean=data.sumMs/Math.max(1,data.frames);
  const bucket=(n,l)=>data.gaps.filter(g=>g.gap>=n&&(l===undefined||lapOf(g.t-g.gap)===l)).length;
  const perLap=data.lapStarts.map((_,l)=>({lap:l,over100:bucket(100,l),over250:bucket(250,l),over500:bucket(500,l),over1000:bucket(1000,l),stalledSecondsOver250:+(data.gaps.filter(g=>g.gap>=250&&lapOf(g.t-g.gap)===l).reduce((n,g)=>n+g.gap,0)/1000).toFixed(1),maxGap:Math.max(0,...data.gaps.filter(g=>lapOf(g.t-g.gap)===l).map(g=>g.gap))}));
  const speeds=data.samples.map(r=>r[6]||0).filter(v=>v>0);
  const summary={url,speed,laps,jeepMode,lightweight,completed:data.done&&!data.error,distanceMetres:Math.round(data.distance),driveError:data.error,jeepSpeed:jeepMode?{max:Math.max(0,...speeds),mean:+(speeds.reduce((a,b)=>a+b,0)/Math.max(1,speeds.length)).toFixed(1)}:null,route:{points:route.length,metres:Math.round(cumulative[cumulative.length-1]),fromZ,toZ,reverse},driveSeconds:Math.round(wall),frames:data.frames,meanFrameMs:+mean.toFixed(1),maxGapMs:Math.round(data.maxGap),
    gapsOver100:bucket(100),gapsOver250:bucket(250),gapsOver500:bucket(500),gapsOver1000:bucket(1000),
    stalledSecondsOver250:+(data.gaps.filter(g=>g.gap>=250).reduce((n,g)=>n+g.gap,0)/1000).toFixed(1),
    uncoveredLongGaps:longGaps.filter(g=>!g.coveredByLoadingJobs.length).length,coveredLongGaps:longGaps.filter(g=>g.coveredByLoadingJobs.length).length,
    bootJobs,driveJobs:history.length-bootJobs,driveJobsHeldMs:Math.round(history.slice(bootJobs).reduce((n,h)=>n+h.heldMs,0)),
    heapMB:{first:data.heap[0]?.[1],max:Math.max(0,...data.heap.map(h=>h[1])),last:data.heap.at(-1)?.[1]},perLap};
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({gcMark,summary,machine:{busiestProcesses:busy,loadavg:loadSamples,cpus:os.cpus().length,heartbeatStallsOver40ms:heartbeat?heartbeat.length:null,heartbeatWorstMs:heartbeat?Math.max(0,...heartbeat.map(h=>h[1])):null},lightChanges:data.lightChanges,longGaps,jobs:history.slice(bootJobs),attribution,resident:data.resident,rendererLong:data.long,logs:data.logs.filter(l=>/StreamingWork|BuildingVisibility|StripLandmarks|Highrise|Hotel|Concourse/.test(l.text)),errors},null,1));
  fs.writeFileSync(path.join(out,'console.log'),logs.join('\n'));
  const lines=[`PROBE ${name}: ${JSON.stringify(summary)}`,'',`Long gaps (>=120 ms), ${longGaps.length}:`];
  for(const g of longGaps)lines.push(`  lap${g.lap} t=${g.at} gap=${g.gap} ms at z=${g.pos?.z} s=${g.pos?.s}  loading=${g.coveredByLoadingJobs.join(',')||'NONE (no loading message)'}  stages=${JSON.stringify(g.renderer?.stagesMs??null)}\n        gpu=${JSON.stringify(g.renderer?.gpuCalls??null)}`);
  lines.push('','Streaming jobs during the drive:');
  for(const h of history.slice(bootJobs))lines.push(`  ${h.key} "${h.label}" prepare ${Math.round(h.prepareMs)} first-frames ${Math.round(h.revealMs)} held ${Math.round(h.heldMs)} ms`);
  if(attribution){lines.push('','CPU attribution for gaps >= 250 ms:');for(const a of attribution){lines.push(`  gap ${a.gap} ms at t=${a.at}: sampled ${a.sampledMs} ms, idle ${a.idleMs}, gc ${a.gcMs}`);for(const [k,v] of a.topInclusive.slice(0,8))lines.push(`     incl ${v} ms  ${k}`);for(const [k,v] of a.topSelf.slice(0,4))lines.push(`     self ${v} ms  ${k}`);}}
  if(errors.length)lines.push('','ERRORS:',...errors.slice(0,10));
  fs.writeFileSync(path.join(out,'summary.txt'),lines.join('\n'));
  console.log(lines.join('\n'));
} finally {
  // Whatever happened, keep the page's console so a failed boot can be read.
  try{fs.writeFileSync(path.join(out,'console.log'),logs.join('\n'));if(errors.length)fs.writeFileSync(path.join(out,'errors.log'),errors.join('\n'));}catch{}
  await browser.close();
}
