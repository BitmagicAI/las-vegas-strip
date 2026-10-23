import fs from 'node:fs';import assert from 'node:assert/strict';import RAPIER from '@dimforge/rapier3d-compat';await RAPIER.init();const w=new RAPIER.World({x:0,y:-9.81,z:0});
const add=c=>w.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
for(const p of ['build/strip-landmarks/signatureExterior-exterior-collision.json','build/highrises/signature-collision.json'])add(JSON.parse(fs.readFileSync(p)));
for(const c of JSON.parse(fs.readFileSync('build/geographic-strip/city-colliders.json')))if(['3,5','3,6','3,7','4,5','4,6','4,7'].includes(c.id))add(c);w.step();
const points=JSON.parse(fs.readFileSync('build/city-exteriors/signature-clearance-points.json')),failures=[];
for(const [x,z]of points){const hit=w.castRay(new RAPIER.Ray({x,y:3.15,z},{x:0,y:-1,z:0}),2.5,true);if(hit)failures.push({x,z,toi:hit.timeOfImpact});}
const report={samples:points.length,failures,scope:'Mapped canopy clearance against new exterior, retained tower collision and surrounding city cell; not a full public route walk.'};fs.writeFileSync('build/city-exteriors/signature-clearance.json',JSON.stringify(report,null,2));w.free();console.log(report);assert.equal(failures.length,0);
