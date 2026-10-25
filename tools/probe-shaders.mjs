// Shader builds at start-up (2026-10-24): boots the game on the dev server with ?shaderAudit (src/work/ShaderAudit.ts) and
// writes .bitmagic/logs/shader-audit.json: node builds and their cost, fragment programs, render contexts, light lists,
// main-thread freezes and the warm-up's compile calls. TELEPORT=x,y,z also lists the builds a teleport there causes.
//   node tools/probe-shaders.mjs
import fs from 'node:fs';
import { launchSystemChrome, browserRendererArgs } from './lib/bitmagic-cli.mjs';
fs.mkdirSync('.bitmagic/logs', { recursive: true });
const port = JSON.parse(fs.readFileSync('.bitmagic/dev.json', 'utf8')).gamePort;
const logs = [];
const browser = await launchSystemChrome({ headless: true, args: [...browserRendererArgs(process.env, 'webgpu'), '--mute-audio'], command: 'fragment probe' });
try {
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 720 } })).newPage();
  page.on('console', (m) => logs.push(m.text().slice(0, 200)));
  const t0 = Date.now(); let longest = 0, stalls = 0;
  await page.goto(`http://localhost:${port}/?probe&shaderAudit`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  for (let i = 0; i < 600 && !logs.some((s) => s.includes('🎮 Starting game...')); i++) {
    const play = page.locator('#play-button, .hud-play-button, .start-screen-selection__option').first();
    if (await play.isVisible().catch(() => false)) await play.click().catch(() => {});
    await page.waitForTimeout(500);
  }
  await page.waitForFunction(() => !!window.__afterlightProbe, null, { timeout: 600000 });
  for (let i = 0; i < 160; i++) { if (!(await page.evaluate(() => window.__afterlightProbe.streaming().busy))) break; await page.waitForTimeout(500); }
  if (process.env.TELEPORT) {
    await page.waitForTimeout(3000);
    const mark = await page.evaluate(() => window.__shaderAudit().recent.length);
    const [x, y, z] = process.env.TELEPORT.split(',').map(Number);
    await page.evaluate(([x, y, z]) => window.__afterlightProbe.teleport(x, y, z), [x, y, z]);
    await page.waitForTimeout(4000);
    for (let i = 0; i < 120; i++) { if (!(await page.evaluate(() => window.__afterlightProbe.streaming().busy))) break; await page.waitForTimeout(500); }
    await page.waitForTimeout(2000);
    const after = await page.evaluate((m) => window.__shaderAudit().recent.slice(m), mark);
    fs.writeFileSync('.bitmagic/logs/teleport-builds.txt', after.join('\n'));
    console.log(after.length, 'builds after the teleport');
  }
  const audit = await page.evaluate(() => window.__shaderAudit());
  fs.writeFileSync('.bitmagic/logs/shader-audit.json', JSON.stringify(audit, null, 1));
  console.log(JSON.stringify(audit.totals), audit.programs.length, 'fragment programs');
  console.log(audit.contexts.join('\n'));
  console.log('freezes', audit.freezes.join(' '));
  console.log('build ms by second', Object.entries(audit.timeline).filter(([, ms]) => ms > 50).map(([s, ms]) => `${s}s:${Math.round(ms)}`).join(' '));
  console.log(logs.filter((s) => /ready|loaded|Starting game|\[Startup\]|\[Load/.test(s)).slice(0, 30).join('\n'));
  const c = audit.compiles; console.log('compiles', c.length, c.slice(0, 3).join(' | '), '...', c.slice(-3).join(' | '));
  console.log(logs.filter((s) => /GPU warmup|ShaderSharing|Unsupported/.test(s)).join('\n'));
} finally { await browser.close(); }
