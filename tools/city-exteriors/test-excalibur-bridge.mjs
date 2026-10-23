import fs from 'node:fs';import assert from 'node:assert/strict';import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0});
for(const c of read('build/geographic-strip/city-colliders.json'))if(c.indices.length)world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
world.step();const checks=read('build/city-exteriors/excalibur-existing-bridge-support.json').samples;const failed=[];
for(const r of checks){const [x,y,z]=r.point;const hit=world.castRay(new RAPIER.Ray({x,y:y+1,z},{x:0,y:-1,z:0}),1.5,true);if(!hit||Math.abs((y+1-hit.timeOfImpact)-y)>.25)failed.push({point:r.point,hit:hit?.timeOfImpact});}
const report={samples:checks.length,failed};fs.writeFileSync('build/city-exteriors/excalibur-bridge-test.json',JSON.stringify(report,null,2));console.log(report);world.free();assert.equal(failed.length,0);
