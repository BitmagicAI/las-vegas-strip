// Append the original pool deck amenities without regenerating existing Westgate geometry or interiors.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {NodeIO} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/core/dist/index.js';
import {ALL_EXTENSIONS} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/extensions/dist/index.js';
import {mergeDocuments,unpartition} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/functions/dist/index.js';
import {MeshoptDecoder} from '../optimize/bm-tools/gltf/node_modules/meshoptimizer/index.js';
await MeshoptDecoder.ready;const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const backup='.bitmagic/city-exterior-backups/westgate-amenities/',base='build/strip-landmarks/';
const doc=await io.read(backup+'westgateExterior-exterior.glb'),extra=await io.read(base+'westgateAmenities-exterior.glb');
const signature=n=>JSON.stringify({name:n.getName(),extras:n.getExtras(),matrix:n.getMatrix(),primitives:n.getMesh()?.listPrimitives().map(p=>({indices:p.getIndices()?Array.from(p.getIndices().getArray()):null,attributes:p.listSemantics().map(s=>[s,Array.from(p.getAttribute(s).getArray())]),material:p.getMaterial()?.getName()}))});
const nodes=doc.getRoot().listNodes(),before=nodes.map(signature),map=mergeDocuments(doc,extra),scene=doc.getRoot().getDefaultScene();
for(const s of extra.getRoot().listScenes()){const copied=map.get(s);for(const n of copied.listChildren()){n.setExtras({...n.getExtras(),property:'westgateExterior'});scene.addChild(n);}copied.dispose();}
assert.deepEqual(nodes.map(signature),before);await doc.transform(unpartition());
for(const e of doc.getRoot().listExtensionsUsed())if(e.extensionName==='EXT_meshopt_compression')e.dispose();
await io.write(base+'westgateExterior-exterior.glb',doc);
const old=JSON.parse(fs.readFileSync(backup+'westgateExterior-exterior-collision.json')),add=JSON.parse(fs.readFileSync(base+'westgateAmenities-exterior-collision.json')),offset=old.vertices.length/3;
const collision={...old,vertices:old.vertices.concat(add.vertices),indices:old.indices.concat(add.indices.map(i=>i+offset))};
fs.writeFileSync(base+'westgateExterior-exterior-collision.json',JSON.stringify(collision));
const report={preservedNodes:nodes.length,preservedNodeGeometry:true,oldCollisionTriangles:old.indices.length/3,addedCollisionTriangles:add.indices.length/3,oldCollisionPrefixPreserved:true,scope:'Append only; no city face removal because no mapped pool deck amenities shell was present in inspected baseline.'};
fs.writeFileSync('docs/project-records/westgate-amenities/preservation.json',JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(base+'version.json',JSON.stringify({revision:crypto.createHash('sha256').update(fs.readFileSync(base+'westgateExterior-exterior.glb')).digest('hex').slice(0,16)}));console.log(report);
