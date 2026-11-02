// Append courtyard studies; existing building, roads and interior geometry is preserved.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {NodeIO} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/core/dist/index.js';
import {ALL_EXTENSIONS} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/extensions/dist/index.js';
import {mergeDocuments,unpartition} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/functions/dist/index.js';
import {MeshoptDecoder} from '../optimize/bm-tools/gltf/node_modules/meshoptimizer/index.js';
import {encodeCollision} from '../optimize/pack-data.mjs';
await MeshoptDecoder.ready;const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const base='build/strip-landmarks/',backup='.bitmagic/city-exterior-backups/westin-platinum-amenities/';fs.mkdirSync(backup,{recursive:true});
for(const [key,addition] of [['westin','westinAmenities'],['platinum','platinumAmenities']]){
 for(const suffix of ['.glb','-collision.json']){const f=key+'-exterior'+suffix;if(!fs.existsSync(backup+f))fs.copyFileSync(base+f,backup+f);}
 const doc=await io.read(backup+key+'-exterior.glb'),extra=await io.read(base+addition+'-exterior.glb');
 const signature=n=>JSON.stringify({name:n.getName(),extras:n.getExtras(),matrix:n.getMatrix(),primitives:n.getMesh()?.listPrimitives().map(p=>({indices:p.getIndices()?Array.from(p.getIndices().getArray()):null,attributes:p.listSemantics().map(s=>[s,Array.from(p.getAttribute(s).getArray())]),material:p.getMaterial()?.getName()}))});
 const mats=key==='westin'?['Strip / we-chair','Strip / we-coping','Strip / westin_pool']:['Strip / pt-chair','Strip / pt-coping','Strip / platinum_pool'];
 const removed=doc.getRoot().listNodes().filter(n=>n.getMesh()?.listPrimitives().every(p=>mats.includes(p.getMaterial()?.getName())));assert.equal(removed.length,3);for(const n of removed)n.dispose();
 const nodes=doc.getRoot().listNodes(),before=nodes.map(signature),map=mergeDocuments(doc,extra),scene=doc.getRoot().getDefaultScene();
 for(const s of extra.getRoot().listScenes()){const copied=map.get(s);for(const n of copied.listChildren()){n.setExtras({...n.getExtras(),property:key+'-exterior'});scene.addChild(n);}copied.dispose();}
 assert.deepEqual(nodes.map(signature),before);await doc.transform(unpartition());
 for(const e of doc.getRoot().listExtensionsUsed())if(e.extensionName==='EXT_meshopt_compression')e.dispose();
 await io.write(base+key+'-exterior.glb',doc);
 const old=JSON.parse(fs.readFileSync(backup+key+'-exterior-collision.json')),add=JSON.parse(fs.readFileSync(base+addition+'-exterior-collision.json')),offset=old.vertices.length/3;
 const kept=[];let removedCollision=0;
 for(let i=0;i<old.indices.length;i+=3){const ids=old.indices.slice(i,i+3);const hit=ids.every(j=>{const x=old.vertices[3*j],y=old.vertices[3*j+1],z=old.vertices[3*j+2];return key==='westin'?Math.abs(y-7.66)<.0001&&x>=595.44&&x<=603.56&&z>=97.44&&z<=108.56:Math.abs(y-12.53)<.0001&&x>=875.54&&x<=884.46&&z>=252.54&&z<=268.46;});if(hit)removedCollision++;else kept.push(...ids);}
 assert(removedCollision>0&&removedCollision<100);
 const collision={...old,vertices:old.vertices.concat(add.vertices),indices:kept.concat(add.indices.map(i=>i+offset))};
 assert.deepEqual(collision.indices.slice(0,kept.length),kept);assert.deepEqual(collision.vertices.slice(0,old.vertices.length),old.vertices);
 fs.writeFileSync(base+key+'-exterior-collision.json',JSON.stringify(collision));fs.writeFileSync(base+key+'-exterior-collision.bin',await encodeCollision([collision]));
 const report={preservedNodes:nodes.length,preservedNodeGeometry:true,retainedCollisionTriangles:kept.length/3,addedCollisionTriangles:add.indices.length/3,removedNodes:removed.length,removedCollisionTriangles:removedCollision};
 fs.writeFileSync('docs/project-records/westin-platinum-amenities/'+key+'-preservation.json',JSON.stringify(report,null,2)+'\n');console.log(report);
}
fs.writeFileSync(base+'version.json',JSON.stringify({revision:crypto.createHash('sha256').update(fs.readFileSync(base+'westin-exterior.glb')).update(fs.readFileSync(base+'platinum-exterior.glb')).digest('hex').slice(0,16)}));

// Existing streamed venue loader applies InteriorLighting; no new light objects or runtime code.
const venues=JSON.parse(fs.readFileSync(base+'venues.json')),p=venues.find(v=>v.key==='platinum');assert(p);p.exteriorOnly=false;p.levelY=12.47;p.preloadDistance=38;p.accessPoints=[877,12.47,268.058];p.zones=[{origin:[882.0895,12.47,268.058],yaw:0,width:18.573,depth:11.457,height:3.4}];p.routes=JSON.parse(fs.readFileSync('docs/project-records/westin-platinum-amenities/platinum-routes.json'));fs.writeFileSync(base+'venues.json',JSON.stringify(venues));
const interior=JSON.parse(fs.readFileSync(base+'platinum-interior-collision.json'));fs.writeFileSync(base+'platinum-interior-collision.bin',await encodeCollision([interior]));
