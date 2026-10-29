#!/usr/bin/env node
/*
 * foliage-trees.mjs: the garden planting's runtime copies (2026-10-25: the owner asked for every model
 * to be compressed, and for the 7.4 MB tree to be optimized further).
 *
 * The three tree LODs (Poly Haven tree_small_02) each carried the same nine 1k maps (6.3 MB). Here:
 *   - tree-1 (the middle LOD) is written without textures: ResortFoliage gives its meshes tree-0's materials by name;
 *   - every foliage GLB goes through the skill's encoder (hero-prop: no simplification, int8 normals, meshopt) with
 *     16-bit positions (instanced and never read by code), colour maps as lossy WebP q90 (the installed set's choice,
 *     owner approved 2026-10-07), normal maps as JPEG 4:4:4 (the preset's), ORM as lossless WebP;
 *   - tree-0 (the near tree, 250k triangles) is also simplified to 71k (error 0.2% of its size; 8.7 -> 5.3 MB, garden
 *     40.8 -> 49.1 fps, canopies slightly thinner: the owner approved it from the A/B sheet on 2026-10-26);
 *   - the sources are tools/foliage/models/ (tools/foliage/README.md builds them; the Blender exporters import them),
 *     and the results are written to public/foliage/, which every checkout, clone and the CDN upload serve as they are
 *     (2026-10-29: a clone used to load the 35 MB sources from public/). A model the encoder cannot make smaller
 *     (grass-1) is served as its source. tools/optimize/foliage-trees.json records the source each copy was made from;
 *     python3 tools/optimize/check-runtime-glbs.py fails when a source changed after its copy was made.
 * Sources stay untouched. Run from the project root: node tools/optimize/foliage-trees.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const ROOT = process.cwd();
if (!fs.existsSync(path.join(ROOT, 'src/work/world.json'))) { console.error('run from the project root'); process.exit(2); }
const BM_TOOLS = process.env.BM_TOOLS ?? path.join(ROOT, 'tools/optimize/bm-tools');
const ENCODER = path.join(ROOT, '.agents/skills/optimizing-assets/scripts/optimize-glb.mjs');
// --code=none: the encoder's scan matched the node name tree-lod0 against a material-name rule in PbrDetailSets.ts and
// kept it float; nothing reads the trees' vertices or node transforms (ResortFoliage bakes each mesh's world matrix,
// dequantization included, into the instance matrices)
const OPTIONS = ['--preset=hero-prop', '--code=none', '--pos-bits=16', '--base=webp:1024:90', '--orm=webp-lossless:512'];
const FILES = ['tree-0', 'tree-1', 'tree-2', 'grass-0', 'grass-1'];
const TEXTURELESS = new Set(['tree-1']);
const EXTRA = { 'tree-0': ['--simplify=0.002'] };
// The encoder refuses a model whose bounds move more than 0.5%, because the engine fits targetHeight to loaded bounds.
// The planting never does: ResortFoliage places every instance with its own position, yaw and scale. tree-0's simplified
// canopy edge moves 0.97% of its size, which is what the approved A/B showed; any other failed check still blocks.
const WAIVED = { 'tree-0': new Set(['bounds']) };
const sha = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const gltf = (m) => import(pathToFileURL(path.join(BM_TOOLS, 'gltf/node_modules', m)).href);

const { NodeIO } = await gltf('@gltf-transform/core/dist/index.js');
const { ALL_EXTENSIONS } = await gltf('@gltf-transform/extensions/dist/index.js');
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);

const RECORD = path.join(ROOT, 'tools/optimize/foliage-trees.json');
const record = { about: 'The garden foliage served from public/foliage/ and the source each copy was made from. Written by '
  + 'tools/optimize/foliage-trees.mjs; read by tools/optimize/check-runtime-glbs.py.', files: {} };
if (fs.existsSync(RECORD)) Object.assign(record.files, JSON.parse(fs.readFileSync(RECORD, 'utf8')).files);
let before = 0, after = 0;
for (const name of FILES) {
  const source = path.join(ROOT, 'tools/foliage/models', name + '.glb');
  const dir = path.join(ROOT, '.bitmagic/optimize/public/foliage', name);
  fs.mkdirSync(dir, { recursive: true });
  let input = source;
  if (TEXTURELESS.has(name)) {
    // the LOD's own copy of tree-0's maps: materials (and their names) stay, every texture goes
    const doc = await io.read(source);
    for (const t of doc.getRoot().listTextures()) t.dispose();
    input = path.join(dir, 'textureless.glb');
    await io.write(input, doc);
  }
  const out = path.join(dir, 'out-foliage.glb');
  const r = spawnSync(process.execPath, [ENCODER, input, out, ...OPTIONS, ...(EXTRA[name] ?? []), '--json'], { cwd: ROOT, env: { ...process.env, BM_TOOLS }, encoding: 'utf8', maxBuffer: 1 << 28 });
  fs.writeFileSync(path.join(dir, 'report-foliage.json'), r.stdout || r.stderr);
  let failed = [];
  try { failed = JSON.parse(r.stdout).checks.filter((c) => c.fail).map((c) => c.name); } catch { failed = ['(no report)']; }
  const waived = r.status === 1 && failed.length > 0 && failed.every((c) => WAIVED[name]?.has(c));
  const asSource = r.status === 1 && failed.length === 1 && failed[0] === 'smaller';
  if (r.status !== 0 && !waived && !asSource) { console.error(`${name}: encoder exit ${r.status}; not written\n${(r.stderr || r.stdout).slice(-2000)}`); continue; }
  if (waived) console.log(`${name}: written with the ${failed.join(', ')} check waived (see WAIVED)`);
  const key = 'public/foliage/' + name + '.glb', target = path.join(ROOT, key), bytes = fs.statSync(source).size;
  fs.copyFileSync(asSource ? source : out, target);
  record.files[key] = { source: path.relative(ROOT, source), sourceSha256: sha(source), sha256: sha(target), bytes: fs.statSync(target).size,
    preset: 'hero-prop', overrides: asSource ? [] : [...OPTIONS.slice(1), ...(EXTRA[name] ?? [])],
    variant: asSource ? 'source (the encoder could not make it smaller)' : TEXTURELESS.has(name) ? 'foliage (textureless; tree-0 materials at load)' : 'foliage' };
  before += bytes; after += fs.statSync(target).size;
  console.log(`${name}: ${(bytes / 1048576).toFixed(2)} MB -> ${(fs.statSync(target).size / 1048576).toFixed(2)} MB${asSource ? ' (the source: the encoder could not make it smaller)' : ''}`);
}
fs.writeFileSync(RECORD, JSON.stringify(record, null, 1) + '\n');
console.log(`foliage: ${(before / 1048576).toFixed(1)} MB -> ${(after / 1048576).toFixed(1)} MB (written to public/foliage/; record ${path.relative(ROOT, RECORD)})`);
