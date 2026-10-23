import * as THREE from 'three';
import {glbUrl} from './OptimizedGlb.js';
import {interiorLightsNode,lightInterior} from './InteriorLighting.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {Door,DEFAULT_DOOR_OPTIONS} from 'engine/Door.js';
import {PhysicsBodyFactory} from 'engine/physics/PhysicsBodyFactory.js';
import {planCollider} from 'engine/meshlevel/MeshLevelColliders.js';
import {GameState,getGameStateManager} from 'engine/GameStateManager.js';
import type {EngineLike} from 'types/game.js';
import type {SiteLights,LightSite} from './SiteLights.js';
import type {GroundSurfaceIndex} from './GroundSurfaceIndex.js';
import type {StreamingWork} from './StreamingWork.js';
import {SphereVideo} from './SphereVideo.js';
import {finishSphereMaterials,addSphereSigns,addSphereSeats,disposeSphereRoot} from './SphereVisuals.js';
import type {SphereMeta} from './SphereVisuals.js';
type Body=ReturnType<typeof PhysicsBodyFactory.createStaticBody>['rigidBody'];
interface Collision {vertices:number[];indices:number[]}
interface Media {exterior:string;exteriorPoster:string;interior:string;interiorPoster:string}
const BASE='/build/sphere/';
export class SphereVenue {
    private meta:SphereMeta|null=null;
    private media:Media|null=null;
    private revision='';
    private exterior:THREE.Group|null=null;
    private interior:THREE.Group|null=null;
    private exosphere:SphereVideo|null=null;
    private immersive:SphereVideo|null=null;
    private body:Body|null=null;
    private exteriorBody:Body|null=null;
    private exteriorCollision:Collision|null=null;
    private doors:Door[]=[];
    private doorMeshes:THREE.Mesh[]=[];
    private approachedPortals=new Set<number>();
    private releaseInterior:(()=>void)|null=null;
    private releaseExterior:(()=>void)|null=null;
    /** The four atrium lights, offered to the shared pool while the player is here (see SiteLights). */
    private sites:LightSite[]=[];
    private pending=false;
    private passing=false;
    private disposed=false;
    private lastNear=0;
    private nextCheck=0;
    private center=new THREE.Vector3();
    private frustum=new THREE.Frustum();
    private clipMatrix=new THREE.Matrix4();
    private sphere=new THREE.Sphere();
    private outdoorEnvironmentIntensity:number|null=null;
    private stopOnPause=(state:GameState)=>{if(state!==GameState.PLAYING){this.exosphere?.setActive(false);this.immersive?.setActive(false);}};
    constructor(private engine:EngineLike,private surfaces:GroundSurfaceIndex,private loading:StreamingWork,private siteLights:SiteLights){getGameStateManager().addListener(this.stopOnPause);}
    async load():Promise<void>{
        const [meta,version,media]=await Promise.all([fetch(BASE+'sphere.json').then(r=>r.json()),fetch(BASE+'version.json').then(r=>r.json()),fetch(BASE+'media.json').then(r=>r.json())]);
        if(this.disposed)return;this.meta=meta as SphereMeta;this.media=media as Media;this.revision=version.revision;this.center.set(...this.meta.center);this.sphere.set(this.center.clone().add(new THREE.Vector3(0,48,0)),95);
        const [gltf,collision]=await Promise.all([new GLTFLoader().loadAsync(await glbUrl(BASE+'exterior.glb?v='+this.revision)),fetch(BASE+'exterior-collision.json?v='+this.revision).then(r=>r.json())]);
        if(this.disposed){disposeSphereRoot(gltf.scene);return;}
        this.exterior=gltf.scene;this.exterior.position.copy(this.center);this.exterior.name='Sphere / permanent exterior';this.exterior.userData.perfOwner='Sphere · exterior';this.exterior.userData.perfKind='exterior';finishSphereMaterials(this.exterior);addSphereSigns(this.exterior,this.meta,'exterior');this.engine.scene!.add(this.exterior);
        this.exosphere=new SphereVideo(BASE+this.media.exterior,BASE+this.media.exteriorPoster);this.exosphere.material.side=THREE.FrontSide;this.applyScreen(this.exterior,'shell',this.exosphere.material);
        this.exteriorCollision=collision as Collision;
        this.releaseExterior=this.surfaces.register(this.exterior);
        const radius=this.meta.radius,cy=this.meta.height-radius;
        const shadow=new THREE.Mesh(new THREE.SphereGeometry(radius,32,20,0,Math.PI*2,0,Math.acos(-cy/radius)),new THREE.MeshBasicMaterial());
        shadow.position.y=cy;shadow.layers.set(30);shadow.castShadow=true;shadow.name='Sphere / low detail sun silhouette';this.exterior.add(shadow);
        console.info('[Sphere] Exterior ready; detailed interior unloaded');
    }
    private applyScreen(root:THREE.Group,part:string,material:THREE.Material):void {
        root.traverse(o=>{if(o instanceof THREE.Mesh && o.userData.spherePart===part){const old=o.material;if(!Array.isArray(old)){if(old instanceof THREE.MeshStandardMaterial){old.map?.dispose();old.emissiveMap?.dispose();}old.dispose();}o.material=material;o.receiveShadow=false;}});
    }
    private makeBody(data:Collision):Body {
        const p=planCollider({name:'Sphere',shape:'trimesh',vertices:data.vertices,indices:data.indices},'terrain');p.position.copy(this.center);
        return PhysicsBodyFactory.createStaticBody(this.engine.physicsWorld!,p.position,{shape:p.shape,friction:.8,collisionGroup:p.collisionGroup,collisionMask:p.collisionMask},p.quaternion).rigidBody;
    }
    /** Opaque inner zone; keep outdoors around all entrances and glass vestibules. */
    getView(player:THREE.Vector3,camera:THREE.Vector3):{building:string;outside:boolean;showGround:boolean}|null {
        if(!this.interior)return null;
        const deep=(p:THREE.Vector3)=>Math.hypot(p.x-this.center.x,p.z-this.center.z)<65 && p.y>1 && p.y<78;
        return deep(player)&&deep(camera)?{building:'sphere',outside:false,showGround:false}:null;
    }
    /** A vehicle passing the Sphere does not stream its atrium and auditorium. */
    setPassing(passing:boolean):void {this.passing=passing;}
    update(player:THREE.Vector3,outside:boolean):void {
        if(!this.meta || !this.exterior || this.disposed)return;
        const d=Math.hypot(player.x-this.center.x,player.z-this.center.z),now=performance.now();
        const here=d<130;
        this.exterior.visible=outside || here;
        if(this.interior)this.interior.visible=outside || here;
        for(const m of this.doorMeshes)m.visible=outside || here;
        if(here)this.lastNear=now;
        if(now>this.nextCheck){
            this.nextCheck=now+400;
            if(d<175 && !this.exteriorBody && this.exteriorCollision)this.exteriorBody=this.makeBody(this.exteriorCollision);
            if(here && !this.passing && !this.interior && !this.pending){this.pending=true;this.loading.enqueue('sphere','Sphere atrium and auditorium',async()=>{try{await this.loadInterior();}finally{this.pending=false;}});}
            if(d>190 && now-this.lastNear>15000){this.unloadInterior();if(this.exteriorBody?.isValid())this.engine.physicsWorld!.removeRigidBody(this.exteriorBody);this.exteriorBody=null;}
        }
        const camera=this.engine.camera;
        // Three uses scene.environmentIntensity for a scene-provided IBL, so
        // material.envMapIntensity alone cannot keep sunset out of this bowl.
        const enclosed=!!camera && !!this.getView(player,camera.position);
        if(enclosed){
            if(this.outdoorEnvironmentIntensity===null)this.outdoorEnvironmentIntensity=this.engine.scene!.environmentIntensity;
            this.engine.scene!.environmentIntensity=.025;
        } else this.restoreEnvironment();
        let inFrame=false;if(camera){this.clipMatrix.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);this.frustum.setFromProjectionMatrix(this.clipMatrix);inFrame=this.frustum.intersectsSphere(this.sphere);}
        const playing=getGameStateManager().getCurrentState()===GameState.PLAYING;
        // Entrance pairs welcome approaching visitors automatically. Keep E
        // available, and don't fight a manual close while they remain nearby.
        if(playing)for(let i=0;i<this.meta.portals.length;i++){
            const p=this.meta.portals[i]!,distance=Math.hypot(player.x-this.center.x-p.p[0],player.z-this.center.z-p.p[2]);
            if(distance<3.2 && Math.abs(player.y-p.p[1])<2 && !this.approachedPortals.has(i) && this.doors[i*2]){
                this.approachedPortals.add(i);this.doors[i*2]!.open();
            } else if(distance>8 && this.approachedPortals.delete(i))this.doors[i*2]?.close();
        }
        this.exosphere?.setActive(playing && outside && d<2300 && inFrame);
        this.immersive?.setActive(playing && !!this.interior && d<88 && player.y>5 && (player.y>12 || player.z-this.center.z>-36));
        this.siteLights.offer('sphere',here&&this.interior?this.sites:[]);this.siteLights.apply(player);
    }
    private async loadInterior():Promise<void>{
        if(!this.meta || !this.media)return;
        const [gltf,collision]=await Promise.all([new GLTFLoader().loadAsync(await glbUrl(BASE+'interior.glb?v='+this.revision)),fetch(BASE+'interior-collision.json?v='+this.revision).then(r=>r.json())]);
        if(this.disposed){disposeSphereRoot(gltf.scene);return;}
        this.interior=gltf.scene;this.interior.position.copy(this.center);this.interior.name='Sphere / streamed atrium and four-tier auditorium';this.interior.userData.perfOwner='Sphere · interior';this.interior.userData.perfKind='interior';finishSphereMaterials(this.interior);addSphereSigns(this.interior,this.meta,'interior');this.engine.scene!.add(this.interior);
        this.immersive=new SphereVideo(BASE+this.media.interior,BASE+this.media.interiorPoster);this.applyScreen(this.interior,'screen',this.immersive.material);
        this.releaseInterior=this.surfaces.register(this.interior);addSphereSeats(this.interior,this.meta);
        // Lit by sun, sky, ambient and the four shared venue lights only (see InteriorLighting).
        lightInterior(this.interior,interiorLightsNode(this.engine.scene!,this.siteLights.pointLights));
        this.body=this.makeBody(collision as Collision);
        for(const portal of this.meta.portals){
            const [dx,dz]=portal.direction,yaw=Math.atan2(dx,dz),pair:Door[]=[];
            for(const side of [-1,1]){
                const before=new Set(this.engine.scene!.children),w=portal.width/2;
                const door=new Door(this.engine,{...DEFAULT_DOOR_OPTIONS,position:new THREE.Vector3(this.center.x+portal.p[0]+dz*side*w/2,portal.p[1]+portal.height/2,this.center.z+portal.p[2]-dx*side*w/2),rotation:yaw,width:w-.015,height:portal.height,thickness:.14,slideDistance:side*(w+.08),slideDurationMs:650,onOpen:()=>pair.forEach(d=>d.open()),onClose:()=>pair.forEach(d=>d.close())});
                pair.push(door);this.doors.push(door);
                const leaf=this.engine.scene!.children.find(o=>!before.has(o));if(leaf instanceof THREE.Mesh){
                    const mat=leaf.material as THREE.MeshStandardMaterial;mat.color.setHex(0x819dae);mat.opacity=.22;mat.transparent=true;mat.depthWrite=false;mat.metalness=.2;mat.roughness=.2;
                    for(const [x,y,bw,bh] of [[-w/2,0,.07,portal.height],[w/2,0,.07,portal.height],[0,-portal.height/2,w,.09],[0,portal.height/2,w,.09],[side*-.8,0,.06,.8]]){const bar=new THREE.Mesh(new THREE.BoxGeometry(bw,bh,.17),new THREE.MeshStandardMaterial({color:0x4e6570,metalness:.7,roughness:.32}));bar.position.set(x!,y!,0);leaf.add(bar);}
                    this.doorMeshes.push(leaf);
                }
            }
        }
        this.sites=[[0,20,-52,0x70dfff],[0,38,20,0x577bff],[-43,15,-43,0x97ddff],[43,15,-43,0x97ddff]].map(([x,y,z,color],i)=>({x:this.center.x+x!,y:y!,z:this.center.z+z!,color:color!,intensity:i<2?1600:650,distance:65}));
        this.loading.revealUntilReady(this.interior);
        console.info(`[Sphere] Interior ready: ${this.meta.seats.length} instanced seats; one static interior collider; ${this.meta.portals.length} working entrances`);
    }
    review(name:string):{position:THREE.Vector3;yaw:number;pitch:number}|null {
        const v=this.meta?.views[name];if(!v)return null;const d=new THREE.Vector3(...v.target).sub(new THREE.Vector3(...v.p));
        return {position:new THREE.Vector3(...v.p).add(this.center).add(new THREE.Vector3(0,-1.7,0)),yaw:Math.atan2(-d.x,-d.z),pitch:-Math.atan2(d.y,Math.hypot(d.x,d.z))};
    }
    private unloadInterior():void {
        this.releaseInterior?.();this.releaseInterior=null;
        for(const door of this.doors)door.dispose();this.doors=[];this.approachedPortals.clear();
        for(const leaf of this.doorMeshes)for(const child of [...leaf.children])disposeSphereRoot(child);this.doorMeshes=[];
        if(this.body?.isValid())this.engine.physicsWorld!.removeRigidBody(this.body);this.body=null;
        if(this.interior)disposeSphereRoot(this.interior);this.interior=null;this.immersive?.dispose();this.immersive=null;
        this.sites=[];this.siteLights.offer('sphere',[]);
    }
    get stats(){return {interior:!!this.interior,seatInstances:this.interior?this.meta?.seats.length??0:0,physicsBodies:(this.body?1:0)+(this.exteriorBody?1:0)+this.doors.length};}
    private restoreEnvironment():void {if(this.outdoorEnvironmentIntensity!==null){if(this.engine.scene)this.engine.scene.environmentIntensity=this.outdoorEnvironmentIntensity;this.outdoorEnvironmentIntensity=null;}}
    dispose():void {this.disposed=true;this.restoreEnvironment();getGameStateManager().removeListener(this.stopOnPause);this.unloadInterior();this.releaseExterior?.();if(this.exteriorBody?.isValid())this.engine.physicsWorld!.removeRigidBody(this.exteriorBody);if(this.exterior)disposeSphereRoot(this.exterior);this.exosphere?.dispose();}
}
