// Boot the game in headless Chrome (WebGPU), stand at the spawn point, and evaluate a script in the page:
// a quick way to ask the running scene a question (lights, materials, counts) without a bespoke probe.
//
//   node tools/probe-eval.mjs <file.js | --expr "js expression"> [--viewport 960x540] [--dpr 1] [--query lighting=engine64] [--out dir]
// (the script may `await __shot(name)` to save a screenshot into --out)
//
// The script body runs as an async function with `probe` (window.__afterlightProbe), `engine`, `scene`,
// `renderer` in scope and must `return` a JSON-serialisable value. Local only; one headless Chrome.
import fs from 'node:fs';
import {launchSystemChrome} from './lib/bitmagic-cli.mjs';
import {browserRendererArgs} from './lib/bitmagic-cli.mjs';

const argv=process.argv.slice(2);
const opt=(name,fallback)=>{const i=argv.indexOf('--'+name);return i<0?fallback:(argv[i+1]===undefined||argv[i+1].startsWith('--')?true:argv[i+1]);};
const expr=opt('expr',null),file=expr?null:argv.find(a=>!a.startsWith('--'));
const body=expr?`return (${expr});`:fs.readFileSync(file,'utf8');
const [vw,vh]=String(opt('viewport','960x540')).split('x').map(Number),dpr=Number(opt('dpr',1));
const port=JSON.parse(fs.readFileSync('.bitmagic/dev.json','utf8')).gamePort;
const browser=await launchSystemChrome({headless:true,args:[...browserRendererArgs(process.env,'webgpu'),'--mute-audio'],command:'local eval probe'});
const watchdog=setTimeout(()=>{console.error('probe watchdog');browser.close().finally(()=>process.exit(2));},600000);
const logs=[];
try {
  const context=await browser.newContext({viewport:{width:vw,height:vh},deviceScaleFactor:dpr,serviceWorkers:opt('lod-baseline',false)?'block':'allow'});
  const page=await context.newPage();
  page.on('console',m=>logs.push(m.text()));page.on('pageerror',e=>logs.push('PAGEERROR '+e));
  // Browser-only A/B: use the pre-facade LOD path without reverting live files.
  let lodBaselinePatches=0;
  if(opt('lod-baseline',false))await page.route('**/CityLod.js*',async route=>{
    const response=await route.fetch(),source=await response.text(),marker='const facade = !!options.facade';
    if(!source.includes(marker))throw new Error('LOD baseline marker missing; comparison is invalid');
    lodBaselinePatches++;
    await route.fulfill({response,body:source.replace(marker,'const facade = false')});
  });
  await page.addInitScript(()=>Object.defineProperty(Element.prototype,'requestPointerLock',{configurable:true,writable:true,value:()=>Promise.resolve()}));
  // --storage 'key=json;key2=json': localStorage entries set before the game loads (e.g. afterlight:film=1).
  const storage=String(opt('storage','')).split(';').filter(Boolean).map(e=>{const i=e.indexOf('=');return [e.slice(0,i),e.slice(i+1)];});
  if(storage.length)await page.addInitScript(entries=>{for(const [k,v] of entries)localStorage.setItem(k,v);},storage);
  if(opt('load-metrics',false))await page.addInitScript(()=>{
    const metrics=window.__cellLoadMetrics={frames:[],longTasks:[],started:performance.now()};
    let previous=performance.now();
    const frame=now=>{metrics.frames.push([now,now-previous]);previous=now;requestAnimationFrame(frame);};
    requestAnimationFrame(frame);
    new PerformanceObserver(list=>{for(const e of list.getEntries())metrics.longTasks.push([e.startTime,e.duration]);}).observe({type:'longtask',buffered:true});
    performance.setResourceTimingBufferSize(10000);
  });
  await page.goto(`http://localhost:${port}/?probe&quality=${process.env.PROBE_QUALITY??"ultra"}${opt('query',null)?'&'+opt('query'):''}`,{waitUntil:'domcontentloaded',timeout:60000});
  const end=Date.now()+180000;let clickedPlay=false;
  while(Date.now()<end&&!logs.some(s=>s.includes('🎮 Starting game...'))){
    const choice=page.locator('.start-screen-selection__option').first(),play=page.locator('#play-button, .hud-play-button').first();
    // Probe is installed before the title screen; require a completed PLAY click too.
    if(clickedPlay&&!await play.isVisible()&&await page.evaluate(()=>!!window.__afterlightProbe))break;
    if(await choice.isVisible())await choice.click();else if(await play.isVisible()){await page.waitForTimeout(500);if(await play.isVisible()){await play.click();clickedPlay=true;}}
    await page.waitForTimeout(500);
  }
  await page.waitForFunction(()=>!!window.__afterlightProbe,null,{timeout:120000});
  if(opt('lod-baseline',false)&&!lodBaselinePatches)throw new Error('LOD baseline was not installed');
  // await window.__shot('name') in the script saves a screenshot to --out <dir> (default build/probe/eval).
  const outDir=String(opt('out','build/probe/eval'));fs.mkdirSync(outDir,{recursive:true});
  await page.exposeFunction('__shot',async name=>{await page.screenshot({path:`${outDir}/${name}.png`});return true;});
  await page.waitForTimeout(4000);
  const result=await page.evaluate(async body=>{const probe=window.__afterlightProbe,engine=probe.engine(),scene=engine.scene,renderer=probe.renderer();
    return await (new Function('probe','engine','scene','renderer',`return (async()=>{${body}})()`))(probe,engine,scene,renderer);},body);
  fs.writeFileSync(`${outDir}/results.json`,JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result,null,1));
  if(opt('lod-baseline',false)){if(!lodBaselinePatches)throw new Error('LOD baseline was not installed');console.error(`LOD baseline installed in ${lodBaselinePatches} module response(s)`);}
  const errs=logs.filter(l=>/PAGEERROR|error/i.test(l)).slice(0,8);if(errs.length)console.error('page errors:\n'+errs.join('\n'));
} catch(error) { console.error('Probe failed; recent browser messages:\n'+logs.slice(-35).join('\n')); throw error; }
finally {clearTimeout(watchdog);await browser.close();}

// CLI imports may leave background handles after Chrome has closed.
// A successful local probe has no work left once captures and results are saved.
process.exit(0);
