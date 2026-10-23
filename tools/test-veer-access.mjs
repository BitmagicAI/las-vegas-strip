import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';
import {colliderVertices,moduleMatrix} from '../src/work/hotels/HotelGeometry.ts';
import {geometryScene} from './hotel-test-geometry.mjs';

const towers=JSON.parse(fs.readFileSync('src/work/hotels/towers.json')).filter(t=>t.set==='veer');
await RAPIER.init();
const world=new RAPIER.World({x:0,y:-9.81,z:0}),names=new Map();
function add(c,m){
 let body,desc;
 if(c.shape==='box'&&!m){
  body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(...c.position).setRotation({x:0,y:Math.sin((c.yaw??0)/2),z:0,w:Math.cos((c.yaw??0)/2)}));
  desc=RAPIER.ColliderDesc.cuboid(...c.size.map(n=>n/2));
 }else{
  const vs=colliderVertices(c),v=new THREE.Vector3();
  if(m)for(let i=0;i<vs.length;i+=3){v.fromArray(vs,i).applyMatrix4(m);v.toArray(vs,i);}
  body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());
  desc=c.shape==='trimesh'?RAPIER.ColliderDesc.trimesh(new Float32Array(vs),new Uint32Array(c.indices)):RAPIER.ColliderDesc.convexHull(new Float32Array(vs));
 }
 const col=world.createCollider(desc,body);names.set(col.handle,c.name);
}
for(const c of JSON.parse(fs.readFileSync('build/hotels/staged-vegas.mesh-level.json')).colliders)add(c);
for(const t of towers)for(const kind of ['entry','stair'])for(const c of JSON.parse(fs.readFileSync(`build/hotels/veer-${kind}.mesh-level.json`)).colliders)add(c,moduleMatrix(t,{x:0,y:0,z:0},0,true));
world.step();
const height=JSON.parse(fs.readFileSync('src/work/world.json')).worldProfileData.characterConfig.height;
const capsule=new RAPIER.Capsule(height/2-.3,.3),q={x:0,y:0,z:0,w:1};
const east=towers[0],west=towers[1];
const routes=[
 {name:'east from Aria Place',points:[[-93,480],[-93,east.origin[2]],[-128,east.origin[2]],[-132.35,east.origin[2]]]},
 {name:'west from Boulevard',points:[[-25,381],[-92,381],[-92,397],[-163,397],[-163,west.origin[2]],[-196.35,west.origin[2]]]},
 {name:'east from Boulevard',points:[[-25,381],[-92,381],[-93,397],[-93,east.origin[2]],[-132.35,east.origin[2]]]},
 {name:'west from Aria Place',points:[[-93,480],[-93,397],[-163,397],[-163,west.origin[2]],[-196.35,west.origin[2]]]}
];
const report={checks:0,failures:[],routes:routes.map(r=>r.name)};
for(const route of routes)for(let j=1;j<route.points.length;j++){
 const a=route.points[j-1],b=route.points[j],n=Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.2);
 for(let i=0;i<=n;i++){
  const x=a[0]+(b[0]-a[0])*i/n,z=a[1]+(b[1]-a[1])*i/n;
  const floor=world.castRay(new RAPIER.Ray({x,y:.4,z},{x:0,y:-1,z:0}),.6,true),y=floor?.timeOfImpact!==undefined?.4-floor.timeOfImpact:0;
  const hits=[];world.intersectionsWithShape({x,y:y+.04+height/2,z},q,capsule,c=>{hits.push(names.get(c.handle));return true;});
  if(hits.length||!floor)report.failures.push({route:route.name,x,z,y,hits,grounded:!!floor});report.checks++;
 }
}
world.free();
if(!process.argv.includes('--diagnose')){
 const scene=geometryScene('build/hotels/staged-vegas.glb'),meshes=[],ray=new THREE.Raycaster();
 scene.traverse(o=>{if(o.isMesh&&!o.material.transparent)meshes.push(o);});
 // Closed leaves are animated engine objects, absent from this static scene.
 // Cast the actual exported walls/trim to catch decorative visual barriers
 // even where they deliberately have no physics shapes.
 for(const r of routes)for(let j=1;j<r.points.length;j++)for(const y of [1.25,1.95]){
  const a=r.points[j-1],b=r.points[j],v=new THREE.Vector3(b[0]-a[0],0,b[1]-a[1]);ray.far=v.length();ray.set(new THREE.Vector3(a[0],y,a[1]),v.normalize());
  const hit=ray.intersectObjects(meshes,false)[0];
  assert(!hit,`${r.name}: render obstruction ${hit?.object.parent.name} at ${JSON.stringify(hit?.point)}`);report.checks++;
 }
 for(const m of meshes){m.geometry.dispose();m.material.dispose();}
}
fs.writeFileSync('build/veer-access/route-test.json',JSON.stringify(report,null,2));
console.log({checks:report.checks,failures:report.failures.length,blockers:[...new Set(report.failures.flatMap(f=>f.hits))]});
if(!process.argv.includes('--diagnose'))assert.equal(report.failures.length,0,'Veer public approach blocked; see build/veer-access/route-test.json');
