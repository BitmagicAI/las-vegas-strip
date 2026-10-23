import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';
import {moduleMatrix,colliderVertices} from '../../src/work/hotels/HotelGeometry.ts';
import {worldPoint,bayPoint,roomAt,insideTower,roomId,guestVisibility} from '../../src/work/hotels/HotelLayout.ts';
const towers=JSON.parse(fs.readFileSync('src/work/hotels/highrise-towers.json'));
const selected=new Set(JSON.parse(fs.readFileSync('build/highrises/replacement-ids.json')));
assert(!JSON.parse(fs.readFileSync('build/geographic-strip/building-index.json')).some(b=>selected.has(b.id)),'source boxes still present');
await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0}),names=new Map();
function add(c,m=new THREE.Matrix4()){
 if(c.shape==='box' && m.equals(new THREE.Matrix4())){const b=world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(...c.position).setRotation({x:0,y:Math.sin(c.yaw/2),z:0,w:Math.cos(c.yaw/2)}));world.createCollider(RAPIER.ColliderDesc.cuboid(...c.size.map(v=>v/2)),b);names.set(b.handle,c.name);return b;}
 const vs=colliderVertices(c),v=[],p=new THREE.Vector3();
 for(let i=0;i<vs.length;i+=3){p.set(vs[i],vs[i+1],vs[i+2]).applyMatrix4(m);v.push(p.x,p.y,p.z);}
 const desc=c.shape==='trimesh'?RAPIER.ColliderDesc.trimesh(new Float32Array(v),new Uint32Array(c.indices)):RAPIER.ColliderDesc.convexHull(new Float32Array(v));
 assert(desc,'invalid collider '+c.name);const b=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());world.createCollider(desc,b);names.set(b.handle,c.name);return b;
}
for(const c of JSON.parse(fs.readFileSync('build/geographic-strip/detailed.mesh-level.json')).colliders)add(c);
for(const c of JSON.parse(fs.readFileSync('build/geographic-strip/city-colliders.json')))add({...c,shape:'trimesh',name:'city '+c.id});
for(const key of new Set(towers.map(t=>t.set)))add({...JSON.parse(fs.readFileSync(`build/highrises/${key}-collision.json`)),shape:'trimesh',name:'exterior '+key});
const read=name=>JSON.parse(fs.readFileSync(`build/hotels/${name}.mesh-level.json`));
function module(t,name,p={x:0,y:0,z:0},rotation=0){return read(name).colliders.map(c=>add(c,moduleMatrix(t,p,rotation,name.endsWith('-stair'))));}
const report={checks:0,failures:[],virtualRooms:0,properties:new Set(towers.map(t=>t.set)).size,towers:towers.length};
const capsule=new RAPIER.Capsule(.8,.3),q={x:0,y:0,z:0,w:1};
function probe(t,p,label){
 const w=worldPoint(t,p),center={...w,y:w.y+1.1};
 const hit=world.intersectionWithShape(center,q,capsule);
 const floor=world.castRay(new RAPIER.Ray({...w,y:w.y+.04},{x:0,y:-1,z:0}),.36,true);
 report.checks++;if(hit||!floor)report.failures.push({tower:t.id,label,p,blocker:hit?names.get(hit.parent().handle):null,floor:!!floor});
}
function route(t,a,b,label){const steps=Math.ceil(Math.hypot(b.x-a.x,b.y-a.y,b.z-a.z)/.3);for(let j=0;j<=steps;j++)probe(t,{x:a.x+(b.x-a.x)*j/steps,y:a.y+(b.y-a.y)*j/steps+.055,z:a.z+(b.z-a.z)*j/steps},label);}
for(const t of towers){
 const bodies=[...module(t,t.id+'-lobby'),...module(t,t.set+'-entry')];
 for(let f=0;f<4;f++)bodies.push(...module(t,t.set+'-stair',{x:0,y:f*3.6,z:0}));
 const f=t.firstGuestFloor;
 for(let b=0;b<t.bays;b++)bodies.push(...module(t,t.set+'-corridor',bayPoint(t,f,b)));
 world.step();
 route(t,{x:0,y:0,z:t.lobbyFront-3},{x:0,y:0,z:-3.65},'outside → lobby → stairs');
 for(let floor=0;floor<3;floor++){
  const y=floor*3.6;
  route(t,{x:-1.65,y,z:-2.5},{x:-1.65,y:y+1.8,z:2.5},'outbound flight');
  route(t,{x:-1.65,y:y+1.8,z:3.6},{x:1.65,y:y+1.8,z:3.6},'middle landing');
  route(t,{x:1.65,y:y+1.8,z:2.5},{x:1.65,y:y+3.6,z:-2.5},'return flight');
 }
 route(t,{x:0,y:f*3.6,z:-3.65},{x:0,y:f*3.6,z:-5.1-6*t.bays},'landing → corridor');
 for(const b of [0,t.bays-1])for(const side of [-1,1]){
  const p=bayPoint(t,f,b),rp={...p,x:side*1.85},room=module(t,t.set+'-room',rp,side>0?0:Math.PI);world.step();
  route(t,{...p,x:side*1.2},{...p,x:side*8.6},'door → bedroom → window');
  for(const body of room)world.removeRigidBody(body);
 }
 for(let floor=f;floor<t.floors;floor++)for(let b=0;b<t.bays;b++)for(const side of [-1,1]){
  const p=bayPoint(t,floor,b);p.x+=side*4;p.y+=.05;
  assert(insideTower(t,p));assert.equal(roomAt(t,p).bay,b);
  assert.equal(guestVisibility(t,floor,p,p,false,true).hideTower,t.source);
  assert(roomId(t,floor,b,side));report.virtualRooms++;
 }
 for(const body of bodies)world.removeRigidBody(body);
 console.log(t.id,report.failures.filter(e=>e.tower===t.id).length,'failures');
}
world.free();fs.writeFileSync('build/highrises/route-audit.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({...report,failures:report.failures.slice(0,12)},null,2));
assert.equal(report.failures.length,0,'see build/highrises/route-audit.json');
