import fs from 'node:fs';
import assert from 'node:assert/strict';
import R from '@dimforge/rapier3d-compat';
await R.init();
const c=JSON.parse(fs.readFileSync('build/strip-landmarks/northStripMotels-exterior-collision.json'));
const world=new R.World({x:0,y:-9.81,z:0});
world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));world.step();
const angle=-20*Math.PI/180,failures=[];let samples=0;
for(const z of [-4,4])for(let x=-7;x<=7;x+=.5){
 const px=1557+x*Math.cos(angle)-z*Math.sin(angle),pz=-3263+x*Math.sin(angle)+z*Math.cos(angle);
 const hit=world.castRay(new R.Ray({x:px,y:.63,z:pz},{x:0,y:-1,z:0}),.1,true);samples++;
 if(!hit||Math.abs(hit.timeOfImpact-.05)>.01)failures.push({x:px,z:pz,toi:hit?.timeOfImpact});
}
const report={samples,failures,scope:'Support along both long coping sides at 0.5 m intervals; does not establish pool enclosure or whole-court access.'};
fs.writeFileSync('build/city-exteriors/north-strip-pool-support.json',JSON.stringify(report,null,2));
world.free();console.log(report);assert.equal(failures.length,0);
