#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {CollisionPack} from '../../src/work/CollisionPack.ts';
const [baseline, directory] = process.argv.slice(2);
const decode = async file => { const b = fs.readFileSync(file); return CollisionPack.decode(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength)); };
const original = await decode(baseline), remaining = new Map();
for (let i = 0; i < original.count; i++) remaining.set(`${original.cellX[i]},${original.cellZ[i]}`, i);
let count = 0;
for (const c of JSON.parse(fs.readFileSync(path.join(directory, 'manifest.json'), 'utf8')).cells) {
  const pack = await decode(path.join(directory, c.file));
  for (let j = 0; j < pack.count; j++) {
    const key = `${pack.cellX[j]},${pack.cellZ[j]}`, i = remaining.get(key);
    assert.notEqual(i, undefined, `Missing or duplicated ${key}`);
    assert.equal(`${Math.floor(pack.cellX[j]/5)},${Math.floor(pack.cellZ[j]/5)}`, c.cell);
    assert.deepEqual(pack.vertices(j), original.vertices(i), `Vertices ${key}`);
    // meshopt's triangle codec may cyclically rotate a triangle at stream boundaries.
    // Preserve triangle order and winding; never accept reversed or reordered faces.
    const actual = pack.indices(j), expected = original.indices(i);
    assert.equal(actual.length, expected.length);
    for (let k = 0; k < actual.length; k += 3) {
      let same = false;
      for (let r = 0; r < 3; r++) if (actual[k] === expected[k+r] && actual[k+1] === expected[k+(r+1)%3] && actual[k+2] === expected[k+(r+2)%3]) same = true;
      assert.ok(same, `Triangle ${key}:${k/3}`);
    }
    remaining.delete(key); count++;
  }
}
assert.equal(remaining.size, 0);
console.log(`PASS: ${count} collision records have identical decoded positions and ordered, oriented triangles`);
