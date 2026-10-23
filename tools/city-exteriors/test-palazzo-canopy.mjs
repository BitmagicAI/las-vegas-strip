import fs from 'node:fs';import assert from 'node:assert/strict';import RAPIER from '@dimforge/rapier3d-compat';
await RAPIER.init();const w=new RAPIER.World({x:0,y:-9.81,z:0});
const add=c=>w.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
for(const c of JSON.parse(fs.readFileSync('build/geographic-strip/city-colliders.json'))){if(Math.hypot(c.center[0]-321,c.center[1]+887)<180)add(c);}
for(const c of JSON.parse(fs.readFileSync('build/geographic-strip/detailed.mesh-level.json')).colliders){
 if(c.vertices){const v=new Float32Array(c.vertices);const d=c.indices?RAPIER.ColliderDesc.trimesh(v,new Uint32Array(c.indices)):RAPIER.ColliderDesc.convexHull(v);if(d)w.createCollider(d);}
}
add(JSON.parse(fs.readFileSync('build/strip-landmarks/palazzo-exterior-collision.json')));w.step();
const yaw=Math.atan2(28.327,15.295),co=Math.cos(yaw),si=Math.sin(yaw),failed=[];let count=0;
// Approximate center, inset well clear of perimeter columns. Ensure real road
// support and 3m vehicle headroom, rather than only testing the new mesh alone.
for(let x=-10;x<=10;x+=2)for(let z=-10;z<=10;z+=2){
 const p={x:321.17+co*x+si*z,y:2,z:-887.47-si*x+co*z};
 const floor=w.castRay(new RAPIER.Ray(p,{x:0,y:-1,z:0}),3,true);
 const roof=w.castRay(new RAPIER.Ray(p,{x:0,y:1,z:0}),3,true);count++;
 if(!floor||roof)failed.push({p,floor:floor?.timeOfImpact,roof:roof?.timeOfImpact});
}
const r={samples:count,failed,scope:'Combined current city and canopy collision: central driveway support and headroom. Does not establish full driving route.'};
fs.writeFileSync('build/city-exteriors/palazzo-canopy-test.json',JSON.stringify(r,null,2));console.log(r);w.free();assert.equal(failed.length,0);
