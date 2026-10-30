#!/usr/bin/env node
// Preserve every 160 m collision record and existing codec; package by 800 m parent.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
export async function packCityCollision(input,output,{check=false,encodeCollision}={}) {
const source=fs.readFileSync(input),sourceSha256=crypto.createHash('sha256').update(source).digest('hex');
const indexFile=path.join(output,'manifest.json');
if(check){
 if(!fs.existsSync(indexFile))return {fresh:false};
 const index=JSON.parse(fs.readFileSync(indexFile));
 return {fresh:index.sourceSha256===sourceSha256&&index.cells.every(cell=>{
  const file=path.join(output,cell.file);
  return fs.existsSync(file)&&crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')===cell.sha256;
 })};
}
encodeCollision??=(await import('../optimize/pack-data.mjs')).encodeCollision;
const groups = new Map();
for (const record of JSON.parse(source.toString('utf8'))) {
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
const manifest = JSON.stringify({version: 1, cellSize: 800, collisionCellSize: 160, sourceSha256, cells}, null, 2) + '\n';
const destination = path.join(output, 'manifest.json');
if (!fs.existsSync(destination) || fs.readFileSync(destination, 'utf8') !== manifest) fs.writeFileSync(destination, manifest);
return {fresh:true,cells: cells.length, records: cells.reduce((n, c) => n + c.records, 0), bytes: cells.reduce((n, c) => n + c.bytes, 0)};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href){
 const [input,output]=process.argv.slice(2);
 if(!input||!output)throw new Error('Usage: pack-collision.mjs input.json output-directory');
 console.log(JSON.stringify(await packCityCollision(input,output)));
}
