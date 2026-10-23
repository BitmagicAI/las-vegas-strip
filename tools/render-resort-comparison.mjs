import fs from 'node:fs';
import path from 'node:path';
import { launchSystemChrome } from './lib/bitmagic-cli.mjs';

const out = 'build/public-resorts/comparison';
const browser = await launchSystemChrome({ headless: true, command: 'local photo comparison' });
const errors = [];
try {
  const page = await browser.newPage({viewport:{width:1600,height:1200},deviceScaleFactor:1});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto('http://localhost:3090/build/public-resorts/comparison/index.html', { waitUntil:'networkidle' });
  await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode().catch(()=>{}))));
  const broken = await page.evaluate(()=>[...document.images].filter(i=>!i.naturalWidth).map(i=>i.src));
  if (broken.length) throw Error('Missing comparison images: '+broken.join(', '));
  const ids = await page.locator('article').evaluateAll(articles=>articles.map(a=>a.id));
  for (const id of ids) {
    await page.evaluate(id=>{location.hash=id;},id);
    const card = page.locator(`article#${id}`);
    await card.waitFor({state:'visible'});
    await card.screenshot({path:path.join(out,`${id}-comparison.png`)});
  }
  await page.evaluate(()=>{location.hash='all';});
  await page.waitForFunction(()=>[...document.querySelectorAll('article')].every(a=>!a.hidden));
  if(errors.length)throw Error(errors.join('\n'));
  fs.writeFileSync(path.join(out,'gallery-check.json'),JSON.stringify({properties:ids.length,images:await page.locator('img').count(),broken,errors},null,2));
  console.log(`Checked ${ids.length} property comparisons; all images loaded.`);
} finally { await browser.close(); }
