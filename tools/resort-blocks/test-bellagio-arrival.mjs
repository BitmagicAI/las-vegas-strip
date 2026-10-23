import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';import {colliderVertices} from '../../src/work/hotels/HotelGeometry.ts';
const read=p=>JSON.parse(fs.readFileSync(p));await R.init();const w=new R.World({x:0,y:-9.81,z:0});const names=new Map();
function add(c,name){const v=c.shape?colliderVertices(c):c.vertices;if(!v?.length)return;const d=c.indices?R.ColliderDesc.trimesh(new Float32Array(v),new Uint32Array(c.indices)):R.ColliderDesc.convexHull(new Float32Array(v));if(!d)return;const rb=w.createRigidBody(R.RigidBodyDesc.fixed());w.createCollider(d,rb);names.set(rb.handle,name);}
const root='build/resort-blocks/bellagio/';for(const v of read(root+'venues.json'))for(const layer of ['exterior','interior'])add(read(root+(layer==='exterior'&&v.exteriorCollision?v.exteriorCollision:v.key+'-'+layer+'-collision.json')),v.key+'/'+layer);
for(const c of read('build/geographic-strip/city-colliders.json'))add(c,'city '+c.id);for(const c of read('src/work/geographic/level.json').colliders)add(c,c.name);w.step();
let checks=0,failures=[];const body=new R.Cuboid(.8,.65,1.5),suv=new R.Cuboid(1.05,1.05,2.4);
const roads=[...read(root+'south-arrival-report.json').roads,...read(root+'routes.json').filter(r=>r.vehicle).map(r=>({...r,id:r.name,garage:true}))];
for(const r of roads)for(let j=1;j<r.points.length;j++){
 const a=r.points[j-1],b=r.points[j],len=Math.hypot(b[0]-a[0],b[2]-a[2]),n=Math.ceil(len/1.5),yaw=Math.atan2(b[0]-a[0],b[2]-a[2]),q={x:0,y:Math.sin(yaw/2),z:0,w:Math.cos(yaw/2)};
 for(let i=0;i<=n;i++){const p=a.map((v,k)=>v+(b[k]-v)*i/n);if(!r.garage&&(p[0]<-219||p[0]>-25||p[2]<401||p[2]>592))continue;
 const floor=w.castRayAndGetNormal(new R.Ray({x:p[0],y:p[1]+.45,z:p[2]},{x:0,y:-1,z:0}),.8,true);const hit=w.intersectionWithShape({x:p[0],y:p[1]+(r.garage?1.5:1.25),z:p[2]},q,r.garage?suv:body);checks++;
 if(!floor||floor.normal.y<.7||hit)failures.push({road:r.id,p,missingFloor:!floor,normalY:floor?.normal.y,blocker:hit?names.get(hit.parent().handle):null});
 }
}
const report={checks,failures,vehicleEnvelopeM:[1.6,1.3,3],garageVehicleEnvelopeM:[2.1,2.1,4.8],note:'Continuous centerline floor support and compact vehicle envelope; all city/retained colliders active. Does not replace in-game driving.'};fs.writeFileSync(root+'south-arrival-drive-audit.json',JSON.stringify(report,null,2));console.log(JSON.stringify({...report,failures:failures.slice(0,20)},null,2));assert.equal(failures.length,0);
