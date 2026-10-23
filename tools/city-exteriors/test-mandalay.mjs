import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));
const meta=read('build/strip-landmarks/venues.json').filter(v=>v.key==='mandalayExterior');
assert.equal(meta.length,1);assert(meta[0].exteriorOnly);assert.equal(meta[0].lights.length,0);
await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0});
for(const c of [...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/mandalayExterior-exterior-collision.json')]){
 if(c.indices.length)world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
}
world.step();const capsule=new RAPIER.Capsule(.65,.29),q={x:0,y:0,z:0,w:1},blocked=[];
const points=[[-119,2620],[-119,2650],[-105,2670],[-85,2683]];let samples=0;
for(let j=1;j<points.length;j++)for(let i=0;i<=40;i++){
 const t=i/40,x=points[j-1][0]*(1-t)+points[j][0]*t,z=points[j-1][1]*(1-t)+points[j][1]*t;samples++;
 if(world.intersectionWithShape({x,y:1.4,z},q,capsule))blocked.push({x,z});
}
const report={samples,blocked,colliderTriangles:read('build/strip-landmarks/mandalayExterior-exterior-collision.json').indices.length/3};
fs.writeFileSync('build/city-exteriors/mandalay-collision.json',JSON.stringify(report,null,2));world.free();console.log(report);assert.equal(blocked.length,0,'Arrival canopy obstructs through lane');
