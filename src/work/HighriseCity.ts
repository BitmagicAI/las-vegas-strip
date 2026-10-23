import {batchCityShadows} from './CityShadows.js';
import {glbUrl} from './OptimizedGlb.js';
import {CityLod} from './CityLod.js';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {PhysicsBodyFactory} from 'engine/physics/PhysicsBodyFactory.js';
import {planCollider} from 'engine/meshlevel/MeshLevelColliders.js';
import type {EngineLike} from 'types/game.js';
import type {GroundSurfaceIndex} from './GroundSurfaceIndex.js';
import type {StreamingWork} from './StreamingWork.js';
interface Collision{vertices:number[];indices:number[]}
type Body=ReturnType<typeof PhysicsBodyFactory.createStaticBody>['rigidBody'];
interface Property{key:string;box:THREE.Box3;nodes:THREE.Mesh[];body:Body|null;pending:boolean;lastNear:number}
/** Towers whose exterior another owner draws; their collision still streams from here. The Bellagio Spa Tower is
 * part of the Bellagio block; Venetian tower facades are owned by StripLandmarks (2026-10-09). */
const DRAWN_ELSEWHERE=new Set(['strat','horseshoe-east','palms','rio','martin','panorama','signature','grand-chateau','elara','mirage','wynn','encore','trump','springhill','westgate','turnberry-place','turnberry-towers','allure','sky','hgv-boulevard','sahara','circus-circus','resorts-world','fontainebleau','bellagio-spa','park-mgm','luxor','mandalay-bay','w-las-vegas','venetian','palazzo','harrahs','treasure-island']);
/** Detailed surveyed towers replace their OSM volumes; they are never overlays. */
export class HighriseCity{
 private root:THREE.Group|null=null;
 private lod:CityLod|null=null;
 private nextCheck=0;
 private properties=new Map<string,Property>();
 private disposed=false;
 private revision='';
 private release:(()=>void)|null=null;
 constructor(private engine:EngineLike,private surfaces:GroundSurfaceIndex,private loading:StreamingWork){}
 async load():Promise<void>{
  const v=await fetch('/build/highrises/version.json').then(r=>r.json()) as {revision:string};this.revision=v.revision;
  const gltf=await new GLTFLoader().loadAsync(await glbUrl('/build/highrises/exteriors.glb?v='+v.revision));
  if(this.disposed){this.destroy(gltf.scene);return;}
  this.root=gltf.scene;this.root.name='Photo-referenced mapped high-rises';this.engine.scene!.add(this.root);this.root.updateMatrixWorld(true);
  const proxies:THREE.Mesh[]=[],drawnElsewhere:THREE.Mesh[]=[];
  this.root.traverse(o=>{if(!(o instanceof THREE.Mesh))return;
   const key=String(o.userData.property??o.parent?.userData.property??'');if(!key)return;
   let p=this.properties.get(key);if(!p){p={key,box:new THREE.Box3(),nodes:[],body:null,pending:false,lastNear:0};this.properties.set(key,p);}
   p.box.expandByObject(o);
   if(DRAWN_ELSEWHERE.has(key)){drawnElsewhere.push(o);return;}
   p.nodes.push(o);o.castShadow=false;o.receiveShadow=true;
   for(const m of Array.isArray(o.material)?o.material:[o.material]){m.side=THREE.DoubleSide;if(m instanceof THREE.MeshStandardMaterial)m.envMapIntensity=.7;}
   if(!o.userData.detail){const proxy=new THREE.Mesh(o.geometry,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));proxy.matrix.copy(o.matrix);proxy.matrixAutoUpdate=false;proxy.layers.set(30);proxy.castShadow=true;proxies.push(proxy);}
  });
  // Not disposed: the optimizer may share a material or accessor with a tower that stays.
  for(const o of drawnElsewhere)o.removeFromParent();
  this.release=this.surfaces.register(this.root);for(const proxy of proxies)this.root.add(proxy);batchCityShadows(this.root);
  this.lod=new CityLod(this.root,{key:m=>String(m.userData.property??'')+'/'+String(m.userData.source??''),skyline:true,facade:true});
  console.info(`[HighriseCity] ${this.properties.size} properties; near facade detail, streamed collision/interiors`);
 }
 update(player:THREE.Vector3,outside:boolean,hideSource?:string):void{
  if(!this.root||this.disposed)return;
  this.root.visible=outside;this.lod?.hideSource(hideSource);const now=performance.now();if(now<this.nextCheck)return;this.nextCheck=now+250;
  for(const p of this.properties.values()){
   const distance=p.box.distanceToPoint(player);
   if(distance<100){p.lastNear=now;if(!p.body&&!p.pending){p.pending=true;
    this.loading.enqueue('highrise-collision:'+p.key,p.key+' exterior',async()=>{
     try{const r=await fetch(`/build/highrises/${p.key}-collision.json?v=${this.revision}`);if(!r.ok)throw new Error('High-rise collision unavailable');const data=await r.json() as Collision;if(this.disposed)return;
      if(data.indices.length){const plan=planCollider({name:p.key,shape:'trimesh',...data},'terrain');p.body=PhysicsBodyFactory.createStaticBody(this.engine.physicsWorld!,plan.position,{shape:plan.shape,friction:.8,collisionGroup:plan.collisionGroup,collisionMask:plan.collisionMask},plan.quaternion).rigidBody;}
     }finally{p.pending=false;}
    },{background:distance>=30});
   }}else if(distance>160&&now-p.lastNear>20000&&p.body){if(p.body.isValid())this.engine.physicsWorld!.removeRigidBody(p.body);p.body=null;}
  }
 }
 private destroy(root:THREE.Group):void{const gs=new Set<THREE.BufferGeometry>(),ms=new Set<THREE.Material>();root.traverse(o=>{if(o instanceof THREE.Mesh){gs.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:[o.material])ms.add(m);}});for(const g of gs)g.dispose();for(const m of ms)m.dispose();root.removeFromParent();}
 dispose():void{this.disposed=true;this.lod?.dispose();this.release?.();for(const p of this.properties.values())if(p.body?.isValid())this.engine.physicsWorld?.removeRigidBody(p.body);if(this.root)this.destroy(this.root);this.properties.clear();}
}
