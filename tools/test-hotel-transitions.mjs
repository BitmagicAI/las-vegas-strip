import assert from 'node:assert/strict';
import fs from 'node:fs';
import {registerHooks} from 'node:module';
import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';
import {StreamingWork} from '../src/work/StreamingWork.ts';
import {stairVisible,STORY,bayPoint,worldPoint} from '../src/work/hotels/HotelLayout.ts';
import {moduleMatrix} from '../src/work/hotels/HotelGeometry.ts';
import {geometryScene} from './hotel-test-geometry.mjs';
registerHooks({resolve(specifier,context,next){if(specifier.startsWith('engine/'))return {url:new URL('../engine/'+specifier.replace(/\.js$/,'.ts'),import.meta.url).href,shortCircuit:true};return next(specifier,context);}});
const {CameraObstruction}=await import('../src/work/CameraObstruction.ts');
const {CollisionGroup,CollisionMask,makeCollisionGroups}=await import('../engine/engine/CollisionLayers.ts');
const towers=JSON.parse(fs.readFileSync('src/work/hotels/towers.json'));
let checks=0;
const meshes=[];const ray=new THREE.Raycaster();
function cast(scene,from,to){scene.updateMatrixWorld(true);meshes.length=0;scene.traverseVisible(o=>{if(o.isMesh && !o.material.transparent)meshes.push(o);});ray.set(new THREE.Vector3(from.x,from.y,from.z),new THREE.Vector3(to.x-from.x,to.y-from.y,to.z-from.z).normalize());ray.far=100;return ray.intersectObjects(meshes,false);}
const bases=new Map();
function part(scene,t,kind,p){const key=t.set+'-'+kind;if(!bases.has(key))bases.set(key,geometryScene('build/hotels/'+key+'.glb'));const root=bases.get(key).clone(true);root.matrixAutoUpdate=false;root.matrix.copy(moduleMatrix(t,p,0,kind==='stair'||kind==='closure'));scene.add(root);return root;}
for(const t of towers){
 const f=t.firstGuestFloor,scene=new THREE.Group(),sp=n=>({x:(t.lean?.[0]??0)*n*STORY,y:n*STORY,z:0});
 for(let n=f-1;n<=f+2;n++){assert(stairVisible(n,f,true,true,false));part(scene,t,'stair',sp(n));}
 part(scene,t,'closure',sp(f+3));
 // Upward ray fan from both flights and the landing: no sky at streamed boundaries.
 for(const [x,y,z] of [[-1.65,1.7,0],[1.65,3.2,-1.4],[0,.15,-3.65]])for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++){
  const p={x:x+(t.lean?.[0]??0)*(f*STORY+y),y:f*STORY+y+1.7,z};
  const from=worldPoint(t,p),to=worldPoint(t,{x:p.x+dx*4,y:p.y+20,z:p.z+dz*4});
  assert(cast(scene,from,to).length,`${t.id}: sky visible above ${JSON.stringify(p)}`);checks++;
 }
 for(let bay=0;bay<2;bay++)part(scene,t,'corridor',bayPoint(t,f,bay));
 // Walkway surfaces must have exactly one upward face (not duplicate coplanar floors).
 for(const z of [-5.16,-5.08,-4.99,-4.90,-4.82,-4.72,-10.96,-11.06,-11.14,-11.24])for(const x of [-.43,.28]){
  const p=sp(f);p.x+=x;p.z=z;p.y+=.1;
  const from=worldPoint(t,p),to=worldPoint(t,{...p,y:p.y-1});
  const hits=cast(scene,from,to).filter(h=>Math.abs(h.distance-.1)<.001);
  assert.equal(hits.length,1,`${t.id} floor ${x}/${z}: ${JSON.stringify(hits.map(h=>({name:h.object.parent.name,distance:h.distance,normal:h.face.normal})) )}`);checks++;
 }
 // Corridor wall just outside the shaft should not coincide with shaft wall.
 for(const z of [-5.12,-5.18,-11.04,-11.16]){
  const p=sp(f);p.y+=1.1;p.z=z;
  const from=worldPoint(t,p),to=worldPoint(t,{...p,x:p.x+4});
  const hits=cast(scene,from,to);assert(hits.length);
  assert.equal(hits.filter(h=>Math.abs(h.distance-hits[0].distance)<1e-4).length,1);checks++;
 }
}
// Exercise the actual final camera check with Rapier kinematic door geometry.
await RAPIER.init();const world=new RAPIER.World({x:0,y:0,z:0});
const door=world.createRigidBody(RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(0,1.325,1));
world.createCollider(RAPIER.ColliderDesc.cuboid(.89,1.325,.065).setCollisionGroups(makeCollisionGroups(CollisionGroup.ENVIRONMENT,CollisionMask.ENVIRONMENT)),door);
// Player sensor/capsule at the ray origin must be excluded by the camera mask.
const player=world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(0,1,0));
world.createCollider(RAPIER.ColliderDesc.capsule(.65,.3).setCollisionGroups(makeCollisionGroups(CollisionGroup.PLAYER,CollisionMask.PLAYER)),player);
const adapter={raycast(origin,direction,distance,mask,out){const h=world.castRayAndGetNormal(new RAPIER.Ray(origin,direction),distance,true,undefined,makeCollisionGroups(0xffff,mask),undefined,undefined,c=>!c.isSensor());out.hasHit=!!h;out.hitDistance=h?.timeOfImpact??0;return out;}};
const camera=new THREE.PerspectiveCamera(60,1,.1,1000),clamp=new CameraObstruction(),feet=new THREE.Vector3();
world.step();camera.position.set(0,2.2,4);camera.lookAt(0,1.65,0);camera.updateMatrixWorld();clamp.update(camera,feet,adapter);
assert(camera.position.z<.94,'closed kinematic door must stop camera');checks++;
door.setNextKinematicTranslation({x:2,y:1.325,z:1});world.step();camera.position.set(0,2.2,4);camera.updateMatrixWorld();clamp.update(camera,feet,adapter);assert.equal(camera.position.z,4,'open door must clear camera');checks++;world.free();
// Deterministic paint barrier: no generation before feedback has painted;
// hold persists through render, duplicates coalesce, failure/disposal release it.
let paints=[],events=[];
const warmRoot=new THREE.Group(),warmChild=new THREE.Object3D();warmChild.frustumCulled=false;warmRoot.add(warmChild);
const work=new StreamingWork({show:(l,n)=>events.push('progress:'+n),hide:()=>events.push('hide'),failed:()=>events.push('error')},v=>events.push('hold:'+v),()=>new Promise(r=>paints.push(r)),()=>events.push('settle'));
work.enqueue('floor','corridor',()=>{events.push('build');work.revealUntilReady(warmRoot);assert(!warmRoot.frustumCulled);});work.enqueue('floor','duplicate',()=>assert.fail('duplicate work'));
assert.deepEqual(events,['hold:true','progress:0']);assert(work.busy);
async function paint(){paints.shift()();await Promise.resolve();}
await paint();assert(events.includes('build'));assert(work.busy);await paint();assert(work.busy);await paint();assert(!work.busy);assert.deepEqual(events,['hold:true','progress:0','build','settle','progress:1','progress:2','hide','hold:false']);assert(warmRoot.frustumCulled);assert(!warmChild.frustumCulled);checks++;
work.enqueue('bad','room',()=>{throw Error('fixture');});await paint();assert(!work.busy);assert(events.includes('error'));checks++;
work.enqueue('cancel','room',()=>assert.fail('disposed work ran'));work.dispose();await paint();assert(!work.busy);checks++;
const report={checks,skyAndSeams:'passed',kinematicDoorCamera:'passed',loadingPaintBarrier:'passed'};
fs.writeFileSync('build/hotels/transition-repair/transitions-test.json',JSON.stringify(report,null,2));console.log(report);
