import fs from 'node:fs';
import path from 'node:path';
import {launchSystemChrome} from './lib/bitmagic-cli.mjs';
import {browserRendererArgs} from './lib/bitmagic-cli.mjs';
const selected=process.argv.slice(2);
const out='build/public-resorts/comparison/captures';fs.mkdirSync(out,{recursive:true});
const shots=JSON.parse(fs.readFileSync('src/work/public-resorts/review.json'));
const browser=await launchSystemChrome({headless:true,args:[...browserRendererArgs(process.env,'webgpu'),'--mute-audio'],command:'local resort review'});
const errors=[],logs=[],requests=[],report=[];
try {
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('console',m=>{const s=m.text();logs.push(s);if(m.type()==='error' && /Failed to load Voxel|MeshLevelSchemaError|Hotel template|Streaming/.test(s))errors.push(s);if(s.includes('[Hotel')||s.includes('[BuildingVisibility]'))console.log(s);});
 page.on('request',r=>{if(/\/build\/hotels\/.*\.glb/.test(r.url()))requests.push(r.url());});
 await page.addInitScript(()=>Object.defineProperty(Element.prototype,'requestPointerLock',{configurable:true,writable:true,value:()=>Promise.resolve()}));
 await page.goto('http://localhost:3090/?hotelDebug&publicReview',{waitUntil:'domcontentloaded',timeout:60000});await page.bringToFront();
 const deadline=Date.now()+180000;
 while(Date.now()<deadline && !logs.some(s=>s.includes('🎮 Starting game...'))){
  if(errors.length)throw Error(errors.join('\n'));
  const choice=page.locator('.start-screen-selection__option').first();
  const play=page.locator('#play-button, .hud-play-button').first();
  if(await choice.isVisible())await choice.click();
  else if(await play.isVisible()){await page.waitForTimeout(500);if(await play.isVisible())await play.click();}
  await page.waitForTimeout(500);
 }
 if(!logs.some(s=>s.includes('🎮 Starting game...')))throw Error('Game did not start');
 await page.locator('#public-review-area').waitFor({state:'visible',timeout:60000});
 await page.waitForTimeout(2500);
 const bootRooms=requests.filter(u=>/-room\.glb/.test(u));if(bootRooms.length)throw Error('Detailed rooms requested at boot');
 await page.screenshot({path:path.join(out,'startup.png')});
 for(const shot of shots){
  if(!shot.name.startsWith('comparison-'))continue;
  if(selected.length && !selected.includes(shot.name))continue;
  await page.selectOption('#public-review-area',shot.name);
  const mark=logs.length;
  await page.getByRole('button',{name:'Inspect public area',exact:true}).click();
  await page.waitForFunction(()=>!document.querySelector('.hud-progress-bar--busy'),{},{timeout:60000});
  await page.waitForTimeout(3000);
  const stats=await page.locator('#hotel-stream-stats').innerText();
  // Hide overlays only; preserve the full camera frame, geometry and lighting.
  const overlayState=await page.evaluate(()=>{
    const elements=[...document.querySelectorAll('body *')].filter(e=>e instanceof HTMLElement && !e.querySelector('canvas') && getComputedStyle(e).position==='absolute' && e.tagName!=='CANVAS');
    return elements.map((e,i)=>{e.dataset.compareOverlay=String(i);const before=e.style.visibility;e.style.visibility='hidden';return {i,before};});
  });
  await page.screenshot({path:path.join(out,`${shot.name}.png`)});
  await page.evaluate(state=>{for(const {i,before} of state){const e=document.querySelector(`[data-compare-overlay="${i}"]`);if(e){e.style.visibility=before;delete e.dataset.compareOverlay;}}},overlayState);
  report.push({area:shot.name,stats,events:logs.slice(mark).filter(s=>s.includes('[Hotel')||s.includes('[BuildingVisibility]'))});
  console.log('REVIEW',shot.name,stats);
 }
 await page.getByRole('button',{name:'Leave hotel',exact:true}).click();await page.waitForTimeout(13000);
 report.push({cleanup:await page.locator('#hotel-stream-stats').innerText()});
 await page.screenshot({path:path.join(out,'cleanup.png')});
 if(errors.length)throw Error(errors.join('\n'));
} finally {
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({errors,requests,report},null,2));
 fs.writeFileSync(path.join(out,'console.log'),logs.join('\n'));await browser.close();
}
