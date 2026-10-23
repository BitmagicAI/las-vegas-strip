import fs from 'node:fs';
import path from 'node:path';
import {launchSystemChrome} from './lib/bitmagic-cli.mjs';
import {browserRendererArgs} from './lib/bitmagic-cli.mjs';
const out='build/hotels/resort-expansion/live';fs.mkdirSync(out,{recursive:true});
const towers=JSON.parse(fs.readFileSync('src/work/hotels/towers.json')).filter(t=>!['bellagio','veer'].includes(t.set));
const browser=await launchSystemChrome({headless:true,args:[...browserRendererArgs(process.env,'webgpu'),'--mute-audio'],command:'local resort review'});
const errors=[],logs=[],requests=[],report=[];
try {
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('console',m=>{const s=m.text();logs.push(s);if(m.type()==='error' && /Failed to load Voxel|MeshLevelSchemaError|Hotel template|Streaming/.test(s))errors.push(s);if(s.includes('[Hotel')||s.includes('[BuildingVisibility]'))console.log(s);});
 page.on('request',r=>{if(/\/build\/hotels\/.*\.glb/.test(r.url()))requests.push(r.url());});
 await page.addInitScript(()=>Object.defineProperty(Element.prototype,'requestPointerLock',{configurable:true,writable:true,value:()=>Promise.resolve()}));
 await page.goto('http://localhost:3090/?hotelDebug',{waitUntil:'domcontentloaded',timeout:60000});await page.bringToFront();
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
 await page.locator('#hotel-review-property').waitFor({state:'visible',timeout:60000});
 await page.waitForTimeout(2500);
 const bootRooms=requests.filter(u=>/-room\.glb/.test(u));if(bootRooms.length)throw Error('Detailed rooms requested at boot');
 await page.screenshot({path:path.join(out,'startup.png')});
 for(const t of towers){
  await page.selectOption('#hotel-review-property',t.id);
  for(const kind of ['hallway','room']){
   const mark=logs.length;
   await page.getByRole('button',{name:`Inspect ${kind}`,exact:true}).click();
   await page.waitForFunction(()=>!document.querySelector('.hud-progress-bar--busy'),{},{timeout:60000});
   await page.waitForTimeout(2500);
   const stats=await page.locator('#hotel-stream-stats').innerText();
   await page.screenshot({path:path.join(out,`${t.id}-${kind}.png`)});
   report.push({tower:t.id,kind,stats,events:logs.slice(mark).filter(s=>s.includes('[Hotel')||s.includes('[BuildingVisibility]'))});
   console.log('REVIEW',t.id,kind,stats);
  }
 }
 await page.getByRole('button',{name:'Leave hotel',exact:true}).click();await page.waitForTimeout(13000);
 report.push({cleanup:await page.locator('#hotel-stream-stats').innerText()});
 await page.screenshot({path:path.join(out,'cleanup.png')});
 if(errors.length)throw Error(errors.join('\n'));
} finally {
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({errors,requests,report},null,2));
 fs.writeFileSync(path.join(out,'console.log'),logs.join('\n'));await browser.close();
}
