import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';
import {geometryScene} from './hotel-test-geometry.mjs';
import {colliderVertices} from '../src/work/hotels/HotelGeometry.ts';

const doors=JSON.parse(fs.readFileSync('build/level/vegas.doors.json')).filter(d=>['bellagio_south_entrance','bellagio_north_gallery_exit','bellagio_lobby_service','bellagio_casino_service'].includes(d.id));
let visualChecks=0,walkingChecks=0;
for(const path of ['build/level/vegas.glb','build/hotels/staged-vegas.glb']){
 const scene=geometryScene(path),meshes=[];
 scene.traverse(o=>{if(o.isMesh && /_b_|_ba_/.test(o.parent.name))meshes.push(o);});
 const ray=new THREE.Raycaster();ray.far=2;
 for(const d of doors)for(const y of [.18,.30,.7,1.12,1.6,2.1])for(const fraction of [-.44,-.25,0,.25,.44])for(const sign of [-1,1]){
  const yaw=d.rotationY??0,nx=Math.sin(yaw),nz=Math.cos(yaw),tx=Math.cos(yaw),tz=-Math.sin(yaw);
  ray.set(new THREE.Vector3(d.position.x-sign*nx+fraction*d.width*tx,y,d.position.z-sign*nz+fraction*d.width*tz),new THREE.Vector3(sign*nx,0,sign*nz));
  const hit=ray.intersectObjects(meshes,false)[0];
  assert(!hit,`${path} ${d.id}: visual obstruction at height ${y}, width ${fraction}: ${hit?.object.parent.name}`);visualChecks++;
 }
 for(const mat of new Set(meshes.map(m=>m.material)))mat.dispose();
 scene.traverse(o=>{if(o.isMesh)o.geometry.dispose();});
}
// Standing-player clearance through the real static world at the open leaves.
await RAPIER.init();const world=new RAPIER.World({x:0,y:0,z:0}),names=new Map();
for(const c of JSON.parse(fs.readFileSync('build/hotels/staged-vegas.mesh-level.json')).colliders){
 let body,desc;
 if(c.shape==='box'){
  const yaw=c.yaw??0;
  body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(...c.position).setRotation({x:0,y:Math.sin(yaw/2),z:0,w:Math.cos(yaw/2)}));
  desc=RAPIER.ColliderDesc.cuboid(...c.size.map(v=>v/2));
 }else{
  body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());const v=new Float32Array(colliderVertices(c));
  desc=c.shape==='trimesh'?RAPIER.ColliderDesc.trimesh(v,new Uint32Array(c.indices)):RAPIER.ColliderDesc.convexHull(v);
 }
 const collider=world.createCollider(desc,body);names.set(collider.handle,c.name);
}
world.step();const height=JSON.parse(fs.readFileSync('src/work/world.json')).worldProfileData.characterConfig.height;
const capsule=new RAPIER.Capsule(height/2-.30,.30),rotation={x:0,y:0,z:0,w:1};
for(const d of doors)for(const side of [-.6,0,.6])for(let i=-16;i<=16;i++){
 const yaw=d.rotationY??0;
 const p={x:d.position.x+i*.1*Math.sin(yaw)+side*Math.cos(yaw),y:.065+height/2,z:d.position.z+i*.1*Math.cos(yaw)-side*Math.sin(yaw)};
 const hit=world.intersectionWithShape(p,rotation,capsule);
 assert(!hit,`${d.id} blocked at ${JSON.stringify(p)} by ${hit?names.get(hit.handle):''}`);
 const floor=world.castRay(new RAPIER.Ray({...p,y:.20},{x:0,y:-1,z:0}),.30,true);
 assert(floor,`${d.id}: missing floor at ${p.x}/${p.z}`);walkingChecks++;
}
let arrivalChecks=0;
for(const route of [{start:[-155,-106],end:[-155,-73],axis:'x'}, {start:[-119.5,34],end:[-134,34],axis:'z'}]){
 for(const side of [-1.4,0,1.4])for(let i=0;i<=132;i++){
  const t=i/132,p={x:route.start[0]*(1-t)+route.end[0]*t,y:.08+height/2,z:route.start[1]*(1-t)+route.end[1]*t};p[route.axis]+=side;
  const hit=world.intersectionWithShape(p,rotation,capsule);
  assert(!hit,`Arrival route blocked at ${JSON.stringify(p)} by ${hit?names.get(hit.handle):''}`);
  const floor=world.castRay(new RAPIER.Ray({...p,y:.20},{x:0,y:-1,z:0}),.35,true);
  assert(floor,`Arrival route has no support at ${JSON.stringify(p)}`);arrivalChecks++;
 }
}
world.free();const report={visualChecks,walkingChecks,arrivalChecks,doors:doors.map(d=>d.id),passed:true};
fs.writeFileSync('build/hotels/bellagio-door-repair/test.json',JSON.stringify(report,null,2));console.log(report);
