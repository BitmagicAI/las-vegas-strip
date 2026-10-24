import * as THREE from 'three';
import {filmDetail} from './FilmDetail.js';
import {glbUrl} from './OptimizedGlb.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {PhysicsBodyFactory} from 'engine/physics/world3d/PhysicsBodyFactory.js';
import {planCollider} from 'engine/meshlevel/MeshLevelColliders.js';
import type {EngineLike} from 'types/game.js';
import type {PlayerController} from 'engine/player/PlayerController.js';
import type {GameHUD} from './GameHUD.js';
import type {GroundSurfaceIndex} from './GroundSurfaceIndex.js';
import {CoasterTrack,CoasterRun,type CoasterRoute} from './CoasterTrack.js';
import {runtimeUrl} from './RuntimeAssets.js';
type Body=ReturnType<typeof PhysicsBodyFactory.createStaticBody>['rigidBody'];
/** Local, deterministic track ride. Updates share the game's pause/background lifecycle. */
export class BigAppleCoaster {
 private root=new THREE.Group();private cars:THREE.Object3D[]=[];private track:CoasterTrack|null=null;
 private run:CoasterRun|null=null;private held=false;private requested=false;private release:(()=>void)|null=null;
 private body:Body|null=null;private collision:{vertices:number[];indices:number[]}|null=null;
 private savedFov=60;private savedUp=new THREE.Vector3(0,1,0);private savedVisible=true;private savedSuppression=false;
 private p=new THREE.Vector3();private q=new THREE.Quaternion();private target=new THREE.Vector3();private up=new THREE.Vector3();
 private details:THREE.Object3D[]=[];
 private hint='';private lastSecond=-1;
 /** Local filming: a ride the train runs on its own (nobody aboard), for a camera that flies in and rides along. */
 private filmRun:CoasterRun|null=null;
 get riding():boolean{return this.run!==null;}
 constructor(private engine:EngineLike,private controller:PlayerController,private player:THREE.Object3D,private hud:GameHUD,private surfaces:GroundSurfaceIndex,private restoreCamera:()=>void){
  controller.registerCustomAction({action:'coasterRide',desktop:{keys:['KeyR']},mobile:{label:'RIDE',behavior:'tap'}});
  hud.createIconText('big-apple-ride',{anchor:'top-center',icon:'',text:''});
  hud.createActionRow('coaster-board',{anchor:'bottom-center',controls:[{id:'ride',label:'Ride Big Apple Coaster · R',onSelect:()=>{this.requested=true;}}]});hud.setActionRowVisible('coaster-board',false);
  hud.createActionRow('coaster-return',{anchor:'bottom-center',controls:[{id:'return',label:'Return to platform · R',onSelect:()=>{this.requested=true;}}]});hud.setActionRowVisible('coaster-return',false);
 }
 async load():Promise<void>{
  const v=await fetch(runtimeUrl('/build/south-strip/version.json')).then(r=>r.json()) as {revision:string};const suffix='?v='+v.revision;
  const [environment,train,route,collision]=await Promise.all([
   new GLTFLoader().loadAsync(await glbUrl('/build/south-strip/coaster.glb'+suffix)),new GLTFLoader().loadAsync(await glbUrl('/build/south-strip/train.glb'+suffix)),
   fetch(runtimeUrl('/build/south-strip/route.json'+suffix)).then(r=>r.json()) as Promise<CoasterRoute>,
   fetch(runtimeUrl('/build/south-strip/coaster-collision.json'+suffix)).then(r=>r.json()) as Promise<{vertices:number[];indices:number[]}>
  ]);
  this.track=new CoasterTrack(route);this.collision=collision;this.root.name='Big Apple Coaster • OSM mapped route';this.root.add(environment.scene);
  for(let i=0;i<3;i++){const car=train.scene.clone(true);car.name='NYC taxi car '+(i+1);this.cars.push(car);this.root.add(car);}
  this.root.traverse(o=>{if(o.userData.source==='ties')this.details.push(o);if(o instanceof THREE.Mesh){o.castShadow=true;o.receiveShadow=true;for(const m of Array.isArray(o.material)?o.material:[o.material]){m.side=THREE.DoubleSide;if(m instanceof THREE.MeshStandardMaterial)m.envMapIntensity=.7;}}});
  this.engine.scene!.add(this.root);this.root.updateMatrixWorld(true);this.release=this.surfaces.register(environment.scene);this.placeTrain(0);
 }
 setOutsideVisibility(visible:boolean):void{this.root.visible=visible||this.riding;const camera=this.engine.camera!.position,near=filmDetail.full||Math.hypot(camera.x+130,camera.z-1540)<650;for(const node of this.details)node.visible=near;for(const car of this.cars)car.visible=this.riding||filmDetail.full||camera.distanceToSquared(car.position)<300*300;}
 reviewPosition(mode:string):THREE.Vector3|null{
  if(!this.track)return null;return new THREE.Vector3().fromArray(mode==='station'?this.track.route.exit:this.track.route.entrance);
 }
 private setHint(text:string):void{if(text===this.hint)return;this.hint=text;this.hud.updateIconText('big-apple-ride',{text});}
 private placeTrain(distance:number):void{
  if(!this.track)return;for(let i=0;i<this.cars.length;i++){const car=this.cars[i]!;this.track.sample(distance-i*4.6,car.position,car.quaternion);}
 }
 /** Local filming: run the train from `elapsed` seconds into a ride (deterministic: the same ride every take), advanced by
  * update() on the game clock; null parks it at the station. */
 film(elapsed:number|null):void{
  if(!this.track)return;
  if(elapsed===null){if(this.filmRun){this.filmRun=null;if(!this.run)this.placeTrain(0);}return;}
  const run=new CoasterRun(this.track);for(let t=0;t<elapsed&&!run.finished;t+=.25)run.advance(Math.min(.25,elapsed-t));
  this.filmRun=run;this.placeTrain(run.distance);
 }
 /** The front car's pose while the film's train runs. */
 filmPose(position:THREE.Vector3,orientation:THREE.Quaternion):boolean{if(!this.filmRun||!this.track)return false;this.track.sample(this.filmRun.distance,position,orientation);return true;}
 private board():void{
  if(!this.track||this.run||this.controller.isPlayerInVehicle())return;
  const camera=this.engine.camera!;if(!(camera instanceof THREE.PerspectiveCamera))return;this.savedFov=camera.fov;this.savedUp.copy(camera.up);this.savedVisible=this.player.visible;this.savedSuppression=this.controller.areInteractionsSuppressed();
  this.controller.setInteractionsSuppressed(true);this.controller.setCapsuleBodyEnabled(false);this.player.visible=false;
  this.run=new CoasterRun(this.track);this.lastSecond=-1;camera.fov=84;camera.updateProjectionMatrix();
  this.controller.getMobileControls().resetPressed('coasterRide');
  this.hud.setActionRowVisible('coaster-board',false);this.hud.setActionRowVisible('camera-view',false);
  this.hud.setActionRowVisible('coaster-return',true);
  this.hud.showToast('Big Apple Coaster • Hold tight! R / RIDE returns to the platform.',{variant:'success'});
 }
 private leave(completed:boolean):void{
  if(!this.run||!this.track)return;this.run=null;
  const p=this.track.route.exit;this.controller.teleportTo(p[0]!,p[1]!,p[2]!);this.controller.setCapsuleBodyEnabled(true);this.controller.setInteractionsSuppressed(this.savedSuppression);this.player.visible=this.savedVisible;
  const camera=this.engine.camera!;camera.up.copy(this.savedUp);if(camera instanceof THREE.PerspectiveCamera){camera.fov=this.savedFov;camera.updateProjectionMatrix();}this.restoreCamera();
  this.placeTrain(0);this.hud.setActionRowVisible('camera-view',true);this.setHint('');this.hud.showToast(completed?'Welcome back to New York!':'Returned to the coaster platform.',{variant:'success'});
  this.hud.setActionRowVisible('coaster-return',false);
 }
 update(dt:number):void{
  if(!this.track)return;
  // The walking controller is suspended in the seat, so drain its mobile tap
  // and look deltas here. This keeps RIDE usable without moving the capsule.
  if(this.run){const mobile=this.controller.getMobileControls();if(mobile.isEnabled()){if(mobile.isPressed('coasterRide')){this.requested=true;mobile.resetPressed('coasterRide');}mobile.update();}}
  const pressed=!!this.controller.keys.coasterRide;const fresh=this.requested||(pressed&&!this.held);this.requested=false;this.held=pressed;
  // One local station/ramp mesh collider, resident only while close to the attraction.
  const near=Math.hypot(this.player.position.x+100,this.player.position.z-1485)<190;
  if(near&&!this.body&&this.collision){const plan=planCollider({name:'Big Apple Coaster station',shape:'trimesh',...this.collision},'terrain');this.body=PhysicsBodyFactory.createStaticBody(this.engine.physicsWorld!,plan.position,{shape:plan.shape,friction:.8,collisionGroup:plan.collisionGroup,collisionMask:plan.collisionMask},plan.quaternion).rigidBody;}
  if(!near&&!this.run&&this.body){if(this.body.isValid())this.engine.physicsWorld!.removeRigidBody(this.body);this.body=null;}
  if(this.filmRun&&!this.run){this.filmRun.advance(dt);this.placeTrain(this.filmRun.distance);}
  if(this.run){
   if(fresh){this.leave(false);return;}
   this.run.advance(dt);if(this.run.finished){this.leave(true);return;}
   this.placeTrain(this.run.distance);this.track.sample(this.run.distance,this.p,this.q);
   this.player.position.copy(this.p);this.player.visible=false;
   const camera=this.engine.camera!;camera.position.copy(this.p).add(this.target.set(-.43,1.77,1.03).applyQuaternion(this.q));this.up.set(0,1,0).applyQuaternion(this.q);camera.up.copy(this.up);
   this.target.set(0,.02,12).applyQuaternion(this.q).add(camera.position);camera.lookAt(this.target);camera.updateMatrixWorld();
   const second=Math.floor(this.run.elapsed);if(second!==this.lastSecond){this.lastSecond=second;this.setHint(`BIG APPLE COASTER · ${Math.round(this.run.speed*3.6)} km/h · ${Math.min(100,Math.round(this.run.distance/this.track.route.length*100))}% · R to return`);}
  }else{
   const exit=this.target.fromArray(this.track.route.exit);const available=this.player.position.distanceTo(exit)<4.6&&!this.controller.isPlayerInVehicle();
   this.hud.setActionRowVisible('coaster-board',available);this.hud.setActionRowVisible('camera-view',!available);
   this.setHint(available?'THE BIG APPLE COASTER · 18 seats · R / RIDE to board':'');if(available&&fresh)this.board();
  }
 }
 dispose():void{
  if(this.run)this.leave(false);this.release?.();if(this.body?.isValid())this.engine.physicsWorld?.removeRigidBody(this.body);
  const gs=new Set<THREE.BufferGeometry>(),ms=new Set<THREE.Material>();this.root.traverse(o=>{if(o instanceof THREE.Mesh){gs.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:[o.material])ms.add(m);}});for(const g of gs)g.dispose();for(const m of ms)m.dispose();this.root.removeFromParent();
 }
}
