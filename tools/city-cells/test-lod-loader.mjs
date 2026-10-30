import assert from 'node:assert/strict';
import fs from 'node:fs';
import {LodBake,parse,decodeLod} from '../../src/work/CityBakeLoad.ts';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {readBlocks,partitionLod,readBlockCells} from './lod-files.mjs';
await MeshoptDecoder.ready;
const bytes=fs.readFileSync(process.argv[2]??'build/baked/city-lod.bin');
const source=parse(bytes);
const files=[...partitionLod(bytes,'OpenStreetMap / geographic Strip',fs.existsSync('.bitmagic/bake/raw')?readBlockCells('.bitmagic/bake/raw'):undefined).values()].map(parse);
const combined=LodBake.combine(files);
assert.equal(combined.partCount,source.partCount);
let batches=0;
for(const block of readBlocks(bytes))for(let i=0;i<block.batches;i++){
 const expected=source.batch(block.part,block.key,i),actual=combined.batch(block.part,block.key,i);
 assert.deepEqual(actual,expected,`${block.part}/${block.key}/${i}`);
 assert.deepEqual(decodeLod(actual),decodeLod(expected));batches++;
}
assert.throws(()=>LodBake.combine([...files,files[0]]),/Duplicate LOD block/);
console.log(`PASS: runtime recombination preserves ${batches} decoded LOD batches and rejects duplicate identities`);
