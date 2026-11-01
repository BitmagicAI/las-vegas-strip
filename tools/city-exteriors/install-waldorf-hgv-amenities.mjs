// Append the original pool deck amenities without regenerating existing Waldorf and HGV geometry or interiors.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {NodeIO} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/core/dist/index.js';
import {ALL_EXTENSIONS} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/extensions/dist/index.js';
import {mergeDocuments,unpartition} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/functions/dist/index.js';
import {MeshoptDecoder} from '../optimize/bm-tools/gltf/node_modules/meshoptimizer/index.js';
await MeshoptDecoder.ready;const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
for(const key of ['waldorf','hgvFlamingo']){
const backup='.bitmagic/city-exterior-backups/waldorf-hgv-amenities/',base='build/strip-landmarks/';
const doc=await io.read(backup+key+'.glb'),extra=await io.read(base+key+'Amenities-exterior.glb');
const signature=n=>JSON.stringify({name:n.getName(),extras:n.getExtras(),matrix:n.getMatrix(),primitives:n.getMesh()?.listPrimitives().map(p=>({indices:p.getIndices()?Array.from(p.getIndices().getArray()):null,attributes:p.listSemantics().map(s=>[s,Array.from(p.getAttribute(s).getArray())]),material:p.getMaterial()?.getName()}))});
const removed=doc.getRoot().listNodes().filter(n=>n.getExtras().source===(key==='waldorf'?'pool-deck':'courtyard'));assert.equal(removed.length,6);for(const n of removed)n.dispose();
const nodes=doc.getRoot().listNodes(),before=nodes.map(signature),map=mergeDocuments(doc,extra),scene=doc.getRoot().getDefaultScene();
for(const s of extra.getRoot().listScenes()){const copied=map.get(s);for(const n of copied.listChildren()){n.setExtras({...n.getExtras(),property:key+'Exterior'});scene.addChild(n);}copied.dispose();}
assert.deepEqual(nodes.map(signature),before);await doc.transform(unpartition());
for(const e of doc.getRoot().listExtensionsUsed())if(e.extensionName==='EXT_meshopt_compression')e.dispose();
await io.write(base+key+'Exterior-exterior.glb',doc);
const old=JSON.parse(fs.readFileSync(backup+key+'-collision.json')),add=JSON.parse(fs.readFileSync(base+key+'Amenities-exterior-collision.json')),offset=old.vertices.length/3;
const kept=[];let removedCollision=0;
for(let i=0;i<old.indices.length;i+=3){const ids=old.indices.slice(i,i+3);const within=ids.every(j=>{const x=old.vertices[3*j],y=old.vertices[3*j+1],z=old.vertices[3*j+2];return key==='waldorf' ? x>=-210.01&&x<=-99.99&&z>=1039.99&&z<=1140.01&&[25.6,26.92,27.08,27.11,27.1,28.2].some(v=>Math.abs(y-v)<.0001) : y>=-1.1001&&y<=.2901&&x>=313.99&&x<=354.01&&z>=-135.01&&z<=-98.99;});if(within)removedCollision++;else kept.push(...ids);}
assert(removedCollision>0&&removedCollision<old.indices.length/3,'Bounded pool-only collision removal expected');
const collision={...old,vertices:old.vertices.concat(add.vertices),indices:kept.concat(add.indices.map(i=>i+offset))};
fs.writeFileSync(base+key+'Exterior-exterior-collision.json',JSON.stringify(collision));
const {encodeCollision}=await import('../optimize/pack-data.mjs');fs.writeFileSync(base+key+'Exterior-exterior-collision.bin',await encodeCollision([collision]));
const report={preservedNodes:nodes.length,preservedNodeGeometry:true,oldCollisionTriangles:old.indices.length/3,addedCollisionTriangles:add.indices.length/3,removedPoolNodes:removed.length,removedPoolCollisionTriangles:removedCollision,retainedCollisionTriangles:kept.length/3,scope:'Replace pool nodes and bounded pool collision; preserve tower, podium, arrival and guest routes.'};
fs.writeFileSync('docs/project-records/waldorf-hgv-amenities/'+key+'-preservation.json',JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(base+'version.json',JSON.stringify({revision:crypto.createHash('sha256').update(fs.readFileSync(base+key+'Exterior-exterior.glb')).digest('hex').slice(0,16)}));console.log(report);

}
