import fs from 'node:fs';import R from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));await R.init();const world=new R.World({x:0,y:-9.81,z:0});
const sources=[...read('build/geographic-strip/city-colliders.json'),...read('src/work/geographic/level.json').colliders,read('build/strip-landmarks/planetHollywood-exterior-collision.json')];
const owners=new Map();for(const [i,c] of sources.entries())if(c.vertices?.length&&c.indices?.length){const h=world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));owners.set(h.handle,c.name??`collision entry ${i}`);}
world.step();const failures=[],points=read('build/city-exteriors/harmon-terrace-points.json');
for(const p of points){
 const floor=world.castRay(new R.Ray({x:p.x,y:p.y+.15,z:p.z},{x:0,y:-1,z:0}),.3,true);
 const head=world.castRay(new R.Ray({x:p.x,y:p.y+.2,z:p.z},{x:0,y:1,z:0}),1.6,true);
 if(!floor||Math.abs(floor.timeOfImpact-.15)>.045||head)failures.push({...p,floor:floor?.timeOfImpact,head:head?.timeOfImpact,headOwner:head?owners.get(head.collider.handle):undefined,floorOwner:floor?owners.get(floor.collider.handle):undefined});
}
fs.writeFileSync('build/city-exteriors/harmon-terrace-results.json',JSON.stringify({samples:points.length,failures},null,2));console.log({samples:points.length,failures:failures.length,first:failures.slice(0,10)});world.free();if(failures.length)process.exitCode=1;
