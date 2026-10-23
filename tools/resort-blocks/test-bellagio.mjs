import fs from 'node:fs';import assert from 'node:assert/strict';import RAPIER from '@dimforge/rapier3d-compat';
import {colliderVertices} from '../../src/work/hotels/HotelGeometry.ts';
const read=p=>JSON.parse(fs.readFileSync(p)),B='build/resort-blocks/bellagio/';await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0});const names=new Map();
function add(c,name){const vertices=c.shape?colliderVertices(c):c.vertices;if(!vertices?.length)return;const desc=c.indices?RAPIER.ColliderDesc.trimesh(new Float32Array(vertices),new Uint32Array(c.indices)):RAPIER.ColliderDesc.convexHull(new Float32Array(vertices));assert(desc,name);const rb=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());world.createCollider(desc,rb);names.set(rb.handle,name);}
for(const v of read(B+'venues.json'))for(const layer of ['exterior','interior'])add(read(B+(layer==='exterior'&&v.exteriorCollision?v.exteriorCollision:v.key+'-'+layer+'-collision.json')),v.key+'/'+layer);
if(process.argv.includes('--city'))for(const c of read('build/geographic-strip/city-colliders.json'))add(c,'city '+c.id);
// The separately retained bridge passage owns this part of the north route.
const passage=read('build/geographic-strip/access/bellagio-via.json');add(passage.collision,'Via Bellagio');
for(const c of read('src/work/geographic/level.json').colliders)add(c,'retained '+c.name);
world.step();const capsule=new RAPIER.Capsule(.60,.28),q={x:0,y:0,z:0,w:1},report={checks:0,failures:[],city:process.argv.includes('--city'),note:'New geometry, retained static interior, Via Bellagio and optional city collision. Door state and streaming require in-game verification.'};
const routes=[...read(B+'routes.json'),...passage.routes.map((points,i)=>({name:`Via Bellagio ${i+1}`,points}))];
for(const route of routes.filter(r=>!r.vehicle))for(let s=1;s<route.points.length;s++){
 const a=route.points[s-1],b=route.points[s],n=Math.max(1,Math.ceil(Math.hypot(...a.map((v,i)=>v-b[i]))/.3));
 for(let i=0;i<=n;i++){const p=a.map((v,j)=>v+(b[j]-v)*i/n);const body=world.intersectionWithShape({x:p[0],y:p[1]+1.25,z:p[2]},q,capsule),floor=world.castRay(new RAPIER.Ray({x:p[0],y:p[1]+.35,z:p[2]},{x:0,y:-1,z:0}),.75,true);report.checks++;if(body||!floor)report.failures.push({route:route.name,p,blocker:body?names.get(body.parent().handle):null,floor:!!floor});}
}
fs.writeFileSync(B+'route-audit.json',JSON.stringify(report,null,2));console.log(JSON.stringify({...report,failures:report.failures.slice(0,20)},null,2));assert.equal(report.failures.length,0);
