// Uploads the runtime set to the Bitmagic CDN, where forged assets live, so a published game (one file in object
// storage, no same-origin siblings) can stream the city (2026-10-24: the owner
// asked to host these files on the CDN, as the asset forger does).
//
//   node tools/release/cdn-upload.mjs            # upload what is new or changed, then write src/work/runtime-cdn.json
//   node tools/release/cdn-upload.mjs --dry-run  # list what would go up
//   node tools/release/cdn-upload.mjs --limit 5  # only the first few (a test)
//
// The bytes are runtime-assets/ (the optimized copies, exactly what a clone runs) plus public/foliage/ (the garden's
// optimized copies, tools/optimize/foliage-trees.mjs). Each file goes
// up through the CLI's own signed-upload lane (`bitmagic assets add` uses it) under worlds/v3/<this game's id>/, named
// <sha256 prefix>-<file name>: uploads are immutable and cannot be deleted, so a changed file gets a new name and an
// unchanged one is never sent twice. The map is saved after every file, so a dropped connection resumes. JSON and the
// packed .bin data (tools/optimize/pack-data.mjs) are stored compressed (the server binds gzip or brotli). src/work/RuntimeAssets.ts reads the map.
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { cliRoot } from '../lib/bitmagic-cli.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const MAP = path.join(ROOT, 'src/work/runtime-cdn.json');
const dry = process.argv.includes('--dry-run');
const li = process.argv.indexOf('--limit'), limit = li > 0 ? Number(process.argv[li + 1]) : Infinity;
const TYPES = { glb: 'model/gltf-binary', json: 'application/json', bin: 'application/octet-stream', webp: 'image/webp', jpg: 'image/jpeg', png: 'image/png', mp4: 'video/mp4' };
const PUBLIC = ['foliage/tree-0.glb', 'foliage/tree-1.glb', 'foliage/tree-2.glb', 'foliage/grass-0.glb', 'foliage/grass-1.glb', 'foliage/bellagio-placements.bin'];

// (the CLI's own modules: its login, its environment and its signed-upload lane)
const cli = (file) => import(pathToFileURL(path.join(cliRoot, 'dist', file)).href);
const { selectEnvironmentForCommand, resolveAuth0ClientId } = await cli('config/environments.js');
const { getAccessToken } = await cli('auth/session.js');
const { uploadProjectFile } = await cli('http/signed-upload.js');

const gameId = JSON.parse(fs.readFileSync(path.join(ROOT, 'bitmagic.json'), 'utf8')).gameId;
const list = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/release/asset-pack.json'), 'utf8'));
const map = fs.existsSync(MAP) ? JSON.parse(fs.readFileSync(MAP, 'utf8')) : { files: {} };
map.about = 'Where a published game loads each runtime file: the Bitmagic CDN copy of runtime-assets/ (as build/<path>) '
  + 'and public/. Written by tools/release/cdn-upload.mjs; read by src/work/RuntimeAssets.ts.';
map.gameId = gameId;

const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
// (path as the game requests it, without the leading slash) -> file on disk
const wanted = [...list.files.map((f) => [f.path, path.join(ROOT, 'runtime-assets', f.path.slice('build/'.length))]),
  ...PUBLIC.map((p) => [p, path.join(ROOT, 'public', p)])];

const save = () => fs.writeFileSync(MAP, JSON.stringify({ about: map.about, gameId: map.gameId, files: Object.fromEntries(Object.entries(map.files).sort()) }, null, 1) + '\n');
// files the game no longer loads leave the map (each published game keeps the map it was built with)
const keys = new Set(wanted.map(([key]) => key));
const stale = Object.keys(map.files).filter((key) => !keys.has(key));
for (const key of stale) delete map.files[key];
if (stale.length) console.log(`${stale.length} files the game no longer loads left the map`);
const todo = [];
for (const [key, file] of wanted) {
  const bytes = fs.readFileSync(file);
  const digest = sha(bytes);
  if (map.files[key]?.sha256 === digest) continue;
  todo.push({ key, file, digest, size: bytes.length });
}
if (todo.length > limit) todo.length = limit;
const total = todo.reduce((s, t) => s + t.size, 0);
console.log(`${wanted.length} runtime files; ${todo.length} to upload (${(total / 1048576).toFixed(1)} MiB) to worlds/v3/${gameId}/`);
if (dry) { for (const t of todo.slice(0, 20)) console.log('  ' + t.key); process.exit(0); }
if (!todo.length) { save(); console.log(`nothing to upload; map: ${path.relative(ROOT, MAP)} (${Object.keys(map.files).length} files)`); process.exit(0); }

const environment = selectEnvironmentForCommand({ explicit: undefined, cwd: ROOT }).environment;
const deps = { fetch: globalThis.fetch };
let token = await getAccessToken(environment, resolveAuth0ClientId(environment), { ...deps, sleep: (ms) => new Promise((r) => setTimeout(r, ms)) });

let done = 0, sent = 0, failed = 0;
const t0 = Date.now();
async function upload(t) {
  const ext = path.extname(t.key).slice(1).toLowerCase();
  const contentType = TYPES[ext];
  if (!contentType) throw new Error(`no content type for ${t.key}`);
  const filename = `${t.digest.slice(0, 12)}-${path.basename(t.key)}`;
  for (let attempt = 1; ; attempt++) {
    try {
      const bytes = new Uint8Array(fs.readFileSync(t.file));
      const r = await uploadProjectFile(environment, token, { gameId, filename, contentType, bytes }, deps);
      map.files[t.key] = { url: r.url, sha256: t.digest, bytes: t.size };
      sent += t.size; done++;
      return;
    } catch (e) {
      if (attempt >= 4) { failed++; console.error(`FAILED ${t.key}: ${e.message}`); return; }
      if (/401|expired|token/i.test(e.message)) token = await getAccessToken(environment, resolveAuth0ClientId(environment), { ...deps, sleep: (ms) => new Promise((r) => setTimeout(r, ms)) });
      await new Promise((r) => setTimeout(r, 3000 * attempt));
    }
  }
}
// Four at a time; the map is written as each finishes.
let next = 0;
await Promise.all(Array.from({ length: 4 }, async () => {
  while (next < todo.length) {
    const t = todo[next++];
    await upload(t);
    save();
    if ((done + failed) % 25 === 0) console.log(`${done + failed}/${todo.length} (${(sent / 1048576).toFixed(0)} MiB, ${(sent / 1048576 / ((Date.now() - t0) / 1000)).toFixed(1)} MiB/s)`);
  }
}));
save();
console.log(`uploaded ${done}, failed ${failed}; map: ${path.relative(ROOT, MAP)} (${Object.keys(map.files).length} files)`);
process.exit(failed ? 1 : 0);
