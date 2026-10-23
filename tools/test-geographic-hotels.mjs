import assert from 'node:assert/strict';
import fs from 'node:fs';
import RAPIER from '@dimforge/rapier3d-compat';
import * as THREE from 'three';
import {HotelResidency,RoomStateStore} from '../src/work/hotels/HotelResidency.ts';
import {STORY,roomId,roomSeed,localPoint,worldPoint,bayPoint,insideTower,roomAt,guestVisibility,stairVisible} from '../src/work/hotels/HotelLayout.ts';
import {moduleMatrix,stairStopMatrix,colliderVertices} from '../src/work/hotels/HotelGeometry.ts';
const transforms=JSON.parse(fs.readFileSync('build/geographic-strip/anchors.json')).transforms;
function mapped(p,key){const t=transforms[key],[a,b,c,d]=t.linear;return {x:a*p.x+b*p.z+t.translation[0],y:p.y,z:c*p.x+d*p.z+t.translation[1]};}
const towers=JSON.parse(fs.readFileSync('src/work/hotels/towers.json'));
for(const t of towers){
 // Approaching the entrance crosses residency's 12 m boundary, not a visual
 // boundary. Ground entrances remain; upper service doors never pop into view.
 for(const z of [-19,-17.01,-16.99,-15,-5.4]){
  const inside=insideTower(t,{x:0,y:.04,z}),preloaded=Math.abs(z+5)<12;
  assert.equal(inside,false);
  assert.equal(stairVisible(0,0,preloaded,inside,false),true);
  assert.equal(stairVisible(0,0,false,inside,false),true,'other lobby entrance must stay visible');
  for(const floor of [1,2])assert.equal(stairVisible(floor,0,preloaded,inside,false),false);
 }
 assert.equal(stairVisible(1,0,true,false,true),true,'open entrance reveals next flight');
 assert.equal(stairVisible(2,1,true,true,false),true,'ascending loads and reveals the next flight');
 const p={x:-1.65,y:1.8,z:3.6},camera={x:0,y:3,z:0};
 assert.equal(guestVisibility(t,0,p,camera,false,false).outside,false);
 assert.equal(guestVisibility(t,0,p,camera,false,false).showGround,false);
 assert.equal(guestVisibility(t,0,p,{x:8,y:2,z:0},false,false).showGround,false,'side wall is not a portal');
 assert.equal(guestVisibility(t,0,p,camera,true,false).showGround,true,'opening and closing doors retain public floor');
 assert.equal(guestVisibility(t,0,p,{x:0,y:2,z:-6},false,false).showGround,true,'camera in entrance retains lobby');
 const floor=t.firstGuestFloor,q=bayPoint(t,floor,0);
 assert.equal(guestVisibility(t,floor,q,camera,false,false).outside,false);
 assert.equal(guestVisibility(t,floor,q,camera,false,true).outside,true,'open room window reveals exterior from corridor');
 assert.equal(guestVisibility(t,floor,q,camera,false,true).hideTower,t.building==='veer'?t.id:t.building);
}
let live=0,peak=0,releases=0;
const cache=new HotelResidency(2,10,()=>{live--;releases++;});
for(let floor=0;floor<400;floor++){
 const required=new Map([[`floor/${floor}`,()=>{live++;peak=Math.max(peak,live);return floor;}]]);
 cache.reconcile(required,floor*.25);assert(cache.entries.has(`floor/${floor}`));assert(live<=2);
}
cache.reconcile(new Map(),111);assert.equal(live,0);assert.equal(releases,400);
const disk=new Map(),storage={getItem:k=>disk.get(k)??null,setItem:(k,v)=>disk.set(k,v)};
const states=new RoomStateStore(storage),ids=new Set();let total=0;
for(const t of towers)for(let floor=t.firstGuestFloor;floor<t.floors;floor++)for(let bay=0;bay<t.bays;bay++)for(const side of [-1,1]){
 const id=roomId(t,floor,bay,side);assert(!ids.has(id));ids.add(id);total++;
 states.set(id,{visited:true,visits:2,searched:true});assert(states.residentStates<=64);
 assert.equal(roomSeed(id),roomSeed(id));
 const p=bayPoint(t,floor,bay);p.x+=side*3;p.y+=.04;
 assert(insideTower(t,p));assert.equal(roomAt(t,p)?.bay,bay);
 const back=localPoint(t,worldPoint(t,p));assert(Math.hypot(back.x-p.x,back.y-p.y,back.z-p.z)<1e-8);
}
const oldest=[...ids][0];assert.deepEqual(new RoomStateStore(storage).get(oldest),{visited:true,visits:2,searched:true});
await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0});
const report={totalRooms:total,residencyPeak:peak,persistence:'passed',checks:0,failures:[]};
const bodyNames=new Map();
function add(c,matrix=new THREE.Matrix4()){
 // MeshLevel preserves source boxes as native boxes. Turning the kilometre-
 // wide, thin district foundation into a hull loses its top face in Rapier.
 if(c.shape==='box' && matrix.equals(new THREE.Matrix4())){
  const body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(...c.position).setRotation({x:0,y:Math.sin(c.yaw/2),z:0,w:Math.cos(c.yaw/2)}));
  world.createCollider(RAPIER.ColliderDesc.cuboid(...c.size.map(v=>v/2)),body);bodyNames.set(body.handle,c.name);return body;
 }
 const vs=colliderVertices(c),out=[],p=new THREE.Vector3();
 for(let i=0;i<vs.length;i+=3){p.set(vs[i],vs[i+1],vs[i+2]).applyMatrix4(matrix);out.push(p.x,p.y,p.z);}
 const desc=c.shape==='trimesh'?RAPIER.ColliderDesc.trimesh(new Float32Array(out),new Uint32Array(c.indices)):RAPIER.ColliderDesc.convexHull(new Float32Array(out));
 assert(desc,'invalid collider '+c.name);const b=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());world.createCollider(desc,b);bodyNames.set(b.handle,c.name);return b;
}
const staged='build/geographic-strip/detailed.mesh-level.json';
if(!fs.existsSync(staged))throw Error('Staged shell required for route validation');
const level=JSON.parse(fs.readFileSync(staged));
for(const key of ['colliders','volumes','lights','landmarks']){const names=(level[key]??[]).map(x=>x.name);assert.equal(new Set(names).size,names.length,`duplicate ${key} name`);}
const furnitureBodies=new Set();
for(const c of [...level.colliders,...JSON.parse(fs.readFileSync('build/geographic-strip/city-colliders.json')).map(c=>({...c,shape:'trimesh',name:'OSM '+c.id}))]){
 const body=add(c);
 if(/poker table|slot collision|reception curved desk|gaming floor column|casino arcade column/i.test(c.name))furnitureBodies.add(body.handle);
}
world.step();
// Guest cores and their approach are outside the gaming furniture layout.
for(const t of towers.filter(t=>t.set==='bellagio')){
 const p=worldPoint(t,{x:0,y:1.3,z:-1.4});
 const hits=[];
 world.intersectionsWithShape(p,{x:0,y:Math.sin(t.yaw/2),z:0,w:Math.cos(t.yaw/2)},new RAPIER.Cuboid(4.2,1.05,7.2),c=>{if(furnitureBodies.has(c.parent().handle))hits.push(c.handle);return true;});
 assert.deepEqual(hits,[],`${t.id}: guest vestibule intersects casino furniture`);
 assert(Math.abs(Math.sin(t.yaw))<1e-8,'Bellagio entry must align with the public floor grid');
}
const templates={};for(const p of [...new Set(towers.map(t=>t.set))])for(const k of ['stair','corridor','room','cap','entry'])templates[p+'-'+k]=JSON.parse(fs.readFileSync(`build/hotels/${p}-${k}.mesh-level.json`));
function module(t,k,p,rotation=0){return templates[t.set+'-'+k].colliders.map(c=>add(c,moduleMatrix(t,p,rotation,k==='stair')));}
function stop(t,p){return templates[t.set+'-cap'].colliders.map(c=>add(c,stairStopMatrix(t,p)));}
function remove(bodies){for(const b of bodies)world.removeRigidBody(b);}
// Include the persistent entrance shells in every collision/clearance check,
// including the transition out of the podium into the first guest corridor.
for(const t of towers)for(const c of templates[t.set+'-entry'].colliders)add(c,moduleMatrix(t,{x:0,y:0,z:0},0,true));
report.permanentEntryColliders=towers.reduce((n,t)=>n+templates[t.set+'-entry'].colliders.length,0);
// Match the runtime headless player's configured standing capsule, not a
// shorter generic human. The old 1.70 m test missed the 1.82 m player's head.
const height=JSON.parse(fs.readFileSync('src/work/world.json')).worldProfileData.characterConfig.height;
const radius=.30,half=height/2,cylinder=half-radius;
const capsule=new RAPIER.Capsule(cylinder,radius),clearanceCapsule=new RAPIER.Capsule(1.1-radius,radius),q={x:0,y:0,z:0,w:1};
function probe(t,p,label,floorRequired=true,clearance=false){
 const w=worldPoint(t,p),center={x:w.x,y:w.y+(clearance?1.1:half),z:w.z};
 const hit=world.intersectionWithShape(center,q,clearance?clearanceCapsule:capsule);
 let grounded=true;
 if(floorRequired){const ray=new RAPIER.Ray({x:w.x,y:w.y+.04,z:w.z},{x:0,y:-1,z:0});grounded=!!world.castRay(ray,.22,true);}
 report.checks++;
 if(hit||!grounded)report.failures.push({tower:t.id,label,p,w,hit:!!hit,blocker:hit?bodyNames.get(hit.parent().handle):null,grounded});
}
// Continuous public-floor approach samples include the existing lobby entry,
// marble spine, and side turn into each new vestibule (doors open).
const entryGround=towers.filter(t=>t.set==='bellagio').flatMap(t=>module(t,'stair',{x:0,y:0,z:0}));
world.step();
const groundFrame={origin:[0,0,0],yaw:0};
for(const route of [
 [[-155,-77],[-155,-62],[-166,-62],[-166,-69.35]],
 [[-161,12],[-161,30],[-166,30],[-166,35.35]]
])for(let s=1;s<route.length;s++){
 const ar=mapped({x:route[s-1][0],z:route[s-1][1]},'bellagio'),br=mapped({x:route[s][0],z:route[s][1]},'bellagio'),a=[ar.x,ar.z],b=[br.x,br.z],n=Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.25);
 for(let i=0;i<=n;i++){
  const x=a[0]+(b[0]-a[0])*i/n,z=a[1]+(b[1]-a[1])*i/n;
  const ground=world.castRay(new RAPIER.Ray({x,y:1.2,z},{x:0,y:-1,z:0}),1.6,true);
  assert(ground,`public approach floor missing at ${x},${z}`);const y=1.2-ground.timeOfImpact;
  assert(y<.2 && y>-.4,'public approach must remain at pavement / lobby floor height');
  probe(groundFrame,{x,y:y+.045,z},`public approach ${s}/${i}`);
 }
}
remove(entryGround);
// Walkable public approach into every added core, including the two galleries.
const newTowers=towers.filter(t=>t.set!=='bellagio' && t.set!=='veer');
const newGround=newTowers.flatMap(t=>module(t,'stair',{x:0,y:0,z:0}));world.step();
for(const t of newTowers){
 const w=z=>worldPoint(t,{x:0,y:0,z});
 const route=t.set==='paris'?[mapped({x:128,z:-43},'paris'),mapped({x:156,z:-43},'paris'),w(-10),w(-3.65)]:
  t.set==='caesars'?[mapped({x:-168,z:-234},'caesars'),mapped({x:-199,z:-234},'caesars'),w(-3.65)]:[w(-12),w(-3.65)];
 for(let j=1;j<route.length;j++){
  const a=route[j-1],b=route[j],n=Math.ceil(Math.hypot(b.x-a.x,b.z-a.z)/.25);
  for(let i=0;i<=n;i++){
   const x=a.x+(b.x-a.x)*i/n,z=a.z+(b.z-a.z)*i/n;
   const ground=world.castRay(new RAPIER.Ray({x,y:1.2,z},{x:0,y:-1,z:0}),1.6,true);
   const y=ground?1.2-ground.timeOfImpact:.075;
   // A capsule spans both sides of the 7.5 cm foyer sill before its centre crosses it.
   probe(groundFrame,{x,y:Math.max(y,t.set==='horseshoe'?.145:.075)+.045,z},`${t.id} public approach ${j}/${i}`);
  }
 }
}
remove(newGround);
for(const t of towers){
 for(let f=0;f<t.floors;f++){
  const bodies=[];const drift=y=>({x:(t.lean?.[0]??0)*y,y,z:(t.lean?.[1]??0)*y});
  for(let j=Math.max(0,f-1);j<=Math.min(t.floors-1,f+1);j++)bodies.push(...module(t,'stair',drift(j*STORY)));
  if(f===t.floors-1)bodies.push(...stop(t,drift(f*STORY)));
  if(f>=t.firstGuestFloor)for(let bay=0;bay<t.bays;bay++)bodies.push(...module(t,'corridor',bayPoint(t,f,bay)));
  world.step();
  const point=(x,y,z)=>{const p=drift(f*STORY+y);p.x+=x;p.z+=z;p.y+=.045;return p;};
  probe(t,point(0,0,-3.65),`floor ${f} landing`);
  if(f===0)for(let i=0;i<=12;i++)probe(t,point(0,0,-6.15+i*.2),`ground entry ${i}`);
  if(f<t.floors-1){
   for(let i=0;i<=20;i++){
    const z=-2.5+5*i/20;probe(t,point(-1.65,1.8*i/20,z),`floor ${f} outbound ${i}`,true,true);
    probe(t,point(1.65,1.8+1.8*i/20,-z),`floor ${f} return ${i}`,true,true);
   }
   for(let i=0;i<=10;i++)probe(t,point(-1.65+3.3*i/10,1.8,3.6),`floor ${f} middle landing ${i}`,true,true);
  }
  if(f>=t.firstGuestFloor){
   for(let bay=0;bay<t.bays;bay++){
    const p=bayPoint(t,f,bay);probe(t,{x:p.x,y:p.y+.045,z:p.z},`floor ${f} corridor ${bay}`);
    for(const side of [-1,1]){
     const r={...p,x:p.x+side*1.85,y:p.y+.015},roomBodies=module(t,'room',r,side>0?0:Math.PI);world.step();
     for(let i=0;i<=10;i++)probe(t,{x:p.x+side*(1.3+i*.4),y:p.y+.06,z:p.z},`floor ${f} room ${bay}/${side} route ${i}`);
     // Closed room door blocks the threshold; sliding into its jamb clears it.
     const dp=worldPoint(t,{x:p.x+side*1.85,y:p.y+1.325,z:p.z});
     const rot=t.yaw+side*Math.PI/2;
     const body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(dp.x,dp.y,dp.z).setRotation({x:0,y:Math.sin(rot/2),z:0,w:Math.cos(rot/2)}));
     world.createCollider(RAPIER.ColliderDesc.cuboid(.65,1.325,.065),body);world.step();
     const wp=worldPoint(t,{x:p.x+side*1.85,y:p.y+.9,z:p.z});assert(world.intersectionWithShape(wp,q,capsule),'closed door must block');
     world.removeRigidBody(body);remove(roomBodies);
    }
   }
  }
  remove(bodies);
 }
}
fs.writeFileSync('build/geographic-strip/hotel-test.json',JSON.stringify(report,null,2));
console.log('Clearance checks',report.checks,'failures',report.failures.length);
// Drive a real Rapier capsule up and down both flights, including the Veer shear.
// This catches continuous-motion snags that isolated clearance probes miss.
report.stairTraversals=[];
for(const t of towers)for(const f of [0,t.firstGuestFloor-1,t.floors-2]){
 const drift=y=>({x:(t.lean?.[0]??0)*y,y,z:(t.lean?.[1]??0)*y}),bodies=[];
 for(let j=Math.max(0,f-1);j<=Math.min(t.floors-1,f+2);j++)bodies.push(...module(t,'stair',drift(j*STORY)));
 if(f+1===t.floors-1)bodies.push(...stop(t,drift((f+1)*STORY)));
 const point=(x,y,z)=>{const p=drift(f*STORY+y);p.x+=x;p.z+=z;return worldPoint(t,p);};
 const path=[...(f===0?[point(0,0,-7)]:[]),point(0,0,-3.65),point(-1.65,0,-3.65),point(-1.65,1.8,3.6),point(1.65,1.8,3.6),point(1.65,3.6,-3.65),point(0,3.6,-3.65)];
 const p=path[0],body=world.createRigidBody(RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(p.x,p.y+half+.05,p.z));
 const col=world.createCollider(RAPIER.ColliderDesc.capsule(cylinder,radius),body),cc=world.createCharacterController(.08);
 // Same skin, seam nudge, step and slope settings as PhysicsWorld's native KCC.
 cc.setNormalNudgeFactor(.01);cc.setApplyImpulsesToDynamicBodies(false);cc.setSlideEnabled(true);
 cc.enableAutostep(.65,.30,false);cc.enableSnapToGround(.5);
 cc.setMaxSlopeClimbAngle(50*Math.PI/180);cc.setMinSlopeSlideAngle(45*Math.PI/180);world.step();
 for(const [direction,points] of [['up',path.slice(1)],['down',[...path].reverse().slice(1)]]){
  for(const target of points){
   let arrived=false;
   for(let tick=0,limit=400+Math.ceil(Math.hypot(target.x-body.translation().x,target.z-body.translation().z)/.035);tick<limit;tick++){
    const at=body.translation(),dx=target.x-at.x,dz=target.z-at.z,d=Math.hypot(dx,dz);
    if(d<.08){arrived=true;break;}
    // A small grounded adhesion velocity, with snap-to-ground on descents.
    // Applying terminal falling velocity here would cancel uphill movement.
    const s=Math.min(.045,d)/d;cc.computeColliderMovement(col,{x:dx*s,y:-.008,z:dz*s});
    const move=cc.computedMovement();body.setNextKinematicTranslation({x:at.x+move.x,y:at.y+move.y,z:at.z+move.z});world.step();
   }
   assert(arrived,`${t.id} ${direction}: continuous stair route blocked ${JSON.stringify({target,at:body.translation(),movement:cc.computedMovement()})}`);
  }
  const target=points.at(-1),at=body.translation();assert(Math.abs(at.y-half-target.y)<.15,`${t.id} ${direction}: wrong landing height ${JSON.stringify({at,target,half})}`);
  report.stairTraversals.push({tower:t.id,floor:f,direction,landingHeight:at.y-half});
 }
 world.removeCharacterController(cc);world.removeRigidBody(body);remove(bodies);
}
world.free();fs.writeFileSync('build/geographic-strip/hotel-test.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({...report,failures:report.failures.slice(0,12)},null,2));
assert.equal(report.failures.length,0,`${report.failures.length} guest-floor geometry failures; see build/geographic-strip/hotel-test.json`);
