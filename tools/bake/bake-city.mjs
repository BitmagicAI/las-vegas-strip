#!/usr/bin/env node
/*
 * bake-city.mjs: the city bake (2026-10-26, the owner: "add a build step so that when any new geometry is updated, we bake
 * the city so that it's only done once and not in the client at every load", then: "store a pre-processed but not fully
 * baked data that is a tiny fraction"). The client keeps merging the source GLBs into near batches; what the bake stores
 * is the expensive, small part: each block's distant LOD as a compact vertex subset and index list (src/work/CityBakeLoad.ts).
 *
 * Step 1, capture: the game runs once in headless Chrome on the dev server with `?bake=capture` (src/work/CityBake.ts):
 * it builds the city exactly as a visitor's browser would and sends every block's near batches here. They are kept in
 * .bitmagic/bake/raw/ (ignored; ~3 GB) for the next step.
 *
 * Step 2, lod: each near batch is simplified (meshoptimizer, edge collapse across attribute seams) to an absolute error of
 * one 1080p pixel where its block switches to the LOD (CityLod: from 0.88 x its near distance, 70-degree vertical field
 * of view): 0.27 m for the mapped city's blocks (240 m), 0.63-2 m for resort facades (550-1,800 m). Written to
 * build/baked/city-lod.bin (VLOD; read by src/work/CityBakeLoad.ts):
 *   u32 magic 'VLOD', u16 version 1, u16 0, then varints: part count; per part its id (length + UTF-8) and block count;
 *   per block its key and batch count; per batch: the near batch's vertex and index counts, a u32 hash of 64 of its
 *   positions (a stale bake is never applied), the LOD's vertex count and index count, its vertices' batch ids as zigzag
 *   deltas in first-use order, then the index list over them (vertex-cache order, meshopt index codec; 16-bit below
 *   65,536 vertices), each as byte length + bytes. Before simplifying, vertices sharing a position and surface row are
 *   welded (and UV on facades): at LOD distance hard edges and seams only cost vertices.
 *
 * The build step: `node tools/bake/bake-city.mjs` hashes everything the bake depends on (every exterior GLB the city
 * builds from, original and optimized copy; the record files that name blocks; the bake-relevant code) and runs both
 * steps only when that hash changed, recording it in build/baked/city-lod.inputs.json. Run it after regenerating any
 * city geometry (after tools/optimize and pack-data.mjs); tools/release/asset-pack.py refuses a stale bake. The game
 * never draws a stale one either: each batch's counts and sampled positions are checked, and a batch that differs is
 * clustered in the browser as before (CityLod).
 *
 *   node tools/bake/bake-city.mjs             # bake if anything changed (needs `bitmagic dev` running)
 *   node tools/bake/bake-city.mjs check       # exit 1 when the bake is stale or missing
 *   node tools/bake/bake-city.mjs capture     # the two steps by hand
 *   node tools/bake/bake-city.mjs lod
 */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { launchSystemChrome, browserRendererArgs } from '../lib/bitmagic-cli.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const BM = path.join(ROOT, 'tools/optimize/bm-tools/gltf/node_modules/meshoptimizer');
export const LOD_FILE = path.join(ROOT, 'build/baked/city-lod.bin');
export const RAW = path.join(ROOT, '.bitmagic/bake/raw');
const safe = (id) => id.replace(/[^A-Za-z0-9._-]+/g, '_').slice(0, 120);

/** Reads a part sent by CityBake.export: a JSON head and the arrays it names. */
export function readPart(file) {
  const bytes = fs.readFileSync(file), length = bytes.readUInt32LE(0), head = JSON.parse(bytes.subarray(4, 4 + length).toString('utf8'));
  const base = 4 + length, types = { Float32Array, Int8Array, Uint8Array, Uint16Array, Uint32Array };
  const view = (b) => { const T = types[b.type]; const copy = bytes.buffer.slice(bytes.byteOffset + base + b.at, bytes.byteOffset + base + b.at + b.bytes); return new T(copy); };
  for (const block of head.blocks) for (const batch of block.batches)
    for (const k of ['position', 'normal', 'uv', 'color', 'silhouette', 'row', 'index']) if (batch[k]) batch[k] = view(batch[k]);
  return head;
}

async function capture() {
  fs.rmSync(RAW, { recursive: true, force: true }); fs.mkdirSync(RAW, { recursive: true });
  let done, failed; const finished = new Promise((resolve, reject) => { done = resolve; failed = reject; });
  let parts = 0, bytes = 0;
  const pending = new Map();
  const server = http.createServer((req, res) => {
    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => {
      res.setHeader('Access-Control-Allow-Origin', '*');
      try {
        const body = Buffer.concat(chunks), url = new URL(req.url, 'http://x'), route = url.pathname;
        if (route === '/part') {
          // a part arrives in chunks, in order
          const n = url.searchParams.get('n'), chunk = Number(url.searchParams.get('chunk')), of = Number(url.searchParams.get('of'));
          const list = pending.get(n) ?? []; list[chunk] = body; pending.set(n, list);
          if (list.filter(Boolean).length === of) {
            const whole = Buffer.concat(list); pending.delete(n);
            const head = JSON.parse(whole.subarray(4, 4 + whole.readUInt32LE(0)).toString('utf8'));
            fs.writeFileSync(path.join(RAW, safe(head.id) + '.bin'), whole); parts++; bytes += whole.length;
          }
        } else if (route === '/done') done();
        res.end('ok');
      } catch (e) { res.statusCode = 500; res.end(String(e)); failed(e); }
    });
  });
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const address = `http://127.0.0.1:${server.address().port}`;
  const port = JSON.parse(fs.readFileSync(path.join(ROOT, '.bitmagic/dev.json'), 'utf8')).gamePort;
  const browser = await launchSystemChrome({ headless: true, args: [...browserRendererArgs(process.env, 'webgpu'), '--mute-audio'], command: 'city bake' });
  try {
    const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
    const logs = [];
    page.on('console', (m) => logs.push(m.text())); page.on('pageerror', (e) => logs.push('PAGEERROR ' + e));
    await page.goto(`http://localhost:${port}/?probe&quality=ultra&bake=capture&bakeServer=${encodeURIComponent(address)}`, { waitUntil: 'domcontentloaded', timeout: 120000 });
    for (let i = 0; i < 1200 && !logs.some((s) => s.includes('🎮 Starting game...')); i++) {
      const play = page.locator('#play-button, .hud-play-button, .start-screen-selection__option').first();
      if (await play.isVisible().catch(() => false)) await play.click().catch(() => {});
      await page.waitForTimeout(500);
    }
    await page.waitForFunction(() => !!window.__afterlightProbe && !!window.__cityBake, null, { timeout: 600000 });
    const result = await page.evaluate((server) => window.__cityBake.export(server), address);
    await finished;
    console.log(`captured ${result.parts} parts, ${result.batches} near batches, ${(bytes / 1048576).toFixed(0)} MB in ${path.relative(ROOT, RAW)}`);
  } finally { await browser.close(); server.close(); }
}

/** FNV-1a over the float bits of 64 evenly spaced positions: the client checks it against the batch it built. */
export function sampleHash(positions, vertices) {
  const bits = new Uint32Array(positions.buffer, positions.byteOffset, vertices * 3);
  let h = 0x811c9dc5;
  for (let s = 0; s < 64; s++) { const v = Math.floor((s * vertices) / 64) * 3; for (let c = 0; c < 3; c++) { h ^= bits[v + c] ?? 0; h = Math.imul(h, 0x01000193); } }
  return h >>> 0;
}

class Bytes {
  constructor() { this.a = new Uint8Array(1 << 20); this.n = 0; }
  need(k) { if (this.n + k > this.a.length) { const b = new Uint8Array(Math.max(this.a.length * 2, this.n + k)); b.set(this.a.subarray(0, this.n)); this.a = b; } }
  u8(x) { this.need(1); this.a[this.n++] = x; }
  u32(x) { this.need(4); new DataView(this.a.buffer).setUint32(this.n, x, true); this.n += 4; }
  u16(x) { this.need(2); new DataView(this.a.buffer).setUint16(this.n, x, true); this.n += 2; }
  varint(x) { do { let b = x % 128; x = Math.floor(x / 128); if (x) b |= 128; this.u8(b); } while (x); }
  raw(b) { this.need(b.length); this.a.set(b, this.n); this.n += b.length; }
  text(s) { const b = new TextEncoder().encode(s); this.varint(b.length); this.raw(b); }
  done() { return this.a.slice(0, this.n); }
}

async function lod() {
  const { MeshoptSimplifier: S } = await import(path.join(BM, 'meshopt_simplifier.js'));
  const { MeshoptEncoder: E } = await import(path.join(BM, 'meshopt_encoder.js'));
  await S.ready; await E.ready;
  const files = fs.readdirSync(RAW).filter((f) => f.endsWith('.bin')).sort();
  if (!files.length) throw new Error('nothing captured: run `node tools/bake/bake-city.mjs capture` first');
  const out = new Bytes();
  out.u32(0x444f4c56); out.u16(1); out.u16(0); out.varint(files.length);
  let near = 0, kept = 0, batches = 0, vertices = 0, subsetBytes = 0, indexBytes = 0;
  const split = {};
  let ascending = 0;
  for (const f of files) {
    const part = readPart(path.join(RAW, f));
    out.text(part.id); out.varint(part.blocks.length);
    for (const block of part.blocks) {
      out.text(block.key); out.varint(block.batches.length);
      for (const b of block.batches) {
        // simplified on welded topology (hard edges do not stop it), then every corner takes back the original vertex
        // whose normal matches its triangle (the near level's flat shading). Facades keep their UV seams and never
        // collapse across one (their textures would smear); the untextured city silhouettes may (Permissive).
        let simple;
        if (block.facade) simple = facadeLod(b, block.spacing ?? 0.7);
        else {
          // the silhouette colour (vertex colour x texture average) is an attribute to keep: collapses may cross material
          // seams (Permissive) where the colours match, not where dark asphalt meets a light sidewalk
          const welded = weld(b, WELD_CITY), lin = new Float32Array(b.vertices * 3);
          for (let i = 0; i < b.vertices * 3; i++) { const c = b.silhouette[i] / 255; lin[i] = c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; }
          const w = COLOR_WEIGHT, [merged] = process.env.CITY_MODE === 'colour-seams'
            ? S.simplify(welded.index, b.position, 3, 0, lodError(block), ['ErrorAbsolute', 'Prune'])
            : S.simplifyWithAttributes(welded.index, b.position, 3, lin, 3, [w, w, w], null, 0, lodError(block), ['ErrorAbsolute', 'Permissive', 'Prune']);
          simple = resplit(merged, b, welded);
        }
        // the LOD's vertices, ascending in the batch; triangles in vertex-cache order over them
        const used = new Uint8Array(b.vertices); for (const i of simple) used[i] = 1;
        const subset = new Uint32Array(b.vertices), at = new Uint32Array(b.vertices); let n = 0;
        for (let v = 0; v < b.vertices; v++) if (used[v]) { at[v] = n; subset[n++] = v; }
        // triangles in vertex-cache order; the vertices numbered either by first use (cheapest for the index codec) or in
        // ascending batch order (cheapest for the vertex list when they are scattered, as facade cluster representatives
        // are): whichever is smaller compressed. The client decodes both the same way.
        const local = Uint32Array.from(simple, (i) => at[i]), wide = n >= 65536;
        const candidate = (firstUse) => {
          const ordered = Uint32Array.from(local), ids = subset.slice(0, n);
          if (n) {
            const [remap] = E.reorderMesh(ordered, true, false);
            if (firstUse) { for (let v = 0; v < n; v++) ids[remap[v]] = subset[v]; }
            else { const back = new Uint32Array(n); for (let v = 0; v < n; v++) back[remap[v]] = v; for (let i = 0; i < ordered.length; i++) ordered[i] = back[ordered[i]]; }
          }
          const list = wide ? ordered : Uint16Array.from(ordered);
          const coded = list.length ? E.encodeIndexBuffer(new Uint8Array(list.buffer, list.byteOffset, list.byteLength), list.length, wide ? 4 : 2) : new Uint8Array(0);
          const deltas = new Bytes(); for (let i = 0, prev = 0; i < n; i++) { const d = ids[i] - prev; deltas.varint(d < 0 ? -2 * d - 1 : 2 * d); prev = ids[i]; }
          const d = deltas.done();
          return { list, coded, d, size: zlib.brotliCompressSync(Buffer.concat([d, coded]), { params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 6 } }).length };
        };
        const a = candidate(true), c = candidate(false), pick = c.size < a.size ? c : a, { list, coded, d } = pick;
        if (pick === c) ascending++;
        out.varint(b.vertices); out.varint(b.indices); out.u32(sampleHash(b.position, b.vertices)); out.varint(n); out.varint(list.length);
        out.varint(d.length); out.raw(d); out.varint(coded.length); out.raw(coded);
        near += b.indices / 3; kept += list.length / 3; batches++; vertices += n; subsetBytes += d.length; indexBytes += coded.length;
        const kind = block.facade ? 'facade' : 'city', s = split[kind] ??= { near: 0, kept: 0, vertices: 0, bytes: 0 };
        s.near += b.indices / 3; s.kept += list.length / 3; s.vertices += n; s.bytes += d.length + coded.length;
      }
    }
    process.stdout.write(`\r${batches} batches`);
  }
  console.log(`\n  ${ascending} of ${batches} batches smaller in ascending vertex order`);
  for (const [k, s] of Object.entries(split)) console.log(`\n  ${k}: ${(s.near / 1e6).toFixed(1)} M -> ${(s.kept / 1e6).toFixed(2)} M triangles (${(100 * s.kept / s.near).toFixed(1)}%), ${(s.vertices / 1e6).toFixed(2)} M vertices, ${(s.bytes / 1048576).toFixed(2)} MB before brotli`);
  fs.mkdirSync(path.dirname(LOD_FILE), { recursive: true });
  const bytes = out.done(); fs.writeFileSync(LOD_FILE, bytes);
  console.log(`\n${batches} batches: ${(near / 1e6).toFixed(1)} M near triangles -> ${(kept / 1e6).toFixed(2)} M LOD triangles (${(100 * kept / near).toFixed(1)}%), ${(vertices / 1e6).toFixed(2)} M LOD vertices; subsets ${(subsetBytes / 1048576).toFixed(2)} MB + indices ${(indexBytes / 1048576).toFixed(2)} MB = ${path.relative(ROOT, LOD_FILE)} ${(bytes.length / 1048576).toFixed(2)} MB, gzip ${(zlib.gzipSync(bytes, { level: 9 }).length / 1048576).toFixed(2)} MB, brotli ${(zlib.brotliCompressSync(bytes).length / 1048576).toFixed(2)} MB`);
}
// facades keep their UV seams (atlas textures); that costs 1% more vertices
const WELD_CITY = process.env.CITY_MODE === 'colour-seams' ? 'colour' : 'row-colour', WELD_FACADE = 'row-uv';
const COLOR_WEIGHT = Number(process.env.COLOR_WEIGHT ?? 1);
/** The batch's triangles with each vertex replaced by the first one sharing its position and surface row (and UV for
 * 'row-uv'), and the groups (CSR: members of each first vertex) for resplit. */
function weld(b, mode) {
  const src = b.index instanceof Uint32Array ? b.index : Uint32Array.from(b.index);
  const bits = new Uint32Array(b.position.buffer, b.position.byteOffset, b.vertices * 3), uv = new Uint32Array(b.uv.buffer, b.uv.byteOffset, b.vertices * 2);
  const first = new Map(), rep = new Uint32Array(b.vertices), size = new Uint32Array(b.vertices + 1);
  for (let v = 0; v < b.vertices; v++) {
    let key = `${bits[v * 3]},${bits[v * 3 + 1]},${bits[v * 3 + 2]}` + (mode === 'colour' ? '' : `,${b.row[v]}`);
    if (mode === 'row-uv') key += `,${uv[v * 2]},${uv[v * 2 + 1]}`;
    if (mode === 'row-colour' || mode === 'colour') key += `,${b.silhouette[v * 3]},${b.silhouette[v * 3 + 1]},${b.silhouette[v * 3 + 2]}`;
    const r = first.get(key); if (r === undefined) { first.set(key, v); rep[v] = v; } else rep[v] = r;
    size[rep[v] + 1]++;
  }
  for (let v = 0; v < b.vertices; v++) size[v + 1] += size[v];
  const start = size.slice(), members = new Uint32Array(b.vertices), fill = size.slice(0, b.vertices);
  for (let v = 0; v < b.vertices; v++) members[fill[rep[v]]++] = v;
  return { index: Uint32Array.from(src, (i) => rep[i]), start, members };
}
/** Each corner of each simplified triangle (welded vertices) becomes the member of its group whose normal is closest to
 * the triangle's face normal. */
function resplit(indices, b, { start, members }) {
  const P = b.position, N = b.normal, scale = N instanceof Int8Array ? 1 / 127 : 1, out = new Uint32Array(indices.length);
  for (let t = 0; t < indices.length; t += 3) {
    const a = indices[t], c1 = indices[t + 1], c2 = indices[t + 2];
    const ux = P[c1 * 3] - P[a * 3], uy = P[c1 * 3 + 1] - P[a * 3 + 1], uz = P[c1 * 3 + 2] - P[a * 3 + 2];
    const vx = P[c2 * 3] - P[a * 3], vy = P[c2 * 3 + 1] - P[a * 3 + 1], vz = P[c2 * 3 + 2] - P[a * 3 + 2];
    const fx = uy * vz - uz * vy, fy = uz * vx - ux * vz, fz = ux * vy - uy * vx;
    for (let k = 0; k < 3; k++) {
      const r = indices[t + k]; let best = r, score = -Infinity;
      for (let m = start[r]; m < start[r + 1]; m++) { const v = members[m], d = (N[v * 3] * fx + N[v * 3 + 1] * fy + N[v * 3 + 2] * fz) * scale; if (d > score) { score = d; best = v; } }
      out[t + k] = best;
    }
  }
  return out;
}
/** Facade LOD: CityBatches.facadeFromBatch's clustering, exactly (0.7 m cells; a vertex joins a cluster whose first member
 * has its surface row, colour, a normal within 0.98, its plane within 5 mm and its UV within 0.25), but each cluster is
 * drawn with its member closest to the cluster's average instead of a new averaged vertex: the LOD stays a list of the
 * batch's own vertices (UVs move with their positions, so textures stay aligned). Degenerate triangles drop. */
function facadeLod(b, spacing) {
  const P = b.position, N = b.normal, U = b.uv, C = b.color, R = b.row, n = b.vertices;
  const ns = N instanceof Int8Array ? (x) => Math.max(x / 127, -1) : (x) => x;
  const heads = new Map(), next = new Int32Array(n), first = new Uint32Array(n), remap = new Uint32Array(n), sums = new Float64Array(n * 3), counts = new Uint32Array(n);
  let clusters = 0;
  for (let i = 0; i < n; i++) {
    const x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2], nx = ns(N[i * 3]), ny = ns(N[i * 3 + 1]), nz = ns(N[i * 3 + 2]), u = U[i * 2], v = U[i * 2 + 1], row = R[i], ci = i * 4;
    const key = ((Math.round(x / spacing) + 16384) * 32768 + (Math.round(y / spacing) + 16384)) * 32768 + (Math.round(z / spacing) + 16384);
    const head = heads.get(key) ?? -1; let id = head;
    for (; id !== -1; id = next[id]) {
      const r = first[id], rc = r * 4;
      if (R[r] === row && C[ci] === C[rc] && C[ci + 1] === C[rc + 1] && C[ci + 2] === C[rc + 2] &&
        nx * ns(N[r * 3]) + ny * ns(N[r * 3 + 1]) + nz * ns(N[r * 3 + 2]) > 0.98 &&
        Math.abs((x - P[r * 3]) * nx + (y - P[r * 3 + 1]) * ny + (z - P[r * 3 + 2]) * nz) < 0.005 &&
        Math.abs(u - U[r * 2]) < 0.25 && Math.abs(v - U[r * 2 + 1]) < 0.25) break;
    }
    if (id === -1) { id = clusters++; next[id] = head; first[id] = i; heads.set(key, id); }
    remap[i] = id; counts[id]++; sums[id * 3] += x; sums[id * 3 + 1] += y; sums[id * 3 + 2] += z;
  }
  // each cluster's member closest to its average
  const best = new Float64Array(clusters).fill(Infinity), rep = new Uint32Array(clusters);
  for (let i = 0; i < n; i++) {
    const id = remap[i], k = counts[id], d = (P[i * 3] - sums[id * 3] / k) ** 2 + (P[i * 3 + 1] - sums[id * 3 + 1] / k) ** 2 + (P[i * 3 + 2] - sums[id * 3 + 2] / k) ** 2;
    if (d < best[id]) { best[id] = d; rep[id] = i; }
  }
  const I = b.index, out = new Uint32Array(I.length); let t = 0;
  for (let i = 0; i < I.length; i += 3) {
    const a = remap[I[i]], c = remap[I[i + 1]], d = remap[I[i + 2]];
    if (a === c || c === d || a === d) continue;
    out[t++] = rep[a]; out[t++] = rep[c]; out[t++] = rep[d];
  }
  return out.slice(0, t);
}
/** One 1080p pixel (70-degree vertical field of view) at the distance the block's LOD can appear from (CityLod.lodLevel). */
const lodError = (block) => 0.88 * block.near * (2 * Math.tan((35 * Math.PI) / 180)) / 1080;
const INPUT_DIRS = ['build/geographic-strip', 'build/strip-landmarks', 'build/resort-blocks', 'build/highrises', 'build/sphere', 'build/south-strip'];
const INPUT_CODE = ['src/work/CityBatches.ts', 'src/work/CityLod.ts', 'src/work/CityBake.ts', 'src/work/CityBakeLoad.ts', 'src/work/AttributeReader.ts', 'src/work/CityAtlas.ts',
  'src/work/MaterialFixes.ts', 'src/work/StripLandmarks.ts', 'src/work/ResortBlocks.ts', 'src/work/HighriseCity.ts', 'src/work/GeographicCity.ts',
  'src/work/GeographicStreetMaterials.ts', 'src/work/PbrDetailSets.ts', 'src/work/Game.ts', 'tools/bake/bake-city.mjs',
  // the planting replaces the GLBs' old tree crowns, so where it goes counts; the tree models do not (instanced, never batched)
  'public/foliage/bellagio-placements.bin'];
const MANIFEST_FILE = path.join(ROOT, 'build/optimized/manifest.json');
const INPUTS_FILE = path.join(ROOT, 'build/baked/city-lod.inputs.json');
/** One SHA-256 over every input of the bake: exterior GLBs (not interiors, which CityLod never sees) and their optimized
 * copies, the record files (not collision), the code above, and the optimized-manifest entries for those folders (which
 * copy loads; entries for anything else, such as the foliage, are not inputs). */
export function inputsHash() {
  const files = [];
  const walk = (dir) => {
    if (!fs.existsSync(path.join(ROOT, dir))) return;
    for (const e of fs.readdirSync(path.join(ROOT, dir), { withFileTypes: true })) {
      if (e.name.startsWith('.')) continue;
      const rel = dir + '/' + e.name;
      if (e.isDirectory()) walk(rel);
      else if ((e.name.endsWith('.glb') && !/-interior\.glb$/.test(e.name)) || (e.name.endsWith('.bin') && !/collision/.test(e.name))) files.push(rel);
    }
  };
  for (const dir of INPUT_DIRS) { walk(dir); walk('build/optimized/' + dir); }
  for (const f of INPUT_CODE) if (fs.existsSync(path.join(ROOT, f))) files.push(f);
  files.sort();
  const hash = crypto.createHash('sha256');
  for (const f of files) { hash.update(f + '\0'); hash.update(fs.readFileSync(path.join(ROOT, f))); }
  const manifest = fs.existsSync(MANIFEST_FILE) ? JSON.parse(fs.readFileSync(MANIFEST_FILE, 'utf8')).files ?? {} : {};
  const entries = Object.keys(manifest).filter((key) => INPUT_DIRS.some((dir) => key.startsWith(dir + '/'))).sort().map((key) => [key, manifest[key]]);
  hash.update('manifest\0'); hash.update(JSON.stringify(entries));
  return { hash: hash.digest('hex'), files: files.length + entries.length };
}
/** Whether build/baked/city-lod.bin was made from the current inputs. */
export function bakeFresh() {
  if (!fs.existsSync(LOD_FILE) || !fs.existsSync(INPUTS_FILE)) return { fresh: false, reason: 'no bake' };
  const recorded = JSON.parse(fs.readFileSync(INPUTS_FILE, 'utf8')), now = inputsHash();
  return now.hash === recorded.hash ? { fresh: true } : { fresh: false, reason: 'inputs changed since ' + recorded.at, now };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const step = process.argv[2] ?? 'build';
  if (step === 'capture') await capture();
  else if (step === 'lod') await lod();
  else if (step === 'check') { const s = bakeFresh(); console.log(s.fresh ? 'city bake is up to date' : `city bake is stale (${s.reason}): node tools/bake/bake-city.mjs`); process.exit(s.fresh ? 0 : 1); }
  else if (step === 'build') {
    const before = inputsHash(), s = bakeFresh();
    if (s.fresh) console.log(`city bake is up to date (${before.files} inputs)`);
    else {
      console.log(`baking the city (${s.reason}; ${before.files} inputs)`);
      await capture(); await lod();
      const after = inputsHash();
      if (after.hash !== before.hash) { console.error('inputs changed while baking; run again'); process.exit(1); }
      fs.writeFileSync(INPUTS_FILE, JSON.stringify({ hash: after.hash, files: after.files, at: new Date().toISOString() }, null, 1) + '\n');
    }
  } else { console.error('usage: node tools/bake/bake-city.mjs [build|check|capture|lod]'); process.exit(2); }
}
