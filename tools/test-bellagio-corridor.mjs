import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';
import {colliderVertices} from '../src/work/hotels/HotelGeometry.ts';
import {geometryScene} from './hotel-test-geometry.mjs';
await RAPIER.init();
const world=new RAPIER.World({x:0,y:0,z:0}),scene=new THREE.Group();
const bases=new Map(),names=new Map();let checks=0;
function part(name,p,yaw=0,physics=true){
 if(!bases.has(name))bases.set(name,geometryScene('build/hotels/'+name+'.glb'));
 const root=bases.get(name).clone(true);root.position.set(...p);root.rotation.y=yaw;scene.add(root);root.updateMatrixWorld(true);
 if(physics)for(const c of JSON.parse(fs.readFileSync('build/hotels/'+name+'.mesh-level.json')).colliders){
  const vs=colliderVertices(c),points=[],v=new THREE.Vector3();
  for(let i=0;i<vs.length;i+=3){v.set(vs[i],vs[i+1],vs[i+2]).applyMatrix4(root.matrixWorld);points.push(v.x,v.y,v.z);}
  const desc=RAPIER.ColliderDesc.convexHull(new Float32Array(points));assert(desc);
  const col=world.createCollider(desc,world.createRigidBody(RAPIER.RigidBodyDesc.fixed()));names.set(col.handle,c.name);
 }
 return root;
}
const leaves=[];
for(let bay=0;bay<3;bay++){
 part('bellagio-corridor',[0,0,-6*bay]);
 for(const side of [-1,1])leaves.push(part('bellagio-door',[side*1.85,1.325,-6*bay],side*Math.PI/2,false));
}
part('bellagio-corridor-end',[0,0,-14.96]);
for(const side of [-1,1])part('bellagio-room',[side*1.85,0,0],side>0?0:Math.PI);
world.step();
const height=JSON.parse(fs.readFileSync('src/work/world.json')).worldProfileData.characterConfig.height;
const shape=new RAPIER.Capsule(height/2-.3,.3),rotation={x:0,y:0,z:0,w:1};
function walk(x,z){
 const p={x,y:height/2+.07,z};
 const hit=world.intersectionWithShape(p,rotation,shape);
 assert(!hit,`Capsule blocked at ${x},${z}: ${hit?names.get(hit.handle):''}`);
 assert(world.castRay(new RAPIER.Ray({x,y:.08,z},{x:0,y:-1,z:0}),.15,true),'missing floor');checks++;
}
for(let z=2.8;z>=-14;z-=.075)for(const x of [-1.08,0,1.08])walk(x,z);
for(const side of [-1,1])for(let x=0;x<3.8;x+=.05)walk(side*x,0);
scene.updateMatrixWorld(true);
for(const side of [-1,1])for(const y of [.15,1,2.5])for(const z of [-.55,0,.55]){
 const ray=new THREE.Raycaster(new THREE.Vector3(0,y,z),new THREE.Vector3(side,0,0),0,2.4);
 assert(ray.intersectObjects(leaves,true).length,'closed detailed door must face the corridor');checks++;
}
// Module joints, terminal junction, and room thresholds have one visible floor.
for(const [x,z] of [[0,-2.99],[0,-3.01],[0,-8.99],[0,-9.01],[0,-14.90],[1.89,0],[1.91,0],[-1.89,0],[-1.91,0]]){
 const hits=new THREE.Raycaster(new THREE.Vector3(x,.05,z),new THREE.Vector3(0,-1,0),0,.1).intersectObject(scene,true);
 assert.equal(hits.length,1,`floor ownership at ${x}/${z}: ${hits.map(h=>h.object.parent.name)}`);checks++;
}
assert.equal(JSON.parse(fs.readFileSync('build/hotels/bellagio-door.mesh-level.json')).colliders.length,0,'skin must not duplicate the engine door collider');
world.free();
const report={checks,capsuleRoutes:'passed',closedDoorFaces:'passed',floorSeams:'passed',doorSkinColliders:0};
fs.writeFileSync('build/hotels/bellagio-corridor/circulation-test.json',JSON.stringify(report,null,2));console.log(report);
