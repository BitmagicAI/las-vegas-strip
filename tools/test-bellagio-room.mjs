import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';
import {roomAt,insideTower,bayPoint,DOOR_X,worldPoint,roomDepth} from '../src/work/hotels/HotelLayout.ts';
import {moduleMatrix,colliderVertices} from '../src/work/hotels/HotelGeometry.ts';
import {geometryScene} from './hotel-test-geometry.mjs';
await RAPIER.init();
const towers=JSON.parse(fs.readFileSync('src/work/hotels/towers.json'));
const level=JSON.parse(fs.readFileSync('build/hotels/staged-vegas.mesh-level.json'));
const room=JSON.parse(fs.readFileSync('build/hotels/bellagio-room.mesh-level.json'));
const height=JSON.parse(fs.readFileSync('src/work/world.json')).worldProfileData.characterConfig.height;
const capsule=new RAPIER.Capsule(height/2-.30,.30),rotation={x:0,y:0,z:0,w:1};
let checks=0;const failures=[];
// Actual level colliders, plus the generated room at both wings, low/high floor,
// and both sides of the corridor. This catches room expansion into shell walls.
for(const t of towers.filter(t=>t.set==='bellagio'))for(const f of [t.firstGuestFloor,t.floors-2])for(const side of [-1,1]){
 const world=new RAPIER.World({x:0,y:0,z:0}),names=new Map();
 function add(c,matrix){
  let desc,body;
  if(!matrix && c.shape==='box'){
   body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(...c.position).setRotation({x:0,y:Math.sin(c.yaw/2),z:0,w:Math.cos(c.yaw/2)}));
   desc=RAPIER.ColliderDesc.cuboid(...c.size.map(v=>v/2));
  }else{
   const p=new THREE.Vector3(),vs=colliderVertices(c),out=[];
   for(let i=0;i<vs.length;i+=3){p.set(vs[i],vs[i+1],vs[i+2]);if(matrix)p.applyMatrix4(matrix);out.push(p.x,p.y,p.z);}
   body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());
   desc=c.shape==='trimesh'?RAPIER.ColliderDesc.trimesh(new Float32Array(out),new Uint32Array(c.indices)):RAPIER.ColliderDesc.convexHull(new Float32Array(out));
  }
  assert(desc);const col=world.createCollider(desc,body);names.set(col.handle,c.name);
 }
 for(const c of level.colliders)add(c);
 const bay=bayPoint(t,f,0),origin={...bay,x:bay.x+side*DOOR_X};
 const matrix=moduleMatrix(t,origin,side>0?0:Math.PI);
 for(const c of room.colliders)add(c,matrix);world.step();
 const paths={
  'foyer to window':[[.55,0],[2.45,0],[3.50,.78],[6.65,.78],[7.47,.70]],
  'bedside':[[3.50,.78],[3.50,-1.4]],
  'bath vanity and shower':[[1.66,0],[1.66,-1.62],[1.56,-1.62],[1.50,-1.09],[.63,-1.09],[.63,-2.42]],
  'media cabinet':[[3.5,.78],[4.6,1.63],[5.25,1.63]],
 };
 for(const [name,path] of Object.entries(paths))for(let segment=1;segment<path.length;segment++){
  const a=path[segment-1],b=path[segment],n=Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.08);
  for(let i=0;i<=n;i++){
   const local=new THREE.Vector3(a[0]+(b[0]-a[0])*i/n,.07,a[1]+(b[1]-a[1])*i/n).applyMatrix4(matrix);
   const hit=world.intersectionWithShape({x:local.x,y:local.y+height/2,z:local.z},rotation,capsule);
   const floor=world.castRay(new RAPIER.Ray({...local,y:local.y+.01},{x:0,y:-1,z:0}),.15,true);
   checks++;if(hit||!floor)failures.push({tower:t.id,f,side,name,segment,i,at:[a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n],hit:hit?names.get(hit.handle):null,floor:!!floor});
  }
 }
 const p={...bay,x:bay.x+side*(DOOR_X+7.47),y:bay.y+.07,z:bay.z+side*.7};
 assert(insideTower(t,p));assert.equal(roomAt(t,p)?.side,side);assert.equal(roomDepth(t),8.1);
 world.free();
}
assert.equal(roomDepth(towers.find(t=>t.set==='veer')),5.4,'Veer envelope must stay unchanged');
const report={checks,colliders:room.colliders.length,failures};
fs.writeFileSync('build/hotels/bellagio-premier/circulation-test.json',JSON.stringify(report,null,2));
console.log({checks,failures:failures.length,examples:failures.slice(0,12)});assert.equal(failures.length,0);
// Regression: legacy structural bays used to cut through the enlarged room.
// Keep those faces outdoors but associate them with Bellagio's hidden shell.
const shell=geometryScene('build/hotels/staged-vegas.glb');
for(const a of [.14,.18,.22,.26]){
 const direction=new THREE.Vector3(Math.sin(1.2)+a*Math.cos(1.2),0,-Math.cos(1.2)+a*Math.sin(1.2)).normalize();
 const ray=new THREE.Raycaster(new THREE.Vector3(-160.7,12.57,31.68),direction,0,7);
 const hit=ray.intersectObject(shell,true)[0];
 assert(hit,'Legacy exterior bay still exists outside');
 assert.equal(hit.object.parent.userData.visibilityTower,'bellagio','Structural bay must hide inside the streamed room');
}
// Inset sinks must really be hollow, rather than flat ceramic/counter disks.
const detail=geometryScene('build/hotels/bellagio-room.glb');
for(const x of [1.68,2.49]){
 const hit=new THREE.Raycaster(new THREE.Vector3(x,1.2,-2.57),new THREE.Vector3(0,-1,0),0,.6).intersectObject(detail,true)[0];
 assert(hit && hit.point.y<.80,'Basin centre should be recessed below the .918m rim');
 const mirror=new THREE.Raycaster(new THREE.Vector3(x,1.76,-1.4),new THREE.Vector3(0,0,-1),0,2).intersectObject(detail,true)[0];
 assert.equal(mirror?.object.parent.name,'Level_pk_mirror','Both mirrors must face the room');
}
console.log('Bellagio shell ownership and inset basin geometry passed');
