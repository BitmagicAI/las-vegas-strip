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
// --only key,key: test just these venues. The Venetian's three streamed interiors (2026-10-23) join up, so each is walked
// with the other two and the Venetian's exterior.
const only=process.argv.includes('--only')?new Set(process.argv[process.argv.indexOf('--only')+1].split(',')):null;
const VENETIAN=['venetian','venetianCasino','grandCanal'];
for(const v of venues){
 if(only&&!only.has(v.key))continue;
 const bodies=[];for(const layer of v.exteriorOnly?['exterior']:['exterior','interior'])bodies.push(add(read(`build/strip-landmarks/${v.key}-${layer}-collision.json`),v.key+' '+layer));
 if(VENETIAN.includes(v.key))for(const k of VENETIAN){if(k===v.key||!fs.existsSync(`build/strip-landmarks/${k}-interior-collision.json`))continue;bodies.push(add(read(`build/strip-landmarks/${k}-interior-collision.json`),k+' interior'));if(k==='venetian')bodies.push(add(read('build/strip-landmarks/venetian-exterior-collision.json'),'venetian exterior'));}
 const t=towers.find(t=>t.building===v.key && ['linq','vanderpump','polo'].includes(v.key));
 const attached=towers.filter(t=>v.connections?.some(c=>c.tower===t.id));
 for(const t of attached){bodies.push(...module(t,t.id+'-lobby'),...module(t,t.set+'-entry'));for(let f=0;f<3;f++)bodies.push(...module(t,t.set+'-stair',{x:0,y:f*3.6,z:0}));}
 if(v.connections)bodies.push(add(read(`build/highrises/${v.building}-collision.json`),v.key+' tower collision'));
 if(t){
  bodies.push(...module(t,t.id+'-lobby'),...module(t,t.set+'-entry'));
  for(let f=0;f<4;f++)bodies.push(...module(t,t.set+'-stair',{x:0,y:f*3.6,z:0}));
  for(let b=0;b<t.bays;b++)bodies.push(...module(t,t.set+'-corridor',bayPoint(t,t.firstGuestFloor,b)));
 }
 world.step();
 for(const r of v.routes)for(let i=1;i<r.points.length;i++)route(r.points[i-1],r.points[i],v.key+' public route');
 for(const t of attached){
  const c=v.connections.find(c=>c.tower===t.id);
  const p=worldPoint(t,{x:c.side*9.4,y:.05,z:c.at}),m=worldPoint(t,{x:0,y:.05,z:c.at}),end=worldPoint(t,{x:0,y:.05,z:-3.65});
  route([p.x,p.y,p.z],[m.x,m.y,m.z],v.key+' guest lobby threshold');route([m.x,m.y,m.z],[end.x,end.y,end.z],v.key+' guest lobby to stairs');
 }
 if(v.key==='arena')for(let i=0;i<12;i++){
  const a=i*Math.PI/6,r=Math.hypot(60*Math.cos(a),65*Math.sin(a)),dx=60*Math.cos(a)/r,dz=65*Math.sin(a)/r;
  const p=(distance,height)=>[-471+r*.5*dx+distance*dx,.32+height,1470+r*.5*dz+distance*dz];
  route(p(0,0),p(r*.29,11.4),'arena lower seating aisle');
  route(p(r*.29,11.4),p(r*.34,14.4),'arena middle seating aisle');
  route(p(r*.34,14.4),p(r*.50,25.4),'arena upper seating aisle');
 }
 if(v.key==='arena')for(let i=0;i<6;i++){
  const a=Math.PI/12+i*Math.PI/3,p=r=>[-471+60*r*Math.cos(a),.32,1470+65*r*Math.sin(a)];
  route(p(1.1),p(.48),'arena concourse passage');
 }
 if(t){
  const local=(a,b,label)=>{const a1=worldPoint(t,a),b1=worldPoint(t,b);route([a1.x,a1.y+.05,a1.z],[b1.x,b1.y+.05,b1.z],t.id+' '+label);};
  const start=v.portals[0].p,end=worldPoint(t,{x:0,y:0,z:-3.65});route(start,[end.x,end.y+.05,end.z],t.id+' lobby connection');
  for(let f=0;f<3;f++){
   const y=f*3.6;local({x:-1.65,y,z:-2.5},{x:-1.65,y:y+1.8,z:2.5},'flight up');local({x:-1.65,y:y+1.8,z:3.6},{x:1.65,y:y+1.8,z:3.6},'middle landing');local({x:1.65,y:y+1.8,z:2.5},{x:1.65,y:y+3.6,z:-2.5},'flight return');
  }
  local({x:0,y:7.2,z:-3.65},{x:0,y:7.2,z:-5.1-6*t.bays},'hallway');
  for(const b of [0,t.bays-1])for(const side of [-1,1]){
   const p=bayPoint(t,2,b),room=module(t,t.set+'-room',{...p,x:side*1.85},side>0?0:Math.PI);world.step();local({...p,x:side*1.2},{...p,x:side*8.6},'room');for(const body of room)world.removeRigidBody(body);
  }
  for(let f=2;f<t.floors;f++)for(let b=0;b<t.bays;b++)for(const side of [-1,1]){const p={...bayPoint(t,f,b),x:side*4};assert(insideTower(t,p));assert.equal(roomAt(t,p).bay,b);report.virtualRooms++;}
 }
 for(const b of bodies)world.removeRigidBody(b);
 console.log(v.key,report.failures.filter(f=>f.label.startsWith(v.key)).length,'failures');
}
world.free();fs.writeFileSync('build/strip-landmarks/route-audit.json',JSON.stringify({...report,city},null,2));console.log(JSON.stringify({...report,city,failures:report.failures.slice(0,15)},null,2));assert.equal(report.failures.length,0);
