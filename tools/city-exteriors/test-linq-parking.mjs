import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';await R.init();
const w=new R.World({x:0,y:-9.81,z:0});const c=JSON.parse(fs.readFileSync('build/strip-landmarks/linqParking-exterior-collision.json'));w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));for(const cell of JSON.parse(fs.readFileSync('build/geographic-strip/city-colliders.json'))){if(Math.abs(cell.center[0]-354)>90||Math.abs(cell.center[1]+274)>90)continue;w.createCollider(R.ColliderDesc.trimesh(new Float32Array(cell.vertices),new Uint32Array(cell.indices)));}w.step();const failures=[];let samples=0;
function sample(x,y,z){samples++;const floor=w.castRay(new R.Ray({x,y:y+.05,z},{x:0,y:-1,z:0}),.1,true);if(!floor||Math.abs(floor.timeOfImpact-.05)>.02)failures.push({kind:'floor',x,y,z});if(w.castRay(new R.Ray({x,y:y+.1,z},{x:0,y:1,z:0}),2.5,true))failures.push({kind:'headroom',x,y,z});}
const pitch=(20-.24)/6;
for(let level=0;level<5;level++){
 for(let z=-300.5;z<-263;z+=.5)sample(353.5,.24+level*pitch+(z+301)/38*pitch,z);
 for(let z=-305;z<-259;z++)sample(362,.24+level*pitch,z);
 for(let x=353.5;x<362;x+=.5){sample(x,.24+level*pitch,-304);sample(x,.24+(level+1)*pitch,-260);}
}
for(let x=362;x<379;x+=.5)sample(x,.24,-274);
const report={samples,failures,scope:'Garage and nearby city collision: ramp support, 2.5m headroom, floor return lanes and eastern entrance. External city boundary inspected separately.'};fs.writeFileSync('build/city-exteriors/linq-parking-collision-test.json',JSON.stringify(report,null,2));console.log(report);w.free();assert.equal(failures.length,0);
