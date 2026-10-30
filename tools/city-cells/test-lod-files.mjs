import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {readBlocks,encodeBlocks,partitionLod,readBlockCells} from './lod-files.mjs';
const bytes=fs.readFileSync(process.argv[2]??'build/baked/city-lod.bin'),part='OpenStreetMap / geographic Strip';
const original=readBlocks(bytes),split=partitionLod(bytes,part),repeat=partitionLod(bytes,part);
const key=b=>JSON.stringify([b.part,b.key]);
const expected=new Map(original.map(b=>[key(b),b]));
assert.equal(expected.size,original.length,'duplicate block identities');
for(const [file,data] of split){
 assert.deepEqual(data,repeat.get(file),'nondeterministic output');
 for(const b of readBlocks(data)){
  assert.deepEqual(b.bytes,expected.get(key(b))?.bytes,`Changed block ${key(b)}`);
  expected.delete(key(b));
 }
}
assert.equal(expected.size,0,'lost blocks');
// Simulate a changed batch hash in one city block: unrelated files must not change.
const changed=original.map(b=>({...b,bytes:Buffer.from(b.bytes)}));
const target=changed.find(b=>b.part===part);target.bytes[target.bytes.length-1]^=1;
const altered=partitionLod(encodeBlocks(changed),part);
assert.equal([...split].filter(([name,data])=>!data.equals(altered.get(name))).length,1,'change escaped its cell');
assert.throws(()=>readBlocks(bytes.subarray(0,bytes.length-1)),/Truncated/);
console.log(`PASS: ${original.length} blocks preserved byte-for-byte in ${split.size} files; no-op deterministic; one-cell change isolated`);

if(fs.existsSync('.bitmagic/bake/raw')){
 const cells=readBlockCells('.bitmagic/bake/raw');
 const spatial=partitionLod(bytes,part,cells),repeatSpatial=partitionLod(bytes,part,cells);
 const remaining=new Map(original.map(b=>[key(b),b.bytes]));
 assert(!spatial.has('other-parts'),'non-geographic blocks must be spatially packaged');
 for(const [file,data] of spatial){
  assert.deepEqual(data,repeatSpatial.get(file));
  for(const block of readBlocks(data)){
   assert.deepEqual(block.bytes,remaining.get(key(block)));
   if(block.part!==part)assert.equal(file,cells.get(key(block)));
   remaining.delete(key(block));
  }
 }
 assert.equal(remaining.size,0);
 const adjusted=partitionLod(encodeBlocks(changed),part,cells);
 assert.equal([...spatial].filter(([name,data])=>!data.equals(adjusted.get(name))).length,1);
 assert.throws(()=>partitionLod(bytes,part,new Map()),/Missing cell/);
 console.log(`PASS: all ${original.length} blocks spatially packaged in ${spatial.size} files with exact bytes`);
}

const fixture=fs.mkdtempSync(path.join(os.tmpdir(),'city-lod-cells-'));
try{
 const head=Buffer.from(JSON.stringify({id:'fixture',blocks:[
  {key:'negative',box:[-900,0,-10,-700,20,10]},
  {key:'positive',box:[800,0,1600,900,20,1700]}
 ]}));
 const size=Buffer.alloc(4);size.writeUInt32LE(head.length);
 fs.writeFileSync(path.join(fixture,'part.bin'),Buffer.concat([size,head]));
 const cells=readBlockCells(fixture);
 assert.equal(cells.get(JSON.stringify(['fixture','negative'])),'cell--1_0');
 assert.equal(cells.get(JSON.stringify(['fixture','positive'])),'cell-1_2');
 fs.writeFileSync(path.join(fixture,'bad.bin'),Buffer.from([0]));
 assert.throws(()=>readBlockCells(fixture),/Truncated/);
}finally{fs.rmSync(fixture,{recursive:true,force:true});}
console.log('PASS: block bounds use 800 m cells, including negative coordinates; truncated headers rejected');
