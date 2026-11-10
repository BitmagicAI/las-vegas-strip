import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';await R.init();
const world=new R.World({x:0,y:-9.81,z:0});
const c=JSON.parse(fs.readFileSync('build/strip-landmarks/grandDesert-exterior-collision.json'));
world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));world.step();
const model=JSON.parse(fs.readFileSync('build/strip-landmarks/grandDesert-exterior.json'));
let samples=0;const failures=[];
for(const g of model.meshes){if(!['gd-paving','gd-coping'].includes(g.material))continue;
 for(const f of g.faces){const a=g.vertices[f[0]],b=g.vertices[f[1]],d=g.vertices[f[2]];
  if(Math.abs((b[0]-a[0])*(d[2]-a[2])-(b[2]-a[2])*(d[0]-a[0]))<1e-7)continue;
  const x=(a[0]+b[0]+d[0])/3,y=(a[1]+b[1]+d[1])/3,z=(a[2]+b[2]+d[2])/3;
  const hit=world.castRay(new R.Ray({x,y:y+.03,z},{x:0,y:-1,z:0}),.06,true);samples++;
  if(!hit||Math.abs(hit.timeOfImpact-.03)>.015)failures.push({x,y,z,toi:hit?.timeOfImpact});
 }
}
world.free();const report={samples,failures,scope:'Pool deck/coping triangle support; does not establish public entrance access or pool safety.'};
fs.writeFileSync('build/city-exteriors/grand-desert-pool-support.json',JSON.stringify(report,null,2));console.log(report);assert.ok(samples>100);assert.equal(failures.length,0);
