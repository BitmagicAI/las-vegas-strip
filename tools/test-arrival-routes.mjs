import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
import * as THREE from 'three';
import {moduleMatrix,colliderVertices} from '../src/work/hotels/HotelGeometry.ts';
await RAPIER.init();
const level=JSON.parse(fs.readFileSync('build/hotels/staged-vegas.mesh-level.json'));
const specs=JSON.parse(fs.readFileSync('build/arrival-reconstruction/report.json')).properties;
const world=new RAPIER.World({x:0,y:0,z:0}), names=new Map();
for(const c of level.colliders){
 let shape;
 if(c.shape==='box')shape=RAPIER.ColliderDesc.cuboid(...c.size.map(v=>v/2)).setTranslation(...c.position).setRotation({x:0,y:Math.sin((c.yaw??0)/2),z:0,w:Math.cos((c.yaw??0)/2)});
 else if(c.shape==='trimesh')shape=RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices));
 else if(c.shape==='convexHull')shape=RAPIER.ColliderDesc.convexHull(new Float32Array(c.vertices));
 if(shape){const collider=world.createCollider(shape);names.set(collider.handle,c.name);}
}
// Persistent guest entries and ground stairs exist in the game even while guest
// rooms are unloaded. Include them in the public arrival clearance check.
const towers=JSON.parse(fs.readFileSync('src/work/hotels/towers.json'));
let guestColliders=0;
for(const t of towers)for(const kind of ['entry','stair']){
 const matrix=moduleMatrix(t,{x:0,y:0,z:0},0,true);
 const template=JSON.parse(fs.readFileSync(`build/hotels/${t.set}-${kind}.mesh-level.json`));
 for(const c of template.colliders){
  const vs=colliderVertices(c),out=[],p=new THREE.Vector3();
  for(let i=0;i<vs.length;i+=3){p.set(vs[i],vs[i+1],vs[i+2]).applyMatrix4(matrix);out.push(p.x,p.y,p.z);}
  const desc=c.shape==='trimesh'?RAPIER.ColliderDesc.trimesh(new Float32Array(out),new Uint32Array(c.indices)):RAPIER.ColliderDesc.convexHull(new Float32Array(out));
  assert(desc,'Invalid guest collider');const collider=world.createCollider(desc);names.set(collider.handle,`${t.id}/${kind}/${c.name}`);guestColliders++;
 }
}
world.step();
const q={x:0,y:0,z:0,w:1}, capsule=new RAPIER.Capsule(.64,.31), failures=[], report=[];let checks=0;
for(const [name,s] of Object.entries(specs)){
 const [ox,,oz]=s.origin,c=Math.cos(s.yaw),sin=Math.sin(s.yaw),[width,depth]=s.dimensions;
 // A 50 cm navigation grid verifies a standing route from pavement, through the
 // door, around the existing stair cores, and onward to the original casino.
 const step=.5, minX=-width/2+1,maxX=width/2-1,minZ=-3,maxZ=depth+.5;
 const nx=Math.floor((maxX-minX)/step)+1,nz=Math.floor((maxZ-minZ)/step)+1,blocked=new Map();
 function probe(ix,iz){const key=iz*nx+ix;if(blocked.has(key))return blocked.get(key);const x=minX+ix*step,z=minZ+iz*step;checks++;const p={x:ox+c*x+sin*z,y:1.14,z:oz-sin*x+c*z};let block=null;world.intersectionsWithShape(p,q,capsule,col=>{block=names.get(col.handle);return false;});blocked.set(key,block);return block;}
 const start=[Math.round(((s.doorOffset??0)-minX)/step),0], queue=[start],seen=new Set([start[1]*nx+start[0]]);let found=null;
 for(let at=0;at<queue.length;at++){
  const [x,z]=queue[at];if(z===nz-1){found=[x,z];break;}
  for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]]){const xx=x+dx,zz=z+dz,key=zz*nx+xx;if(xx<0||xx>=nx||zz<0||zz>=nz||seen.has(key)||probe(xx,zz))continue;seen.add(key);queue.push([xx,zz]);}
 }
 const blockers=[...new Set([...blocked.values()].filter(Boolean))];
 report.push({name,reachedCasino:!!found,reachableCells:seen.size,blockers});if(!found)failures.push({name,blockers});
}
world.free();const result={checks,colliders:level.colliders.length,guestColliders,report,failures};fs.writeFileSync('build/arrival-reconstruction/routes-test.json',JSON.stringify(result,null,2));console.log(JSON.stringify({checks,colliders:level.colliders.length,guestColliders,failures},null,2));assert.equal(failures.length,0,'Arrival has no standing route from outdoors to onward circulation');
