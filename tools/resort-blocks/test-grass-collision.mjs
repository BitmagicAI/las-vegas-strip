import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';import {colliderVertices} from '../../src/work/hotels/HotelGeometry.ts';
const read=p=>JSON.parse(fs.readFileSync(p));await R.init();const w=new R.World({x:0,y:-9.81,z:0});const names=new Map();
function add(c,name){const v=c.shape?colliderVertices(c):c.vertices;if(!v?.length)return;const d=c.indices?R.ColliderDesc.trimesh(new Float32Array(v),new Uint32Array(c.indices)):R.ColliderDesc.convexHull(new Float32Array(v));if(!d)return;const rb=w.createRigidBody(R.RigidBodyDesc.fixed());w.createCollider(d,rb);names.set(rb.handle,name);}
const root='build/resort-blocks/bellagio/';for(const v of read(root+'venues.json'))for(const layer of ['exterior','interior'])add(read(root+(layer==='exterior'&&v.exteriorCollision?v.exteriorCollision:v.key+'-'+layer+'-collision.json')),v.key+'/'+layer);
for(const c of read('build/geographic-strip/city-colliders.json'))add(c,'city '+c.id);for(const c of read('src/work/geographic/level.json').colliders)add(c,c.name);w.step();



const geometry=read(root+'bellagioBlock-exterior.json');let checks=0;
for(const g of geometry.meshes.filter(g=>g.source==='south-arrival-landscape' && g.material==='sage'))for(const f of g.faces){
 const p=[0,1,2].map(k=>f.reduce((sum,i)=>sum+g.vertices[i][k],0)/f.length);
 const hit=w.castRayAndGetNormal(new R.Ray({x:p[0],y:p[1]+.05,z:p[2]},{x:0,y:-1,z:0}),.1,true);
 assert(hit && hit.normal.y>.99 && Math.abs(hit.timeOfImpact-.05)<.005,'Grass must have matching upward collision');checks++;
}
fs.writeFileSync('docs/project-records/grass-collision-audit.json',JSON.stringify({checks,passed:true},null,2));console.log(`${checks} rendered grass triangles have matching upward collision`);
