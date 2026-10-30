#!/usr/bin/env node
/*
 * optimize-runtime-glbs.mjs: reproducible driver for the optimizing-assets skill on the GLBs that
 * the Las Vegas Strip loads at runtime. It never touches a source file, world.json or src/: every
 * candidate goes to .bitmagic/optimize/<path relative to the project, minus .glb>/out.glb, next to
 * source.sha256 and the encoder's --json report (report.json). Nothing is swapped into the game.
 *
 *   node tools/optimize/optimize-runtime-glbs.mjs --list          resolve the runtime list -> tools/optimize/runtime-glbs.json
 *   node tools/optimize/optimize-runtime-glbs.mjs                 encode everything that is not up to date (by source sha256)
 *   node tools/optimize/optimize-runtime-glbs.mjs --only=hotels/  only entries whose path contains the text
 *   node tools/optimize/optimize-runtime-glbs.mjs --force         re-encode even when up to date
 *   node tools/optimize/optimize-runtime-glbs.mjs --analyze       vertex layouts, glossy meshes, merge-type checks -> tools/optimize/analysis.json
 *   node tools/optimize/optimize-runtime-glbs.mjs --summary       tables -> tools/optimize/REPORT.md (generated block) + summary.json
 *   node tools/optimize/optimize-runtime-glbs.mjs --variant=webp-textures   EXPERIMENT: level files with colour maps as WebP q90 -> out-webp-textures.glb
 *   node tools/optimize/optimize-runtime-glbs.mjs --psnr          PSNR of the WebP colour maps against the originals -> report-webp-textures.json
 * Characters: the encoder cannot read them (required BITMAGIC_sparse_correctives); the driver then runs
 * tools/optimize/character-textures-webp.mjs for a texture-only candidate (out-textures-only.glb).
 *
 * Run it from the project root. One encoder process at a time (the city files are ~350 MB each).
 * Tools: BM_TOOLS (default tools/optimize/bm-tools; install them with `sh tools/optimize/setup-tools.sh`).
 * Encoder: the project's .agents/skills copy when it exists, otherwise the one the installed
 * @bitmagic/cli ships (CLI 0.1.81+). No KTX2 anywhere: there is no `ktx` binary on this machine
 * and the vendored engine lacks the KTX2 boot-race wait.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const ROOT = process.cwd();
if (!fs.existsSync(path.join(ROOT, 'src/work/world.json'))) { console.error('run from the project root (src/work/world.json not found)'); process.exit(2); }
const argv = process.argv.slice(2);
const flag = (n) => { const a = argv.find((x) => x === `--${n}` || x.startsWith(`--${n}=`)); return a === undefined ? undefined : a.includes('=') ? a.slice(a.indexOf('=') + 1) : true; };
const OUT_ROOT = path.join(ROOT, '.bitmagic/optimize');
const BM_TOOLS = process.env.BM_TOOLS ?? path.join(ROOT, 'tools/optimize/bm-tools');
const SCRIPT = [
  path.join(ROOT, '.agents/skills/optimizing-assets/scripts/optimize-glb.mjs'),
  path.join(path.dirname(process.execPath), '../lib/node_modules/@bitmagic/cli/assets/optimizing-assets/scripts/optimize-glb.mjs'),
].find((p) => fs.existsSync(p));
const HEAP_MB = Number(process.env.OPT_HEAP_MB) || 16384;

// ------------------------------------------------------------------------------------ presets
// One preset per asset class (SKILL.md section 2), with the overrides this game needs.
const NO_KTX_CHARACTER = ['--base=webp:1024:90', '--emissive=webp:1024:90', '--orm=webp-lossless:512'];
const CLASSES = {
  level: { preset: 'level', overrides: [], why: 'architecture / walkable level: float32 positions, triangle order kept, textures untouched' },
  'code-driven': { preset: 'code-driven', overrides: [], why: 'vehicle: code reads node names/parts; float positions, base maps kept, never KTX2' },
  character: { preset: 'character', overrides: NO_KTX_CHARACTER, why: 'skinned character: float positions, exact normals, every key; WebP instead of UASTC (no ktx)' },
};

// ------------------------------------------------------------------------------------ resolve
const exists = (rel) => fs.existsSync(path.join(ROOT, rel));
const readJson = (rel) => JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));
function resolveList() {
  const list = [];
  const add = (rel, cls, loader, when, extra = {}) => { if (!exists(rel)) { list.push({ rel, cls, loader, when, missing: true }); return; } list.push({ rel, cls, loader, when, ...extra }); };
  // GeographicCity
  add('build/geographic-strip/city.glb', 'level', 'src/work/GeographicCity.ts', 'boot');
  // Opt-in while the cell migration is being verified; retain the existing runtime set.
  if (flag('city-cells')) {
    for (const cell of readJson('build/geographic-strip/cells/manifest.json').cells)
      add(`build/geographic-strip/cells/${cell.file}`, 'level', 'src/work/GeographicCity.ts (cell migration)', 'boot');
  }
  // MeshLevel (Game.ts)
  add('build/geographic-strip/detailed.glb', 'level', 'src/work/Game.ts -> engine MeshLevel', 'boot');
  // StripLandmarks: base + key + -exterior.glb (boot) / -interior.glb (streamed on approach)
  for (const base of ['build/strip-landmarks/', 'build/resort-blocks/cosmo/', 'build/resort-blocks/bellagio/', 'build/resort-blocks/paris/']) {
    const loader = base.includes('resort-blocks') ? 'src/work/ResortBlocks.ts -> StripLandmarks' : 'src/work/StripLandmarks.ts';
    for (const m of readJson(base + 'venues.json')) {
      add(`${base}${m.key}-exterior.glb`, 'level', loader, 'boot');
      if(!m.exteriorOnly)add(`${base}${m.key}-interior.glb`, 'level', loader, 'streamed on approach');
    }
  }
  add('build/highrises/exteriors.glb', 'level', 'src/work/HighriseCity.ts', 'boot');
  add('build/south-strip/coaster.glb', 'level', 'src/work/BigAppleCoaster.ts', 'boot');
  add('build/south-strip/train.glb', 'code-driven', 'src/work/BigAppleCoaster.ts', 'boot');
  add('build/sphere/exterior.glb', 'level', 'src/work/SphereVenue.ts', 'boot');
  add('build/sphere/interior.glb', 'level', 'src/work/SphereVenue.ts', 'streamed on approach');
  add('build/vehicles/afterlight-jeep.glb', 'code-driven', 'src/work/SanctuaryJeep.ts', 'boot');
  // HotelTemplates: /build/hotels/<HotelSet>-<part>.glb and <anything>-lobby.glb
  const layout = fs.readFileSync(path.join(ROOT, 'src/work/hotels/HotelLayout.ts'), 'utf8');
  const sets = [...(/export type HotelSet\s*=\s*([^;]+);/.exec(layout)?.[1] ?? '').matchAll(/'([^']+)'/g)].map((m) => m[1]);
  const parts = ['stair', 'corridor', 'room', 'cap', 'entry', 'closure', 'door', 'corridor-end'];
  const hotelFiles = fs.readdirSync(path.join(ROOT, 'build/hotels')).filter((f) => f.endsWith('.glb')).sort();
  for (const f of hotelFiles) {
    const name = f.slice(0, -4);
    const module = name.endsWith('-lobby') ? sets.some((s) => name.startsWith(s + '-')) : sets.some((s) => parts.some((p) => name === `${s}-${p}`));
    if (!module) continue;   // e.g. staged-vegas.glb: not a module name HotelTemplates can request
    add(`build/hotels/${f}`, 'level', 'src/work/hotels/HotelTemplates.ts', name.endsWith('-lobby') || ['room', 'corridor', 'door', 'corridor-end'].some((p) => name.endsWith('-' + p)) ? 'streamed (hotel visit)' : 'streamed (hotel shell)');
  }
  // (ResortFoliage's /foliage/<file>.glb are not listed: public/foliage/ holds their optimized copies, which
  // tools/optimize/foliage-trees.mjs makes from tools/foliage/models/)
  // Characters (a game built on the city, e.g. vegas-afterlight-game: VegasCast loads world.json row character-b610N by its
  // remote url; the local src/work/characters/b610N/character.glb is that row's source). The city itself has none.
  const world = readJson('src/work/world.json');
  const index = fs.existsSync(path.join(ROOT, 'src/work/characters/index.json')) ? readJson('src/work/characters/index.json') : [];
  for (const c of index) {
    const rel = `src/work/characters/${c.directory}/character.glb`;
    const row = world.assets.find((a) => a.id === `character-${c.id}`);
    add(rel, 'character', 'src/work/characters/VegasCast.ts -> VegasCharacter (world.json row url)', 'boot', { worldRow: row?.id, remoteUrl: row?.url, indexSha256: c.sha256 });
  }
  // world.json rows with local /build URLs (engine-spawned door leaves: DungeonDoor fits them by bounds)
  const remote = [];
  for (const a of world.assets) {
    const url = String(a.url ?? '');
    if (!/\.glb(\?|$)/i.test(url)) continue;
    if (url.startsWith('/build/')) add(url.split('?')[0].slice(1), 'level', `world.json asset ${a.id} (engine DungeonDoor via worldProfileData.doors)`, 'boot', { worldRow: a.id });
    else remote.push({ id: a.id, name: a.name, url, size: a.size ?? null, localSource: a.id.startsWith('character-') ? `src/work/characters/${a.id.slice(10)}/character.glb` : null });
  }
  return { list, remote };
}

function sha256(file) {
  const h = crypto.createHash('sha256'), fd = fs.openSync(file, 'r'), buf = Buffer.alloc(16 << 20);
  for (let n; (n = fs.readSync(fd, buf, 0, buf.length, null)) > 0;) h.update(buf.subarray(0, n));
  fs.closeSync(fd);
  return h.digest('hex');
}
const mib = (n) => `${(n / 1048576).toFixed(2)} MiB`;
const outDir = (rel) => path.join(OUT_ROOT, rel.replace(/\.glb$/i, ''));

// ------------------------------------------------------------------------------------ run one
function encode(entry, dst, overrides, label) {
  const cls = CLASSES[entry.cls];
  const args = [`--max-old-space-size=${HEAP_MB}`, SCRIPT, entry.rel, path.relative(ROOT, dst), `--preset=${cls.preset}`, ...cls.overrides, ...overrides, '--json'];
  const t0 = Date.now();
  const r = spawnSync(process.execPath, args, { cwd: ROOT, env: { ...process.env, BM_TOOLS }, encoding: 'utf8', maxBuffer: 1 << 30 });
  let report = null;
  try { report = JSON.parse(r.stdout); } catch { /* crashed before the report */ }
  const failed = (report?.checks ?? []).filter((c) => c.fail).map((c) => `${c.name}: ${c.detail}`);
  return {
    label, preset: cls.preset, overrides: [...cls.overrides, ...overrides], exitCode: r.status, signal: r.signal, seconds: (Date.now() - t0) / 1000,
    command: `BM_TOOLS=${path.relative(ROOT, BM_TOOLS)} node --max-old-space-size=${HEAP_MB} <optimize-glb.mjs> ${args.slice(2).join(' ')}`,
    failed, stderr: (r.stderr ?? '').split('\n').filter(Boolean).slice(-12), report,
  };
}
/** The documented fallback for a failed run: texture keep for a texture failure, otherwise quantization only. */
function fallbackFor(run) {
  const text = run.failed.join(' ') + ' ' + run.stderr.join(' ');
  if (/^smaller:/m.test(run.failed.join('\n')) && run.failed.length === 1) return null;   // nothing to fall back to: the original ships
  if (/texture slots|paired sizes|texture|ktx|webp|jpeg|sharp/i.test(text)) return ['--base=keep', '--emissive=keep', '--normal=keep', '--orm=keep'];
  return ['--meshopt=off'];
}

function runOne(entry, done) {
  const file = path.join(ROOT, entry.rel), dir = outDir(entry.rel);
  const sha = sha256(file);
  const shaFile = path.join(dir, 'source.sha256'), reportFile = path.join(dir, 'report.json');
  if (!flag('force') && fs.existsSync(shaFile) && fs.readFileSync(shaFile, 'utf8').split(/\s/)[0] === sha && fs.existsSync(reportFile)) {
    return { rel: entry.rel, skipped: true };
  }
  fs.mkdirSync(dir, { recursive: true });
  for (const f of ['out.glb', 'out-fallback.glb', 'report-fallback.json', 'out-textures-only.glb', 'report-textures-only.json']) fs.rmSync(path.join(dir, f), { force: true });
  const key = `${sha}|${entry.cls}`;
  let result;
  if (done.has(key)) {   // byte-identical source already encoded with the same class: copy, do not re-encode
    const first = done.get(key);
    for (const f of ['out.glb', 'out-fallback.glb', 'report-fallback.json', 'out-textures-only.glb', 'report-textures-only.json']) if (fs.existsSync(path.join(outDir(first), f))) fs.copyFileSync(path.join(outDir(first), f), path.join(dir, f));
    result = { ...JSON.parse(fs.readFileSync(path.join(outDir(first), 'report.json'), 'utf8')), identicalTo: first };
  } else {
    const primary = encode(entry, path.join(dir, 'out.glb'), [], 'primary');
    result = { ...primary };
    if (primary.exitCode !== 0) {
      const fb = fallbackFor(primary);
      if (fb) {
        const second = encode(entry, path.join(dir, 'out-fallback.glb'), fb, 'fallback');
        fs.writeFileSync(path.join(dir, 'report-fallback.json'), JSON.stringify({ rel: entry.rel, sourceSha256: sha, ...second }, null, 1));
        result.fallback = { overrides: second.overrides, exitCode: second.exitCode, failed: second.failed, file: second.report ? 'out-fallback.glb' : null };
      } else result.fallback = { skipped: 'the only failure is "smaller": the original is what ships' };
      if (!primary.report) fs.rmSync(path.join(dir, 'out.glb'), { force: true });
    }
    // The characters REQUIRE BITMAGIC_sparse_correctives (per-vertex CSR rows addressed by bufferView
    // index), which the encoder cannot read and must not renumber. Their only safe candidate is a
    // texture-only rewrite that leaves every vertex byte alone: character-textures-webp.mjs.
    if (entry.cls === 'character' && primary.exitCode !== 0 && /Missing required extension/.test(primary.stderr.join(' '))) {
      const t0 = Date.now();
      const r = spawnSync(process.execPath, [path.join(ROOT, 'tools/optimize/character-textures-webp.mjs'), entry.rel, path.relative(ROOT, path.join(dir, 'out-textures-only.glb')), '--json'],
        { cwd: ROOT, env: { ...process.env, BM_TOOLS }, encoding: 'utf8', maxBuffer: 1 << 28 });
      let rep = null; try { rep = JSON.parse(r.stdout); } catch { /* crashed */ }
      fs.writeFileSync(path.join(dir, 'report-textures-only.json'), JSON.stringify({ rel: entry.rel, sourceSha256: sha, label: 'textures-only', exitCode: r.status, seconds: (Date.now() - t0) / 1000, stderr: (r.stderr ?? '').split('\n').filter(Boolean).slice(-8), report: rep }, null, 1));
      result.texturesOnly = { exitCode: r.status, file: rep ? 'out-textures-only.glb' : null, bytesBefore: rep?.bytesBefore, bytesAfter: rep?.bytesAfter, failed: (rep?.checks ?? []).filter((c) => c.fail).map((c) => `${c.name}: ${c.detail}`) };
    }
    done.set(key, entry.rel);
  }
  result = { rel: entry.rel, sourceSha256: sha, cls: entry.cls, loader: entry.loader, when: entry.when, ...result };
  fs.writeFileSync(reportFile, JSON.stringify(result, null, 1));
  fs.writeFileSync(shaFile, `${sha}  ${entry.rel}\n`);
  return result;
}

// ------------------------------------------------------------------------------------ analysis (GLB JSON only; works on meshopt files)
const CT = { 5120: 'int8', 5121: 'uint8', 5122: 'int16', 5123: 'uint16', 5125: 'uint32', 5126: 'float32' };
const SIZE = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 };
function glbJson(file) {
  const fd = fs.openSync(file, 'r'), head = Buffer.alloc(20);
  fs.readSync(fd, head, 0, 20, 0);
  if (head.readUInt32LE(0) !== 0x46546c67) { fs.closeSync(fd); throw new Error(`${file}: not a GLB`); }
  const len = head.readUInt32LE(12), buf = Buffer.alloc(len);
  fs.readSync(fd, buf, 0, len, 20); fs.closeSync(fd);
  return JSON.parse(buf.toString('utf8'));
}
const fmt = (a) => (a ? `${CT[a.componentType]}${a.normalized ? ' norm' : ''} x${SIZE[a.type]}` : 'absent');
function analyzeGlb(file) {
  const j = glbJson(file);
  const prims = (j.meshes ?? []).flatMap((m, mi) => m.primitives.map((p) => ({ ...p, mi })));
  const layout = {};
  for (const p of prims) for (const [sem, ai] of Object.entries(p.attributes)) {
    const k = `${sem}: ${fmt(j.accessors[ai])}`;
    layout[k] = (layout[k] ?? 0) + 1;
  }
  const mats = j.materials ?? [];
  const pbr = (m) => ({ metal: m?.pbrMetallicRoughness?.metallicFactor ?? 1, rough: m?.pbrMetallicRoughness?.roughnessFactor ?? 1, mrTex: !!m?.pbrMetallicRoughness?.metallicRoughnessTexture });
  const glossyMeshes = new Set(), glossyWithMap = new Set();
  for (const p of prims) {
    if (p.material === undefined) { glossyMeshes.add(p.mi); continue; }   // glTF default material: metalness 1
    const { metal, rough, mrTex } = pbr(mats[p.material]);
    if (metal > 0.5 || rough < 0.2) { glossyMeshes.add(p.mi); if (mrTex) glossyWithMap.add(p.mi); }
  }
  // The game's batch mergers need one array type per attribute: CityBatches.batchStaticMeshes keeps
  // position/normal/uv (a missing normal/uv becomes float32) and SanctuaryJeep.batchPart merges per
  // material + attribute-name set. Count the kinds a merge could meet.
  const kinds = (sem, absentAs) => new Set(prims.map((p) => (p.attributes[sem] === undefined ? absentAs : fmt(j.accessors[p.attributes[sem]]))));
  const byMaterial = new Map();
  for (const p of prims) {
    const key = `${p.material}|${Object.keys(p.attributes).sort().join(',')}`;
    const sig = Object.entries(p.attributes).map(([s, ai]) => `${s}=${fmt(j.accessors[ai])}`).sort().join(';');
    (byMaterial.get(key) ?? byMaterial.set(key, new Set()).get(key)).add(sig);
  }
  // CityBatches.batchStaticMeshes eligibility, as three will build the material: MeshStandardMaterial
  // only (no KHR_materials_* that make it physical/unlit), opaque, no alphaTest, and no normal, AO,
  // roughness/metalness or emissive map; a base map on UV channel 0 is allowed. Grouped by side.
  const PHYSICAL = /KHR_materials_(clearcoat|ior|specular|transmission|volume|sheen|iridescence|anisotropy|dispersion|unlit)/;
  const eligible = (m) => m && (m.alphaMode ?? 'OPAQUE') === 'OPAQUE' && !Object.keys(m.extensions ?? {}).some((e) => PHYSICAL.test(e))
    && !m.normalTexture && !m.occlusionTexture && !m.emissiveTexture && !m.pbrMetallicRoughness?.metallicRoughnessTexture
    && (m.pbrMetallicRoughness?.baseColorTexture?.texCoord ?? 0) === 0;
  const batchGroups = new Map();
  for (const p of prims) {
    const m = p.material === undefined ? {} : mats[p.material];
    if (!eligible(m) || (p.mode ?? 4) !== 4) continue;
    const side = m.doubleSided ? 'double' : 'front';
    const g = batchGroups.get(side) ?? batchGroups.set(side, { prims: 0, normal: {}, uv: {} }).get(side);
    g.prims++;
    const n = p.attributes.NORMAL === undefined ? 'absent -> float32 (computed)' : fmt(j.accessors[p.attributes.NORMAL]);
    const u = p.attributes.TEXCOORD_0 === undefined ? 'absent -> float32 (added)' : fmt(j.accessors[p.attributes.TEXCOORD_0]);
    g.normal[n] = (g.normal[n] ?? 0) + 1; g.uv[u] = (g.uv[u] ?? 0) + 1;
  }
  const arrayType = (k) => (k.startsWith('absent') ? 'float32' : k.split(' ')[0]);
  const mixed = (counts) => new Set(Object.keys(counts).map((k) => arrayType(k) + (k.includes('norm') ? 'n' : ''))).size > 1;
  const cityBatch = [...batchGroups.entries()].map(([side, g]) => ({ side, ...g, mixedNormal: mixed(g.normal), mixedUv: mixed(g.uv) }));
  const images = (j.images ?? []).map((im) => ({ mime: im.mimeType, bytes: im.bufferView !== undefined ? j.bufferViews[im.bufferView].byteLength : 0 }));
  const texBytes = {};
  for (const im of images) texBytes[im.mime] = (texBytes[im.mime] ?? 0) + im.bytes;
  const triangles = prims.reduce((n, p) => n + ((p.mode ?? 4) === 4 ? (p.indices !== undefined ? j.accessors[p.indices].count : j.accessors[p.attributes.POSITION].count) / 3 : 0), 0);
  // What three actually draws: meshes reached from the scenes' nodes (an unreferenced mesh is never loaded).
  const meshTris = (j.meshes ?? []).map((m) => m.primitives.reduce((n, p) => n + ((p.mode ?? 4) === 4 ? (p.indices !== undefined ? j.accessors[p.indices].count : j.accessors[p.attributes.POSITION].count) / 3 : 0), 0));
  let drawnTriangles = 0, unreferencedMeshes = 0;
  const used = new Set(), seenNodes = new Set();
  const walk = (i) => { if (seenNodes.has(i)) return; seenNodes.add(i); const nd = j.nodes[i]; if (nd.mesh !== undefined) { drawnTriangles += meshTris[nd.mesh]; used.add(nd.mesh); } (nd.children ?? []).forEach(walk); };
  for (const sc of j.scenes ?? []) (sc.nodes ?? []).forEach(walk);
  unreferencedMeshes = (j.meshes ?? []).length - used.size;
  return {
    meshes: (j.meshes ?? []).length, primitives: prims.length, triangles, drawnTriangles, unreferencedMeshes, layout,
    glossyMeshes: glossyMeshes.size, glossyMeshesWithMrMap: glossyWithMap.size,
    batchMix: {
      normal: [...kinds('NORMAL', 'float32 x3 (computed)')], uv: [...kinds('TEXCOORD_0', 'float32 x2 (added)')],
      jeepStyleMixedMaterialGroups: [...byMaterial.values()].filter((s) => s.size > 1).length,
      cityBatch, cityBatchMixed: cityBatch.some((g) => g.mixedNormal || g.mixedUv),
    },
    textureBytesByMime: texBytes, extensionsUsed: j.extensionsUsed ?? [], extensionsRequired: j.extensionsRequired ?? [],
  };
}

// ------------------------------------------------------------------------------------ main
const { list, remote } = resolveList();
const filtered = list.filter((e) => !flag('only') || e.rel.includes(flag('only')));
// Keep the installer inventory synchronized with newly authored venues on every run.
{
  const rows = list.map((e) => ({ ...e, bytes: e.missing ? null : fs.statSync(path.join(ROOT, e.rel)).size, preset: CLASSES[e.cls].preset, overrides: CLASSES[e.cls].overrides }));
  const total = rows.reduce((n, r) => n + (r.bytes ?? 0), 0);
  fs.writeFileSync(path.join(ROOT, 'tools/optimize/runtime-glbs.json'), JSON.stringify({
    generated: new Date().toISOString(), totalBytes: total, count: rows.length,
    notLoaded: ['build/hotels/staged-vegas.glb (no HotelTemplates module name)', 'build/south-strip/liberty-scan.glb (no loader in src/)', 'every */before/*, *-before/*, uthana/inputs copy'],
    remoteWorldRows: remote, files: rows,
  }, null, 1));
  console.log(`${rows.length} runtime GLBs, ${mib(total)}; ${remote.length} remote world.json GLB rows listed (not fetched) -> tools/optimize/runtime-glbs.json`);
  if (flag('list')) process.exit(0);
}
if (flag('analyze')) {
  const out = [];
  for (const e of filtered.filter((x) => !x.missing)) {
    const dir = outDir(e.rel), rep = fs.existsSync(path.join(dir, 'report.json')) ? JSON.parse(fs.readFileSync(path.join(dir, 'report.json'), 'utf8')) : null;
    const row = { rel: e.rel, cls: e.cls, before: analyzeGlb(path.join(ROOT, e.rel)) };
    if (fs.existsSync(path.join(dir, 'out.glb'))) row.after = analyzeGlb(path.join(dir, 'out.glb'));
    if (fs.existsSync(path.join(dir, 'out-fallback.glb'))) row.afterFallback = analyzeGlb(path.join(dir, 'out-fallback.glb'));
    if (fs.existsSync(path.join(dir, 'out-textures-only.glb'))) row.afterTexturesOnly = analyzeGlb(path.join(dir, 'out-textures-only.glb'));
    row.exitCode = rep?.exitCode ?? null;
    out.push(row);
  }
  fs.writeFileSync(path.join(ROOT, 'tools/optimize/analysis.json'), JSON.stringify(out, null, 1));
  console.log(`analysis of ${out.length} files -> tools/optimize/analysis.json`);
  process.exit(0);
}
if (flag('summary')) { writeSummary(); process.exit(0); }
// --variant=webp-textures: an EXPERIMENT beyond the level preset (which keeps textures): colour maps as
// lossy WebP q90 at their own size, ORM as lossless WebP, normal maps kept. Download only (GPU memory is
// RGBA8 either way); lossy, so it needs the in-game A/B before anyone uses it. Writes out-webp-textures.glb.
// --psnr: for each out-webp-textures.glb, PSNR of every re-encoded colour map against the original
// (matched by material name + slot), written into report-webp-textures.json as `psnr`. A numbers aid
// for choosing what to A/B first, not a visual verdict.
if (flag('psnr')) {
  const sharp = (await import(pathToFileURL(path.join(BM_TOOLS, 'gltf/node_modules/sharp/dist/index.mjs')).href)).default;
  const slots = (file) => {
    const b = fs.readFileSync(file), L = b.readUInt32LE(12), j = JSON.parse(b.subarray(20, 20 + L)), bin = b.subarray(20 + L + 8), m = new Map();
    const img = (ti) => { const t = j.textures[ti]; const src = t.extensions?.EXT_texture_webp?.source ?? t.source; const im = j.images[src], bv = j.bufferViews[im.bufferView]; return { mime: im.mimeType, bytes: bin.subarray(bv.byteOffset ?? 0, (bv.byteOffset ?? 0) + bv.byteLength) }; };
    for (const mat of j.materials ?? []) for (const [slot, info] of [['base', mat.pbrMetallicRoughness?.baseColorTexture], ['emissive', mat.emissiveTexture]]) if (info && !m.has(`${mat.name}|${slot}`)) m.set(`${mat.name}|${slot}`, img(info.index));
    return m;
  };
  for (const e of filtered.filter((x) => !x.missing)) {
    const dir = outDir(e.rel), rf = path.join(dir, 'report-webp-textures.json');
    if (!fs.existsSync(path.join(dir, 'out-webp-textures.glb')) || !fs.existsSync(rf)) continue;
    const a = slots(path.join(ROOT, e.rel)), b = slots(path.join(dir, 'out-webp-textures.glb')), seen = new Map(), psnr = [];
    for (const [k, x] of a) {
      const y = b.get(k); if (!y || y.mime === x.mime) continue;
      const key = crypto.createHash('sha1').update(x.bytes).digest('hex');
      if (seen.has(key)) continue;
      const X = await sharp(x.bytes).removeAlpha().raw().toBuffer({ resolveWithObject: true }), Y = await sharp(y.bytes).removeAlpha().raw().toBuffer({ resolveWithObject: true });
      if (X.info.width !== Y.info.width || X.info.height !== Y.info.height) { psnr.push({ key: k, note: 'size differs' }); continue; }
      let se = 0, max = 0; for (let i = 0; i < X.data.length; i++) { const d = X.data[i] - Y.data[i]; se += d * d; if (Math.abs(d) > max) max = Math.abs(d); }
      const v = se ? +(10 * Math.log10((255 * 255) / (se / X.data.length))).toFixed(1) : Infinity;
      seen.set(key, v); psnr.push({ key: k, size: `${X.info.width}x${X.info.height}`, psnr: v, maxAbs: max });
    }
    const rep = JSON.parse(fs.readFileSync(rf, 'utf8'));
    rep.psnr = { min: psnr.reduce((m, p) => Math.min(m, p.psnr ?? Infinity), Infinity), maps: psnr };
    fs.writeFileSync(rf, JSON.stringify(rep, null, 1));
  }
  console.log('psnr written into report-webp-textures.json files');
  process.exit(0);
}
if (flag('variant') === 'webp-textures') {
  if (!SCRIPT) { console.error('optimize-glb.mjs not found'); process.exit(2); }
  for (const e of filtered.filter((x) => !x.missing && x.cls === 'level')) {
    if (!(glbJson(path.join(ROOT, e.rel)).images ?? []).length) continue;   // no textures: identical to the level output
    const dir = outDir(e.rel); fs.mkdirSync(dir, { recursive: true });
    const shaNow = sha256(path.join(ROOT, e.rel)), prev = path.join(dir, 'report-webp-textures.json');
    if (!flag('force') && fs.existsSync(prev) && JSON.parse(fs.readFileSync(prev, 'utf8')).sourceSha256 === shaNow && fs.existsSync(path.join(dir, 'out-webp-textures.glb'))) continue;
    const r = encode(e, path.join(dir, 'out-webp-textures.glb'), ['--base=webp', '--emissive=webp', '--orm=webp-lossless'], 'variant webp-textures');
    fs.writeFileSync(path.join(dir, 'report-webp-textures.json'), JSON.stringify({ rel: e.rel, sourceSha256: shaNow, ...r }, null, 1));
    console.log(`${e.rel} webp-textures exit ${r.exitCode} ${r.report ? `${mib(r.report.before.bytes)} -> ${mib(r.report.after.bytes)}` : 'CRASH'} ${r.failed.join('; ')}`);
  }
  process.exit(0);
}
if (!SCRIPT) { console.error('optimize-glb.mjs not found (.agents/skills or the installed @bitmagic/cli)'); process.exit(2); }
console.log(`encoder ${SCRIPT}\nBM_TOOLS ${BM_TOOLS}`);
const done = new Map();
let n = 0;
for (const e of filtered) {
  n++;
  if (e.missing) { console.log(`[${n}/${filtered.length}] MISSING ${e.rel}`); continue; }
  const r = runOne(e, done);
  if (r.skipped) { console.log(`[${n}/${filtered.length}] up to date ${e.rel}`); continue; }
  const b = r.report?.before?.bytes, a = r.report?.after?.bytes;
  console.log(`[${n}/${filtered.length}] ${r.identicalTo ? 'copied ' : ''}${e.rel} ${r.preset ?? ''} exit ${r.exitCode} ${b ? `${mib(b)} -> ${mib(a)}` : ''} ${r.failed?.length ? `FAIL ${r.failed.join('; ')}` : ''}${!r.report ? ` CRASH ${r.stderr?.slice(-2).join(' | ')}` : ''}${r.fallback ? ` fallback: ${JSON.stringify(r.fallback)}` : ''}${r.texturesOnly ? ` textures-only: ${JSON.stringify(r.texturesOnly)}` : ''}`);
}

// ------------------------------------------------------------------------------------ summary -> REPORT.md (generated block)
function writeSummary() {
  const analysis = new Map(JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/optimize/analysis.json'), 'utf8')).map((a) => [a.rel, a]));
  const MERGERS = (rel) => rel === 'build/geographic-strip/city.glb' || rel === 'build/geographic-strip/detailed.glb' || rel === 'build/highrises/exteriors.glb' || /-exterior\.glb$/.test(rel) && /strip-landmarks|resort-blocks/.test(rel);
  const group = (rel) => rel.startsWith('src/work/characters') ? 'characters' : rel.split('/').slice(0, rel.startsWith('build/resort-blocks') ? 3 : 2).join('/');
  const rows = [];
  for (const e of list) {
    if (e.missing) continue;
    const dir = outDir(e.rel), rep = JSON.parse(fs.readFileSync(path.join(dir, 'report.json'), 'utf8'));
    const before = fs.statSync(path.join(ROOT, e.rel)).size, an = analysis.get(e.rel);
    let candidate = null, after = before, afterAn = null, result;
    if (rep.exitCode === 0) { candidate = 'out.glb'; after = rep.report.after.bytes; afterAn = an?.after; result = 'ok'; }
    else if (rep.texturesOnly?.exitCode === 0) { candidate = 'out-textures-only.glb'; after = rep.texturesOnly.bytesAfter; afterAn = an?.afterTexturesOnly; result = 'encoder cannot read it (required BITMAGIC_sparse_correctives); texture-only candidate'; }
    else if (rep.fallback?.exitCode === 0) { candidate = 'out-fallback.glb'; after = fs.statSync(path.join(dir, 'out-fallback.glb')).size; afterAn = an?.afterFallback; result = `primary failed (${rep.failed.join('; ')}); fallback ${rep.fallback.overrides.join(' ')}`; }
    else result = rep.failed?.length ? `no candidate: ${rep.failed.join('; ')} -> the original ships` : 'no candidate (encoder crashed)';
    const R = rep.report, val = R?.checks?.find((c) => c.name === 'Khronos validator')?.detail ?? (rep.texturesOnly ? JSON.parse(fs.readFileSync(path.join(dir, 'report-textures-only.json'), 'utf8')).report?.checks?.find((c) => c.name === 'Khronos validator')?.detail : null);
    const mergeRisk = !MERGERS(e.rel) && e.rel !== 'build/vehicles/afterlight-jeep.glb' ? '-' : e.rel === 'build/vehicles/afterlight-jeep.glb'
      ? (afterAn?.batchMix.jeepStyleMixedMaterialGroups ? `JEEP MERGE: ${afterAn.batchMix.jeepStyleMixedMaterialGroups} material group(s) mix types` : 'ok')
      : (afterAn?.batchMix.cityBatchMixed ? `CityBatches MIX (${afterAn.batchMix.cityBatch.filter((g) => g.mixedNormal || g.mixedUv).map((g) => `${g.side}: ${g.mixedNormal ? 'normal' : ''}${g.mixedNormal && g.mixedUv ? '+' : ''}${g.mixedUv ? 'uv' : ''}`).join(', ')})` : candidate === 'out.glb' ? 'ok' : '-');
    rows.push({ rel: e.rel, group: group(e.rel), when: e.when, cls: e.cls, preset: CLASSES[e.cls].preset, overrides: CLASSES[e.cls].overrides.join(' '), before, after, candidate, result,
      trisBefore: an?.before.drawnTriangles, trisAfter: candidate ? afterAn?.drawnTriangles : an?.before.drawnTriangles,
      unreferenced: an?.before.unreferencedMeshes && candidate === 'out.glb' && !afterAn?.unreferencedMeshes ? `${an.before.unreferencedMeshes} meshes no node references (${(an.before.triangles - an.before.drawnTriangles).toLocaleString()} triangles three never loads) pruned; drawn triangles unchanged` : '',
      gpuTexBefore: R?.before.gpuTextures, gpuTexAfter: R?.after.gpuTextures, gpuGeoBefore: R?.before.gpuGeometry, gpuGeoAfter: R?.after.gpuGeometry,
      validator: val, glossy: an ? `${an.before.glossyMeshes}/${an.before.meshes}${an.before.glossyMeshesWithMrMap ? ` (${an.before.glossyMeshesWithMrMap} w/ MR map)` : ''}` : '?',
      mergeRisk, mergeRiskBefore: MERGERS(e.rel) ? (an?.before.batchMix.cityBatchMixed ? 'MIX' : 'ok') : '-',
      webp: (() => { const f = path.join(dir, 'report-webp-textures.json'); if (!fs.existsSync(f)) return null; const w = JSON.parse(fs.readFileSync(f, 'utf8')); return w.exitCode === 0 ? { bytes: w.report.after.bytes, psnrMin: w.psnr?.min ?? null } : { failed: w.failed }; })(),
      layoutBefore: an?.before.layout, layoutAfter: afterAn?.layout, notes: (R?.notes ?? []).filter((n) => !/shared tools differ/.test(n)), identicalTo: rep.identicalTo ?? null });
  }
  const M = (n) => (n === undefined || n === null ? '' : (n / 1048576).toFixed(2));
  const pct = (a, b) => (a ? `${b <= a ? '-' : '+'}${Math.abs(100 - (b / a) * 100).toFixed(0)}%` : '');
  const sum = (rs, k) => rs.reduce((n, r) => n + (r[k] ?? 0), 0);
  const out = [];
  out.push(`Generated ${new Date().toISOString()} by \`node tools/optimize/optimize-runtime-glbs.mjs --analyze && ... --summary\`. MiB = 1,048,576 bytes.`, '');
  out.push('### Totals by group', '', '| Group | Files | With candidate | Before MiB | After MiB | Change |', '|---|---:|---:|---:|---:|---:|');
  const groups = [...new Set(rows.map((r) => r.group))];
  for (const g of groups) { const rs = rows.filter((r) => r.group === g); out.push(`| ${g} | ${rs.length} | ${rs.filter((r) => r.candidate).length} | ${M(sum(rs, 'before'))} | ${M(sum(rs, 'after'))} | ${pct(sum(rs, 'before'), sum(rs, 'after'))} |`); }
  out.push(`| **all runtime GLBs** | **${rows.length}** | **${rows.filter((r) => r.candidate).length}** | **${M(sum(rows, 'before'))}** | **${M(sum(rows, 'after'))}** | **${pct(sum(rows, 'before'), sum(rows, 'after'))}** |`, '');
  const withStats = rows.filter((r) => r.gpuGeoBefore !== undefined && r.candidate === 'out.glb');
  out.push(`GPU estimate (encoder, ${withStats.length} files with an encoder candidate): geometry ${M(sum(withStats, 'gpuGeoBefore'))} -> ${M(sum(withStats, 'gpuGeoAfter'))} MiB, textures ${M(sum(withStats, 'gpuTexBefore'))} -> ${M(sum(withStats, 'gpuTexAfter'))} MiB. Drawn triangles unchanged in every candidate (${rows.filter((r) => r.candidate).every((r) => r.trisAfter === r.trisBefore) ? 'checked: all equal' : 'NOT all equal: see table'}).`, '');
  const webpAfter = (r) => (r.webp?.bytes !== undefined ? r.webp.bytes : r.after);
  const anyWebp = rows.some((r) => r.webp?.bytes !== undefined);
  if (anyWebp) {
    const ws = rows.filter((r) => r.webp?.bytes !== undefined), lowest = ws.filter((r) => r.webp.psnrMin !== null && r.webp.psnrMin !== Infinity).sort((a, b) => a.webp.psnrMin - b.webp.psnrMin);
    out.push('### Variant: level + WebP colour maps (experiment, needs the A/B)', '', `\`--variant=webp-textures\` re-encodes base/emissive maps as lossy WebP q90 at their own size and ORM maps as lossless WebP; normal maps and everything else as the level preset. Files: ${ws.length} (every level file that has textures). Those files: ${M(sum(ws, 'after'))} MiB (level) -> ${M(ws.reduce((n, r) => n + r.webp.bytes, 0))} MiB (variant). All runtime GLBs with the variant where it exists: **${M(sum(rows, 'before'))} -> ${M(rows.reduce((n, r) => n + webpAfter(r), 0))} MiB**. GPU memory does not change (WebP and PNG both upload as RGBA8).`, '');
    if (lowest.length) out.push(`Lowest colour-map PSNR (original vs WebP, whole map): ${lowest.slice(0, 8).map((r) => `\`${r.rel.replace(/^build\//, '')}\` ${r.webp.psnrMin} dB`).join(', ')}. Median file minimum: ${lowest[Math.floor(lowest.length / 2)].webp.psnrMin} dB.`, '');
    const wf = rows.filter((r) => r.webp?.failed); if (wf.length) out.push(`Variant failures: ${wf.map((r) => `\`${r.rel}\` (${r.webp.failed.join('; ')})`).join(', ')}`, '');
  }
  const boot = rows.filter((r) => r.when.startsWith('boot'));
  out.push(`Loaded at boot (local dev view): ${boot.length} files, ${M(sum(boot, 'before'))} -> ${M(sum(boot, 'after'))} MiB. Streamed later: ${rows.length - boot.length} files, ${M(sum(rows, 'before') - sum(boot, 'before'))} -> ${M(sum(rows, 'after') - sum(boot, 'after'))} MiB.`, '');
  // Layout transitions
  out.push('### Vertex layouts (attribute: componentType [norm] x itemSize; counts are primitives)', '');
  const sig = (l) => (l ? Object.keys(l).sort().join(', ') : 'n/a');
  for (const g of groups) {
    const rs = rows.filter((r) => r.group === g), trans = new Map();
    for (const r of rs) { const k = `${sig(r.layoutBefore)}\n=> ${r.candidate ? sig(r.layoutAfter) : '(original kept)'}`; trans.set(k, (trans.get(k) ?? 0) + 1); }
    out.push(`**${g}**`, '');
    for (const [k, n] of [...trans.entries()].sort((a, b) => b[1] - a[1])) { const [b, a] = k.split('\n=> '); out.push(`- ${n} file(s): before \`${b}\``, `  after \`${a}\``); }
    out.push('');
  }
  const big = rows.filter((r) => r.before > 30 * 1048576);
  out.push('Primitive counts per format, largest files:', '');
  for (const r of big) {
    out.push(`- \`${r.rel}\``);
    out.push(`  - before: ${Object.entries(r.layoutBefore ?? {}).map(([k, v]) => `${k} (${v})`).join('; ')}`);
    out.push(`  - after: ${Object.entries(r.layoutAfter ?? {}).map(([k, v]) => `${k} (${v})`).join('; ')}`);
  }
  out.push('');
  // Distinct notes
  const notes = new Map();
  for (const r of rows) for (const n of r.notes) { const k = n.replace(/\d[\d,.]*/g, '#'); notes.set(k, (notes.get(k) ?? 0) + 1); }
  out.push('### Encoder notes (distinct, numbers folded; count = files)', '');
  for (const [n, c] of [...notes.entries()].sort((a, b) => b[1] - a[1])) out.push(`- ${c} x ${n.slice(0, 400)}`);
  out.push('', '### Per file', '', 'Glossy = meshes with a material of metalness factor > 0.5 or roughness factor < 0.2 (glTF defaults count: metalness 1). Merge = the game-side batch merge check (see Risks); "-" = no merge consumer. GPU = the encoder\'s estimate (textures RGBA8 + mips; geometry = accessor bytes, so int8 normals count 3 bytes where the GPU stores 4).', '',
    '| File | When | Preset (+overrides) | Before MiB | After MiB | Change | WebP-tex variant MiB (min PSNR) | Drawn triangles | GPU tex MiB | GPU geom MiB | Validator (after) | Glossy | Merge | Result |', '|---|---|---|---:|---:|---:|---|---:|---|---|---|---|---|---|');
  for (const r of rows) {
    out.push(`| \`${r.rel.replace(/^build\//, '')}\` | ${r.when} | ${r.preset}${r.overrides ? ` ${r.overrides}` : ''} | ${M(r.before)} | ${M(r.after)} | ${pct(r.before, r.after)} | ${r.webp?.bytes !== undefined ? `${M(r.webp.bytes)}${r.webp.psnrMin !== null && r.webp.psnrMin !== Infinity ? ` (${r.webp.psnrMin} dB)` : ''}` : r.webp?.failed ? 'FAIL' : ''} | ${r.trisBefore?.toLocaleString?.() ?? ''}${r.trisAfter !== undefined && r.trisAfter !== r.trisBefore ? ` -> ${r.trisAfter.toLocaleString()}` : ''} | ${r.gpuTexBefore !== undefined ? `${M(r.gpuTexBefore)} -> ${M(r.gpuTexAfter)}` : 'unchanged'} | ${r.gpuGeoBefore !== undefined ? `${M(r.gpuGeoBefore)} -> ${M(r.gpuGeoAfter)}` : 'unchanged'} | ${(r.validator ?? '').replace(/\|/g, '/').slice(0, 90)} | ${r.glossy} | ${r.mergeRisk} | ${r.result}${r.unreferenced ? `; ${r.unreferenced}` : ''}${r.identicalTo ? ` (identical source to ${r.identicalTo}, output copied)` : ''} |`);
  }
  fs.writeFileSync(path.join(ROOT, 'tools/optimize/summary.json'), JSON.stringify(rows.map(({ layoutBefore, layoutAfter, ...r }) => ({ ...r, layoutBefore, layoutAfter })), null, 1));
  const file = path.join(ROOT, 'tools/optimize/REPORT.md'), START = '<!-- generated:start -->', END = '<!-- generated:end -->';
  const old = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : `# Runtime GLB optimization\n\n${START}\n${END}\n`;
  const [head, rest] = old.includes(START) ? old.split(START) : [old + '\n', END];
  fs.writeFileSync(file, `${head}${START}\n${out.join('\n')}\n${END}${rest.split(END)[1] ?? '\n'}`);
  console.log(`summary: ${rows.length} files, ${M(sum(rows, 'before'))} -> ${M(sum(rows, 'after'))} MiB -> tools/optimize/REPORT.md, tools/optimize/summary.json`);
}
