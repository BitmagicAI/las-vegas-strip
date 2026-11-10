// Append the original pool deck amenities without regenerating existing Panorama and Martin geometry or interiors.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {NodeIO} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/core/dist/index.js';
import {ALL_EXTENSIONS} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/extensions/dist/index.js';
import {mergeDocuments,unpartition} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/functions/dist/index.js';
import {MeshoptDecoder} from '../optimize/bm-tools/gltf/node_modules/meshoptimizer/index.js';
await MeshoptDecoder.ready;const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
for(const key of ['panorama','martin']){
const backup='.bitmagic/city-exterior-backups/panorama-martin-amenities/',base='build/strip-landmarks/';
const doc=await io.read(backup+key+'.glb'),extra=await io.read(base+key+'Amenities-exterior.glb');
const signature=n=>JSON.stringify({name:n.getName(),extras:n.getExtras(),matrix:n.getMatrix(),primitives:n.getMesh()?.listPrimitives().map(p=>({indices:p.getIndices()?Array.from(p.getIndices().getArray()):null,attributes:p.listSemantics().map(s=>[s,Array.from(p.getAttribute(s).getArray())]),material:p.getMaterial()?.getName()}))});
const removed=doc.getRoot().listNodes().filter(n=>n.getExtras().source===(key==='panorama'?'pool-courts':'pool-court')&&n.getName()!=='THE MARTIN');assert.equal(removed.length,4);for(const n of removed)n.dispose();
const nodes=doc.getRoot().listNodes(),before=nodes.map(signature),map=mergeDocuments(doc,extra),scene=doc.getRoot().getDefaultScene();
for(const s of extra.getRoot().listScenes()){const copied=map.get(s);for(const n of copied.listChildren()){n.setExtras({...n.getExtras(),property:key+'Exterior'});scene.addChild(n);}copied.dispose();}
assert.deepEqual(nodes.map(signature),before);await doc.transform(unpartition());
for(const e of doc.getRoot().listExtensionsUsed())if(e.extensionName==='EXT_meshopt_compression')e.dispose();
await io.write(base+key+'Exterior-exterior.glb',doc);
const old=JSON.parse(fs.readFileSync(backup+key+'-collision.json')),add=JSON.parse(fs.readFileSync(base+key+'Amenities-exterior-collision.json')),offset=old.vertices.length/3;
const kept=[];let removedCollision=0;
for(let i=0;i<old.indices.length;i+=3){const ids=old.indices.slice(i,i+3);const within=ids.every(j=>{const x=old.vertices[3*j],y=old.vertices[3*j+1],z=old.vertices[3*j+2];return key==='panorama' ? y>=.009&&y<=.35&&x>=-901.01&&x<=-870.99&&[935,1024].some(cz=>z>=cz-22.01&&z<=cz+22.01) : y>=-1.11&&y<=1.46&&x>=-909.01&&x<=-884.99&&z>=819.99&&z<=855.01;});if(within)removedCollision++;else kept.push(...ids);}
assert(removedCollision>0&&removedCollision<old.indices.length/3,'Bounded pool-only collision removal expected');
const collision={...old,vertices:old.vertices.concat(add.vertices),indices:kept.concat(add.indices.map(i=>i+offset))};
fs.writeFileSync(base+key+'Exterior-exterior-collision.json',JSON.stringify(collision));
const report={preservedNodes:nodes.length,preservedNodeGeometry:true,oldCollisionTriangles:old.indices.length/3,addedCollisionTriangles:add.indices.length/3,removedPoolNodes:removed.length,removedPoolCollisionTriangles:removedCollision,retainedCollisionTriangles:kept.length/3,scope:'Replace four pool nodes and bounded pool collision; preserve tower, podium, existing identity sign and guest routes.'};
fs.writeFileSync('docs/project-records/panorama-martin-amenities/'+key+'-preservation.json',JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(base+'version.json',JSON.stringify({revision:crypto.createHash('sha256').update(fs.readFileSync(base+key+'Exterior-exterior.glb')).digest('hex').slice(0,16)}));console.log(report);

}
