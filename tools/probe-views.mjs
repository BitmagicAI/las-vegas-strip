// Repeatable views for before/after comparisons: boots the game in headless Chrome (WebGPU), and for each
// named view teleports the player, fixes a first-person yaw/pitch, waits for streaming and shader builds to
// settle, then saves a full-resolution screenshot and a short frame-rate sample.
//
//   node tools/probe-views.mjs --name before [--set lawn|city|all] [--viewport 1505x772] [--dpr 2] [--sample 3]
//
// Output: build/probe/views/<name>/<view>.png and report.json. Reloads are held (.bitmagic/hold-reload) while it
// runs so an edit elsewhere cannot restart the page mid-capture. Local only; one headless Chrome, closed in `finally`.
import fs from 'node:fs';
import path from 'node:path';
import {launchSystemChrome} from './lib/bitmagic-cli.mjs';
import {browserRendererArgs} from './lib/bitmagic-cli.mjs';

const argv=process.argv.slice(2);
const opt=(name,fallback)=>{const i=argv.indexOf('--'+name);return i<0?fallback:(argv[i+1]===undefined||argv[i+1].startsWith('--')?true:argv[i+1]);};
const name=String(opt('name','views')),set=String(opt('set','all')),dpr=Number(opt('dpr',2)),sample=Number(opt('sample',3));
const [vw,vh]=String(opt('viewport','1505x772')).split('x').map(Number);
const port=JSON.parse(fs.readFileSync('.bitmagic/dev.json','utf8')).gamePort;
const out=path.join(process.env.PROBE_OUT??'build/probe/views',name);fs.mkdirSync(out,{recursive:true});

// [name, set, x, y, z, yaw, pitch]. Positions are game metres; yaw/pitch radians for the first-person camera.
const VIEWS=[
  ['spawn-level','lawn',-60,0.4,540,1.5708,0],
  ['spawn-down','lawn',-60,0.4,540,1.5708,-0.45],
  ['lawn-south','lawn',-110,0.4,560,0,-0.2],
  ['lawn-west','lawn',-60,0.4,540,3.1416,-0.25],
  ['garden-trees','lawn',-120,0.4,470,0.8,-0.05],
  ['strip-north','city',0,0.4,300,3.1416,0.05],
  ['strip-south','city',0,0.4,300,0,0.05],
  ['bellagio-facade','city',-60,0.4,540,-1.5708,0.15],
  ['paris','city',0,0.4,180,1.5708,0.1],
  ['skyline-high','city',-60,60,540,0.6,-0.1],
];
// --query "hotel=…" captures one view the game positions itself (review URLs), named by --shot.
const extraQuery=opt('query',null),shot=String(opt('shot','query'));
const views=extraQuery?[[shot,'query',null,null,null,null,null]]:VIEWS.filter(v=>set==='all'||v[1]===set||String(set).split(',').includes(v[0]));

fs.mkdirSync('.bitmagic',{recursive:true});const hold='.bitmagic/hold-reload';const heldBefore=fs.existsSync(hold);if(!heldBefore)fs.writeFileSync(hold,'probe-views\n');
const browser=await launchSystemChrome({headless:true,args:[...browserRendererArgs(process.env,'webgpu'),'--mute-audio'],command:'local view probe'});
const watchdog=setTimeout(()=>{console.error('probe watchdog: closing the browser');browser.close().finally(()=>process.exit(2));},900000);
const logs=[],errors=[];
try {
  const context=await browser.newContext({viewport:{width:vw,height:vh},deviceScaleFactor:dpr});
  const page=await context.newPage();
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{const s=m.text();logs.push(s);if(m.type()==='error')errors.push(s);});
  await page.addInitScript(()=>Object.defineProperty(Element.prototype,'requestPointerLock',{configurable:true,writable:true,value:()=>Promise.resolve()}));
  await page.goto(`http://localhost:${port}/?probe&quality=${process.env.PROBE_QUALITY??"ultra"}${extraQuery?'&'+extraQuery:''}${process.env.PROBE_EXTRA?'&'+process.env.PROBE_EXTRA:''}`,{waitUntil:'domcontentloaded',timeout:60000});await page.bringToFront();
  const bootDeadline=Date.now()+180000;
  while(Date.now()<bootDeadline&&!logs.some(s=>s.includes('🎮 Starting game...'))){
    const choice=page.locator('.start-screen-selection__option').first(),play=page.locator('#play-button, .hud-play-button').first();
    if(await choice.isVisible())await choice.click();
    else if(await play.isVisible()){await page.waitForTimeout(500);if(await play.isVisible())await play.click();}
    await page.waitForTimeout(500);
  }
  if(!logs.some(s=>s.includes('🎮 Starting game...')))throw Error('Game did not start');
  await page.waitForFunction(()=>!!window.__afterlightProbe,null,{timeout:120000});
  const idle=async(n=6)=>{let quiet=0;const end=Date.now()+90000;while(quiet<n&&Date.now()<end){quiet=(await page.evaluate(()=>window.__afterlightProbe.streaming().busy))?0:quiet+1;await page.waitForTimeout(400);}};
  const settle=async()=>{const end=Date.now()+30000;let last=-1,stable=0;while(Date.now()<end&&stable<4){const n=await page.evaluate(()=>{const R=window.__afterlightProbe.renderer();return (R._pipelines?.caches?.size??0)+(R.info.memory.programs??0);});stable=n===last?stable+1:0;last=n;await page.waitForTimeout(500);}};
  await idle(8);
  const results=[];
  for(const [view,,x,y,z,yaw,pitch] of views){
    if(x!==null)await page.evaluate(([x,y,z,yaw,pitch])=>{const p=window.__afterlightProbe;p.teleport(x,y,z);p.look(yaw,pitch);},[x,y,z,yaw,pitch]);
    await page.waitForTimeout(1200);await idle(4);
    // Foliage cells re-select from the new camera position on their next throttled hook; make it explicit.
    if(opt('toggle-foliage',false)===true)await page.evaluate(()=>{const b=document.getElementById('foliage-enabled');if(b?.checked){b.click();b.click();}});
    await settle();if(x!==null)await page.evaluate(([yaw,pitch])=>window.__afterlightProbe.look(yaw,pitch),[yaw,pitch]);await page.waitForTimeout(1500);
    const fps=await page.evaluate(ms=>new Promise(r=>{let n=0;const t0=performance.now();const f=()=>{n++;if(performance.now()-t0<ms)requestAnimationFrame(f);else r({frames:n,fps:+(n*1000/(performance.now()-t0)).toFixed(1)});};requestAnimationFrame(f);}),sample*1000);
    const info=await page.evaluate(()=>{const p=window.__afterlightProbe,R=p.renderer(),pl=p.engine().scene.getObjectByName('Bellagio botanical planting');let foliageGroups=0;pl?.children.forEach(g=>{if(g.visible)foliageGroups++;});return {position:p.position(),draws:R.info.render.drawCalls,triangles:R.info.render.triangles,foliageGroups};});
    await page.screenshot({path:path.join(out,view+'.png')});
    if(opt('ablate',false)===true){
      // What each part of the view costs: frame rate with one part hidden at a time.
      const extra={
        // Trees drawn unlit (lower bound of their shading cost), and trees without shadow casting.
        'trees-unlit':"()=>{let B=null;const S=window.__afterlightProbe.engine().scene;S.traverse(o=>{for(const m of [o.material].flat())if(m?.isMeshBasicMaterial&&!B)B=m.constructor;});const saved=[];S.traverse(o=>{if((o.isInstancedMesh||o.geometry?.isInstancedBufferGeometry)&&o.parent?.name?.startsWith('Trees')){saved.push([o,o.material]);o.material=[o.material].flat().map(m=>new B({map:m.map,alphaTest:m.alphaTest,side:m.side,alphaToCoverage:m.alphaToCoverage}));if(o.material.length===1)o.material=o.material[0];}});return ()=>saved.forEach(([o,m])=>o.material=m);}",
        'tree-shadows-off':"()=>{const S=window.__afterlightProbe.engine().scene,saved=[];S.traverse(o=>{if((o.isInstancedMesh||o.geometry?.isInstancedBufferGeometry)&&o.castShadow&&o.parent?.name?.startsWith('Trees')){saved.push(o);o.castShadow=false;}});return ()=>saved.forEach(o=>o.castShadow=true);}",
      };
      for(const [label,code] of Object.entries(extra)){
        await page.evaluate(code=>{window.__undoPart=new Function('return ('+code+')()')();},code);
        await settle();await page.waitForTimeout(800);
        fps[label]=await page.evaluate(ms=>new Promise(r=>{let n=0;const t0=performance.now();const f=()=>{n++;if(performance.now()-t0<ms)requestAnimationFrame(f);else r(+(n*1000/(performance.now()-t0)).toFixed(1));};requestAnimationFrame(f);}),sample*1000);
        await page.evaluate(()=>{window.__undoPart?.();window.__undoPart=null;});await settle();
      }
      const parts={'no-grass':"o=>(o.isInstancedMesh||o.geometry?.isInstancedBufferGeometry)&&o.parent?.name?.startsWith('Lawn')",'no-trees':"o=>(o.isInstancedMesh||o.geometry?.isInstancedBufferGeometry)&&o.parent?.name?.startsWith('Trees')",'no-jeep':"o=>/jeep|Jeep|charging bay/.test(o.name)"};
      for(const [label,test] of Object.entries(parts)){
        const n=await page.evaluate(test=>{const f=new Function('return '+test)(),S=window.__afterlightProbe.engine().scene,hidden=[];S.traverse(o=>{if(o.visible&&f(o))hidden.push(o);});for(const o of hidden)o.visible=false;window.__hiddenParts=hidden;return hidden.length;},test);
        await page.waitForTimeout(800);
        const f=await page.evaluate(ms=>new Promise(r=>{let n=0;const t0=performance.now();const f=()=>{n++;if(performance.now()-t0<ms)requestAnimationFrame(f);else r(+(n*1000/(performance.now()-t0)).toFixed(1));};requestAnimationFrame(f);}),sample*1000);
        await page.evaluate(()=>{for(const o of window.__hiddenParts)o.visible=true;window.__hiddenParts=[];});
        fps[label]=n?f:'n/a';
      }
    }
    results.push({view,yaw,pitch,...info,...fps});console.log(view.padEnd(16),JSON.stringify({fps:fps.fps,ablate:opt('ablate',false)===true?{grass:fps['no-grass'],trees:fps['no-trees'],treesUnlit:fps['trees-unlit'],treeShadowsOff:fps['tree-shadows-off'],jeep:fps['no-jeep']}:undefined,draws:info.draws,triangles:info.triangles,foliageGroups:info.foliageGroups,at:[Math.round(info.position.x),+info.position.y.toFixed(1),Math.round(info.position.z)]}));
  }
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({viewport:[vw,vh],dpr,results,errors:errors.slice(0,20)},null,1));
  if(errors.length)console.log('page errors:',errors.slice(0,5).join('\n'));
} finally {
  clearTimeout(watchdog);
  try{fs.writeFileSync(path.join(out,'console.log'),logs.join('\n'));}catch{}
  await browser.close();
  if(!heldBefore)try{fs.unlinkSync(hold);}catch{}
}
