#!/usr/bin/env node
/*
 * compare-lods.mjs: the baked distant LODs against the browser-clustered ones (2026-10-26), from fixed viewpoints, as the
 * game shows them and with every block forced to its LOD (`?lodLevel=1`, which magnifies the difference). One headless
 * Chrome at a time on the dev server; writes .bitmagic/bake/compare/<view>.png (2 x 2: clustered | baked, normal / forced).
 *   node tools/bake/compare-lods.mjs [view ...]
 */
import fs from 'node:fs';
import path from 'node:path';
import { launchSystemChrome, browserRendererArgs } from '../lib/bitmagic-cli.mjs';

const VIEWS = {
  'linq-aerial': ['linq', 'facade-aerial'], 'ti-aerial': ['ti', 'facade-aerial'], 'bellagio-aerial': ['bellagioBlock', 'aerial'],
  'harrahs-street': ['harrahs', 'strip'], 'venetian-skyline': ['venetian', 'skyline'], 'park-skyline': ['park', 'skyline'],
};
const wanted = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(VIEWS);
const OUT = path.resolve('.bitmagic/bake/compare'); fs.mkdirSync(OUT, { recursive: true });
const port = JSON.parse(fs.readFileSync('.bitmagic/dev.json', 'utf8')).gamePort;
const ALL = { clustered: 'bake=off', baked: '', truth: 'lodLevel=0', 'clustered-forced': 'bake=off&lodLevel=1', 'baked-forced': 'lodLevel=1' };
// CONFIGS=truth,clustered,baked limits the runs
const CONFIGS = (process.env.CONFIGS ?? 'clustered,baked,truth,clustered-forced,baked-forced').split(',').map((k) => [k, ALL[k]]);

for (const [name, query] of CONFIGS) {
  const browser = await launchSystemChrome({ headless: true, args: [...browserRendererArgs(process.env, 'webgpu'), '--mute-audio'], command: 'LOD comparison' });
  try {
    const page = await (await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 })).newPage();
    const logs = []; page.on('console', (m) => logs.push(m.text()));
    await page.addInitScript(() => Object.defineProperty(Element.prototype, 'requestPointerLock', { configurable: true, writable: true, value: () => Promise.resolve() }));
    await page.goto(`http://localhost:${port}/?probe&quality=ultra&${query}`, { waitUntil: 'domcontentloaded', timeout: 120000 });
    for (let i = 0; i < 1200 && !logs.some((s) => s.includes('🎮 Starting game...')); i++) {
      const play = page.locator('#play-button, .hud-play-button, .start-screen-selection__option').first();
      if (await play.isVisible().catch(() => false)) await play.click().catch(() => {});
      await page.waitForTimeout(500);
    }
    await page.waitForFunction(() => !!window.__afterlightProbe, null, { timeout: 600000 });
    // streaming idle, and every block at full detail has its near level filled (lazy near detail, CityLod)
    const idle = async () => {
      for (let i = 0; i < 360; i++) {
        const busy = await page.evaluate(async () => {
          if (window.__afterlightProbe.streaming().busy) return true;
          const lod = await import('/dist/src/work/CityLod.js').catch(() => null), s = lod?.cityLodStats?.(window.__afterlightProbe.engine().scene);
          return !!s && s.lazy > 0 && s.nearFilled < s.full;
        });
        if (!busy) return; await page.waitForTimeout(500);
      }
    };
    for (const view of wanted) {
      const [key, v] = VIEWS[view];
      await page.evaluate(([key, v]) => {
        const p = window.__afterlightProbe, at = p.landmark(key, v);
        // hold the capsule where the view is (aerial views would fall)
        const body = p.engine().getPlayerLoader?.()?.getPlayerBody?.(); body?.setEnabled(false);
        return at;
      }, [key, v]);
      await page.waitForTimeout(3000); await idle(); await page.waitForTimeout(2500);
      // place the camera again right before the shot (the capsule can fall while held views stream): two frames, no more
      await page.evaluate(([key, v]) => new Promise((r) => { window.__afterlightProbe.landmark(key, v); requestAnimationFrame(() => requestAnimationFrame(r)); }), [key, v]);
      await page.screenshot({ path: path.join(OUT, `${view}.${name}.png`) });
      await page.evaluate(() => window.__afterlightProbe.engine().getPlayerLoader?.()?.getPlayerBody?.()?.setEnabled(true));
    }
    console.log(`${name}: ${logs.find((l) => l.includes('LODs:')) ?? ''}`);
  } finally { await browser.close(); }
}
console.log(`shots in ${path.relative(process.cwd(), OUT)}`);
