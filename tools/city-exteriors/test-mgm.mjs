import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));
const meta=read('build/strip-landmarks/venues.json').filter(v=>v.key==='mgmGrand');
assert.equal(meta.length,1);assert(meta[0].exteriorOnly);assert.equal(meta[0].lights.length,0);
await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0});
for(const c of [...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/mgmGrand-exterior-collision.json')]){
 if(!c.indices.length)continue;
 world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
}
world.step();const capsule=new RAPIER.Capsule(.65,.29),q={x:0,y:0,z:0,w:1};
const blocked=[];let samples=0;
// The through lane under the mapped octagonal canopy; centreline avoids columns.
for(let t=-20;t<=20;t+=.5){const x=411+t*.70710678,z=1593-t*.70710678;samples++;
 const hit=world.intersectionWithShape({x,y:1.4,z},q,capsule);if(hit)blocked.push({x,z});
}
const report={canopySamples:samples,blocked,newColliderTriangles:read('build/strip-landmarks/mgmGrand-exterior-collision.json').indices.length/3};
fs.writeFileSync('build/city-exteriors/mgm-collision.json',JSON.stringify(report,null,2));
console.log(report);world.free();assert.equal(blocked.length,0,'Canopy lane obstructed');
