import fs from 'node:fs';import assert from 'node:assert/strict';import RAPIER from '@dimforge/rapier3d-compat';
import {colliderVertices} from '../../src/work/hotels/HotelGeometry.ts';
import {contains,visibilityState} from '../../src/work/BuildingVisibility.ts';
import visibility from '../../src/work/vegas-visibility.json';
for(const z of visibility.zones.filter(z=>z.building==='paris'))assert.equal(contains(z,{x:126.8,y:1.7,z:453}),false,'Covered motor court stays outdoors');
assert(visibility.zones.some(z=>z.building==='paris'&&contains(z,{x:126.8,y:1.7,z:423})),'Retained casino remains indoors');
assert(visibilityState({x:126.8,y:1.7,z:432},{x:126.8,y:1.7,z:429},()=>null).outside,'Glazed vestibule retains the outdoor view with doors closed');
const read=p=>JSON.parse(fs.readFileSync(p)),B='build/resort-blocks/paris/';await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0});const names=new Map();
function add(c,name){const vertices=c.shape?colliderVertices(c):c.vertices;if(!vertices?.length)return;const desc=c.indices?RAPIER.ColliderDesc.trimesh(new Float32Array(vertices),new Uint32Array(c.indices)):RAPIER.ColliderDesc.convexHull(new Float32Array(vertices));assert(desc,name);const rb=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());world.createCollider(desc,rb);names.set(rb.handle,name);}
for(const v of read(B+'venues.json'))for(const layer of ['exterior','interior'])add(read(B+(layer==='exterior'&&v.exteriorCollision?v.exteriorCollision:v.key+'-'+layer+'-collision.json')),v.key+'/'+layer);
if(process.argv.includes('--city'))for(const c of read('build/geographic-strip/city-colliders.json'))add(c,'city '+c.id);
for(const c of read('src/work/geographic/level.json').colliders)add(c,'retained '+c.name);
world.step();const capsule=new RAPIER.Capsule(.60,.28),q={x:0,y:0,z:0,w:1},report={checks:0,failures:[],city:process.argv.includes('--city'),note:'New geometry, retained static interior, optional city collision. Door state and streaming require in-game verification.'};
const colliderNames=read('src/work/geographic/level.json').colliders.map(c=>c.name);assert.equal(new Set(colliderNames).size,colliderNames.length,'Unique retained collider names required by MeshLevel');
const routes=read(B+'routes.json');
for(const route of routes)for(let s=1;s<route.points.length;s++){
 const a=route.points[s-1],b=route.points[s],n=Math.max(1,Math.ceil(Math.hypot(...a.map((v,i)=>v-b[i]))/.3));
 for(let i=0;i<=n;i++){const p=a.map((v,j)=>v+(b[j]-v)*i/n);const body=world.intersectionWithShape({x:p[0],y:p[1]+1.25,z:p[2]},q,capsule),floor=world.castRay(new RAPIER.Ray({x:p[0],y:p[1]+.35,z:p[2]},{x:0,y:-1,z:0}),.75,true);report.checks++;if(body||!floor)report.failures.push({route:route.name,p,blocker:body?names.get(body.parent().handle):null,floor:!!floor});}
}
// Clearance above the floor misses small curbs. Sweep an actual grounded
// character along the approach, with autostep disabled, to catch that regression.
const walker=world.createRigidBody(RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(126.8,1.05,447));
const feet=world.createCollider(RAPIER.ColliderDesc.capsule(.60,.28),walker),controller=world.createCharacterController(.01);
controller.enableSnapToGround(.2);world.step();
for(let i=0;i<650;i++){
 controller.computeColliderMovement(feet,{x:0,y:-.06,z:-.04});
 const p=walker.translation(),m=controller.computedMovement();
 walker.setNextKinematicTranslation({x:p.x+m.x,y:p.y+m.y,z:p.z+m.z});world.step();
}
report.approachSweep={end:walker.translation(),passed:walker.translation().z<424};
if(!report.approachSweep.passed)report.failures.push({route:'Grounded main entrance sweep',p:walker.translation()});
fs.writeFileSync(B+'route-audit.json',JSON.stringify(report,null,2));console.log(JSON.stringify({...report,failures:report.failures.slice(0,20)},null,2));assert.equal(report.failures.length,0);
