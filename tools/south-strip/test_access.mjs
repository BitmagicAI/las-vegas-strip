import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
import * as THREE from 'three';
import {CoasterTrack} from '../../build/south-strip/test/CoasterTrack.js';
await RAPIER.init();
const read=p=>JSON.parse(fs.readFileSync(p));
const world=new RAPIER.World({x:0,y:-9.81,z:0}),names=new Map();
function add(c,name){
 const body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());
 const collider=world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)),body);
 names.set(collider.handle,name);
}
for(const c of read('build/geographic-strip/city-colliders.json'))add(c,'city '+c.id);
add(read('build/highrises/new-york-collision.json'),'New York exterior');
add(read('build/south-strip/coaster-collision.json'),'coaster station');
world.step();
const route=read('build/south-strip/route.json');
const waypoints=route.access.map(([x,y,z])=>({x,y,z}));
const failures=[];let checks=0;
const capsule=new RAPIER.Capsule(.75,.3),q={x:0,y:0,z:0,w:1};
for(let k=1;k<waypoints.length;k++){
 const a=waypoints[k-1],b=waypoints[k],n=Math.ceil(Math.hypot(b.x-a.x,b.y-a.y,b.z-a.z)/.3);
 for(let i=0;i<=n;i++){
  const t=i/n,p={x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t,z:a.z+(b.z-a.z)*t};
  const hit=world.intersectionWithShape({...p,y:p.y+1.18},q,capsule);
  const floor=world.castRay(new RAPIER.Ray({...p,y:p.y+.15},{x:0,y:-1,z:0}),.4,true);
  checks++;if(hit||!floor)failures.push({p,blocker:hit?names.get(hit.handle):null,floor:!!floor});
 }
}
const ids=new Set(read('build/south-strip/replacement-ids.json'));
assert(!read('build/geographic-strip/building-index.json').some(b=>ids.has(b.id)),'overlapping OSM source mesh');
const track=new CoasterTrack(route),position=new THREE.Vector3(),rotation=new THREE.Quaternion(),up=new THREE.Vector3(),seat=new RAPIER.Capsule(.35,.65);
const rideFailures=[];let rideChecks=0;
for(let s=0;s<route.length;s+=2){
 track.sample(s,position,rotation);position.add(up.set(0,1.15,0).applyQuaternion(rotation));
 const hit=world.intersectionWithShape(position,rotation,seat);rideChecks++;
 if(hit)rideFailures.push({distance:s,position:position.toArray(),blocker:names.get(hit.handle)});
}
world.free();
fs.writeFileSync('build/south-strip/access-audit.json',JSON.stringify({checks,failures,rideChecks,rideFailures},null,2));
console.log({checks,failures:failures.slice(0,10),rideChecks,rideFailures:rideFailures.slice(0,10)});
assert.equal(failures.length,0,'blocked station route; see access-audit.json');
assert.equal(rideFailures.length,0,'ride passes through a building; see access-audit.json');
