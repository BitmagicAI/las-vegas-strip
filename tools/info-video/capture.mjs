// Capture story frames: node tools/info-video/capture.mjs <outdir> <dpr> <firstFrame> <lastFrame> <jpg|png> [query]
// Frame f shows story time f/60. Skips frames that already exist (resumable). Needs tools/info-video/serve.sh running.
// Writes the story's sound-effect events to tools/info-video/events.json on every run.
import {createRequire} from 'module';
import fs from 'fs';
import { cliRequire } from '../lib/bitmagic-cli.mjs';
const require = cliRequire;
const {chromium} = require('playwright-core');
const [out, dpr, f0, f1, fmt, query = ''] = process.argv.slice(2);
fs.mkdirSync(out, {recursive: true});
const browser = await chromium.launch({headless: true, channel: 'chrome', args: ['--use-angle=metal', '--ignore-gpu-blocklist', '--enable-gpu-rasterization']});
const page = await browser.newPage({viewport: {width: 1920, height: 1080}, deviceScaleFactor: +dpr});
const errors = [];
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 300)); });
await page.goto(`http://127.0.0.1:8098/tools/info-video/story.html?dpr=${dpr}${query ? '&' + query : ''}`);
await page.waitForFunction(() => window.story && window.story.ready, null, {timeout: 300000});
const fps = await page.evaluate(() => window.story.fps);
fs.writeFileSync(new URL('./events.json', import.meta.url), JSON.stringify(await page.evaluate(() => window.story.events), null, 0));
const t0 = Date.now(); let n = 0;
for (let f = +f0; f <= +f1; f++) {
  const path = `${out}/f${String(f).padStart(5, '0')}.${fmt}`;
  if (fs.existsSync(path)) continue;
  await page.evaluate(t => window.story.render(t), f / fps);
  await page.screenshot(fmt === 'png' ? {path, type: 'png'} : {path, type: 'jpeg', quality: 92});
  n++;
  if (n % 300 === 0) console.log(`${out} f${f} ${(n / ((Date.now() - t0) / 1000)).toFixed(2)} fps`);
}
console.log('done', f0, f1, n, 'frames', ((Date.now() - t0) / 1000).toFixed(0), 's', errors.slice(0, 5).join(' | '));
await browser.close();
