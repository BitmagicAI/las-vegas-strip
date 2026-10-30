#!/usr/bin/env node
/*
 * pack-data.mjs: the runtime data files as compact binary (2026-10-25: the owner ruled out JSON
 * parsing and JS arrays at runtime, and asked for formats that are optimal from the start: no redundant data, 16-bit
 * integers where 32 bits are too many, 8-16-bit values instead of 32-bit floats where the result is about the same).
 *
 * The pipelines keep writing JSON into build/ (and public/foliage/); this writes a .bin beside each file the game loads,
 * and the game reads only the .bin (src/work/CollisionPack.ts, src/work/Plants.ts). Formats, all little-endian:
 *
 * Collision meshes (VCOL): every *-collision.json and the mapped city's city-colliders.json.
 *   u32 magic 'VCOL', u16 version 1, u16 flags (1: meshes carry a cell x, z), u32 mesh count, then columns:
 *   [i16 cell x, i16 cell z per mesh], i32 x 3 origin per mesh, u8 grid exponent per mesh, u32 vertex count per mesh,
 *   u32 triangle count per mesh, then three meshopt-coded sections (u32 byte length + bytes each, 4-byte aligned):
 *   positions (u16 x, y, z and a zero pad: the codec needs a 4-byte stride; the pad codes to nothing), indices of the
 *   meshes with at most 65,536 vertices as u16, indices of the larger meshes as u32. Offsets are prefix sums of the counts.
 *   A vertex is (origin + q) * 2^-e metres. Each mesh takes the finest grid from 1/256 m (error at most 2 mm) that fits
 *   its extent in 16 bits (the 28 widest of 1,770 meshes: 1/128 or 1/64 m, error at most 8 mm); physics never notices.
 *   Vertices are welded on the grid (the city's were 19% duplicates), degenerate and unused ones dropped, and the mesh
 *   reordered for the codec. The JSON's per-cell `center` (derived from the cell) is not stored.
 *
 * Plants (VPLT): public/foliage/bellagio-placements.json.
 *   u32 magic 'VPLT', u16 version 1, u16 0, then two lists (trees, grass): u32 count, f32 x 3 origin, f32 x 3 step,
 *   f32 scale min, f32 scale step, then per plant u16 x, u16 y, u16 z, u8 yaw (1/256 turn), u8 scale; meshopt-coded as
 *   8-byte attributes. Positions on a 16-bit grid over the list's bounds (lawn: ~5 mm), yaw within 0.7 degrees, scale
 *   within 0.1%: the picture is the same. Trees keep the yaw and scale their seeds gave them.
 *
 * Road speed map (VSPD): build/geographic-strip/speed-map.bin from road-network.json and the Bellagio's
 *   south-arrival-report.json (whose roads replace the network's by id, as service roads): only what the jeep's speed
 *   assist reads (src/work/DrivingSpeedAssist.ts, SpeedMapFile.ts): per road its point count (u16), reach (u16, cm;
 *   widths are whole decimetres) and comfort target (u8); the 40 m cells' keys, segment counts and segments as varint deltas; points as i32 cm x 3,
 *   meshopt-coded. Names, OSM ids and nodes, one-way, access and bridge flags are not stored.
 *
 * Records (VDAT): the remaining metadata the game reads (venue lists, the Sphere, the coaster's route, the PBR sets, hotel
 *   module levels, bridge concourses), read by src/work/PackedRecords.ts into plain objects whose number lists are typed
 *   arrays. u32 magic 'VDAT', u16 version 1, u16 0, u32 skeleton length, the skeleton, then 8-byte aligned number data.
 *   The skeleton: a varint count of strings (keys and values, each stored once) as varint length + UTF-8, then the root
 *   value as tagged items: 0 null, 1 false, 2 true, 3 integer (zigzag varint), 4 f32, 5 f64, 6 string (varint index),
 *   7 array (varint length, items), 8 object (varint size, varint key index + item each), 9 numbers (u8 kind, varint
 *   stride, varint count, varint data offset; quantized kinds then f64 step and one f64 offset per component),
 *   10 table (varint rows, varint columns, then varint key index + a numbers item per column).
 *   Number kinds: 1 u8, 2 i8, 3 u16, 4 i16, 5 u32, 6 i32, 7 f32, 8 f64, 9 u16 grid, 10 u32 grid (offset + value * step).
 *   Integers take the narrowest kind. Coordinates take a 1 mm grid and directions a 1e-4 grid (PRECISION, by the key the
 *   list belongs to), on 16 bits whenever the list's range allows; other floats are f32 unless that loses more than a
 *   millionth. Lists of equal-length number lists are flattened (stride), and long lists of records with only numeric
 *   fields become columns.
 *
 *   node tools/optimize/pack-data.mjs           # pack what is missing or older than its JSON
 *   node tools/optimize/pack-data.mjs --force   # pack everything
 *   node tools/optimize/pack-data.mjs --check   # exit 1 when a .bin is missing or stale
 *   node tools/optimize/pack-data.mjs <file.json ...>
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { buildSpeedMap } from '../../src/work/DrivingSpeedAssist.ts';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const BM_TOOLS = process.env.BM_TOOLS ?? path.join(ROOT, 'tools/optimize/bm-tools');
let encoder = null;
async function meshopt() {
  if (!encoder) {
    ({ MeshoptEncoder: encoder } = await import(pathToFileURL(path.join(BM_TOOLS, 'gltf/node_modules/meshoptimizer/index.js')).href));
    await encoder.ready;
  }
  return encoder;
}

/** A growable little-endian byte writer. */
class Writer {
  constructor() { this.bytes = new Uint8Array(1 << 16); this.length = 0; }
  reserve(n) { if (this.length + n > this.bytes.length) { let size = this.bytes.length; while (size < this.length + n) size *= 2; const b = new Uint8Array(size); b.set(this.bytes.subarray(0, this.length)); this.bytes = b; } }
  view(n) { this.reserve(n); const v = new DataView(this.bytes.buffer, this.length, n); this.length += n; return v; }
  u8(x) { this.view(1).setUint8(0, x); }
  u16(x) { this.view(2).setUint16(0, x, true); }
  u32(x) { this.view(4).setUint32(0, x, true); }
  f32(x) { this.view(4).setFloat32(0, x, true); }
  raw(bytes) { this.reserve(bytes.length); this.bytes.set(bytes, this.length); this.length += bytes.length; }
  align() { while (this.length & 3) this.u8(0); }
  /** a typed array's bytes, then 4-byte alignment */
  array(a) { this.raw(new Uint8Array(a.buffer, a.byteOffset, a.byteLength)); this.align(); }
  section(bytes) { this.u32(bytes.length); this.raw(bytes); this.align(); }
  varint(x) { do { let b = x % 128; x = Math.floor(x / 128); if (x) b |= 128; this.u8(b); } while (x); }
  done() { return this.bytes.slice(0, this.length); }
}

const STEP_FINEST = 8, STEP_COARSEST = 4;

/** Quantize, weld, clean and reorder one mesh. */
function packMesh(enc, vertices, indices) {
  const n = vertices.length / 3;
  const min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
  for (let i = 0; i < n; i++) for (let a = 0; a < 3; a++) { const x = vertices[i * 3 + a]; if (x < min[a]) min[a] = x; if (x > max[a]) max[a] = x; }
  if (!n) return { origin: [0, 0, 0], e: STEP_FINEST, q: new Uint16Array(0), tris: new Uint32Array(0), count: 0 };
  let e = STEP_FINEST;
  // the origin is floored and the values rounded, so allow two grid steps of slack
  while (e > STEP_COARSEST && Math.max(max[0] - min[0], max[1] - min[1], max[2] - min[2]) * 2 ** e > 65533) e--;
  if (Math.max(max[0] - min[0], max[1] - min[1], max[2] - min[2]) * 2 ** e > 65533) throw new Error(`mesh too wide for a 16-bit grid at 2^-${e} m`);
  const s = 2 ** e, origin = min.map((m) => Math.floor(m * s));
  const weld = new Map(), remap = new Uint32Array(n), welded = [];
  for (let i = 0; i < n; i++) {
    const x = Math.round(vertices[i * 3] * s) - origin[0], y = Math.round(vertices[i * 3 + 1] * s) - origin[1], z = Math.round(vertices[i * 3 + 2] * s) - origin[2];
    const key = (x * 65536 + y) * 65536 + z;
    let id = weld.get(key);
    if (id === undefined) { id = weld.size; weld.set(key, id); welded.push(x, y, z); }
    remap[i] = id;
  }
  const kept = [];
  for (let t = 0; t + 2 < indices.length; t += 3) {
    const a = remap[indices[t]], b = remap[indices[t + 1]], c = remap[indices[t + 2]];
    if (a !== b && b !== c && a !== c) kept.push(a, b, c);
  }
  const tris = new Uint32Array(kept);
  if (!tris.length) return { origin, e, q: new Uint16Array(0), tris, count: 0 };
  // triangles reordered for the index codec and renumbered in place; vertices in order of first use (unused ones drop)
  const [order, count] = enc.reorderMesh(tris, true, true);
  const q = new Uint16Array(count * 4);
  for (let i = 0; i < order.length; i++) { const j = order[i]; if (j === 0xffffffff) continue; q[j * 4] = welded[i * 3]; q[j * 4 + 1] = welded[i * 3 + 1]; q[j * 4 + 2] = welded[i * 3 + 2]; }
  return { origin, e, q, tris, count };
}

/** meshes: [{vertices, indices, cell?: [x, z]}] -> VCOL bytes */
export async function encodeCollision(meshes, { cells = false } = {}) {
  const enc = await meshopt();
  const packed = meshes.map((m) => packMesh(enc, m.vertices, m.indices));
  const w = new Writer();
  w.u32(0x4c4f4356); w.u16(1); w.u16(cells ? 1 : 0); w.u32(meshes.length);
  if (cells) {
    w.array(Int16Array.from(meshes, (m) => m.cell[0]));
    w.array(Int16Array.from(meshes, (m) => m.cell[1]));
  }
  w.array(Int32Array.from(packed.flatMap((p) => p.origin)));
  w.array(Uint8Array.from(packed, (p) => p.e));
  w.array(Uint32Array.from(packed, (p) => p.count));
  w.array(Uint32Array.from(packed, (p) => p.tris.length / 3));
  const total = packed.reduce((s, p) => s + p.count, 0);
  const positions = new Uint16Array(total * 4);
  let at = 0;
  for (const p of packed) { positions.set(p.q, at); at += p.q.length; }
  w.section(total ? enc.encodeVertexBufferLevel(new Uint8Array(positions.buffer), total, 8, 2, 0) : new Uint8Array(0));
  for (const wide of [false, true]) {
    const group = packed.filter((p) => (p.count > 65536) === wide);
    const length = group.reduce((s, p) => s + p.tris.length, 0);
    const all = wide ? new Uint32Array(length) : new Uint16Array(length);
    let k = 0;
    for (const p of group) { all.set(p.tris, k); k += p.tris.length; }
    w.section(length ? enc.encodeIndexBuffer(new Uint8Array(all.buffer), length, wide ? 4 : 2) : new Uint8Array(0));
  }
  return w.done();
}

/** five numbers per plant (x, y, z, yaw, scale) -> one VPLT list */
async function writePlants(w, enc, plants) {
  const n = plants.length / 5;
  const min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
  let smin = Infinity, smax = -Infinity;
  for (let i = 0; i < n; i++) {
    for (let a = 0; a < 3; a++) { const x = plants[i * 5 + a]; if (x < min[a]) min[a] = x; if (x > max[a]) max[a] = x; }
    const s = plants[i * 5 + 4]; if (s < smin) smin = s; if (s > smax) smax = s;
  }
  if (!n) { min.fill(0); max.fill(0); smin = smax = 1; }
  const step = min.map((m, a) => Math.max(max[a] - m, 1e-6) / 65535), sstep = Math.max(smax - smin, 1e-6) / 255;
  w.u32(n); for (const v of min) w.f32(v); for (const v of step) w.f32(v); w.f32(smin); w.f32(sstep);
  // round the origin and steps through f32 first, as the game reads them
  const f = new Float32Array([...min, ...step, smin, sstep]);
  const body = new Uint8Array(n * 8), dv = new DataView(body.buffer);
  for (let i = 0; i < n; i++) {
    for (let a = 0; a < 3; a++) dv.setUint16(i * 8 + a * 2, Math.max(0, Math.min(65535, Math.round((plants[i * 5 + a] - f[a]) / f[3 + a]))), true);
    const turn = ((plants[i * 5 + 3] / (2 * Math.PI)) % 1 + 1) % 1;
    dv.setUint8(i * 8 + 6, Math.round(turn * 256) & 255);
    dv.setUint8(i * 8 + 7, Math.max(0, Math.min(255, Math.round((plants[i * 5 + 4] - f[6]) / f[7]))));
  }
  w.section(n ? enc.encodeVertexBufferLevel(body, n, 8, 2, 0) : new Uint8Array(0));
}

export async function encodePlants(json) {
  const enc = await meshopt();
  const trees = json.trees.flatMap((t) => [...t.position, (t.seed % 6283) / 1000, 0.88 + (t.seed % 23) / 100]);
  const grass = json.grass.flat();
  const w = new Writer();
  w.u32(0x544c5056); w.u16(1); w.u16(0);
  await writePlants(w, enc, trees);
  await writePlants(w, enc, grass);
  return w.done();
}

export async function encodeSpeedMap(roads) {
  const enc = await meshopt(), m = buildSpeedMap(roads), R = m.limit.length, P = m.points.length / 3, C = m.cellKeys.length, S = m.segments.length;
  const w = new Writer();
  w.u32(0x44505356); w.u16(1); w.u16(0); w.u32(R); w.u32(P); w.u32(C); w.u32(S);
  w.array(Uint16Array.from({ length: R }, (_, r) => m.roadStart[r + 1] - m.roadStart[r]));
  w.array(m.reach); w.raw(m.limit);
  for (let c = 0, k = 0; c < C; c++) { w.varint(m.cellKeys[c] - k); k = m.cellKeys[c]; }
  for (let c = 0; c < C; c++) w.varint(m.cellStart[c + 1] - m.cellStart[c]);
  for (let c = 0; c < C; c++) for (let s = m.cellStart[c], v = 0; s < m.cellStart[c + 1]; s++) { w.varint(m.segments[s] - v); v = m.segments[s]; }
  w.align();
  w.section(P ? enc.encodeVertexBufferLevel(new Uint8Array(m.points.buffer), P, 12, 2, 0) : new Uint8Array(0));
  return w.done();
}

const PRECISION = { p: 1e-3, position: 1e-3, points: 1e-3, center: 1e-3, eye: 1e-3, target: 1e-3, origin: 1e-3, bounds: 1e-3,
  accessPoints: 1e-3, seats: 1e-3, lights: 1e-3, vertices: 1e-3, size: 1e-3, s: 1e-3, station: 1e-3, exit: 1e-3,
  entrance: 1e-3, access: 1e-3, lift: 1e-3, liftButton: 1e-3, right: 1e-4, up: 1e-4, direction: 1e-4, uv: 1e-4 };
const isNumber = (x) => typeof x === 'number';
const numericList = (x) => Array.isArray(x) && x.length > 0 && x.every(isNumber);

/** any JSON value -> VDAT bytes */
export function encodeRecords(root) {
  const strings = new Map(), skeleton = new Writer(), blob = new Writer();
  const str = (s) => { let i = strings.get(s); if (i === undefined) { i = strings.size; strings.set(s, i); } return i; };
  const zigzag = (n) => (n < 0 ? -2 * n - 1 : 2 * n);
  function numbers(values, stride, key) {
    const count = values.length, ints = values.every((v) => Number.isInteger(v));
    let kind, data, step = 0, offsets = null;
    if (ints) {
      const lo = Math.min(...values.slice(0, 1)), min = values.reduce((a, v) => Math.min(a, v), lo), max = values.reduce((a, v) => Math.max(a, v), lo);
      [kind, data] = min >= 0 ? (max < 256 ? [1, Uint8Array] : max < 65536 ? [3, Uint16Array] : max < 2 ** 32 ? [5, Uint32Array] : [8, Float64Array])
        : (min >= -128 && max < 128 ? [2, Int8Array] : min >= -32768 && max < 32768 ? [4, Int16Array] : min >= -(2 ** 31) && max < 2 ** 31 ? [6, Int32Array] : [8, Float64Array]);
      data = data.from(values);
    } else if (PRECISION[key]) {
      step = PRECISION[key]; offsets = new Float64Array(stride).fill(Infinity);
      for (let i = 0; i < count; i++) offsets[i % stride] = Math.min(offsets[i % stride], values[i]);
      for (let c = 0; c < stride; c++) offsets[c] = Math.floor(offsets[c] / step) * step;
      const q = values.map((v, i) => Math.round((v - offsets[i % stride]) / step)), top = q.reduce((a, v) => Math.max(a, v), 0);
      if (top < 65536) [kind, data] = [9, Uint16Array.from(q)]; else if (top < 2 ** 32) [kind, data] = [10, Uint32Array.from(q)];
      else { kind = 8; data = Float64Array.from(values); step = 0; offsets = null; }
    } else {
      const f = Float32Array.from(values);
      [kind, data] = values.every((v, i) => Math.abs(f[i] - v) <= 1e-6 * Math.max(1, Math.abs(v))) ? [7, f] : [8, Float64Array.from(values)];
    }
    while (blob.length & 7) blob.u8(0);
    const at = blob.length; blob.raw(new Uint8Array(data.buffer, data.byteOffset, data.byteLength));
    skeleton.u8(9); skeleton.u8(kind); skeleton.varint(stride); skeleton.varint(count); skeleton.varint(at);
    if (kind >= 9) { skeleton.view(8).setFloat64(0, step, true); for (const o of offsets) skeleton.view(8).setFloat64(0, o, true); }
  }
  /** lists of equal-length number lists, flattened */
  const matrix = (v) => v.length > 0 && v.every((x) => numericList(x) && x.length === v[0].length) ? v[0].length : 0;
  function table(v) {
    if (v.length < 32 || !v.every((x) => x && typeof x === 'object' && !Array.isArray(x))) return null;
    const keys = Object.keys(v[0]);
    if (!v.every((x) => Object.keys(x).length === keys.length && keys.every((k) => k in x))) return null;
    const columns = [];
    for (const k of keys) {
      const first = v[0][k];
      if (isNumber(first) && v.every((x) => isNumber(x[k]))) columns.push([k, 1, v.map((x) => x[k])]);
      else if (typeof first === 'boolean' && v.every((x) => typeof x[k] === 'boolean')) columns.push([k, 1, v.map((x) => (x[k] ? 1 : 0))]);
      else if (numericList(first) && v.every((x) => numericList(x[k]) && x[k].length === first.length)) columns.push([k, first.length, v.flatMap((x) => x[k])]);
      else return null;
    }
    return columns;
  }
  function value(v, key) {
    if (v === null || v === undefined) skeleton.u8(0);
    else if (v === false) skeleton.u8(1);
    else if (v === true) skeleton.u8(2);
    else if (isNumber(v)) {
      if (Number.isSafeInteger(v)) { skeleton.u8(3); skeleton.varint(zigzag(v)); }
      else if (Math.abs(Math.fround(v) - v) <= 1e-6 * Math.max(1, Math.abs(v))) { skeleton.u8(4); skeleton.f32(v); }
      else { skeleton.u8(5); skeleton.view(8).setFloat64(0, v, true); }
    } else if (typeof v === 'string') { skeleton.u8(6); skeleton.varint(str(v)); }
    else if (Array.isArray(v)) {
      const stride = matrix(v), columns = stride ? null : table(v);
      if (numericList(v)) numbers(v, 1, key);
      else if (stride) numbers(v.flat(), stride, key);
      else if (columns) {
        skeleton.u8(10); skeleton.varint(v.length); skeleton.varint(columns.length);
        for (const [k, s, values] of columns) { skeleton.varint(str(k)); numbers(values, s, k); }
      } else { skeleton.u8(7); skeleton.varint(v.length); for (const x of v) value(x, key); }
    } else {
      const entries = Object.entries(v);
      skeleton.u8(8); skeleton.varint(entries.length);
      for (const [k, x] of entries) { skeleton.varint(str(k)); value(x, k); }
    }
  }
  value(root, '');
  const head = new Writer(), utf8 = new TextEncoder();
  head.varint(strings.size);
  for (const s of strings.keys()) { const b = utf8.encode(s); head.varint(b.length); head.raw(b); }
  const out = new Writer();
  out.u32(0x54414456); out.u16(1); out.u16(0); out.u32(head.length + skeleton.length);
  out.raw(head.done()); out.raw(skeleton.done());
  while (out.length & 7) out.u8(0);
  out.raw(blob.done());
  return out.done();
}

const ARRIVAL = 'build/resort-blocks/bellagio/south-arrival-report.json';

/** What a JSON file becomes, or null when the game never loads it. */
function kindOf(rel) {
  if (rel === 'build/geographic-strip/road-network.json') return 'speed-map';
  if (/^build\/(strip-landmarks|resort-blocks\/[^/]+)\/venues\.json$/.test(rel)) return 'records';
  if (/^build\/(sphere\/(sphere|media)|south-strip\/route|pbr\/strips\/sets)\.json$/.test(rel)) return 'records';
  if (/^build\/hotels\/[^/]+\.mesh-level\.json$/.test(rel)) return 'records';
  if (/^build\/geographic-strip\/access\/[^/]+\.json$/.test(rel) && !rel.endsWith('/audit.json')) return 'records';
  if (rel === 'public/foliage/bellagio-placements.json') return 'plants';
  if (rel === 'build/geographic-strip/city-colliders.json') return 'city-collision';
  if (/^build\/(strip-landmarks|resort-blocks\/[^/]+|highrises|sphere|south-strip)\/[^/]*collision\.json$/.test(rel)) return 'collision';
  return null;
}

async function pack(rel) {
  const kind = kindOf(rel), json = JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));
  if (kind === 'plants') return encodePlants(json);
  if (kind === 'records') return encodeRecords(json);
  if (kind === 'speed-map') {
    const arrival = JSON.parse(fs.readFileSync(path.join(ROOT, ARRIVAL), 'utf8'));
    const replacements = new Map(arrival.roads.map((r) => [r.id, { ...r, highway: 'service' }]));
    return encodeSpeedMap(json.roads.map((r) => replacements.get(r.id) ?? r));
  }
  if (kind === 'city-collision') return encodeCollision(json.map((c) => ({ vertices: c.vertices, indices: c.indices, cell: c.id.split(',').map(Number) })), { cells: true });
  if (!Array.isArray(json.vertices) || !Array.isArray(json.indices)) return null; // an audit report, not a mesh
  return encodeCollision([{ vertices: json.vertices, indices: json.indices }]);
}

function candidates() {
  const out = [];
  const walk = (dir) => {
    for (const e of fs.readdirSync(path.join(ROOT, dir), { withFileTypes: true })) {
      const rel = dir + '/' + e.name;
      if (e.name.startsWith('.')) continue; // backups such as resort-blocks/.bellagio-before-remodel-2026-10-08
      if (e.isDirectory()) walk(rel);
      else if (e.name.endsWith('.json') && kindOf(rel)) out.push(rel);
    }
  };
  for (const dir of ['build/geographic-strip', 'build/strip-landmarks', 'build/resort-blocks', 'build/highrises', 'build/sphere', 'build/south-strip', 'build/pbr/strips', 'build/hotels'])
    if (fs.existsSync(path.join(ROOT, dir))) walk(dir);
  out.push('public/foliage/bellagio-placements.json');
  return out.sort();
}

export const binPath = (rel) => kindOf(rel) === 'speed-map' ? 'build/geographic-strip/speed-map.bin' : rel.replace(/\.json$/, '.bin');
/** every JSON a packed file is made from */
const inputs = (rel) => kindOf(rel) === 'speed-map' ? [rel, ARRIVAL] : [rel];

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2), force = args.includes('--force'), check = args.includes('--check');
  const named = args.filter((a) => !a.startsWith('--')).map((a) => path.relative(ROOT, path.resolve(a)));
  const files = named.length ? named : candidates();
  let packed = 0, stale = 0, before = 0, after = 0;
  for (const rel of files) {
    if(kindOf(rel)==='city-collision'&&!args.includes('--combined-city')){
      const {packCityCollision}=await import('../city-cells/pack-collision.mjs');
      const input=path.join(ROOT,rel),output=path.join(ROOT,'build/geographic-strip/collision-cells');
      const current=await packCityCollision(input,output,{check:true,encodeCollision});
      if(check){if(!current.fresh){stale++;console.log('stale or missing: geographic collision cells');}continue;}
      if(current.fresh&&!force)continue;
      const result=await packCityCollision(input,output,{encodeCollision});
      packed+=result.cells;before+=fs.statSync(input).size;after+=result.bytes;
      console.log(`${rel}: ${result.records} records in ${result.cells} collision cells`);
      continue;
    }
    const src = path.join(ROOT, rel), out = path.join(ROOT, binPath(rel));
    const fresh = fs.existsSync(out) && inputs(rel).every((i) => fs.statSync(out).mtimeMs >= fs.statSync(path.join(ROOT, i)).mtimeMs);
    if (check) { if (!fresh) { stale++; console.log(`stale or missing: ${binPath(rel)}`); } continue; }
    if (fresh && !force) continue;
    const bytes = await pack(rel);
    if (!bytes) continue;
    fs.writeFileSync(out, bytes);
    packed++; before += fs.statSync(src).size; after += bytes.length;
    if (fs.statSync(src).size > 4 << 20) console.log(`${rel}: ${(fs.statSync(src).size / 1048576).toFixed(1)} MB -> ${(bytes.length / 1048576).toFixed(2)} MB`);
  }
  if (check) { console.log(stale ? `${stale} data files need: node tools/optimize/pack-data.mjs` : 'data files packed'); process.exit(stale ? 1 : 0); }
  console.log(`packed ${packed} files: ${(before / 1048576).toFixed(1)} MB of JSON -> ${(after / 1048576).toFixed(1)} MB`);
}
