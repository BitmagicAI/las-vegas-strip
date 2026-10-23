// Stills of the story at given times: node tools/info-video/snap.mjs <outdir> <dpr> <t> [t ...]  (needs serve.sh)
import {createRequire} from 'module';
import fs from 'fs';
import { cliRequire } from '../lib/bitmagic-cli.mjs';
const require = cliRequire;
const {chromium} = require('playwright-core');
const [out, dpr, ...ts] = process.argv.slice(2);
fs.mkdirSync(out, {recursive: true});
const browser = await chromium.launch({headless: true, channel: 'chrome', args: ['--use-angle=metal', '--ignore-gpu-blocklist']});
const page = await browser.newPage({viewport: {width: 1920, height: 1080}, deviceScaleFactor: +dpr});
const errors = []; page.on('pageerror', e => errors.push(e.message)); page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 200)); });
await page.goto(`http://127.0.0.1:8098/tools/info-video/story.html?dpr=${dpr}`);
await page.waitForFunction(() => window.story && window.story.ready, null, {timeout: 300000}).catch(e => errors.push('not ready: ' + e.message));
for (const t of ts) { await page.evaluate(t => window.story.render(t), +t); await page.screenshot({path: `${out}/t${(+t).toFixed(2).padStart(7, '0')}.jpg`, type: 'jpeg', quality: 85}); }
console.log('snaps', ts.length, errors.slice(0, 6).join(' | '));
await browser.close();
