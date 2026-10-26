// Lazy near detail with baked LODs (src/work/CityLod.ts, CityBatches.ts, 2026-10-26): a block whose bake fits loads as its
// LOD alone, built from the sources, and fills its near level only when approached. The LOD's vertices must be exactly the
// ones the full near level would have (bit for bit), the near level filled later exactly the eager one, the shadow casters
// exactly the casting parts' triangles; a block left far behind drops its near level and can fill it again.
// Run: node --import ./tools/ts-register.mjs tests/city-lazy-lod.test.mjs
import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import * as THREE from 'three';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { CityLod, setCityNearDetail } from '../src/work/CityLod.ts';
import { LodBake, useCityLodBake, sampleHash } from '../src/work/CityBakeLoad.ts';
const { MeshoptEncoder } = await import(pathToFileURL(path.resolve('tools/optimize/bm-tools/gltf/node_modules/meshoptimizer/meshopt_encoder.js')).href);
await MeshoptDecoder.ready; await MeshoptEncoder.ready;

/** A small city block: two boxes (one casting), a quantized plane (Int16 positions, Int8 normals, as meshopt GLBs). */
function scene() {
  const s = new THREE.Scene(), owner = new THREE.Group(); owner.name = 'test part'; s.add(owner);
  const a = new THREE.Mesh(new THREE.BoxGeometry(10, 4, 10, 3, 2, 3), new THREE.MeshStandardMaterial({ color: 0xaa3322, roughness: 0.4 }));
  a.position.set(0, 2, 0); a.userData.cityCaster = true; owner.add(a);
  const b = new THREE.Mesh(new THREE.BoxGeometry(4, 8, 4), new THREE.MeshStandardMaterial({ color: 0x22aa44, roughness: 0.9 }));
  b.position.set(20, 4, 0); owner.add(b);
  const plane = new THREE.PlaneGeometry(30, 30, 8, 8), n = plane.getAttribute('position').count;
  const q = new Int16Array(n * 3), qn = new Int8Array(n * 3);
  for (let i = 0; i < n * 3; i++) q[i] = Math.round(plane.getAttribute('position').array[i] / 15 * 32767);
  for (let i = 0; i < n; i++) { qn[i * 3 + 2] = 127; }
  plane.setAttribute('position', new THREE.BufferAttribute(q, 3, true)); plane.setAttribute('normal', new THREE.BufferAttribute(qn, 3, true));
  const c = new THREE.Mesh(plane, new THREE.MeshStandardMaterial({ color: 0x8888ff, roughness: 0.6 }));
  c.scale.setScalar(15); c.rotation.x = -Math.PI / 2; c.position.set(5, 0.1, 5); c.userData.cityCaster = true; owner.add(c);
  return { s, owner };
}
const key = () => 'block';

// 1. Eager: everything built at once (no bake).
useCityLodBake(null);
const eager = scene(), eagerLod = new CityLod(eager.owner, { key, facade: true });
const eagerHigh = eager.owner.getObjectByName('Full detail / block');
const batches = eagerHigh.children.filter((o) => o.isMesh && o.name.startsWith('Full detail /'));
assert.ok(batches.length >= 1);

// 2. A bake for those batches: every other vertex, triangles over consecutive kept vertices.
const lods = new Map([['block', []]]);
const expected = [];
for (const m of batches) {
  const g = m.geometry, n = g.getAttribute('position').count;
  const subset = []; for (let v = n - 1; v >= 0; v -= 2) subset.push(v); // not ascending, as first-use order is not
  const tri = []; for (let i = 0; i + 2 < subset.length; i += 3) tri.push(i, i + 1, i + 2);
  const zig = []; let prev = 0; for (const v of subset) { let d = v - prev; prev = v; let z = d < 0 ? -2 * d - 1 : 2 * d; do { let byte = z & 127; z = Math.floor(z / 128); if (z) byte |= 128; zig.push(byte); } while (z); }
  const list = Uint16Array.from(tri), coded = MeshoptEncoder.encodeIndexBuffer(new Uint8Array(list.buffer), list.length, 2);
  lods.get('block').push({ vertices: n, indices: g.index.count, hash: sampleHash(g.getAttribute('position').array, n), count: subset.length, indexCount: list.length, subset: Uint8Array.from(zig), index: coded });
  expected.push({ g, subset, tri });
}
useCityLodBake(new LodBake(new Map([['test part', lods]])));
setCityNearDetail('lazy');

// 3. Lazy: the LOD alone, from the sources.
const lazy = scene(), lazyLod = new CityLod(lazy.owner, { key, facade: true });
const lazyHigh = lazy.owner.getObjectByName('Full detail / block'), lazyLow = lazy.owner.getObjectByName('Silhouette / block');
assert.equal(lazyHigh.children.filter((o) => o.isMesh && o.name.startsWith('Full detail /')).length, 0, 'no near level yet');
const lowMeshes = lazyLow.children.filter((o) => o.isMesh && o.layers.mask === 1);
assert.equal(lowMeshes.length, batches.length);
for (const [k, lm] of lowMeshes.entries()) {
  const { g, subset, tri } = expected[k], lg = lm.geometry;
  for (const name of ['position', 'normal', 'uv', 'color']) {
    const near = g.getAttribute(name), low = lg.getAttribute(name), size = near.itemSize;
    assert.equal(low.itemSize, size);
    subset.forEach((v, s) => { for (let c = 0; c < size; c++) assert.ok(Object.is(low.array[s * size + c], near.array[v * size + c]), `${name} of LOD vertex ${s} (batch vertex ${v}) is the near level's`); });
  }
  assert.deepEqual([...lg.index.array], tri, 'the baked triangles');
}
// casters: LOD triangles from casting parts, on the shadow layer, sharing the LOD's positions
const lodCasters = lazyLow.children.filter((o) => o.isMesh && o.layers.mask === 1 << 30);
assert.ok(lodCasters.length >= 1, 'LOD casters exist');
for (const c of lodCasters) assert.ok(lowMeshes.some((l) => l.geometry.getAttribute('position') === c.geometry.getAttribute('position')), 'LOD casters share their LOD positions');

// 4. Approach: the near level is filled (nearest first, within the frame budget) and is exactly the eager one.
const camera = new THREE.PerspectiveCamera(70, 1, 1, 10000); camera.position.set(0, 2, 30); camera.updateMatrixWorld(true);
lazyLod.select(camera, 1000);
for (let i = 0; i < 50 && lazyLod.stats.nearFilled === 0; i++) await new Promise((r) => setTimeout(r, 5));
assert.equal(lazyLod.stats.nearFilled, 1, 'near level filled on approach');
const filled = lazyHigh.children.filter((o) => o.isMesh && o.layers.mask === 1 && o.name.startsWith('Full detail /'));
assert.equal(filled.length, batches.length);
for (const [k, m] of filled.entries()) {
  const near = batches[k].geometry, g = m.geometry;
  for (const name of ['position', 'normal', 'uv', 'color']) assert.deepEqual(g.getAttribute(name).array, near.getAttribute(name).array, `${name} filled later = eager`);
  assert.deepEqual(g.index.array, near.index.array);
}
// near casters: exactly the casting parts' index ranges (box a and the plane cast, box b does not)
const nearCasters = lazyHigh.children.filter((o) => o.isMesh && o.layers.mask === 1 << 30);
const eagerCasters = eager.owner.getObjectByName('City block / block').children.filter((o) => o.isMesh && o.layers.mask === 1 << 30);
assert.deepEqual(nearCasters.map((c) => [...c.geometry.index.array]), eagerCasters.map((c) => [...c.geometry.index.array]), 'lazy near casters = eager casters');
const casterTriangles = eagerCasters.reduce((t, c) => t + c.geometry.index.count / 3, 0);
// box a (segments 3 x 2 x 3: 2 x (6 + 9 + 6) quads, 84 triangles) and the 8 x 8 plane (128) cast; box b does not
assert.equal(casterTriangles, 84 + 128, 'casting parts only');
lazyLod.select(camera, 1300); assert.equal(lazyHigh.visible, true); assert.equal(lazyLow.visible, false);

// 5. Far away for long enough: the near level is dropped, and filled again on return.
camera.position.set(0, 2, 3000); camera.updateMatrixWorld(true);
lazyLod.select(camera, 2000); lazyLod.select(camera, 2000 + 25000);
assert.equal(lazyLod.stats.nearFilled, 0, 'evicted'); assert.equal(lazyHigh.children.filter((o) => o.userData.cityNear).length, 0);
camera.position.set(0, 2, 30); camera.updateMatrixWorld(true); lazyLod.select(camera, 30000);
for (let i = 0; i < 50 && lazyLod.stats.nearFilled === 0; i++) await new Promise((r) => setTimeout(r, 5));
assert.equal(lazyLod.stats.nearFilled, 1, 'filled again');
lazyLod.dispose(); eagerLod.dispose();
console.log(`PASS: lazy near detail: LOD vertices bit-identical to the near level (${expected.reduce((n, e) => n + e.subset.length, 0)} checked), near level filled on approach = eager, casters = casting parts, eviction and refill`);
