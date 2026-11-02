// Append original amenity studies; retain every pre-existing node and collision triangle.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {NodeIO} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/core/dist/index.js';
import {ALL_EXTENSIONS} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/extensions/dist/index.js';
import {mergeDocuments,unpartition} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/functions/dist/index.js';
import {MeshoptDecoder} from '../optimize/bm-tools/gltf/node_modules/meshoptimizer/index.js';
import {encodeCollision} from '../optimize/pack-data.mjs';
await MeshoptDecoder.ready;const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const base='build/strip-landmarks/',backup='.bitmagic/city-exterior-backups/royale-carnaval-refinement/';fs.mkdirSync(backup,{recursive:true});const hash=crypto.createHash('sha256');
for(const [key,addition] of [['casinoRoyale','royaleCourtyardRefinement'],['casinoRoyaleGarage','royaleGarageRefinement'],['carnavalCourt','carnavalRefinement']]){
 for(const suffix of ['.glb','-collision.json']){const f=key+'-exterior'+suffix;if(!fs.existsSync(backup+f))fs.copyFileSync(base+f,backup+f);}
 const doc=await io.read(backup+key+'-exterior.glb'),extra=await io.read(base+addition+'-exterior.glb');
 const signature=n=>JSON.stringify({name:n.getName(),extras:n.getExtras(),matrix:n.getMatrix(),primitives:n.getMesh()?.listPrimitives().map(p=>({indices:p.getIndices()?Array.from(p.getIndices().getArray()):null,attributes:p.listSemantics().map(s=>[s,Array.from(p.getAttribute(s).getArray())]),material:p.getMaterial()?.getName()}))});
 const nodes=doc.getRoot().listNodes(),before=nodes.map(signature),map=mergeDocuments(doc,extra),scene=doc.getRoot().getDefaultScene();
 for(const s of extra.getRoot().listScenes()){const copied=map.get(s);for(const n of copied.listChildren()){n.setExtras({...n.getExtras(),property:key+'-exterior'});scene.addChild(n);}copied.dispose();}
 assert.deepEqual(nodes.map(signature),before);await doc.transform(unpartition());
 for(const e of doc.getRoot().listExtensionsUsed())if(e.extensionName==='EXT_meshopt_compression')e.dispose();
 await io.write(base+key+'-exterior.glb',doc);hash.update(fs.readFileSync(base+key+'-exterior.glb'));
 const old=JSON.parse(fs.readFileSync(backup+key+'-exterior-collision.json')),add=JSON.parse(fs.readFileSync(base+addition+'-exterior-collision.json')),offset=old.vertices.length/3;
 const collision={...old,vertices:old.vertices.concat(add.vertices),indices:old.indices.concat(add.indices.map(i=>i+offset))};
 assert.deepEqual(collision.indices.slice(0,old.indices.length),old.indices);assert.deepEqual(collision.vertices.slice(0,old.vertices.length),old.vertices);
 fs.writeFileSync(base+key+'-exterior-collision.json',JSON.stringify(collision));fs.writeFileSync(base+key+'-exterior-collision.bin',await encodeCollision([collision]));
 const report={preservedNodes:nodes.length,preservedNodeGeometry:true,retainedCollisionTriangles:old.indices.length/3,addedCollisionTriangles:add.indices.length/3,removedNodes:0,removedCollisionTriangles:0};
 fs.writeFileSync('docs/project-records/royale-carnaval-refinement/'+key+'-preservation.json',JSON.stringify(report,null,2)+'\n');console.log(key,report);
}
fs.writeFileSync(base+'version.json',JSON.stringify({revision:hash.digest('hex').slice(0,16)}));
