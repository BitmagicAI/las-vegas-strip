#!/usr/bin/env node
/**
 * Record film TAKES with the engine's own frame recorder: 1920x1080 at an exact 60 fps (the recorder pins the game to a 1/60 s step,
 * so the footage is smooth however slowly the machine captures). Nobody plays: this opens the `bitmagic dev` shell (it hosts the game
 * iframe in creator mode and announces the recorder's sink), boots the game with the film director on (localStorage
 * 'afterlight:film'), the highest graphics settings and the filming settings below, then for each take: places and warms the
 * scene (src/work/film/Film.ts load), starts the recorder, runs the take on the game clock, stops, waits for the frames and
 * renames the recording directory to the take's name. Several takes share one boot.
 *
 *   node tools/film/record.mjs <take> [<take> ...] [--test <seconds>] [--headed]
 *
 * Takes: tools/film/takes/<take>.json. Output: .bitmagic/trailer/recordings/<take>/ (PNG frames + timeline.json + poses.json +
 * marks.json); a log per run in tools/film/log/. Graphics: quality pinned to ultra, foliage distance 200 %, shadow distance 192 m.
 * Env: GAME_PORT (from .bitmagic/dev.json), EDITOR_PORT (same), REC_RESOLUTION (1920x1080), REC_BUDGET_S (7200),
 * REC_SUBFRAMES (overrides the takes' sub-frames, e.g. 1 for previews), REC_SUFFIX (recording name suffix, e.g. -preview),
 * REC_RAW=1 (raw RGBA frames instead of the worker's H.264: lossless PNGs). DO NOT use it for a long take: on 2026-10-08/09
 * the raw path starved the game page's main thread, streaming jobs stopped finishing and the tour froze at 88.7 s every
 * time (1920 and 2880), while the sidecar kept writing copies of the last frame; at 2880 it also exhausted the Mac's
 * memory. Finals: REC_RESOLUTION=2880x1620 with the worker's H.264 (~140 Mbps), Lanczos-scaled to 1080p by build.py.
 * Run tools/film/memwatch.sh beside a long recording.
 * One browser, always closed (a watchdog closes it too); nothing else may use the GPU meanwhile; do not edit src/ while it runs.
 */
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

import { cliRequire } from '../lib/bitmagic-cli.mjs';
const { chromium } = cliRequire('playwright-core');
const ROOT = new URL('../..', import.meta.url).pathname;
const argv = process.argv.slice(2);
const flag = (n) => argv.includes(`--${n}`);
const opt = (n) => { const i = argv.indexOf(`--${n}`); return i >= 0 ? argv[i + 1] : undefined; };
const TAKES = argv.filter((a, i) => !a.startsWith('--') && argv[i - 1] !== '--test');
if (!TAKES.length) { console.error('usage: node tools/film/record.mjs <take> [<take> ...] [--test <s>] [--headed]'); process.exit(2); }
const dev = JSON.parse(fs.readFileSync(path.join(ROOT, '.bitmagic/dev.json'), 'utf8'));
const GAME_PORT = process.env.GAME_PORT || String(dev.gamePort);
const EDITOR_PORT = process.env.EDITOR_PORT || String(dev.editorPort);
const RES = process.env.REC_RESOLUTION || '1920x1080';
const [RW, RH] = RES.split('x').map(Number);
// The window is the recording size / 1.5 at a device pixel ratio of 1.5; a size that does not divide exactly (1280x720:
// 853.33 px) leaves one texture a pixel short of the recording, every copy into it fails WebGPU validation, and the frames
// come out black. Use multiples of 3 (960x540, 1920x1080, 2880x1620).
if (RW % 3 || RH % 3) { console.error(`REC_RESOLUTION ${RES}: width and height must be multiples of 3 (black frames otherwise)`); process.exit(2); }
const WIN_W = RW / 1.5, WIN_H = RH / 1.5;
const TEST_S = opt('test') ? Number(opt('test')) : null;
const BUDGET_MS = Number(process.env.REC_BUDGET_S || 7200) * 1000;
const RECS = path.join(ROOT, '.bitmagic/trailer/recordings');
const TAKE_DIR = path.join(ROOT, 'tools/film/takes');
const LOG = path.join(ROOT, 'tools/film/log');
fs.mkdirSync(LOG, { recursive: true });
// REC_SUBFRAMES overrides every take's sub-frames (1 for quick previews); REC_SUFFIX names the recordings <take><suffix>
const takes = TAKES.map((t) => ({ id: t, ...JSON.parse(fs.readFileSync(path.join(TAKE_DIR, `${t}.json`), 'utf8')),
    ...(process.env.REC_SUBFRAMES ? { subframes: Number(process.env.REC_SUBFRAMES) } : {}) }));
const SUFFIX = process.env.REC_SUFFIX || '';
// REC_RAW=1: the engine's recording worker sends raw RGBA (written straight to PNG by the dev server) instead of its
// WebCodecs H.264 at ~0.5 bit a pixel, which smeared fine detail before the final encode. The worker picks raw when it
// has no VideoEncoder, so blob workers are started behind a shim that removes it.
const RAW = process.env.REC_RAW === '1';
const SETTINGS = {
    'afterlight:film': '1',
    'bm.quality': 'ultra',
    'afterlight:foliage:v1': JSON.stringify({ enabled: true, distanceScale: 2 }),
    'afterlight:shadows:v1': JSON.stringify({ distance: 192 }),
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const T0 = Date.now();
const log = (m) => console.log(`[film ${((Date.now() - T0) / 1000).toFixed(0)}s] ${m}`);
const dirs = () => (fs.existsSync(RECS) ? fs.readdirSync(RECS).filter((d) => fs.statSync(path.join(RECS, d)).isDirectory()) : []);
const pngs = (d) => { try { return fs.readdirSync(d).filter((f) => f.endsWith('.png')).length; } catch { return 0; } };

const HOLD = path.join(ROOT, '.bitmagic/hold-reload');
const madeHold = !fs.existsSync(HOLD);
if (madeHold) fs.writeFileSync(HOLD, `film record ${new Date().toISOString()}\n`);

const browser = await chromium.launch({
    channel: 'chrome', headless: !flag('headed'),
    args: ['--use-angle=metal', '--enable-unsafe-webgpu', '--autoplay-policy=no-user-gesture-required', '--mute-audio', '--window-size=2200,1166'],
});
const watchdog = setTimeout(() => { log(`WATCHDOG: over ${BUDGET_MS / 1000} s, closing the browser`); browser.close().catch(() => {}); }, BUDGET_MS);
watchdog.unref();
const results = [];
let exitCode = 0, page = null, game = null, gpuErrors = 0;
const blends = [];
try {
    const context = await browser.newContext({ viewport: { width: WIN_W + 280, height: WIN_H + 86 }, deviceScaleFactor: 1.5 });
    page = await context.newPage();
    page.on('pageerror', (e) => log(`PAGEERROR ${e.message}`));
    page.on('console', (m) => {
        const t = m.text();
        if (m.type() === 'error' && !/service ?worker|sw-cache-buster/i.test(t)) {
            if (/GPUValidationError/.test(t)) gpuErrors++;
            if (!/GPUValidationError/.test(t) || gpuErrors <= 3) log(`console.error ${t.slice(0, 600)}`);
        }
        else if (/📹|\[film\]|GamepadControls|Recording/i.test(t)) log(`console ${t.slice(0, 200)}`);
    });
    if (RAW) await context.addInitScript(() => {
        const RealWorker = window.Worker;
        const Shimmed = function (url, opts) {
            const u = String(url);
            if (u.startsWith('blob:') && opts?.type !== 'module') {
                const shim = new Blob([`self.VideoEncoder = undefined; self.VideoFrame = undefined; importScripts(${JSON.stringify(u)});`], { type: 'text/javascript' });
                return new RealWorker(URL.createObjectURL(shim), opts);
            }
            return new RealWorker(url, opts);
        };
        Shimmed.prototype = RealWorker.prototype;
        window.Worker = Shimmed;
    });
    await context.addInitScript((settings) => {
        try { for (const [k, v] of Object.entries(settings)) localStorage.setItem(k, v); } catch { /* storage */ }
        Object.defineProperty(Element.prototype, 'requestPointerLock', { configurable: true, writable: true, value: () => Promise.resolve() });
        // vite's HMR socket: drop reload / update messages (a save elsewhere must not reload the page mid-take)
        const Real = window.WebSocket;
        window.WebSocket = new Proxy(Real, { construct(T, args) {
            const ws = new T(...args);
            if (String(args[1] ?? '') !== 'vite-hmr') return ws;
            const add = ws.addEventListener.bind(ws);
            ws.addEventListener = (type, fn, opts) => (type !== 'message' ? add(type, fn, opts) : add(type, (e) => {
                try { const d = JSON.parse(e.data); if (d.type === 'full-reload' || d.type === 'update') { window.__heldReloads = (window.__heldReloads ?? 0) + 1; return; } } catch { /* not JSON */ }
                fn(e);
            }, opts));
            return ws;
        } });
    }, SETTINGS);

    const SHELL_URL = `http://localhost:${EDITOR_PORT}/?rec=${encodeURIComponent(RES)}`;
    log(`opening ${SHELL_URL}`);
    await page.goto(SHELL_URL, { waitUntil: 'domcontentloaded', timeout: 30_000 });
    const findGame = () => page.frames().find((f) => f.url().includes(`localhost:${GAME_PORT}`)) ?? null;
    for (let i = 0; i < 150 && !findGame(); i++) await sleep(200);
    game = findGame();
    if (!game) throw new Error('the game iframe never appeared in the dev shell');
    log(`game iframe ${game.url()}`);
    // start screen: pick the option / press Play until the game has started (the engine logs '🎮 Starting game...')
    let started = false;
    page.on('console', (m) => { if (m.text().includes('🎮 Starting game...')) started = true; });
    for (let i = 0; i < 300; i++) {
        if (started && await game.evaluate(() => !!window.__afterlightFilm).catch(() => false)) break;
        if (takes.some(t=>t.scenario) && await game.evaluate(()=>!!window.__afterlightFilm).catch(()=>false)) { await game.evaluate(()=>window.__afterlightProbe.engine().startGame()); await sleep(20000); await game.evaluate(()=>window.__afterlightProbe.engine().startGame()); await sleep(3000); started=true; break; }
        const choice = game.locator('.start-screen-selection__option').first(), play = game.locator('#play-button, .hud-play-button').first();
        if (await choice.isVisible().catch(() => false)) await choice.click().catch(() => {});
        else if (await play.isVisible().catch(() => false)) await play.click().catch(() => {});
        await sleep(1000);
    }
    if (!started || !(await game.evaluate(() => !!window.__afterlightFilm).catch(() => false))) throw new Error('the game or the film director never started');
    // first streaming at the spawn point
    for (let i = 0; i < 240 && await game.evaluate(() => window.__afterlightProbe.streaming().busy).catch(() => true); i++) await sleep(500);
    log(`film ready; window ${(await game.evaluate(() => [innerWidth, innerHeight, devicePixelRatio])).join(' x ')}`);
    await sleep(8000);

    for (const take of takes) {
        const r = { take: take.id, resolution: RES };
        results.push(r);
        log(`── ${take.id}: loading`);
        r.loaded = await game.evaluate((t) => window.__afterlightFilm.load(t), take);
        log(`loaded ${JSON.stringify(r.loaded)}`);
        if(take.scenario)await game.evaluate(seconds=>{
            const e=window.__afterlightProbe.engine(),rec=e.screenRecorder,film=window.__afterlightFilm;
            const capture=rec.captureFrameWithoutHUD.bind(rec);let last=0;
            rec.captureFrameWithoutHUD=function(){const tick=film.frame;if(tick<=last||tick>Math.round(seconds*60))return;last=tick;capture();};
            window.__restoreFilmCapture=()=>{rec.captureFrameWithoutHUD=capture;};
        },take.seconds);
        const before = new Set(dirs());
        await game.evaluate(({ editor, res, recs }) => {
            window.postMessage({ type: 'RECORDING_SETTINGS_CHANGED', settings: {
                resolution: res, mode: 'frames', sinkUrl: editor, host: 'cli', recordingsDir: recs, rawFrames: true,
                streamUrl: editor.replace(/^http/, 'ws') + '/api/dev/record-stream',
            } }, '*');
        }, { editor: `http://localhost:${EDITOR_PORT}`, res: RES, recs: RECS });
        await sleep(300);
        await game.evaluate(() => { window.__afterlightFilm.arm(); window.postMessage({ type: 'TRAILER_RECORDING', action: 'start', mode: 'frames' }, '*'); });
        let dir = null;
        for (let i = 0; i < 150 && !dir; i++) { await sleep(200); dir = dirs().find((d) => !before.has(d)) ?? null; }
        if (!dir) throw new Error('no recording directory appeared');
        r.recording = path.join(RECS, dir);
        log(`recording into ${r.recording}`);
        let s = null, lastLog = 0;
        const state = () => game.evaluate(() => window.__afterlightFilm.state()).catch(() => null);
        s = await state();
        while (s && !s.done && !(TEST_S !== null && s.t >= TEST_S) && Date.now() - T0 < BUDGET_MS - 300_000) {
            await sleep(1000); s = await state();
            if (!s) throw new Error('the game page reloaded mid-take');
            if (Date.now() - lastLog > 15_000) { lastLog = Date.now(); log(`${take.id} t ${s.t.toFixed(1)} s (frame ${s.frame}, dt ${(s.dt * 1000).toFixed(2)} ms, ${s.subframes} sub-frames), step ${s.step}/${s.steps}, frames on disk ${pngs(r.recording)}`); }
        }
        r.state = s;
        await game.evaluate(() => window.postMessage({ type: 'TRAILER_RECORDING', action: 'stop' }, '*'));
        log(`stop (take clock ${s?.t?.toFixed(1)} s, ${s?.frame} frames, warnings ${JSON.stringify(s?.warnings ?? [])})`);
        const extras = await game.evaluate(() => ({ poses: window.__afterlightFilm.poses(), marks: window.__afterlightFilm.marks(), track: window.__afterlightFilm.track(), scene: window.__afterlightScene?.state(), vehicleTrack: window.__afterlightScene?.telemetry() })).catch(() => null);
        const snap = await game.evaluate(() => {
            const eng = window.gameTemplate?.getGameEngine(), rec = eng?.screenRecorder, tl = rec?.pendingTimeline;
            if (!tl) return null;
            return { version: 1, recording: { name: rec.recordingName, width: rec.recordingWidth, height: rec.recordingHeight, fps: 60, frameCount: rec.frameCount,
                missingFrames: Array.from(rec.failedFrameIndices ?? []), frameClock: rec.frameClock, renderer: 'webgpu', ...(rec.recordedWindow ? { window: rec.recordedWindow } : {}) },
                events: tl.events, sounds: tl.sounds, music: tl.music, hud: tl.hud };
        }).catch(() => null);
        // frames stream to disk after the stop: wait until the timeline arrives (or nothing moves for 4 min). Progress is the
        // capture video still growing, the dev server's hidden .extract folder filling, or finished PNGs: a long sub-frame
        // take spends minutes in the first two (the coaster's 43k frames timed out on PNGs alone and were renamed mid-extract).
        const timeline = path.join(r.recording, 'timeline.json');
        const progress = () => { let v = 0; try { v = fs.statSync(path.join(r.recording, 'capture.mp4')).size; } catch { /* none yet */ }
            return `${v}/${pngs(r.recording)}/${pngs(path.join(r.recording, '.extract'))}`; };
        let last = '', idleSince = Date.now();
        while (!fs.existsSync(timeline) && Date.now() - idleSince < 240_000) {
            await sleep(3000);
            const n = progress();
            if (n !== last) { last = n; idleSince = Date.now(); }
        }
        if (!fs.existsSync(timeline) && snap) { fs.writeFileSync(timeline, JSON.stringify(snap)); r.timelineFromSnapshot = true; }
        if(extras?.vehicleTrack) fs.writeFileSync(path.join(r.recording,'vehicle-track.json'),JSON.stringify(extras.vehicleTrack));
        if(extras?.scene) fs.writeFileSync(path.join(r.recording,'scene.json'),JSON.stringify(extras.scene));
        if (extras) { fs.writeFileSync(path.join(r.recording, 'poses.json'), JSON.stringify(extras.poses)); fs.writeFileSync(path.join(r.recording, 'marks.json'), JSON.stringify(extras.marks)); if (extras.track?.length) fs.writeFileSync(path.join(r.recording, 'track.json'), JSON.stringify(extras.track)); }
        await game.evaluate(()=>{window.__restoreFilmCapture?.();delete window.__restoreFilmCapture;});
        r.frames = pngs(r.recording);
        // name the directory after the take (keep an older one aside)
        const named = path.join(RECS, `${take.id}${TEST_S ? '-test' : ''}${SUFFIX}`);
        if (fs.existsSync(named)) fs.renameSync(named, `${named}-old-${Date.now()}`);
        fs.renameSync(r.recording, named); r.recording = named;
        const sub = take.subframes ?? 1;
        if (gpuErrors) { log(`WARNING ${take.id}: ${gpuErrors} WebGPU validation errors so far (frames may be black)`); r.gpuErrors = gpuErrors; }
        log(`${take.id} done: ${r.frames} frames (${(r.frames / 60 / sub).toFixed(1)} s${sub > 1 ? `, ${sub} sub-frames a frame` : ''}) in ${named}`);
        // motion blur: blend the sub-frames to 60 fps in the background while the next take records
        // a take with `blend: false` keeps its sub-frames as real frames (60 x sub a second) for speed changes in the cut
        if (sub > 1 && take.blend === false) fs.writeFileSync(path.join(named, 'subframes.json'), JSON.stringify({ subframes: sub, fps: 60 * sub, blended: false, frames: r.frames }));
        else if (sub > 1) blends.push(new Promise((resolve) => {
            const child = spawn('python3', [path.join(ROOT, 'tools/film/blend-subframes.py'), path.basename(named), '--n', String(sub)], { stdio: ['ignore', 'pipe', 'pipe'] });
            let out = ''; child.stdout.on('data', (b) => { out += b; }); child.stderr.on('data', (b) => { out += b; });
            child.on('close', (code) => { log(`blend ${take.id}: ${code === 0 ? out.trim() : `FAILED (${code}) ${out.trim()}`}`); if (code !== 0) exitCode = 1; resolve(); });
        }));
        await sleep(2000);
    }
} catch (e) {
    exitCode = 1;
    log(`FAILED: ${e?.stack || e}`);
    if (page) await page.screenshot({ path: path.join(LOG, `failure-${Date.now()}.png`) }).catch(() => {});
} finally {
    if (madeHold) { try { fs.unlinkSync(HOLD); } catch { /* gone */ } }
    await Promise.race([browser.close().catch(() => {}),sleep(10000)]);
    if (blends.length) { log(`waiting for ${blends.length} blend(s)`); await Promise.all(blends); }
    fs.writeFileSync(path.join(LOG, `run-${new Date().toISOString().replace(/[:.]/g, '-')}.json`), JSON.stringify(results, null, 2));
}
process.exit(exitCode);
