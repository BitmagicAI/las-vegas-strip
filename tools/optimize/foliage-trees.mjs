#!/usr/bin/env node
/*
 * foliage-trees.mjs: the garden planting's runtime copies (2026-10-25: the owner asked for every model
 * to be compressed, and for the 7.4 MB tree to be optimized further).
 *
 * The three tree LODs (public/foliage/tree-0/1/2.glb, Poly Haven tree_small_02) each carried the same nine 1k maps
 * (6.3 MB), and the published game downloaded the uncompressed originals (cdn-upload took public/foliage). Here:
 *   - tree-1 (the middle LOD) is written without textures: ResortFoliage gives its meshes tree-0's materials by name;
 *   - every foliage GLB goes through the skill's encoder (hero-prop: no simplification, int8 normals, meshopt) with
 *     16-bit positions (instanced and never read by code), colour maps as lossy WebP q90 (the installed set's choice,
 *     owner approved 2026-10-07), normal maps as JPEG 4:4:4 (the preset's), ORM as lossless WebP;
 *   - tree-0 (the near tree, 250k triangles) is also simplified to 71k (error 0.2% of its size; 8.7 -> 5.3 MB, garden
 *     40.8 -> 49.1 fps, canopies slightly thinner: the owner approved it from the A/B sheet on 2026-10-26);
 *   - the results are installed to build/optimized/foliage/ with manifest entries, as install-optimized.mjs does,
 *     so the dev server serves them (OptimizedGlb.ts) and tools/release/cdn-upload.mjs uploads them.
 * Originals stay untouched. Run from the project root: node tools/optimize/foliage-trees.mjs
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

const MANIFEST = path.join(ROOT, 'build/optimized/manifest.json');
const manifest = JSON.parse(fs.readFileSync(MANIFEST, 'utf8'));
let before = 0, after = 0;
for (const name of FILES) {
  const source = path.join(ROOT, 'public/foliage', name + '.glb');
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
  if (r.status !== 0 && !waived) { console.error(`${name}: encoder exit ${r.status}; not installed\n${(r.stderr || r.stdout).slice(-2000)}`); continue; }
  if (waived) console.log(`${name}: installed with the ${failed.join(', ')} check waived (see WAIVED)`);
  const key = 'foliage/' + name + '.glb', target = path.join(ROOT, 'build/optimized', key), stat = fs.statSync(source);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(out, target);
  manifest.files[key] = { size: stat.size, modified: stat.mtimeMs, optimized: path.relative(ROOT, target), sourceSha256: sha(source), bytes: fs.statSync(target).size,
    preset: 'hero-prop', overrides: [...OPTIONS.slice(1), ...(EXTRA[name] ?? [])], variant: TEXTURELESS.has(name) ? 'foliage (textureless; tree-0 materials at load)' : 'foliage' };
  before += stat.size; after += fs.statSync(target).size;
  console.log(`${name}: ${(stat.size / 1048576).toFixed(2)} MB -> ${(fs.statSync(target).size / 1048576).toFixed(2)} MB`);
}
fs.writeFileSync(MANIFEST, JSON.stringify(manifest, null, 1));
console.log(`foliage: ${(before / 1048576).toFixed(1)} MB -> ${(after / 1048576).toFixed(1)} MB (installed to build/optimized/foliage/)`);
