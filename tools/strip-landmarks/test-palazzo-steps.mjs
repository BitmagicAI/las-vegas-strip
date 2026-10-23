import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';
import {moduleMatrix,colliderVertices} from '../../src/work/hotels/HotelGeometry.ts';
import {worldPoint,bayPoint,insideTower,roomAt} from '../../src/work/hotels/HotelLayout.ts';
const read=p=>JSON.parse(fs.readFileSync(p));
const venues=read('build/strip-landmarks/venues.json'),towers=[...read('src/work/hotels/landmark-towers.json'),...read('src/work/hotels/highrise-towers.json')];
await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0}),names=new Map();
function add(c,name,m=new THREE.Matrix4()){
 const vs=c.shape?colliderVertices(c):c.vertices,v=[],p=new THREE.Vector3();
 for(let i=0;i<vs.length;i+=3){p.set(vs[i],vs[i+1],vs[i+2]).applyMatrix4(m);v.push(p.x,p.y,p.z);}
 const desc=c.indices?RAPIER.ColliderDesc.trimesh(new Float32Array(v),new Uint32Array(c.indices)):RAPIER.ColliderDesc.convexHull(new Float32Array(v));
 assert(desc,name);const b=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());world.createCollider(desc,b);names.set(b.handle,name);return b;
}
const report={checks:0,failures:[],virtualRooms:0},q={x:0,y:0,z:0,w:1},capsule=new RAPIER.Capsule(.65,.29);
function probe(p,label){
 const pos={x:p[0],y:p[1]+1.10,z:p[2]},hit=world.intersectionWithShape(pos,q,capsule),floor=world.castRay(new RAPIER.Ray({x:p[0],y:p[1]+.25,z:p[2]},{x:0,y:-1,z:0}),.55,true);
 report.checks++;if(hit||!floor)report.failures.push({label,p,blocker:hit?names.get(hit.parent().handle):null,floor:!!floor});
}
function route(a,b,label){let n=Math.max(1,Math.ceil(new THREE.Vector3(...a).distanceTo(new THREE.Vector3(...b))/.3));for(let i=0;i<=n;i++)probe(a.map((v,j)=>v+(b[j]-v)*i/n),label);}
function module(t,name,p={x:0,y:0,z:0},rotation=0){return read(`build/hotels/${name}.mesh-level.json`).colliders.map(c=>add(c,t.id+'/'+c.name,moduleMatrix(t,p,rotation,name.endsWith('-stair'))));}
const city=process.argv.includes('--city');
if(city){
 const ids=new Set(read('build/strip-landmarks/replacement-ids.json'));
 assert(!read('build/geographic-strip/building-index.json').some(b=>ids.has(b.id)),'Original landmark boxes remain');
 for(const c of read('build/geographic-strip/city-colliders.json'))add(c,'city '+c.id);
 for(const c of read('build/geographic-strip/detailed.mesh-level.json').colliders)add(c,'detailed '+c.name);
}

for(const file of ['venetian-exterior','palazzo-exterior','palazzo-interior'])add(read(file==='venetian-exterior' && process.env.PALAZZO_COLLISION_FIXTURE ? process.env.PALAZZO_COLLISION_FIXTURE : `build/strip-landmarks/${file}-collision.json`),file);
world.step();
for(const route of read('docs/project-records/venetian-exterior-2026-10-09/palazzo-stair-routes.json'))for(const p of route)probe(p,'Palazzo twin stair');
const yaw=Math.atan2(35,19);
for(let x=-12;x<=12;x+=.3)probe([344+Math.cos(yaw)*x-Math.sin(yaw)*7.2,3.24,-850-Math.sin(yaw)*x-Math.cos(yaw)*7.2],'Palazzo terrace cross-route');
// Sweep the same player capsule sideways at each stair edge, both directions.
function point(x,y,z){return {x:344+Math.cos(yaw)*x+Math.sin(yaw)*z,y:y+.24,z:-850-Math.sin(yaw)*x+Math.cos(yaw)*z};}
function edgeCheck(a,b,label){
 const d={x:b.x-a.x,y:0,z:b.z-a.z},len=Math.hypot(d.x,d.z);d.x/=len;d.z/=len;
 // Torso-only sweep isolates the open baluster band from the low parapet.
 const hit=world.castShape(a,q,d,new RAPIER.Capsule(.2,.29),0,len,true);
 report.checks++;if(!hit)report.failures.push({label,a,b,reason:'Uncontained balustrade'});
}
function center(t,side){const u=1-t;return [side*(2*u*u*u+30*u*u*t+36*u*t*t+12*t*t*t),-18*u*u*u-54*u*u*t-42*u*t*t-8.45*t*t*t];}
for(const side of [-1,1])for(let i=1;i<40;i++){
 const t=i/40,c=center(t,side),a=center(t-.001,side),b=center(t+.001,side),dx=b[0]-a[0],dz=b[1]-a[1],len=Math.hypot(dx,dz);
 for(const sign of [-1,1])edgeCheck(point(c[0]-dz/len*sign*.9,3*t+1.10,c[1]+dx/len*sign*.9),point(c[0]-dz/len*sign*2.3,3*t+1.10,c[1]+dx/len*sign*2.3),'Stair rail containment');
}
for(const [a,b] of [[-16,-13.85],[-10.15,10.15],[13.85,16]])for(let x=a+.4;x<b-.3;x+=.4)edgeCheck(point(x,4.10,-7.8),point(x,4.10,-9.1),'Terrace rail containment');
console.log(JSON.stringify(report,null,2));process.exitCode=report.failures.length?1:0;
