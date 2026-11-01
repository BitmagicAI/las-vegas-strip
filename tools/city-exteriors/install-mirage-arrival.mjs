// Replace only the historical arrival canopy; preserve every other resort node and collider.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {NodeIO} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/core/dist/index.js';
import {ALL_EXTENSIONS} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/extensions/dist/index.js';
import {mergeDocuments,unpartition} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/functions/dist/index.js';
import {MeshoptDecoder} from '../optimize/bm-tools/gltf/node_modules/meshoptimizer/index.js';
await MeshoptDecoder.ready;const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const backup='.bitmagic/city-exterior-backups/mirage-arrival/',base='build/strip-landmarks/';
const doc=await io.read(backup+'mirageExterior-exterior.glb'),extra=await io.read(base+'mirageArrival-exterior.glb');
const signature=n=>JSON.stringify({name:n.getName(),extras:n.getExtras(),matrix:n.getMatrix(),primitives:n.getMesh()?.listPrimitives().map(p=>({indices:p.getIndices()?Array.from(p.getIndices().getArray()):null,attributes:p.listSemantics().map(s=>[s,Array.from(p.getAttribute(s).getArray())]),material:p.getMaterial()?.getName()}))});
const removed=doc.getRoot().listNodes().filter(n=>n.getExtras().source==='arrival');assert.equal(removed.length,1);for(const n of removed)n.dispose();
const nodes=doc.getRoot().listNodes(),before=nodes.map(signature),map=mergeDocuments(doc,extra),scene=doc.getRoot().getDefaultScene();
for(const s of extra.getRoot().listScenes()){const copied=map.get(s);for(const n of copied.listChildren()){n.setExtras({...n.getExtras(),property:'mirageExterior'});scene.addChild(n);}copied.dispose();}
assert.deepEqual(nodes.map(signature),before);await doc.transform(unpartition());
for(const e of doc.getRoot().listExtensionsUsed())if(e.extensionName==='EXT_meshopt_compression')e.dispose();
await io.write(base+'mirageExterior-exterior.glb',doc);
const old=JSON.parse(fs.readFileSync(backup+'mirageExterior-exterior-collision.json')),add=JSON.parse(fs.readFileSync(base+'mirageArrival-exterior-collision.json')),offset=old.vertices.length/3;
const triKey=ps=>ps.map(p=>p.map(v=>Math.round(v*1e5)).join(',')).sort().join(';');
const oldKeys=new Set();
for(const [cx,cy,cz,w,h,d] of [[-43,6.3,-587.7,17,.7,28],[-36,3,-599.7,.7,6,.7],[-36,3,-575.7,.7,6,.7]]){
 const pts=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]].map(([x,y,z])=>[cx+x*w/2,cy+y*h/2,cz+z*d/2]);
 for(const [a,b,c,d]of [[0,3,2,1],[4,5,6,7],[0,4,7,3],[1,2,6,5],[3,7,6,2],[0,1,5,4]])for(const ids of [[a,b,c],[a,c,d]])oldKeys.add(triKey(ids.map(i=>pts[i])));
}
const kept=[];let removedCollision=0;
for(let i=0;i<old.indices.length;i+=3){const ids=old.indices.slice(i,i+3);if(oldKeys.has(triKey(ids.map(j=>old.vertices.slice(j*3,j*3+3)))))removedCollision++;else kept.push(...ids);}
assert.equal(removedCollision,36,'only the old canopy slab and two posts may be removed');
const collision={...old,vertices:old.vertices.concat(add.vertices),indices:kept.concat(add.indices.map(i=>i+offset))};
fs.writeFileSync(base+'mirageExterior-exterior-collision.json',JSON.stringify(collision));
const report={preservedNodes:nodes.length,preservedNodeGeometry:true,removedArrivalNodes:removed.length,removedCollisionTriangles:removedCollision,preservedCollisionTriangles:kept.length/3,addedCollisionTriangles:add.indices.length/3,scope:'Only source arrival node and exact 36 old canopy triangles replaced; every other node and collision triangle preserved.'};
fs.writeFileSync('docs/project-records/mirage-arrival/preservation.json',JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(base+'version.json',JSON.stringify({revision:crypto.createHash('sha256').update(fs.readFileSync(base+'mirageExterior-exterior.glb')).digest('hex').slice(0,16)}));console.log(report);
