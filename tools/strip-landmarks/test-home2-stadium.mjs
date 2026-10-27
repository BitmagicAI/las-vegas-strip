// Scoped public-route check, with the current surrounding city collision.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));
assert(!read('build/geographic-strip/building-index.json').some(b=>['way/790044913'].includes(b.id)));
await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0});
for(const c of [...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/home2-stadium-exterior-collision.json'),read('build/strip-landmarks/home2-stadium-interior-collision.json')]){
 const body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());
 world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)),body);
}
world.step();
const meta=read('build/strip-landmarks/home2-stadium-metadata.json'),failures=[];let checks=0;
for(const route of meta.routes)for(let k=1;k<route.points.length;k++){
 const a=route.points[k-1],b=route.points[k],n=Math.ceil(Math.hypot(...b.map((v,i)=>v-a[i]))/.3);
 for(let i=0;i<=n;i++){
  const [x,y,z]=a.map((v,j)=>v+(b[j]-v)*i/n);checks++;
  const hit=world.intersectionWithShape({x,y:y+1.1,z},{x:0,y:0,z:0,w:1},new RAPIER.Capsule(.65,.29));
  const floor=world.castRay(new RAPIER.Ray({x,y:y+.25,z},{x:0,y:-1,z:0}),.55,true);
  if(hit||!floor)failures.push({x,y,z,blocked:!!hit,floor:!!floor});
 }
}
world.free();const result={checks,failures,city:true};
fs.writeFileSync('build/strip-landmarks/home2-stadium-route-audit.json',JSON.stringify(result,null,2));
console.log(result);assert.equal(failures.length,0);
