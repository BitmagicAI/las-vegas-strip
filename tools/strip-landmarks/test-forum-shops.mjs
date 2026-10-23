// Missing-footprint regression: solid roofs on all four tiers, clear Strip
// sidewalk, and one exterior-only owner (no attempt to stream a missing interior).
import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));
const venues=read('build/strip-landmarks/venues.json');
const mall=venues.filter(v=>v.key==='forumShops');
assert.equal(mall.length,1);assert.equal(mall[0].exteriorOnly,true);
assert.equal(mall[0].zones.length,0);assert.equal(mall[0].lights.length,0);
const c=read('build/strip-landmarks/forumShops-exterior-collision.json');
await RAPIER.init();const w=new RAPIER.World({x:0,y:-9.81,z:0});
w.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
w.step();
const heights=[];
for(const [x,z,y] of [[-450,-330,12.8],[-280,-340,16.8],[-60,-400,24.4],[-40,-350,32]]){
 const hit=w.castRay(new RAPIER.Ray({x,y:60,z},{x:0,y:-1,z:0}),60,true);
 assert(hit,`Missing roof at ${x},${z}`);const actual=60-hit.timeOfImpact;
 assert(Math.abs(actual-y)<.01,`Wrong roof: ${actual}, expected ${y}`);heights.push({x,z,expected:y,actual});
}
const capsule=new RAPIER.Capsule(.65,.29),q={x:0,y:0,z:0,w:1};
let clear=0;
for(let z=-407;z<=-299;z+=.5){
 assert(!w.intersectionWithShape({x:18,y:1.15,z},q,capsule),`Mall blocks Strip sidewalk at ${z}`);clear++;
}
assert(c.indices.length/3<2500,'Ornament must not become collision');
const report={roofHeights:heights,sidewalkSamplesClear:clear,collisionTriangles:c.indices.length/3};
fs.writeFileSync('build/strip-landmarks/forum-collision-audit.json',JSON.stringify(report,null,2));
console.log(report);w.free();
