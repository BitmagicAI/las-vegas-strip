// Local heap probe: boots the game in headless Chrome with V8's sampling heap profiler attached from the
// first script, then reports what is still alive after a forced GC, grouped by the function that
// allocated it. A multi-second pause that is not a streaming job is usually a major GC on a huge heap.
//
//   node tools/probe-heap.mjs [--name heap] [--viewport 960x540] [--drive] [--query probe]
//
// --drive also moves the player to the south end of the Strip and waits for the streaming to settle,
// then measures again (the growth between the two is what streaming leaves behind).
// Output: build/probe/heap/<name>/{report.json,summary.txt}. Local only; one headless Chrome, closed in `finally`.
import fs from 'node:fs';
import path from 'node:path';
import {launchSystemChrome} from './lib/bitmagic-cli.mjs';
import {browserRendererArgs} from './lib/bitmagic-cli.mjs';

const argv=process.argv.slice(2);
const opt=(name,fallback)=>{const i=argv.indexOf('--'+name);return i<0?fallback:(argv[i+1]===undefined||argv[i+1].startsWith('--')?true:argv[i+1]);};
const name=String(opt('name','heap')),drive=opt('drive',false)===true,query=String(opt('query','probe'));
const [vw,vh]=String(opt('viewport','960x540')).split('x').map(Number);
const port=JSON.parse(fs.readFileSync('.bitmagic/dev.json','utf8')).gamePort;
const out=path.join('build/probe/heap',name);fs.mkdirSync(out,{recursive:true});
const MB=n=>Math.round(n/1048576);

const browser=await launchSystemChrome({headless:true,args:[...browserRendererArgs(process.env,'webgpu'),'--mute-audio','--enable-precise-memory-info'],command:'local heap probe'});
const logs=[];
try {
  const context=await browser.newContext({viewport:{width:vw,height:vh},deviceScaleFactor:1});
  const page=await context.newPage();
  page.on('console',m=>logs.push(m.text()));
  await page.addInitScript(()=>Object.defineProperty(Element.prototype,'requestPointerLock',{configurable:true,writable:true,value:()=>Promise.resolve()}));
  const cdp=await context.newCDPSession(page);
  await cdp.send('HeapProfiler.enable');
  await cdp.send('HeapProfiler.startSampling',{samplingInterval:131072,includeObjectsCollectedByMajorGC:false,includeObjectsCollectedByMinorGC:false});
  await page.goto(`http://localhost:${port}/?${query}`,{waitUntil:'domcontentloaded',timeout:60000});await page.bringToFront();
  const bootDeadline=Date.now()+180000;
  while(Date.now()<bootDeadline && !logs.some(s=>s.includes('🎮 Starting game...'))){
    const choice=page.locator('.start-screen-selection__option').first();
    const play=page.locator('#play-button, .hud-play-button').first();
    if(await choice.isVisible())await choice.click();
    else if(await play.isVisible()){await page.waitForTimeout(500);if(await play.isVisible())await play.click();}
    await page.waitForTimeout(500);
  }
  await page.waitForFunction(()=>!!window.__afterlightProbe,{timeout:120000});
  const idle=async(quiet=8)=>{let q=0;const end=Date.now()+120000;while(q<quiet&&Date.now()<end){const busy=await page.evaluate(()=>window.__afterlightProbe.streaming().busy);q=busy?0:q+1;await page.waitForTimeout(500);}};
  await idle();await page.waitForTimeout(3000);
  const measure=async label=>{
    const before=await cdp.send('Runtime.getHeapUsage');
    const mem=await page.evaluate(()=>{const m=performance.memory;return {used:m.usedJSHeapSize,total:m.totalJSHeapSize,limit:m.jsHeapSizeLimit};});
    await cdp.send('HeapProfiler.collectGarbage');await cdp.send('HeapProfiler.collectGarbage');
    const after=await cdp.send('Runtime.getHeapUsage');
    const r={label,usedMB:MB(before.usedSize),totalMB:MB(before.totalSize),afterGcUsedMB:MB(after.usedSize),afterGcTotalMB:MB(after.totalSize),limitMB:MB(mem.limit),perfMemoryUsedMB:MB(mem.used)};
    console.log(JSON.stringify(r));return r;
  };
  const measures=[await measure('after boot')];
  if(drive){
    const route=JSON.parse(fs.readFileSync('build/geographic-strip/road-network.json','utf8')).stripRoute.filter(p=>p[2]>=-270&&p[2]<=1270).sort((a,b)=>a[2]-b[2]);
    await page.evaluate(([x,y,z])=>window.__afterlightProbe.teleport(x,y+.2,z),route[0]);
    await page.waitForTimeout(1500);await idle(10);await page.waitForTimeout(3000);
    measures.push(await measure('after moving to the Strip'));
  }
  const {profile}=await cdp.send('HeapProfiler.getSamplingProfile');
  await cdp.send('HeapProfiler.stopSampling');
  // Live allocation by function: self size of each call frame, plus inclusive size by function name.
  const label=f=>`${f.functionName||'(anonymous)'} ${String(f.url||'').replace(/^https?:\/\/[^/]+/,'').split('?')[0].split('/').slice(-3).join('/')}:${f.lineNumber+1}`;
  const self=new Map(),incl=new Map(),paths=new Map();let total=0;
  const walk=(node,stack)=>{
    const l=label(node.callFrame);stack.push(l);
    if(node.selfSize>0){total+=node.selfSize;self.set(l,(self.get(l)||0)+node.selfSize);
      const seen=new Set();for(const s of stack){if(seen.has(s))continue;seen.add(s);incl.set(s,(incl.get(s)||0)+node.selfSize);}
      const key=stack.slice(-6).join(' < ').split(' < ').reverse().join(' < ');paths.set(key,(paths.get(key)||0)+node.selfSize);}
    for(const c of node.children||[])walk(c,stack);stack.pop();
  };
  walk(profile.head,[]);
  const top=(m,n)=>[...m.entries()].sort((a,b)=>b[1]-a[1]).slice(0,n).map(([k,v])=>[k,MB(v)]);
  const result={measures,liveSampledMB:MB(total),topSelf:top(self,30),topInclusive:top(incl,40),topPaths:top(paths,25)};
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(result,null,1));
  const lines=[`HEAP ${name}`,JSON.stringify(measures,null,1),`live sampled MB: ${result.liveSampledMB}`,'','Top live allocation sites (self):',...result.topSelf.map(([k,v])=>`  ${v} MB  ${k}`),'','Top by inclusive stack:',...result.topInclusive.map(([k,v])=>`  ${v} MB  ${k}`),'','Top allocation paths (leaf first):',...result.topPaths.map(([k,v])=>`  ${v} MB  ${k}`)];
  fs.writeFileSync(path.join(out,'summary.txt'),lines.join('\n'));
  console.log(lines.join('\n'));
} finally {
  await browser.close();
}
