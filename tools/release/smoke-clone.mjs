// Release smoke test: boots the game from a checkout's running `bitmagic dev`, visits streamed places (hotel rooms in
// several towers, landmark and resort venues, the Sphere, the coaster), and fails if any request 404s or the page throws.
// Use it on a fresh clone after `node tools/release/fetch-assets.mjs` to prove the asset pack is complete.
//
//   bitmagic dev            # in the background, in the checkout under test
//   node tools/release/smoke-clone.mjs [--viewport 960x540] [--shots]
//
// Writes build/probe/smoke/report.json (and a screenshot per stop with --shots). One headless Chrome, always closed.
import fs from 'node:fs';
import path from 'node:path';
import { launchSystemChrome, browserRendererArgs } from '../lib/bitmagic-cli.mjs';

const argv = process.argv.slice(2);
const opt = (n, d) => { const i = argv.indexOf('--' + n); return i < 0 ? d : (argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : true); };
const [vw, vh] = String(opt('viewport', '960x540')).split('x').map(Number);
const shots = opt('shots', false) === true;
const port = JSON.parse(fs.readFileSync('.bitmagic/dev.json', 'utf8')).gamePort;
const out = 'build/probe/smoke';
fs.mkdirSync(out, { recursive: true });

// Places that load something different: hotel guest floors in four tower systems, three venue builders, the Sphere,
// the coaster. Coordinates are world metres (X east, Y up, Z south).
const STOPS = [
  { name: 'hotel bellagio-north floor 5 room', hotel: ['bellagio-north', 5, 0, null] },
  { name: 'hotel mgm-grand-1 floor 4 corridor', hotel: ['mgm-grand-1', 4, null, 'corridor'] },
  { name: 'hotel venetian-1 floor 4 room', hotel: ['venetian-1', 4, 0, null] },
  { name: 'hotel strat-1 floor 4 room', hotel: ['strat-1', 4, 0, null] },
  { name: 'venue venetian lobby', landmark: ['venetian', 'lobby'] },
  { name: 'venue linq lobby', landmark: ['linq', 'lobby'] },
  { name: 'venue bellagio lobby', landmark: ['bellagioLobby', 'entrance'] },
  { name: 'Sphere approach', teleport: [983, 2, -470] },
  { name: 'New York-New York coaster', teleport: [300, 2, 1500] },
];

const failed = [], pageErrors = [], consoleErrors = [], logs = [];
let browser, page;
try {
  browser = await launchSystemChrome({ headless: true, args: [...browserRendererArgs(process.env, 'webgpu'), '--mute-audio'], command: 'release smoke test' });
  const context = await browser.newContext({ viewport: { width: vw, height: vh } });
  page = await context.newPage();
  page.on('console', (m) => { const t = m.text(); logs.push(t); if (m.type() === 'error') consoleErrors.push(t.slice(0, 300)); });
  page.on('pageerror', (e) => pageErrors.push(String(e).slice(0, 300)));
  page.on('response', (r) => {
    const p = new URL(r.url()).pathname;
    if (r.status() >= 400) failed.push(`${r.status()} ${p}`);
    // the dev server answers a missing file with index.html (200), so a data file served as HTML is missing too
    else if (/\.(json|glb|webp|mp4|jpg|png|bin|wasm)$/i.test(p) && /text\/html/.test(r.headers()['content-type'] || '')
      && p !== '/build/optimized/manifest.json') failed.push(`MISSING (served index.html) ${p}`); // (a clone has no optimizer manifest, by design)
  });
  page.on('requestfailed', (r) => { const f = r.failure()?.errorText || ''; if (!/ERR_ABORTED/.test(f)) failed.push(`FAILED ${new URL(r.url()).pathname} ${f}`); });
  await page.goto(`http://localhost:${port}/?probe`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  const deadline = Date.now() + 240000;
  while (Date.now() < deadline && !logs.some((s) => s.includes('🎮 Starting game...'))) {
    const choice = page.locator('.start-screen-selection__option').first();
    const play = page.locator('#play-button, .hud-play-button').first();
    if (await choice.isVisible()) await choice.click();
    else if (await play.isVisible()) { await page.waitForTimeout(500); if (await play.isVisible()) await play.click(); }
    await page.waitForTimeout(500);
  }
  if (!logs.some((s) => s.includes('🎮 Starting game...'))) throw Error('the game did not start');
  const bootStart = Date.now();
  await page.waitForFunction(() => !!window.__afterlightProbe, null, { timeout: Number(process.env.SMOKE_BOOT_MS || 300000) });
  console.log(`city loaded in ${((Date.now() - bootStart) / 1000).toFixed(0)} s after Play`);
  const idle = async (quietPolls = 6) => {
    let quiet = 0; const end = Date.now() + 90000;
    while (quiet < quietPolls && Date.now() < end) {
      const busy = await page.evaluate(() => window.__afterlightProbe.streaming().busy);
      quiet = busy ? 0 : quiet + 1; await page.waitForTimeout(500);
    }
  };
  await idle(8);
  const visits = [];
  for (const s of STOPS) {
    const before = failed.length;
    const where = await page.evaluate(async (s) => {
      const p = window.__afterlightProbe;
      if (s.hotel) return p.hotel(...s.hotel);
      if (s.landmark) return p.landmark(...s.landmark);
      p.teleport(...s.teleport); return { x: s.teleport[0], y: s.teleport[1], z: s.teleport[2] };
    }, s);
    await page.waitForTimeout(1500); await idle(); await page.waitForTimeout(1500);
    const pos = await page.evaluate(() => window.__afterlightProbe.position());
    if (shots) await page.screenshot({ path: path.join(out, s.name.replace(/[^a-z0-9]+/gi, '-') + '.jpg'), type: 'jpeg', quality: 70 });
    visits.push({ stop: s.name, placed: !!where, position: pos && [pos.x, pos.y, pos.z].map((v) => +(+v).toFixed(1)), newFailures: failed.slice(before) });
    console.log(`${where ? 'ok  ' : 'MISS'} ${s.name}${failed.length > before ? `  (${failed.length - before} failed requests)` : ''}`);
  }
  const report = { port, failed: [...new Set(failed)], pageErrors, consoleErrors: consoleErrors.slice(0, 50), visits };
  fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify(report, null, 1));
  for (const f of report.failed) console.log('FAIL ', f);
  for (const e of pageErrors) console.log('ERROR', e);
  console.log(`${report.failed.length} failed requests, ${pageErrors.length} page errors, ${consoleErrors.length} console errors, ` +
    `${visits.filter((v) => !v.placed).length} stops not placed -> ${out}/report.json`);
  process.exitCode = report.failed.length || pageErrors.length || visits.some((v) => !v.placed) ? 1 : 0;
} catch (e) {
  // boot or a stop failed: keep what the page said, so the cause is visible
  fs.writeFileSync(path.join(out, 'failure.json'), JSON.stringify({ error: String(e), failed: [...new Set(failed)], pageErrors, consoleErrors, lastLogs: logs.slice(-80) }, null, 1));
  await page?.screenshot({ path: path.join(out, 'failure.jpg'), type: 'jpeg', quality: 70 }).catch(() => {});
  console.log(`FAILED: ${String(e).split('\n')[0]}`);
  for (const f of [...new Set(failed)].slice(0, 30)) console.log('FAIL ', f);
  for (const x of pageErrors.slice(0, 10)) console.log('ERROR', x);
  console.log(`last console lines and the screenshot: ${out}/failure.json, failure.jpg`);
  process.exitCode = 1;
} finally {
  // close, but never hang on it: the process must end so scripts and CI can read the exit code
  await Promise.race([browser?.close(), new Promise((r) => setTimeout(r, 15000))]).catch(() => {});
  process.exit(process.exitCode ?? 0);
}
