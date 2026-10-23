import fs from 'node:fs';import assert from 'node:assert/strict';import RAPIER from '@dimforge/rapier3d-compat';
await RAPIER.init();const w=new RAPIER.World({x:0,y:-9.81,z:0});
for(const p of ['build/strip-landmarks/trumpExterior-exterior-collision.json','build/highrises/trump-collision.json']){const c=JSON.parse(fs.readFileSync(p));w.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));}w.step();
const failures=[];let samples=0;
for(let x=10;x<=50;x+=5)for(let z=-1448;z<=-1440;z+=2){samples++;const h=w.castRay(new RAPIER.Ray({x,y:4.5,z},{x:0,y:-1,z:0}),4.0,true);if(h)failures.push({x,z,toi:h.timeOfImpact});}
const r={samples,failures,scope:'New exterior and retained highrise collision only; arrival overhead clearance, not entire city routes.'};fs.writeFileSync('build/city-exteriors/trump-clearance.json',JSON.stringify(r,null,2));w.free();console.log(r);assert.equal(failures.length,0);
