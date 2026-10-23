import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';import {colliderVertices} from '../../src/work/hotels/HotelGeometry.ts';
const read=p=>JSON.parse(fs.readFileSync(p));await R.init();const w=new R.World({x:0,y:-9.81,z:0});const names=new Map();
function add(c,name){const v=c.shape?colliderVertices(c):c.vertices;if(!v?.length)return;const d=c.indices?R.ColliderDesc.trimesh(new Float32Array(v),new Uint32Array(c.indices)):R.ColliderDesc.convexHull(new Float32Array(v));if(!d)return;const rb=w.createRigidBody(R.RigidBodyDesc.fixed());w.createCollider(d,rb);names.set(rb.handle,name);}
const root='build/resort-blocks/bellagio/';for(const v of read(root+'venues.json'))for(const layer of ['exterior','interior'])add(read(root+(layer==='exterior'&&v.exteriorCollision?v.exteriorCollision:v.key+'-'+layer+'-collision.json')),v.key+'/'+layer);
for(const c of read('build/geographic-strip/city-colliders.json'))add(c,'city '+c.id);for(const c of read('src/work/geographic/level.json').colliders)add(c,c.name);w.step();


const anchors=read('src/work/geographic/anchors.json');const results=[];
for(const [name,p] of Object.entries(anchors).filter(([k])=>['sanctuary','companion','jeep','charger'].includes(k))){
 const rx=name==='jeep'?2.5:.5,rz=name==='jeep'?1.1:.5;
 for(const dx of [-rx,0,rx])for(const dz of [-rz,0,rz]){
  const x=p[0]+dx,z=p[2]+dz,hit=w.castRayAndGetNormal(new R.Ray({x,y:4,z},{x:0,y:-1,z:0}),5,true);
  assert(hit,`${name} missing support`);const y=4-hit.timeOfImpact;
  assert(Math.abs(y-.51)<.02 && hit.normal.y>.99,`${name} is not on level sanctuary landscaping: ${y}`);
  results.push({name,x,z,y,normalY:hit.normal.y});
 }
 const shape=name==='jeep'?new R.Cuboid(2.5,1.3,1.1):new R.Cuboid(.5,.9,.5);
 const hit=w.intersectionWithShape({x:p[0],y:name==='jeep'?1.84:1.46,z:p[2]},{x:0,y:0,z:0,w:1},shape);
 assert(!hit,`${name} clearance blocked by ${hit?names.get(hit.parent().handle):''}`);
}
fs.writeFileSync('docs/project-records/spawn-support-audit.json',JSON.stringify({checks:results.length,results},null,2));console.log('36 spawn support samples and four clearance envelopes passed');
