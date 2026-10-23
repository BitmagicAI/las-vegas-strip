import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';await R.init();
const c=JSON.parse(fs.readFileSync('build/strip-landmarks/caesarsExterior-exterior-collision.json')),w=new R.World({x:0,y:-9.81,z:0});w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));w.step();const failures=[];let sampled=0;
const ray=(x,y,z,d)=>w.castRay(new R.Ray({x,y,z},{x:0,y:-1,z:0}),d,true);
// Pools must have floors below water and no accidental solid sheet at water level.
for(const [name,x,z] of [['temple',-349.5+12,-3.5],['venus',-397,-44],['jupiter',-454,-48],['apollo',-453,35],['neptune',-397,-4],['fortuna',-426,-4],['bacchus-north',-461,-13],['bacchus-south',-461,7]]){
 for(let a=-.6;a<=.6;a+=.3)for(let b=-.6;b<=.6;b+=.3){sampled++;const hit=ray(x+a,10.1,z+b,2);if(!hit||Math.abs(hit.timeOfImpact-1.35)>.03)failures.push({name,x:x+a,z:z+b,hit:hit?.timeOfImpact});}}
// Open walkways sampled away from the columns/furniture, at their authored datum.
for(const [x,z,dx,dz] of [[-438,-60,0,1],[-424,-24,1,0],[-424,18,1,0]])for(let i=0;i<=35;i++){sampled++;const h=ray(x+dx*i,10.4,z+dz*i,1);if(!h||Math.abs(h.timeOfImpact-.2)>.06)failures.push({kind:'deck-support',x:x+dx*i,z:z+dz*i,hit:h?.timeOfImpact});}
const report={sampled,failures,scope:'New pool basins and selected deck paths. Full interior-to-pool access and surrounding collision remain unverified.'};fs.writeFileSync('build/city-exteriors/caesars-pool-test.json',JSON.stringify(report,null,2));console.log(report);w.free();assert.equal(failures.length,0);
