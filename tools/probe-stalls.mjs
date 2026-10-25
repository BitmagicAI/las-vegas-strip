// Frame stalls on a first visit (2026-10-24, the owner: pauses of tens of seconds when turning): a fresh browser profile
// on the dev server turns the camera, looks up and down, and teleports to five places, counting new pipelines and
// frames longer than 150 ms at each step. Writes .bitmagic/logs/turn-probe.json.
//   node tools/probe-stalls.mjs
import fs from 'node:fs';
import { launchSystemChrome, browserRendererArgs } from './lib/bitmagic-cli.mjs';
fs.mkdirSync('.bitmagic/logs', { recursive: true });
const port = JSON.parse(fs.readFileSync('.bitmagic/dev.json', 'utf8')).gamePort;
const logs = [];
const browser = await launchSystemChrome({ headless: true, args: [...browserRendererArgs(process.env, 'webgpu'), '--mute-audio'], command: 'turn probe' });
const out = [];
try {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  await ctx.addInitScript(() => { window.__gaps = []; let last = 0; const tick = (t) => { if (last && t - last > 150) window.__gaps.push([Math.round(last), Math.round(t - last)]); last = t; requestAnimationFrame(tick); }; requestAnimationFrame(tick); });
  const page = await ctx.newPage();
  page.on('console', (m) => logs.push(m.text().slice(0, 200)));
  await page.goto(`http://localhost:${port}/?probe`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  for (let i = 0; i < 600 && !logs.some((s) => s.includes('🎮 Starting game...')); i++) {
    const choice = page.locator('.start-screen-selection__option').first(), play = page.locator('#play-button, .hud-play-button').first();
    if (await choice.isVisible().catch(() => false)) await choice.click().catch(() => {}); else if (await play.isVisible().catch(() => false)) await play.click().catch(() => {});
    await page.waitForTimeout(500);
  }
  await page.waitForFunction(() => !!window.__afterlightProbe, null, { timeout: 600000 });
  const state = () => page.evaluate(() => { const r = window.__afterlightProbe.engine().renderer; const p = r._pipelines;
    return { pipelines: p?.caches?.size ?? -1, vs: p?.programs?.vertex?.size ?? -1, fs: p?.programs?.fragment?.size ?? -1, now: Math.round(performance.now()), busy: window.__afterlightProbe.streaming().busy }; });
  const idle = async () => { for (let i = 0; i < 120; i++) { if (!(await state()).busy) break; await page.waitForTimeout(500); } };
  await idle(); await page.waitForTimeout(2000);
  const step = async (label, fn) => {
    const a = await state(); await page.evaluate(() => { window.__gaps.length = 0; });
    await page.evaluate(fn); await page.waitForTimeout(2500); await idle(); await page.waitForTimeout(500);
    const b = await state(); const gaps = await page.evaluate(() => window.__gaps.slice());
    const r = { label, newPipelines: b.pipelines - a.pipelines, newShaders: (b.vs + b.fs) - (a.vs + a.fs), stallMs: gaps.reduce((s, g) => s + g[1], 0), worstMs: Math.max(0, ...gaps.map((g) => g[1])), pipelines: b.pipelines };
    out.push(r); console.log(JSON.stringify(r));
  };
  for (let k = 0; k < 8; k++) await step(`turn yaw ${k * 45}`, `window.__afterlightProbe.look(${(k * Math.PI / 4).toFixed(3)}, 0)`);
  for (let k = 0; k < 8; k++) await step(`look down/up yaw ${k * 45}`, `window.__afterlightProbe.look(${(k * Math.PI / 4).toFixed(3)}, ${k % 2 ? 0.5 : -0.4})`);
  for (const [n, x, z] of [['Bellagio front', -60, 160], ['Venetian', 270, -640], ['Caesars', -100, -250], ['Sphere', 983, -470], ['NY-NY', 300, 1500]]) {
    await step(`teleport ${n}`, `window.__afterlightProbe.teleport(${x}, 2, ${z})`);
    for (let k = 0; k < 4; k++) await step(`  ${n} yaw ${k * 90}`, `window.__afterlightProbe.look(${(k * Math.PI / 2).toFixed(3)}, 0)`);
  }
  fs.writeFileSync('.bitmagic/logs/turn-probe.json', JSON.stringify({ out, logs: logs.slice(-300) }, null, 1));
} finally { await browser.close(); }
