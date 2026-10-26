// The packed runtime data (tools/optimize/pack-data.mjs, read by src/work/CollisionPack.ts and src/work/Plants.ts) must
// carry the same collision and planting as the JSON the pipelines write: every vertex within half a grid step of its
// source, every source vertex still present, triangle counts and surface areas kept (welded duplicates and triangles that
// collapse on the grid are the only things dropped), plants within their stated precision. Runs against the .bin files
// on disk, so it also fails when they are stale: node tools/optimize/pack-data.mjs.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
import { encodeCollision } from '../tools/optimize/pack-data.mjs';

fs.mkdirSync('build', { recursive: true });
fs.writeFileSync('build/runtime-assets-test-stub.mjs', 'export const runtimeUrl=(u)=>u;export const runtimeOnCdn=false;\n');
const transpile = (from, to) => fs.writeFileSync(to, ts.transpileModule(fs.readFileSync(from, 'utf8'), { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 } }).outputText
  .replace("'./RuntimeAssets.js'", "'./runtime-assets-test-stub.mjs'"));
transpile('src/work/CollisionPack.ts', 'build/collision-pack-test-module.mjs');
transpile('src/work/Plants.ts', 'build/plants-test-module.mjs');
const { CollisionPack } = await import('../build/collision-pack-test-module.mjs?' + Date.now());
const { PlantList } = await import('../build/plants-test-module.mjs?' + Date.now());
void PlantList;

const bin = (f) => { const b = fs.readFileSync(f); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength); };
const perimeter = (V, I) => { let s = 0; for (let t = 0; t < I.length; t += 3) { const a = I[t] * 3, b = I[t + 1] * 3, c = I[t + 2] * 3;
  s += Math.hypot(V[b] - V[a], V[b + 1] - V[a + 1], V[b + 2] - V[a + 2]) + Math.hypot(V[c] - V[b], V[c + 1] - V[b + 1], V[c + 2] - V[b + 2]) + Math.hypot(V[a] - V[c], V[a + 1] - V[c + 1], V[a + 2] - V[c + 2]); } return s; };
const area = (V, I) => { let s = 0; for (let t = 0; t < I.length; t += 3) { const a = I[t] * 3, b = I[t + 1] * 3, c = I[t + 2] * 3;
  const ux = V[b] - V[a], uy = V[b + 1] - V[a + 1], uz = V[b + 2] - V[a + 2], vx = V[c] - V[a], vy = V[c + 1] - V[a + 1], vz = V[c + 2] - V[a + 2];
  s += Math.hypot(uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx) / 2; } return s; };

/** Each point of `from` has a point of `to` within `tol` (hash grid of `to`). */
function covered(from, to, tol) {
  const size = Math.max(tol * 4, 0.01), grid = new Map(), key = (x, y, z) => `${x},${y},${z}`;
  for (let i = 0; i < to.length; i += 3) { const k = key(Math.floor(to[i] / size), Math.floor(to[i + 1] / size), Math.floor(to[i + 2] / size)); let l = grid.get(k); if (!l) grid.set(k, l = []); l.push(i); }
  let worst = 0;
  for (let i = 0; i < from.length; i += 3) {
    const cx = Math.floor(from[i] / size), cy = Math.floor(from[i + 1] / size), cz = Math.floor(from[i + 2] / size);
    let best = Infinity;
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++)
      for (const j of grid.get(key(cx + dx, cy + dy, cz + dz)) ?? []) best = Math.min(best, Math.hypot(from[i] - to[j], from[i + 1] - to[j + 1], from[i + 2] - to[j + 2]));
    worst = Math.max(worst, best);
  }
  return worst;
}

function check(name, pack, i, vertices, indices) {
  const V = pack.vertices(i), I = pack.indices(i), step = pack.gridStep(i);
  // half a step on each axis, and f32 rounding of world coordinates up to ~8 km
  const tol = step * Math.sqrt(3) / 2 + 1e-3 * 0.6;
  assert.ok(I.length <= indices.length, `${name}: more triangles than the source`);
  for (let k = 0; k < I.length; k++) assert.ok(I[k] < V.length / 3, `${name}: index out of range`);
  // vertices of triangles that cannot collapse on the grid (shortest edge over one grid diagonal) must all survive;
  // specks a few millimetres across weld to nothing and are dropped
  const used = new Set(), d = (p, q) => Math.hypot(vertices[p * 3] - vertices[q * 3], vertices[p * 3 + 1] - vertices[q * 3 + 1], vertices[p * 3 + 2] - vertices[q * 3 + 2]);
  for (let t = 0; t < indices.length; t += 3) { const a = indices[t], b = indices[t + 1], c = indices[t + 2];
    if (Math.min(d(a, b), d(b, c), d(c, a)) > step * Math.sqrt(3)) { used.add(a); used.add(b); used.add(c); } }
  const usedV = new Float64Array(used.size * 3); let u = 0; for (const x of used) { usedV[u++] = vertices[x * 3]; usedV[u++] = vertices[x * 3 + 1]; usedV[u++] = vertices[x * 3 + 2]; }
  const out = covered(V, vertices, tol), back = covered(usedV, V, tol);
  assert.ok(out <= tol, `${name}: a packed vertex is ${out} m from any source vertex (tolerance ${tol})`);
  assert.ok(back <= tol, `${name}: a source vertex is ${back} m from any packed vertex (tolerance ${tol})`);
  // moving each corner by at most `tol` changes a triangle's area by at most about its perimeter times `tol`
  const a0 = area(vertices, indices), a1 = area(V, I), bound = perimeter(vertices, indices) * tol;
  assert.ok(Math.abs(a1 - a0) <= bound, `${name}: area ${a0} -> ${a1} (bound ${bound})`);
  return { dropped: indices.length / 3 - I.length / 3, step };
}

let meshes = 0, dropped = 0, coarse = 0;
// the mapped city: 1,516 cells
{
  const json = JSON.parse(fs.readFileSync('build/geographic-strip/city-colliders.json', 'utf8'));
  const pack = await CollisionPack.decode(bin('build/geographic-strip/city-colliders.bin'));
  assert.equal(pack.count, json.length);
  for (let i = 0; i < json.length; i++) {
    assert.equal(`${pack.cellX[i]},${pack.cellZ[i]}`, json[i].id);
    const r = check('city ' + json[i].id, pack, i, json[i].vertices, json[i].indices); meshes++; dropped += r.dropped; if (r.step > 1 / 256) coarse++;
  }
}
// every venue, high-rise, the Sphere and the coaster
for (const dir of ['build/strip-landmarks', 'build/resort-blocks/cosmo', 'build/resort-blocks/bellagio', 'build/resort-blocks/paris', 'build/highrises', 'build/sphere', 'build/south-strip']) {
  for (const f of fs.readdirSync(dir).filter((f) => f.endsWith('collision.json'))) {
    const json = JSON.parse(fs.readFileSync(`${dir}/${f}`, 'utf8'));
    if (!Array.isArray(json.vertices)) continue;
    const pack = await CollisionPack.decode(bin(`${dir}/${f.replace(/\.json$/, '.bin')}`));
    assert.equal(pack.count, 1);
    const r = check(`${dir}/${f}`, pack, 0, json.vertices, json.indices); meshes++; dropped += r.dropped; if (r.step > 1 / 256) coarse++;
  }
}
// a mesh past 65,536 vertices takes 32-bit indices; an empty mesh stays empty
{
  const n = 300 * 300, vertices = new Float64Array(n * 3), indices = [];
  for (let z = 0; z < 300; z++) for (let x = 0; x < 300; x++) vertices.set([x * 0.5, Math.sin(x * 0.1) * 2, z * 0.5], (z * 300 + x) * 3);
  for (let z = 0; z < 299; z++) for (let x = 0; x < 299; x++) { const a = z * 300 + x; indices.push(a, a + 300, a + 1, a + 1, a + 300, a + 301); }
  const bytes = await encodeCollision([{ vertices, indices }, { vertices: [], indices: [] }]);
  const pack = await CollisionPack.decode(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength));
  check('synthetic 90k', pack, 0, vertices, indices);
  assert.equal(pack.indices(0).length, indices.length);
  assert.equal(pack.triangleCount(1), 0);
}
console.log(`collision packs match their JSON: ${meshes} meshes, ${dropped} collapsed triangles dropped, ${coarse} meshes on a coarser grid`);

// the Bellagio planting
{
  const json = JSON.parse(fs.readFileSync('public/foliage/bellagio-placements.json', 'utf8'));
  const { loadPlants } = await import('../build/plants-test-module.mjs?' + Date.now());
  const buffer = bin('public/foliage/bellagio-placements.bin');
  globalThis.fetch = async () => ({ ok: true, arrayBuffer: async () => buffer });
  const { trees, grass } = await loadPlants('x');
  assert.equal(trees.count, json.trees.length); assert.equal(grass.count, json.grass.length);
  const turn = (a) => ((a / (2 * Math.PI)) % 1 + 1) % 1, angle = (a, b) => { const d = Math.abs(turn(a) - turn(b)); return Math.min(d, 1 - d) * 2 * Math.PI; };
  let worstP = 0, worstYaw = 0, worstScale = 0;
  const see = (list, i, x, y, z, yaw, scale) => {
    worstP = Math.max(worstP, Math.hypot(list.x(i) - x, list.y(i) - y, list.z(i) - z));
    worstYaw = Math.max(worstYaw, angle(list.yaw(i), yaw)); worstScale = Math.max(worstScale, Math.abs(list.scale(i) - scale) / scale);
  };
  json.trees.forEach((t, i) => see(trees, i, ...t.position, (t.seed % 6283) / 1000, 0.88 + (t.seed % 23) / 100));
  json.grass.forEach((g, i) => see(grass, i, ...g));
  assert.ok(worstP < 0.01, `plant position off by ${worstP} m`);
  assert.ok(worstYaw <= Math.PI / 256 + 1e-6, `plant yaw off by ${worstYaw} rad`);
  assert.ok(worstScale < 0.002, `plant scale off by ${worstScale}`);
  console.log(`plants match: ${trees.count} trees, ${grass.count} tufts; worst ${(worstP * 1000).toFixed(1)} mm, ${(worstYaw * 180 / Math.PI).toFixed(2)} deg, ${(worstScale * 100).toFixed(2)}% scale`);
}

// the jeep's speed map: the baked map gives the targets the JSON-built assist (as of 2026-10-24) gave
{
  transpile('src/work/SpeedMapFile.ts', 'build/speed-map-file-test-module.mjs');
  const { loadSpeedMap } = await import('../build/speed-map-file-test-module.mjs?' + Date.now());
  const { DrivingSpeedAssist, roadSpeedTarget } = await import('../src/work/DrivingSpeedAssist.ts');
  const buffer = bin('build/geographic-strip/speed-map.bin');
  globalThis.fetch = async () => ({ ok: true, arrayBuffer: async () => buffer });
  const baked = new DrivingSpeedAssist(await loadSpeedMap('x'));
  const network = JSON.parse(fs.readFileSync('build/geographic-strip/road-network.json', 'utf8'));
  const arrival = JSON.parse(fs.readFileSync('build/resort-blocks/bellagio/south-arrival-report.json', 'utf8'));
  const replaced = new Map(arrival.roads.map((r) => [r.id, { ...r, highway: 'service' }]));
  const roads = network.roads.map((r) => replaced.get(r.id) ?? r);
  // the previous implementation, verbatim in substance
  const cells = new Map();
  for (const road of roads) for (let i = 1; i < road.points.length; i++) {
    const a = road.points[i - 1], b = road.points[i], width = road.width, segment = { a, b, width, limit: roadSpeedTarget(road) }, pad = width / 2 + 2;
    for (let x = Math.floor((Math.min(a[0], b[0]) - pad) / 40); x <= Math.floor((Math.max(a[0], b[0]) + pad) / 40); x++)
      for (let z = Math.floor((Math.min(a[2], b[2]) - pad) / 40); z <= Math.floor((Math.max(a[2], b[2]) + pad) / 40); z++) { const key = `${x},${z}`; const l = cells.get(key) ?? []; l.push(segment); cells.set(key, l); }
  }
  const before = (x, y, z) => {
    if (x >= -375 && x <= -192 && z >= 488 && z <= 564 && y >= 0 && y <= 13) return 10;
    if (x >= -366 && x <= -203 && z > 564 && z <= 578 && y >= 0 && y <= 13) return 12;
    let nearest = Infinity, target = 10;
    for (const s of cells.get(`${Math.floor(x / 40)},${Math.floor(z / 40)}`) ?? []) {
      const dx = s.b[0] - s.a[0], dz = s.b[2] - s.a[2], l = dx * dx + dz * dz, t = l ? Math.max(0, Math.min(1, ((x - s.a[0]) * dx + (z - s.a[2]) * dz) / l)) : 0;
      const height = s.a[1] + t * (s.b[1] - s.a[1]); if (Math.abs(y - height) > 2.2) continue;
      const distance = Math.hypot(x - s.a[0] - t * dx, z - s.a[2] - t * dz); if (distance > s.width / 2 + 1.5) continue;
      if (distance < nearest) { nearest = distance; target = s.limit; }
    }
    return target;
  };
  // points on and around the roads; a sample within 2 cm of a reach, height or cell boundary may differ by rounding
  let seed = 1; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  let same = 0, differ = 0;
  for (let n = 0; n < 200000; n++) {
    const road = roads[Math.floor(rnd() * roads.length)], p = road.points[Math.floor(rnd() * road.points.length)];
    const x = p[0] + (rnd() - 0.5) * (road.width + 8), y = p[1] + 0.5 + (rnd() - 0.5) * 3, z = p[2] + (rnd() - 0.5) * (road.width + 8);
    if (before(x, y, z) === baked.targetAt(x, y, z)) same++; else differ++;
  }
  assert.ok(differ <= 200000 * 1e-3, `speed map: ${differ} of 200000 targets differ`);
  console.log(`speed map matches: ${same} of ${same + differ} targets equal (${differ} differ at rounding boundaries)`);
}

// metadata records: every record file decodes to its JSON, numbers within their grid (1 mm, 1e-4) or f32 rounding
{
  transpile('src/work/PackedRecords.ts', 'build/packed-records-test-module.mjs');
  const { decodeRecords } = await import('../build/packed-records-test-module.mjs?' + Date.now());
  const PREC = { p: 1e-3, position: 1e-3, points: 1e-3, center: 1e-3, eye: 1e-3, target: 1e-3, origin: 1e-3, bounds: 1e-3, accessPoints: 1e-3, seats: 1e-3, lights: 1e-3, vertices: 1e-3, size: 1e-3, s: 1e-3, station: 1e-3, exit: 1e-3, entrance: 1e-3, access: 1e-3, lift: 1e-3, liftButton: 1e-3, right: 1e-4, up: 1e-4, direction: 1e-4, uv: 1e-4 };
  const close = (a, b, key, where) => { const tol = (PREC[key] ?? 0) / 2 + Math.abs(a) * 1.2e-7 + 1e-9; assert.ok(Math.abs(a - b) <= tol, `${where}: ${a} -> ${b}`); };
  const isNum = (x) => typeof x === 'number', numList = (x) => Array.isArray(x) && x.length > 0 && x.every(isNum);
  function same(a, b, key, where) {
    if (isNum(a)) return close(a, b, key, where);
    if (a === null || typeof a !== 'object') return assert.equal(b, a, where);
    if (Array.isArray(a)) {
      if (numList(a)) { assert.equal(b.length, a.length, where); a.forEach((x, i) => close(x, b[i], key, where)); return; }
      if (a.length && a.every((x) => numList(x) && x.length === a[0].length)) { const flat = a.flat(); assert.equal(b.length, flat.length, where); flat.forEach((x, i) => close(x, b[i], key, where)); return; }
      if (!Array.isArray(b)) { // columns
        assert.equal(b.length, a.length, where);
        a.forEach((row, r) => { for (const [k, x] of Object.entries(row)) { const col = b[k];
          if (Array.isArray(x)) x.forEach((y, j) => close(y, col[r * x.length + j], k, `${where}[${r}].${k}`)); else close(typeof x === 'boolean' ? +x : x, col[r], k, `${where}[${r}].${k}`); } });
        return;
      }
      assert.equal(b.length, a.length, where); a.forEach((x, i) => same(x, b[i], key, `${where}[${i}]`)); return;
    }
    assert.deepEqual(Object.keys(b), Object.keys(a), where);
    for (const [k, x] of Object.entries(a)) same(x, b[k], k, `${where}.${k}`);
  }
  let files = 0;
  const walk = (dir) => { for (const e of fs.readdirSync(dir, { withFileTypes: true })) { const p = `${dir}/${e.name}`;
    if (e.isDirectory() && !e.name.startsWith('.')) walk(p);
    else if (e.name.endsWith('.json') && fs.existsSync(p.replace(/\.json$/, '.bin')) && !/collision|placements|road-network/.test(e.name)) {
      const bytes = bin(p.replace(/\.json$/, '.bin')); if (new DataView(bytes).getUint32(0, true) !== 0x54414456) continue;
      same(JSON.parse(fs.readFileSync(p, 'utf8')), decodeRecords(bytes), '', p); files++; } } };
  for (const dir of ['build/strip-landmarks', 'build/resort-blocks', 'build/sphere', 'build/south-strip', 'build/pbr/strips', 'build/hotels', 'build/geographic-strip/access']) walk(dir);
  assert.ok(files > 400, `only ${files} record files`);
  console.log(`records match their JSON: ${files} files`);
}
