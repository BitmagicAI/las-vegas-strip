#!/usr/bin/env node
// Preserve every 160 m collision record and existing codec; package by 800 m parent.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {encodeCollision} from '../optimize/pack-data.mjs';
const [input, output] = process.argv.slice(2);
if (!input || !output) throw new Error('Usage: node --import ./tools/ts-register.mjs tools/city-cells/pack-collision.mjs input.json output-directory');
const groups = new Map();
for (const record of JSON.parse(fs.readFileSync(input, 'utf8'))) {
  const cell = record.id.split(',').map(Number);
  if (cell.length !== 2 || cell.some(n => !Number.isInteger(n))) throw new Error(`Invalid cell ${record.id}`);
  const parent = `${Math.floor(cell[0] / 5)},${Math.floor(cell[1] / 5)}`;
  if (!groups.has(parent)) groups.set(parent, []);
  groups.get(parent).push({vertices: record.vertices, indices: record.indices, cell});
}
fs.mkdirSync(output, {recursive: true});
const cells = [];
for (const [cell, meshes] of [...groups].sort(([a], [b]) => a.localeCompare(b, 'en'))) {
  const bytes = await encodeCollision(meshes, {cells: true});
  const file = `cell-${cell.replace(',', '_')}.bin`, destination = path.join(output, file);
  if (!fs.existsSync(destination) || !fs.readFileSync(destination).equals(bytes)) fs.writeFileSync(destination, bytes);
  cells.push({cell, file, records: meshes.length, bytes: bytes.length, sha256: crypto.createHash('sha256').update(bytes).digest('hex')});
}
const manifest = JSON.stringify({version: 1, cellSize: 800, collisionCellSize: 160, cells}, null, 2) + '\n';
const destination = path.join(output, 'manifest.json');
if (!fs.existsSync(destination) || fs.readFileSync(destination, 'utf8') !== manifest) fs.writeFileSync(destination, manifest);
console.log(JSON.stringify({cells: cells.length, records: cells.reduce((n, c) => n + c.records, 0), bytes: cells.reduce((n, c) => n + c.bytes, 0)}));
