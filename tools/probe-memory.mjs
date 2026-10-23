// Memory accounting probe: boots the game in headless Chrome, stands at the spawn point, and answers two
// questions about the renderer process's JavaScript memory:
//   1. What is alive: V8 heap vs ArrayBuffer backing stores (CDP Runtime.getHeapUsage), every scene
//      geometry's typed arrays grouped by owner, WebAssembly memories, and large typed arrays allocated by
//      constructor that are still alive (grouped by the code that allocated them).
//   2. What is allocated per second while standing still: typed-array constructions by call site, and V8's
//      sampling heap profiler over the same window (garbage included), by allocation site.
// V8 counts JS heap + ArrayBuffers + embedder memory against one global limit; near that limit it runs a
// full mark-compact every ~100 ms of script time, which is what makes an idle frame rate jump around.
//
//   node tools/probe-memory.mjs [--name memory] [--viewport 960x540] [--seconds 5]
//
// Output: build/probe/memory/<name>/{report.json,summary.txt}. Local only; one headless Chrome, closed in `finally`.
import fs from 'node:fs';
import path from 'node:path';
import {launchSystemChrome} from './lib/bitmagic-cli.mjs';
import {browserRendererArgs} from './lib/bitmagic-cli.mjs';

const argv=process.argv.slice(2);
const opt=(name,fallback)=>{const i=argv.indexOf('--'+name);return i<0?fallback:(argv[i+1]===undefined||argv[i+1].startsWith('--')?true:argv[i+1]);};
const name=String(opt('name','memory')),seconds=Number(opt('seconds',5));
const [vw,vh]=String(opt('viewport','960x540')).split('x').map(Number);
const port=JSON.parse(fs.readFileSync('.bitmagic/dev.json','utf8')).gamePort;
const out=path.join('build/probe/memory',name);fs.mkdirSync(out,{recursive:true});
const MB=n=>Math.round(n/1048576);

const browser=await launchSystemChrome({headless:true,args:[...browserRendererArgs(process.env,'webgpu'),'--mute-audio','--enable-precise-memory-info'],command:'local memory probe'});
const watchdog=setTimeout(()=>{console.error('probe watchdog: closing the browser');browser.close().finally(()=>process.exit(2));},600000);
const logs=[];
try {
  const context=await browser.newContext({viewport:{width:vw,height:vh},deviceScaleFactor:1});
  const page=await context.newPage();
  page.on('console',m=>logs.push(m.text()));
  await page.addInitScript(()=>{
    Object.defineProperty(Element.prototype,'requestPointerLock',{configurable:true,writable:true,value:()=>Promise.resolve()});
    const M=window.__mem={large:[],counting:false,churn:new Map(),wasm:[]};
    const site=()=>String(new Error().stack).split('\n').slice(3,7).map(l=>l.trim().replace(/^at /,'').replace(/https?:\/\/[^/]+/,'').replace(/\?[^:)]*/,'')).join(' <- ');
    // Typed-array constructions are only counted inside the measuring window (installing this from the first
    // script breaks the game's loading). Code looks the global up at call time, so swapping it later works.
    M.install=()=>{M.saved={};for(const n of ['Float32Array','Float64Array','Uint32Array','Int32Array','Uint16Array','Int16Array','Uint8Array','Int8Array','Uint8ClampedArray']){
      const C=window[n];if(!C)continue;M.saved[n]=C;
      window[n]=new Proxy(C,{construct(target,args,newTarget){
        const r=Reflect.construct(target,args,newTarget===window[n]?target:newTarget);
        const a0=args[0];if(a0&&typeof a0==='object'&&Object.prototype.toString.call(a0)==='[object ArrayBuffer]')return r;
        if(M.counting){const bytes=r.byteLength,s=bytes>=4096||Math.random()<.05?site():'(small, unsampled)';const e=M.churn.get(s)||{n:0,bytes:0,type:n};e.n++;e.bytes+=bytes;M.churn.set(s,e);}
        return r;}});}};
    M.uninstall=()=>{for(const [n,C] of Object.entries(M.saved||{}))window[n]=C;};
    const keep=inst=>{try{for(const v of Object.values(inst.exports||{}))if(v instanceof WebAssembly.Memory)M.wasm.push({mem:v,site:site()});}catch{}};
    const inst=WebAssembly.instantiate,stream=WebAssembly.instantiateStreaming;
    WebAssembly.instantiate=async(...a)=>{const r=await inst.apply(WebAssembly,a);keep(r.instance??r);return r;};
    if(stream)WebAssembly.instantiateStreaming=async(...a)=>{const r=await stream.apply(WebAssembly,a);keep(r.instance);return r;};
  });
  await page.goto(`http://localhost:${port}/?probe&quality=${process.env.PROBE_QUALITY??"ultra"}`,{waitUntil:'domcontentloaded',timeout:60000});await page.bringToFront();
  const bootDeadline=Date.now()+180000;
  while(Date.now()<bootDeadline&&!logs.some(s=>s.includes('🎮 Starting game...'))){
    const choice=page.locator('.start-screen-selection__option').first(),play=page.locator('#play-button, .hud-play-button').first();
    if(await choice.isVisible())await choice.click();
    else if(await play.isVisible()){await page.waitForTimeout(500);if(await play.isVisible())await play.click();}
    await page.waitForTimeout(500);
  }
  if(!logs.some(s=>s.includes('🎮 Starting game...')))throw Error('Game did not start');
  await page.waitForFunction(()=>!!window.__afterlightProbe,null,{timeout:120000});
  let quiet=0;for(const end=Date.now()+120000;quiet<8&&Date.now()<end;){quiet=(await page.evaluate(()=>window.__afterlightProbe.streaming().busy))?0:quiet+1;await page.waitForTimeout(500);}
  await page.waitForTimeout(5000);
  const cdp=await context.newCDPSession(page);
  await cdp.send('HeapProfiler.enable');await cdp.send('HeapProfiler.collectGarbage');
  const usage=await cdp.send('Runtime.getHeapUsage');
  const perfMemory=await page.evaluate(()=>performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize,limit:performance.memory.jsHeapSizeLimit}:null);

  // 0. Chrome's own breakdown (memory-infra): which allocator holds the renderer's memory, including native
  // memory V8 is told about (ArrayBuffer partition, Blink GC, images, media, WebGPU) that no JS walk can see.
  let chromeDump=null;
  {
    await cdp.send('Tracing.start',{transferMode:'ReturnAsStream',traceConfig:{recordMode:'recordUntilFull',includedCategories:['disabled-by-default-memory-infra'],memoryDumpConfig:{triggers:[]}}});
    await cdp.send('Tracing.requestMemoryDump',{deterministic:true,levelOfDetail:'detailed'});
    const done=new Promise(r=>cdp.once('Tracing.tracingComplete',r));await cdp.send('Tracing.end');const {stream}=await done;
    let text='';for(;;){const c=await cdp.send('IO.read',{handle:stream,size:4<<20});text+=c.base64Encoded?Buffer.from(c.data,'base64').toString('utf8'):c.data;if(c.eof)break;}await cdp.send('IO.close',{handle:stream});
    fs.writeFileSync(path.join(out,'memory-infra.json'),text);
    const ev=JSON.parse(text).traceEvents??[];const procs=new Map();
    for(const e of ev){const a=e.args?.dumps?.allocators;if(!a)continue;const sizes={};for(const [k,v] of Object.entries(a)){const sz=v.attrs?.size?.value;if(sz)sizes[k]=parseInt(sz,16);}procs.set(e.pid,{...(procs.get(e.pid)||{}),...sizes});}
    // The game's renderer is the process with the largest v8 allocation.
    const [pid,sizes]=[...procs.entries()].sort((a,b)=>(b[1].v8??0)-(a[1].v8??0))[0]??[];
    if(sizes){const top=Object.entries(sizes).filter(([k])=>k.split('/').length<=3).sort((a,b)=>b[1]-a[1]).filter(([,v])=>v>=8<<20).slice(0,45).map(([k,v])=>[k,MB(v)]);
      const gpuPid=[...procs.entries()].filter(([p])=>p!==pid).sort((a,b)=>(b[1].gpu??0)-(a[1].gpu??0))[0];
      chromeDump={rendererPid:pid,renderer:top,gpuProcess:gpuPid?Object.entries(gpuPid[1]).filter(([k])=>k.split('/').length<=2).sort((a,b)=>b[1]-a[1]).filter(([,v])=>v>=16<<20).slice(0,20).map(([k,v])=>[k,MB(v)]):null};}
  }

  // 1. What is alive.
  const alive=await page.evaluate(()=>{
    const pr=window.__afterlightProbe,E=pr.engine(),S=E.scene,M=window.__mem;
    const seen=new Set(),owners=new Map(),kinds=new Map();
    const ownerOf=o=>{let n=o,best=null;while(n&&n!==S){if(typeof n.userData?.perfOwner==='string')return n.userData.perfOwner;best=n;n=n.parent;}return best?.name||best?.type||'(scene)';};
    const add=(owner,kind,arr)=>{if(!arr)return;const buf=arr.buffer??arr;if(!(buf instanceof ArrayBuffer)||seen.has(buf))return;seen.add(buf);const b=buf.byteLength;
      const e=owners.get(owner)||{bytes:0,buffers:0,objects:0};e.bytes+=b;e.buffers++;owners.set(owner,e);kinds.set(kind,(kinds.get(kind)||0)+b);};
    let objects=0;
    S.traverse(o=>{objects++;const g=o.geometry;if(!g)return;const owner=ownerOf(o);
      for(const [k,a] of Object.entries(g.attributes||{}))add(owner,'attribute:'+k,a.isInterleavedBufferAttribute?a.data.array:a.array);
      if(g.index)add(owner,'index',g.index.array);
      for(const list of Object.values(g.morphAttributes||{}))for(const a of list)add(owner,'morph',a.array);
      if(o.isInstancedMesh){add(owner,'instanceMatrix',o.instanceMatrix.array);if(o.instanceColor)add(owner,'instanceColor',o.instanceColor.array);}
      for(const m of [o.material].flat())if(m)for(const v of Object.values(m))if(v?.isTexture&&v.image?.data)add(owner,'texture data',v.image.data);
    });
    const ownerRows=[...owners.entries()].sort((a,b)=>b[1].bytes-a[1].bytes).map(([k,v])=>[k,Math.round(v.bytes/1048576),v.buffers]);
    // Large constructor-allocated arrays still alive, by call site, split into "in the scene" and "not in the scene".
    const largeBy=new Map();let largeAlive=0,largeOff=0;
    for(const l of M.large){const b=l.ref.deref();if(!b)continue;largeAlive+=l.bytes;const inScene=seen.has(b);if(!inScene)largeOff+=l.bytes;const k=(inScene?'[scene] ':'[off-scene] ')+l.type+' '+l.site;const e=largeBy.get(k)||{bytes:0,n:0};e.bytes+=l.bytes;e.n++;largeBy.set(k,e);}
    const wasm=M.wasm.map(w=>({MB:Math.round(w.mem.buffer.byteLength/1048576),site:w.site.slice(0,200)}));
    // Texture sources kept on the CPU after upload (ImageBitmap / image / canvas / typed data), distinct images.
    const images=new Map();const texOwners=new Map();
    S.traverse(o=>{for(const m of [o.material].flat())if(m)for(const v of Object.values(m)){if(!v?.isTexture)continue;const img=v.source?.data??v.image;if(!img||images.has(img))continue;
      const w=img.width??img.videoWidth??0,h=img.height??img.videoHeight??0,kind=img.constructor?.name??typeof img;
      const bytes=img.data?.byteLength??(w*h*4);images.set(img,{kind,bytes,w,h});const owner=ownerOf(o);const e=texOwners.get(owner)||{bytes:0,n:0};e.bytes+=bytes;e.n++;texOwners.set(owner,e);}});
    const imgKinds={};for(const i of images.values()){const e=imgKinds[i.kind]||(imgKinds[i.kind]={n:0,MB:0,largest:''});e.n++;e.MB+=i.bytes/1048576;if(!e.largest||i.w*i.h>Number(e.largest.split('x')[0])*Number(e.largest.split('x')[1]))e.largest=i.w+'x'+i.h;}
    for(const e of Object.values(imgKinds))e.MB=Math.round(e.MB);
    const R=pr.renderer();
    return {textureImages:{distinct:images.size,MB:Math.round([...images.values()].reduce((n,i)=>n+i.bytes,0)/1048576),byKind:imgKinds,byOwner:[...texOwners.entries()].sort((a,b)=>b[1].bytes-a[1].bytes).slice(0,15).map(([k,v])=>[k,Math.round(v.bytes/1048576),v.n])},objects,sceneGeometryMB:Math.round([...owners.values()].reduce((n,e)=>n+e.bytes,0)/1048576),byOwner:ownerRows.slice(0,40),byKind:[...kinds.entries()].sort((a,b)=>b[1]-a[1]).map(([k,v])=>[k,Math.round(v/1048576)]),
      largeConstructedAliveMB:Math.round(largeAlive/1048576),largeConstructedOffSceneMB:Math.round(largeOff/1048576),largeBySite:[...largeBy.entries()].sort((a,b)=>b[1].bytes-a[1].bytes).slice(0,40).map(([k,v])=>[Math.round(v.bytes/1048576),v.n,k]),
      wasm,rendererMemory:{...R.info.memory}};
  });

  // 2. What is allocated per second while standing still.
  await cdp.send('HeapProfiler.startSampling',{samplingInterval:16384,includeObjectsCollectedByMajorGC:true,includeObjectsCollectedByMinorGC:true});
  await page.evaluate(()=>{window.__mem.install();window.__mem.churn.clear();window.__mem.counting=true;window.__mem.t0=performance.now();});
  await page.waitForTimeout(seconds*1000);
  const churn=await page.evaluate(()=>{const M=window.__mem;M.counting=false;M.uninstall();const s=(performance.now()-M.t0)/1000;
    return {seconds:+s.toFixed(2),typedArraysPerSecond:Math.round([...M.churn.values()].reduce((n,e)=>n+e.n,0)/s),typedMBPerSecond:+([...M.churn.values()].reduce((n,e)=>n+e.bytes,0)/1048576/s).toFixed(2),
      bySite:[...M.churn.entries()].sort((a,b)=>b[1].bytes-a[1].bytes).slice(0,25).map(([k,e])=>({perSecond:Math.round(e.n/s),KBPerSecond:Math.round(e.bytes/1024/s),type:e.type,site:k}))};});
  const {profile}=await cdp.send('HeapProfiler.stopSampling');
  const self=new Map();let sampled=0;
  const label=f=>`${f.functionName||'(anonymous)'} ${String(f.url||'').replace(/^https?:\/\/[^/]+/,'').split('?')[0].split('/').slice(-2).join('/')}:${f.lineNumber+1}`;
  const walk=(n,stack)=>{const l=label(n.callFrame),s=[l,...stack].slice(0,4);const own=n.selfSize||0;if(own){sampled+=own;const k=s.join(' <- ');self.set(k,(self.get(k)||0)+own);}for(const c of n.children||[])walk(c,s);};
  walk(profile.head,[]);
  const v8Alloc={sampledMBPerSecond:+(sampled/1048576/seconds).toFixed(1),bySite:[...self.entries()].sort((a,b)=>b[1]-a[1]).slice(0,30).map(([k,v])=>[+(v/1048576/seconds).toFixed(2),k])};

  const report={viewport:[vw,vh],chromeDump,heapUsage:{usedMB:MB(usage.usedSize),totalMB:MB(usage.totalSize),embedderUsedMB:MB(usage.embedderHeapUsedSize??0),backingStorageMB:MB(usage.backingStorageSize??0)},
    performanceMemory:perfMemory&&{usedMB:MB(perfMemory.used),totalMB:MB(perfMemory.total),limitMB:MB(perfMemory.limit)},alive,churn,v8Alloc};
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,1));
  const lines=[`MEMORY ${name}`,`V8 heap used ${report.heapUsage.usedMB} MB (total ${report.heapUsage.totalMB}); ArrayBuffer backing stores ${report.heapUsage.backingStorageMB} MB; embedder ${report.heapUsage.embedderUsedMB} MB; performance.memory used ${report.performanceMemory?.usedMB} MB`,
    `Scene geometry typed arrays: ${alive.sceneGeometryMB} MB over ${alive.objects} objects; large constructed arrays alive ${alive.largeConstructedAliveMB} MB (${alive.largeConstructedOffSceneMB} MB not referenced by the scene)`,
    `WebAssembly memories: ${JSON.stringify(alive.wasm)}`,`Texture images held on the CPU (estimated RGBA): ${alive.textureImages.MB} MB in ${alive.textureImages.distinct} images ${JSON.stringify(alive.textureImages.byKind)}`,...alive.textureImages.byOwner.map(r=>`  ${String(r[1]).padStart(6)} MB ${r[2]} images  ${r[0]}`),'','Chrome memory-infra, game renderer (MB):',...(chromeDump?.renderer??[]).map(r=>`  ${String(r[1]).padStart(6)}  ${r[0]}`),'','Chrome memory-infra, other process with most GPU memory (MB):',...(chromeDump?.gpuProcess??[]).map(r=>`  ${String(r[1]).padStart(6)}  ${r[0]}`),'','Scene geometry by owner (MB, buffers):',...alive.byOwner.slice(0,25).map(r=>`  ${String(r[1]).padStart(6)}  ${r[2]}  ${r[0]}`),
    '','By kind:',...alive.byKind.slice(0,12).map(r=>`  ${String(r[1]).padStart(6)}  ${r[0]}`),
    '','Large constructed arrays alive, by site (MB, count):',...alive.largeBySite.slice(0,25).map(r=>`  ${String(r[0]).padStart(6)} x${r[1]}  ${r[2].slice(0,260)}`),
    '',`Standing still for ${churn.seconds} s: ${churn.typedArraysPerSecond} typed arrays/s, ${churn.typedMBPerSecond} MB/s`,...churn.bySite.slice(0,15).map(r=>`  ${String(r.perSecond).padStart(6)}/s ${String(r.KBPerSecond).padStart(7)} KB/s ${r.type} ${r.site.slice(0,240)}`),
    '',`V8 heap allocation (sampled) ${v8Alloc.sampledMBPerSecond} MB/s:`,...v8Alloc.bySite.slice(0,20).map(r=>`  ${String(r[0]).padStart(6)} MB/s  ${r[1].slice(0,260)}`)];
  fs.writeFileSync(path.join(out,'summary.txt'),lines.join('\n'));console.log(lines.join('\n'));
} finally {
  clearTimeout(watchdog);
  try{fs.writeFileSync(path.join(out,'console.log'),logs.join('\n'));}catch{}
  await browser.close();
}
