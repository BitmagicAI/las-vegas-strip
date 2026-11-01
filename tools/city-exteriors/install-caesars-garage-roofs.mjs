// Replace only two garage roof surface nodes; preserve every other resort node and all original collision.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {NodeIO} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/core/dist/index.js';
import {ALL_EXTENSIONS} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/extensions/dist/index.js';
import {mergeDocuments,unpartition} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/functions/dist/index.js';
import {MeshoptDecoder} from '../optimize/bm-tools/gltf/node_modules/meshoptimizer/index.js';
await MeshoptDecoder.ready;const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const backup='.bitmagic/city-exterior-backups/caesars-garage-roofs/',base='build/strip-landmarks/';
const doc=await io.read(backup+'caesarsExterior-exterior.glb'),extra=await io.read(base+'caesarsGarageRoofs-exterior.glb');
const signature=n=>JSON.stringify({name:n.getName(),extras:n.getExtras(),matrix:n.getMatrix(),primitives:n.getMesh()?.listPrimitives().map(p=>({indices:p.getIndices()?Array.from(p.getIndices().getArray()):null,attributes:p.listSemantics().map(s=>[s,Array.from(p.getAttribute(s).getArray())]),material:p.getMaterial()?.getName()}))});
const roofs=doc.getRoot().listNodes().filter(n=>['caesars/way/134949710','caesars/way/134949713'].includes(n.getExtras().source)&&n.getExtras().surface==='cp-roof');assert.equal(roofs.length,2);const removedRoofTriangles=roofs.reduce((sum,n)=>sum+n.getMesh().listPrimitives().reduce((s,p)=>s+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0),0);for(const n of roofs)n.dispose();
const nodes=doc.getRoot().listNodes(),before=nodes.map(signature),map=mergeDocuments(doc,extra),scene=doc.getRoot().getDefaultScene();
for(const s of extra.getRoot().listScenes()){const copied=map.get(s);for(const n of copied.listChildren()){n.setExtras({...n.getExtras(),property:'caesarsExterior'});scene.addChild(n);}copied.dispose();}
assert.deepEqual(nodes.map(signature),before);await doc.transform(unpartition());
for(const e of doc.getRoot().listExtensionsUsed())if(e.extensionName==='EXT_meshopt_compression')e.dispose();
await io.write(base+'caesarsExterior-exterior.glb',doc);
const old=JSON.parse(fs.readFileSync(backup+'caesarsExterior-exterior-collision.json')),add=JSON.parse(fs.readFileSync(base+'caesarsGarageRoofs-exterior-collision.json')),offset=old.vertices.length/3;
const collision={...old,vertices:old.vertices.concat(add.vertices),indices:old.indices.concat(add.indices.map(i=>i+offset))};
fs.writeFileSync(base+'caesarsExterior-exterior-collision.json',JSON.stringify(collision));
const report={preservedNodes:nodes.length,removedRoofNodes:roofs.length,removedRoofTriangles,preservedNodeGeometry:true,oldCollisionTriangles:old.indices.length/3,addedCollisionTriangles:add.indices.length/3,oldCollisionPrefixPreserved:true,scope:'Replace only two cp-roof nodes. Preserve all other nodes and full old collision prefix, including original garage roof floors. No geographic city export.'};
fs.writeFileSync('docs/project-records/caesars-garage-roofs/preservation.json',JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(base+'version.json',JSON.stringify({revision:crypto.createHash('sha256').update(fs.readFileSync(base+'caesarsExterior-exterior.glb')).digest('hex').slice(0,16)}));console.log(report);
