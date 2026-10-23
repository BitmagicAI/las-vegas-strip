import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));await R.init();const world=new R.World({x:0,y:-9.81,z:0});
for(const c of [...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/mandalayExterior-exterior-collision.json')])if(c.indices.length)world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
world.step();const failures=[],points=read('build/city-exteriors/mandalay-pool-test-points.json');for(const p of points){
 const hit=world.castRay(new R.Ray({x:p.x,y:p.y+.8,z:p.z},{x:0,y:-1,z:0}),1.2,true);
 if(!hit||Math.abs(hit.timeOfImpact-.8)>.06)failures.push({...p,toi:hit?.timeOfImpact});
 const roof=world.castRay(new R.Ray({x:p.x,y:p.y+.9,z:p.z},{x:0,y:1,z:0}),2,true);
 if(roof)failures.push({...p,overhead:roof.timeOfImpact});
}
fs.writeFileSync('build/city-exteriors/mandalay-pool-collision.json',JSON.stringify({samples:points.length,failures},null,2));console.log({samples:points.length,failures:failures.length,first:failures.slice(0,5)});world.free();assert.equal(failures.length,0);
