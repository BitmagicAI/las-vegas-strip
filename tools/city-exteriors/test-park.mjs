import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));
const venue=read('build/strip-landmarks/venues.json').find(v=>v.key==='park'),portal=venue.portals[0];
const old=fs.readFileSync('build/city-exteriors/before/park/park-exterior-collision.json');
const oldCollision=JSON.parse(old),currentCollision=read('build/strip-landmarks/park-exterior-collision.json');
assert.deepEqual(currentCollision.vertices.slice(0,oldCollision.vertices.length),oldCollision.vertices,'Original collision vertices changed');
assert.deepEqual(currentCollision.indices.slice(0,oldCollision.indices.length),oldCollision.indices,'Original collision faces changed');
await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0});
for(const c of [...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/park-exterior-collision.json'),read('build/strip-landmarks/park-interior-collision.json')]){
 if(c.indices.length)world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
}
world.step();let samples=0;const failures=[],shape=new RAPIER.Capsule(.65,.29),q={x:0,y:0,z:0,w:1};
for(let d=-5;d<35;d+=.5){
 const x=portal.p[0]+Math.sin(portal.yaw)*d,z=portal.p[2]+Math.cos(portal.yaw)*d;
 const hit=world.intersectionWithShape({x,y:1.4,z},q,shape);samples++;if(hit)failures.push({x,z});
}
// Roof-only mapped part now has open sides; sample beneath the projection.
let canopySamples=0;for(let u=-976;u<=-964;u+=2)for(let v=892;v<=895;v+=1){
 const x=(u+v)*Math.SQRT1_2,z=(-u+v)*Math.SQRT1_2,p={x,y:1.4,z};
 const floor=world.castRay(new RAPIER.Ray(p,{x:0,y:-1,z:0}),2,true);const blocked=world.intersectionWithShape(p,q,shape);canopySamples++;if(!floor||blocked)failures.push({x,z,canopy:true,floor:!!floor,blocked});
}
const report={samples,canopySamples,failures,scope:'Existing public entry approach and centre aisle plus28open canopy floor/headroom samples; static collision only, dynamic doors excluded.'};
fs.writeFileSync('build/city-exteriors/park-collision.json',JSON.stringify(report,null,2));console.log(report);world.free();assert.equal(failures.length,0);
