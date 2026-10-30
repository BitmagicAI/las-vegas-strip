#!/usr/bin/env node
// Compare decoded cell meshes with the committed optimized whole-city baseline.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import crypto from 'node:crypto';
const dep = name => import(pathToFileURL(path.resolve('tools/optimize/bm-tools/gltf/node_modules', name)).href);
const {NodeIO}=await dep('@gltf-transform/core/dist/index.js');
const {ALL_EXTENSIONS}=await dep('@gltf-transform/extensions/dist/index.js');
const {MeshoptDecoder}=await dep('meshoptimizer/index.js');await MeshoptDecoder.ready;
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const source=await io.read(process.argv[2]??'build/optimized/build/geographic-strip/city.glb');
const signature=primitive=>{
 const h=crypto.createHash('sha256');
 for(const name of primitive.listSemantics().sort()){
  const a=primitive.getAttribute(name),bytes=a.getArray();
  h.update(name+':'+a.getType()+':'+a.getNormalized());
  h.update(Buffer.from(bytes.buffer,bytes.byteOffset,bytes.byteLength));
 }
 // Codec may rotate a triangle cyclically at a compressed-stream boundary.
 const indices=primitive.getIndices().getArray(),canonical=new Uint32Array(indices.length);
 for(let i=0;i<indices.length;i+=3){
  let r=0;if(indices[i+1]<indices[i+r])r=1;if(indices[i+2]<indices[i+r])r=2;
  for(let k=0;k<3;k++)canonical[i+k]=indices[i+(r+k)%3];
 }
 h.update(Buffer.from(canonical.buffer));
 const m=primitive.getMaterial();
 h.update(JSON.stringify({name:m.getName(),base:m.getBaseColorFactor(),metal:m.getMetallicFactor(),rough:m.getRoughnessFactor(),emissive:m.getEmissiveFactor(),alpha:m.getAlphaMode(),cutoff:m.getAlphaCutoff(),double:m.getDoubleSided()}));
 return h.digest('hex');
};
const expected=new Map();
for(const node of source.getRoot().listNodes()){
 const mesh=node.getMesh();
 expected.set(node.getName(),{extras:node.getExtras(),matrix:node.getMatrix(),signatures:mesh?mesh.listPrimitives().map(signature):[]});
}
const manifest=JSON.parse(fs.readFileSync('build/geographic-strip/cells/manifest.json','utf8'));
assert.deepEqual(manifest.nodeOrder,source.getRoot().listNodes().map(n=>n.getName()),'Node traversal order');
let count=0;
for(const cell of manifest.cells){
 const file=path.join('.bitmagic/optimize/build/geographic-strip/cells',path.basename(cell.file,'.glb'),'out.glb');
 const doc=await io.read(file);
 for(const node of doc.getRoot().listNodes()){
  const baseline=expected.get(node.getName());assert.ok(baseline,`Unknown/duplicate ${node.getName()}`);
  assert.deepEqual(node.getExtras(),baseline.extras,`Extras ${node.getName()}`);
  assert.deepEqual(node.getMatrix(),baseline.matrix,`Transform ${node.getName()}`);
  assert.deepEqual(node.getMesh()?node.getMesh().listPrimitives().map(signature):[],baseline.signatures,`Geometry/material ${node.getName()}`);
  expected.delete(node.getName());count++;
 }
}
assert.equal(expected.size,0,'Missing source nodes');
console.log(`PASS: ${count} nodes preserve transforms, metadata, decoded vertex attributes, oriented triangles and material factors`);
