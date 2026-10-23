// Hotel interior profiler: boots the game once in headless Chrome (WebGPU, ?quality=ultra pinned), then for
// each named interior (staircase, hallway, room, lobby) places the player exactly as the ?hotel= review URL
// does, waits for streaming and shader builds to settle, and records:
//   - frame interval, main-thread CPU in rAF callbacks, GPU time per render pass (WebGPU timestamps),
//     draw calls / triangles, the renderer's light list (by type), and a screenshot;
//   - with --ablate, the frame rate with one thing changed at a time: the city outside hidden, hotel
//     materials lit without the city's point lights, hotel materials unlit, shadow maps frozen, half resolution.
//
//   node tools/probe-interiors.mjs --name hotels [--viewport 1505x772] [--dpr 2] [--sample 3] [--ablate]
//        [--views stair-bellagio,corridor-bellagio,...] [--query lighting=engine64]
// --query adds URL parameters, e.g. lighting=engine<cap>|clustered (Game.ts's local boot-time lighting switch; a
// renderer.lighting swapped in after the first frame renders wrong pictures on three r185, so there is no runtime toggle).
//
// Output: build/probe/interiors/<name>/{report.json,summary.txt,<view>.png}. Reloads are held while it runs.
// Local only; one headless Chrome, closed in `finally`.
import fs from 'node:fs';
import path from 'node:path';
import {launchSystemChrome} from './lib/bitmagic-cli.mjs';
import {browserRendererArgs} from './lib/bitmagic-cli.mjs';

const argv=process.argv.slice(2);
const opt=(name,fallback)=>{const i=argv.indexOf('--'+name);return i<0?fallback:(argv[i+1]===undefined||argv[i+1].startsWith('--')?true:argv[i+1]);};
const name=String(opt('name','interiors')),dpr=Number(opt('dpr',2)),sample=Number(opt('sample',3)),ablate=opt('ablate',false)===true;
const [vw,vh]=String(opt('viewport','1505x772')).split('x').map(Number);
const port=JSON.parse(fs.readFileSync('.bitmagic/dev.json','utf8')).gamePort;
const out=path.join('build/probe/interiors',name);fs.mkdirSync(out,{recursive:true});

// [view, tower id, floor, room bay (null = none), review view (null = stair landing)]
const VIEWS=[
  ['stair-bellagio','bellagio-north',3,null,null],
  ['corridor-bellagio','bellagio-north',3,null,'corridor'],
  ['room-bellagio','bellagio-north',3,0,'bedroom'],
  ['bath-bellagio','bellagio-north',3,0,'bathroom'],
  ['stair-caesars','caesars-palace',3,null,null],
  ['corridor-caesars','caesars-palace',3,null,'corridor'],
  ['room-caesars','caesars-palace',3,0,null],
  ['stair-cosmo','cosmo-boulevard',3,null,null],
  ['corridor-cosmo','cosmo-boulevard',3,null,'corridor'],
  ['room-cosmo','cosmo-boulevard',3,0,null],
  ['stair-ground-bellagio','bellagio-north',0,null,null],
  ['lobby-wynn','wynn-1',0,null,'lobby'],
  ['entrance-wynn','wynn-1',0,null,'entrance'],
  // Casino / public interiors of the Strip landmarks ('landmark:<key>', view name).
  ['lobby-venetian','landmark:venetian',0,null,'lobby'],
  ['lobby-palazzo','landmark:palazzo',0,null,'lobby'],
  ['lobby-park','landmark:park',0,null,'lobby'],
  ['lobby-arena','landmark:arena',0,null,'lobby'],
  ['lobby-linq','landmark:linq',0,null,'lobby'],
  ['lobby-ti','landmark:ti',0,null,'lobby'],
];
// --hold fixes only the local review player at --at for aerial captures; never a traversal benchmark.
// Outdoor spots: --at "name=x,y,z,yaw,pitch;name2=..." (first-person), and 'spawn' (camera untouched after boot).
const AT=String(opt('at','')).split(';').filter(Boolean).map(e=>{const [n,v]=e.split('=');return [n,'at:'+v,0,null,null];});
const pick=opt('views',null),all=[...VIEWS,...AT,['spawn','spawn',0,null,null]],views=pick?all.filter(v=>String(pick).split(',').includes(v[0])):VIEWS;
// Named groups for ablations: --groups "jeep=^Body$,chars=^Vegas character|^HeadlessPlayer$" (regex on a top-level scene child's name).
const GROUPS=String(opt('groups','')).split(',').filter(Boolean).map(e=>e.split('='));

fs.mkdirSync('.bitmagic',{recursive:true});const hold='.bitmagic/hold-reload';const heldBefore=fs.existsSync(hold);if(!heldBefore)fs.writeFileSync(hold,'probe-interiors\n');
const browser=await launchSystemChrome({headless:true,args:[...browserRendererArgs(process.env,'webgpu'),'--mute-audio'],command:'local interior probe'});
const watchdog=setTimeout(()=>{console.error('probe watchdog: closing the browser');browser.close().finally(()=>process.exit(2));},1800000);
const logs=[],errors=[];
try {
  const context=await browser.newContext({viewport:{width:vw,height:vh},deviceScaleFactor:dpr});
  const page=await context.newPage();
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{const s=m.text();logs.push(s);if(m.type()==='error')errors.push(s);});
  // --storage 'key=json;key2=json': localStorage entries set before the game loads (settings such as afterlight:shadows:v1).
  const storage=String(opt('storage','')).split(';').filter(Boolean).map(e=>{const i=e.indexOf('=');return [e.slice(0,i),e.slice(i+1)];});
  if(storage.length)await page.addInitScript(entries=>{for(const [k,v] of entries)localStorage.setItem(k,v);},storage);
  await page.addInitScript(()=>{
    Object.defineProperty(Element.prototype,'requestPointerLock',{configurable:true,writable:true,value:()=>Promise.resolve()});
    const raf=window.requestAnimationFrame.bind(window),F=window.__ticks={cpu:new Map(),submits:0};
    window.requestAnimationFrame=cb=>raf(t=>{const s=performance.now();try{cb(t);}finally{F.cpu.set(t,(F.cpu.get(t)||0)+performance.now()-s);}});
    const submit=window.GPUQueue?.prototype.submit;if(submit)window.GPUQueue.prototype.submit=function(...a){F.submits++;return submit.apply(this,a);};
  });
  await page.goto(`http://localhost:${port}/?probe&quality=${process.env.PROBE_QUALITY??'ultra'}${opt('query',null)?'&'+opt('query'):''}`,{waitUntil:'domcontentloaded',timeout:60000});await page.bringToFront();
  const bootDeadline=Date.now()+180000;
  while(Date.now()<bootDeadline&&!logs.some(s=>s.includes('🎮 Starting game...'))){
    const choice=page.locator('.start-screen-selection__option').first(),play=page.locator('#play-button, .hud-play-button').first();
    if(await choice.isVisible())await choice.click();else if(await play.isVisible()){await page.waitForTimeout(500);if(await play.isVisible())await play.click();}
    await page.waitForTimeout(500);
  }
  if(!logs.some(s=>s.includes('🎮 Starting game...')))throw Error('Game did not start');
  await page.waitForFunction(()=>!!window.__afterlightProbe,null,{timeout:120000});
  const idle=async(n=6)=>{let quiet=0;const end=Date.now()+120000;while(quiet<n&&Date.now()<end){quiet=(await page.evaluate(()=>window.__afterlightProbe.streaming().busy))?0:quiet+1;await page.waitForTimeout(400);}};
  const settle=async()=>{const end=Date.now()+40000;let last=-1,stable=0;while(Date.now()<end&&stable<4){const n=await page.evaluate(()=>{const R=window.__afterlightProbe.renderer();return (R._pipelines?.caches?.size??0)+(R.info.memory.programs??0);});stable=n===last?stable+1:0;last=n;await page.waitForTimeout(500);}await page.waitForTimeout(1000);};
  await idle(8);

  // GPU timestamps per render pass, labelled by render target (as probe-idle does).
  await page.evaluate(()=>{
    const pr=window.__afterlightProbe,R=pr.renderer(),B=R.backend;
    if(B.device?.features?.has('timestamp-query'))B.trackTimestamp=true;
    const labels=window.__ctxLabels=new Map(),rc=R._renderContexts,get=rc.get.bind(rc);
    rc.get=(rt=null,...rest)=>{const c=get(rt,...rest);if(!labels.has(c.id))labels.set(c.id,rt?`${rt.name||rt.texture?.name||(rt.depthTexture&&!rt.texture?'depth':'target')} ${rt.width}x${rt.height}`:'screen');return c;};
    const T=window.__m={on:false,rows:[],gpu:[],passes:new Map(),lastTs:0,lastSubmits:0};let seen=0;
    const loop=t=>{
      const prev=T.lastTs,cpu=window.__ticks.cpu.get(prev)||0;window.__ticks.cpu.delete(prev);const submits=window.__ticks.submits-T.lastSubmits;T.lastSubmits=window.__ticks.submits;
      if(T.on&&prev&&submits>0)T.rows.push([t-prev,cpu,R.info.render.drawCalls,R.info.render.triangles]);T.lastTs=t;
      if(B.trackTimestamp&&B.timestampQueryPool?.render)R.resolveTimestampsAsync('render').then(()=>{const p=B.timestampQueryPool.render;const e=[...p.timestamps.entries()],fresh=e.slice(seen);seen=e.length;
        const frames=new Map();for(const [uid,ms] of fresh){const m=uid.match(/^.*?:(\d+):f(\d+)$/);if(!m)continue;const f=frames.get(+m[2])||{ms:0,p:{}};f.ms+=ms;const l=labels.get(+m[1])||'ctx';f.p[l]=(f.p[l]||0)+ms;frames.set(+m[2],f);}
        if(T.on)for(const f of frames.values()){T.gpu.push(f.ms);for(const [k,v] of Object.entries(f.p)){const a=T.passes.get(k)||{ms:0,n:0};a.ms+=v;a.n++;T.passes.set(k,a);}}
        if(e.length>200000){p.timestamps.clear();seen=0;}}).catch(()=>{});
      requestAnimationFrame(loop);
    };requestAnimationFrame(loop);
  });
  const measure=async()=>{
    await page.evaluate(()=>{const T=window.__m;T.rows=[];T.gpu=[];T.passes=new Map();T.on=true;});
    await page.waitForTimeout(sample*1000);
    return page.evaluate(()=>{const T=window.__m;T.on=false;const q=(a,p)=>{const s=[...a].sort((x,y)=>x-y);return s.length?+s[Math.min(s.length-1,Math.floor(s.length*p))].toFixed(2):null;};
      const iv=T.rows.map(r=>r[0]),mean=iv.reduce((a,b)=>a+b,0)/Math.max(1,iv.length),n=Math.max(1,T.gpu.length);
      return {fps:+(1000/mean).toFixed(1),intervalP50:q(iv,.5),intervalP90:q(iv,.9),cpuP50:q(T.rows.map(r=>r[1]),.5),gpuP50:q(T.gpu,.5),gpuP90:q(T.gpu,.9),
        draws:q(T.rows.map(r=>r[2]),.5),triangles:q(T.rows.map(r=>r[3]),.5),passes:[...T.passes.entries()].map(([k,v])=>[k,+(v.ms/n).toFixed(2),+(v.n/n).toFixed(1)]).sort((a,b)=>b[1]-a[1]).slice(0,6)};});
  };
  // Ablations: each returns an undo function (run in the page).
  // Ablations: each returns an undo function (run in the page). "Interior" = anything under a root tagged
  // userData.perfKind 'interior' (hotel modules, landmark/Sphere interiors) or a hotel module root.
  const ABLATIONS={
    'outside-hidden':()=>{const S=window.__afterlightProbe.engine().scene,hidden=[];const inside=o=>{for(let p=o;p;p=p.parent)if(p.userData?.perfKind==='interior'||/^Streamed /.test(p.name))return true;return false;};
      S.traverse(o=>{if(o.isMesh&&o.visible&&!inside(o)&&!o.isSkinnedMesh)hidden.push(o);});for(const o of hidden)o.visible=false;return ()=>{for(const o of hidden)o.visible=true;};},
    'interior-local-lights':()=>{const pr=window.__afterlightProbe,S=pr.engine().scene,R=pr.renderer();const all=R.lighting.getNode(S).getLights();
      // Interior materials keep sun, sky, ambient and the local pools (venue + hotel lights); the city's pooled fixture lights go.
      const keep=all.filter(l=>!l.isPointLight||/^Shared venue light/.test(l.name)||(l.parent===S&&!l.name));const node=pr.lightsNode(keep);const saved=[];
      const inside=o=>{for(let p=o;p;p=p.parent)if(p.userData?.perfKind==='interior'||/^Streamed /.test(p.name))return true;return false;};
      S.traverse(o=>{if(!o.isMesh||!inside(o))return;for(const m of [o.material].flat())if(m&&!saved.some(s=>s[0]===m)){saved.push([m,m.lightsNode]);m.lightsNode=node;m.needsUpdate=true;}});
      window.__kept=keep.length;return ()=>{for(const [m,n] of saved){m.lightsNode=n;m.needsUpdate=true;}};},
    'interior-unlit':()=>{const S=window.__afterlightProbe.engine().scene;let B=null;S.traverse(o=>{for(const m of [o.material].flat())if(m?.isMeshBasicMaterial&&!B)B=m.constructor;});const saved=[];
      const inside=o=>{for(let p=o;p;p=p.parent)if(p.userData?.perfKind==='interior'||/^Streamed /.test(p.name))return true;return false;};
      S.traverse(o=>{if(!o.isMesh||!inside(o))return;saved.push([o,o.material]);o.material=[o.material].flat().map(m=>new B({map:m.map,color:m.color,side:m.side,transparent:m.transparent,opacity:m.opacity,alphaTest:m.alphaTest}));if(o.material.length===1)o.material=o.material[0];});
      return ()=>{for(const [o,m] of saved)o.material=m;};},
    'half-res':()=>{const R=window.__afterlightProbe.renderer(),r=R.getPixelRatio();R.setPixelRatio(r/2);return ()=>R.setPixelRatio(r);},
    // The renderer's full light list on interior materials (undoes InteriorLighting) for A/B.
    'interior-full-lights':()=>{const S=window.__afterlightProbe.engine().scene,saved=[];const inside=o=>{for(let p=o;p;p=p.parent)if(p.userData?.perfKind==='interior'||/^Streamed /.test(p.name))return true;return false;};
      S.traverse(o=>{if(!o.isMesh||!inside(o))return;for(const m of [o.material].flat())if(m?.lightsNode&&!saved.some(s=>s[0]===m)){saved.push([m,m.lightsNode]);m.lightsNode=null;m.needsUpdate=true;}});
      return ()=>{for(const [m,n] of saved){m.lightsNode=n;m.needsUpdate=true;}};},
  };
  for(const [g,re] of GROUPS){
    const sel=`const S=window.__afterlightProbe.engine().scene,re=new RegExp(${JSON.stringify(re.replace(/^\*/,''))}),roots=${JSON.stringify(re)}.startsWith('*')?(()=>{const r2=new RegExp(${JSON.stringify(re.replace(/^\*/,''))}),out=[];S.traverse(o=>{if(r2.test(o.name)&&!out.some(p=>{for(let q=o.parent;q;q=q.parent)if(q===p)return true;return false;}))out.push(o);});return out;})():S.children.filter(c=>re.test(c.name)),meshes=[];for(const r of roots)r.traverse(o=>{if(o.isMesh)meshes.push(o);});`;
    ABLATIONS[g+'-hidden']=new Function(sel+`const h=meshes.filter(o=>o.visible);for(const o of h)o.visible=false;return ()=>{for(const o of h)o.visible=true;};`);
    ABLATIONS[g+'-unlit']=new Function(sel+`let B=null;S.traverse(o=>{for(const m of [o.material].flat())if(m?.isMeshBasicMaterial&&!B)B=m.constructor;});const saved=[];for(const o of meshes){saved.push([o,o.material]);o.material=[o.material].flat().map(m=>new B({map:m.map,color:m.color,side:m.side,transparent:m.transparent,opacity:m.opacity,alphaTest:m.alphaTest}));if(o.material.length===1)o.material=o.material[0];}return ()=>{for(const [o,m] of saved)o.material=m;};`);
    // Sun, sky and ambient only (no point lights at all) on this group's materials.
    // The renderer's full light list on this group (undoes InteriorLighting / NearbyLights) for A/B.
    ABLATIONS[g+'-full-lights']=new Function(sel+`const saved=[];for(const o of meshes)for(const m of [o.material].flat())if(m?.lightsNode&&!saved.some(x=>x[0]===m)){saved.push([m,m.lightsNode]);m.lightsNode=null;m.needsUpdate=true;}return ()=>{for(const [m,n] of saved){m.lightsNode=n;m.needsUpdate=true;}};`);
    ABLATIONS[g+'-no-point-lights']=new Function(sel+`const pr=window.__afterlightProbe,R=pr.renderer(),keep=R.lighting.getNode(S).getLights().filter(l=>!l.isPointLight),node=pr.lightsNode(keep),saved=[];for(const o of meshes)for(const m of [o.material].flat())if(m&&!saved.some(x=>x[0]===m)){saved.push([m,m.lightsNode]);m.lightsNode=node;m.needsUpdate=true;}return ()=>{for(const [m,n] of saved){m.lightsNode=n;m.needsUpdate=true;}};`);
  }
  // --ablations a,b+c: each entry is one test; '+' combines steps (applied in order, undone in reverse).
  const only=opt('ablations',null);
  const PLAN=only?String(only).split(',').map(label=>[label,label.split('+')]):Object.keys(ABLATIONS).map(k=>[k,[k]]);
  const results=[];
  for(const [view,id,floor,room,roomView] of views){
    const placed=await page.evaluate(async([id,floor,room,roomView,hold])=>{const pr=window.__afterlightProbe;
      if(window.__exteriorHold){cancelAnimationFrame(window.__exteriorHold);window.__exteriorHold=0;}
      const holdPoint=(x,y,z)=>{if(!hold)return;const tick=()=>{pr.teleport(x,y,z);window.__exteriorHold=requestAnimationFrame(tick);};tick();};
      if(id==='spawn')return pr.position();
      if(id.startsWith('at:')){const [x,y,z,yaw,pitch]=id.slice(3).split(',').map(Number);pr.teleport(x,y,z);holdPoint(x,y,z);if(Number.isFinite(yaw))pr.look(yaw,pitch);return {x,y,z};}
      const p=id.startsWith('landmark:')?pr.landmark(id.slice(9),roomView):await pr.hotel(id,floor,room,roomView);return p&&{x:+p.x.toFixed(1),y:+p.y.toFixed(1),z:+p.z.toFixed(1)};},[id,floor,room,roomView,opt('hold',false)===true]);
    if(!placed){console.log(view,'could not be placed');results.push({view,error:'not placed'});continue;}
    await page.waitForTimeout(1500);await idle(5);await settle();
    const base=await measure();
    const lights=await page.evaluate(()=>{const p=window.__afterlightProbe,R=p.renderer(),S=p.engine().scene;const L=R.lighting.getNode(S).getLights();const types={};for(const l of L){const k=l.type+(l.castShadow?' (shadow)':'');types[k]=(types[k]||0)+1;}return types;});
    await page.screenshot({path:path.join(out,view+'.png')});
    const ab={};
    if(ablate){
      for(const [label,steps] of PLAN){
        const missing=steps.filter(k=>!ABLATIONS[k]);if(missing.length){ab[label]={error:'unknown '+missing.join(',')};continue;}
        await page.evaluate(srcs=>{const undo=srcs.map(src=>new Function('return ('+src+')()')());window.__undo=()=>{for(const u of undo.reverse())u?.();};},steps.map(k=>ABLATIONS[k].toString()));
        await settle();const m=await measure();ab[label]={fps:m.fps,gpuP50:m.gpuP50,cpuP50:m.cpuP50};
        const shown=await page.evaluate(()=>{const pr=window.__afterlightProbe,n=pr.renderer().lighting.getNode(pr.engine().scene);return n._shown?Object.fromEntries([...n._shown.entries()].map(([k,v])=>[k,v.length])):null;});if(shown)ab[label].batched=shown;
        if(opt('ablate-shots',false)===true)await page.screenshot({path:path.join(out,`${view}--${label}.png`)});
        await page.evaluate(()=>{window.__undo?.();window.__undo=null;});await settle();
      }
    }
    const row={view,tower:id,floor,room,roomView,placed,...base,lights,ablations:ab};results.push(row);
    console.log(`${view.padEnd(22)} ${String(base.fps).padStart(5)} fps  cpu ${base.cpuP50}  gpu ${base.gpuP50}/${base.gpuP90}  draws ${base.draws}  tris ${base.triangles}  lights ${JSON.stringify(lights)}`);
    for(const p of base.passes.slice(0,4))console.log(`      gpu ${String(p[1]).padStart(6)} ms x${p[2]} ${p[0]}`);
    if(ablate)console.log('      ablations',JSON.stringify(ab));
  }
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({viewport:[vw,vh],dpr,results,errors:errors.slice(0,20)},null,1));
  if(errors.length)console.log('page errors:',errors.slice(0,5).join('\n'));
} finally {
  clearTimeout(watchdog);
  try{fs.writeFileSync(path.join(out,'console.log'),logs.join('\n'));}catch{}
  await browser.close();
  if(!heldBefore)try{fs.unlinkSync(hold);}catch{}
}
