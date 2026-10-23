import fs from 'node:fs';
import assert from 'node:assert/strict';
import {colliderVertices} from '../../src/work/hotels/HotelGeometry.ts';
import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));
const v=read('build/strip-landmarks/venues.json').filter(v=>v.key==='planetHollywood');
assert.equal(v.length,1);assert(v[0].exteriorOnly);assert.equal(v[0].lights.length,0);
const c=read('build/strip-landmarks/planetHollywood-exterior-collision.json');
await RAPIER.init();const w=new RAPIER.World({x:0,y:-9.81,z:0});
w.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));w.step();
const checks=[];
for(const [x,z,y] of [[43,551,2.64],[37.8,572,1.3066667],[40,585,.6763636]]){
 const hit=w.castRay(new RAPIER.Ray({x,y:10,z},{x:0,y:-1,z:0}),10,true);assert(hit,`Missing terrace/stair at ${x},${z}`);const actual=10-hit.timeOfImpact;assert(Math.abs(actual-y)<.07,`Floor ${actual}, expected ${y}`);checks.push({x,z,y,actual});
}
const capsule=new RAPIER.Capsule(.65,.29),q={x:0,y:0,z:0,w:1};
for(let z=533;z<774;z++)assert(!w.intersectionWithShape({x:24,y:1.2,z},q,capsule),`Blocked sidewalk at ${z}`);
for(let x=28;x<58;x++)assert(!w.intersectionWithShape({x,y:1.2,z:655.15},q,capsule),`New entrance obstacle at ${x}`);
assert(c.indices.length/3<500,'Decorative facade detail must not create collision');
const report={checks,collisionTriangles:c.indices.length/3,sidewalkSamples:241,entrySamples:30,scope:'New exterior collider only. Existing city/legacy collision must also be checked in game.'};
fs.mkdirSync('build/city-exteriors',{recursive:true});fs.writeFileSync('build/city-exteriors/planet-collision.json',JSON.stringify(report,null,2));console.log(report);
const names=new Map();
for(const [path,prefix] of [['build/geographic-strip/city-colliders.json','city'],['build/geographic-strip/detailed.mesh-level.json','legacy']]){
 const data=read(path);for(const c of data.colliders??data){
  const vs=c.shape?colliderVertices(c):c.vertices;
  let minX=Infinity,maxX=-Infinity,minZ=Infinity,maxZ=-Infinity;
  for(let i=0;i<vs.length;i+=3){minX=Math.min(minX,vs[i]);maxX=Math.max(maxX,vs[i]);minZ=Math.min(minZ,vs[i+2]);maxZ=Math.max(maxZ,vs[i+2]);}
  if(maxX<15||minX>100||maxZ<530||minZ>780)continue;
  const desc=c.indices?RAPIER.ColliderDesc.trimesh(new Float32Array(vs),new Uint32Array(c.indices)):RAPIER.ColliderDesc.convexHull(new Float32Array(vs));
  if(desc){const collider=w.createCollider(desc);names.set(collider.handle,prefix+' '+(c.name??c.id));}
 }
}
w.step();const combined=[];
for(let x=28;x<94;x+=.5){
 const z=655.15;const hit=w.intersectionWithShape({x,y:1.34,z},q,capsule);
 const floor=w.castRay(new RAPIER.Ray({x,y:.6,z},{x:0,y:-1,z:0}),1,true);
 if(hit||!floor)combined.push({x,z,blocker:hit?names.get(hit.handle)??'new-exterior':null,floor:floor?.timeOfImpact});
}
fs.writeFileSync('build/city-exteriors/planet-combined-collision.json',JSON.stringify({samples:132,failures:combined},null,2));
console.log('Combined city entrance failures',combined.slice(0,15));w.free();
