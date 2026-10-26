import {makeDoorTrim} from './DoorTrim.js';
import * as THREE from 'three';
import {InteractableComponent} from 'engine/interaction/InteractableComponent.js';
import {Door,DEFAULT_DOOR_OPTIONS} from 'engine/gameplay/doors/Door.js';
import {PhysicsBodyFactory} from 'engine/physics/world3d/PhysicsBodyFactory.js';
import {planCollider} from 'engine/meshlevel/MeshLevelColliders.js';
import type {EngineLike} from 'types/game.js';
import type {GroundSurfaceIndex} from './GroundSurfaceIndex.js';
import type {StreamingWork} from './StreamingWork.js';
import {createPassageGeometry} from './GeographicPassageGeometry.js';
import type {PassageData,PassageEntry} from './GeographicPassageGeometry.js';
import {interiorLightsNode,lightInterior} from './InteriorLighting.js';
import type {LightsNode} from 'three/webgpu';
import {loadRecords} from './PackedRecords.js';
interface Resident {data:PassageData;root:THREE.Group;doors:Door[];lights:THREE.Vector3[];dispose:()=>void;lastNear:number}
export class GeographicPassages {
    private entries:PassageEntry[]=[];
    private resident=new Map<string,Resident>();
    private pending=new Set<string>();
    private lightPool:THREE.PointLight[]=[];
    private passing=false;
    private disposed=false;
    private player=new THREE.Vector3();
    private nextCheck=0;
    private interiorLights:LightsNode|null=null;
    private proxyRoot=new THREE.Group();
    private proxies:{id:string;index:number;door:THREE.Matrix4;frame:THREE.Matrix4;hidden?:boolean}[]=[];
    private proxyDoors:THREE.InstancedMesh|null=null;
    private proxyFrames:THREE.InstancedMesh|null=null;
    private hiddenProxy=new THREE.Matrix4().makeScale(0,0,0);
    constructor(private engine:EngineLike,private surfaces:GroundSurfaceIndex,private loading:StreamingWork){}
    async load():Promise<void>{
        this.entries=await loadRecords<PassageEntry[]>('/build/geographic-strip/access/manifest.bin');
        // Closed entrance silhouettes remain visible from afar. Interior
        // residency changes never expose an empty hole in the building shell.
        const count=this.entries.reduce((n,e)=>n+e.portals.length,0);
        this.proxyDoors=new THREE.InstancedMesh(new THREE.BoxGeometry(4.15,3.1,.24),new THREE.MeshStandardMaterial({color:0xffffff,roughness:.32,metalness:.2}),count);
        this.proxyFrames=new THREE.InstancedMesh(new THREE.BoxGeometry(4.8,3.65,.18),new THREE.MeshStandardMaterial({color:0xffffff,roughness:.6}),count);
        this.proxyDoors.frustumCulled=this.proxyFrames.frustumCulled=false;
        this.proxyRoot.add(this.proxyFrames,this.proxyDoors);this.engine.scene!.add(this.proxyRoot);
        let index=0;for(const e of this.entries)for(const p of e.portals){
            const q=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),Math.atan2(p.direction[0],p.direction[1]));
            const width=p.width??4.14,height=p.height??3.1;
            const door=new THREE.Matrix4().compose(new THREE.Vector3(p.p[0],p.y+height/2,p.p[1]),q,new THREE.Vector3(width/4.14,height/3.1,1));
            const frame=new THREE.Matrix4().compose(new THREE.Vector3(p.p[0],p.y+(height+.55)/2,p.p[1]),q,new THREE.Vector3((width+.66)/4.8,(height+.55)/3.65,1));
            this.proxyDoors.setColorAt(index,new THREE.Color(p.metal?0xa5aaa9:0x253638));this.proxyFrames.setColorAt(index,new THREE.Color(p.width?0x9fa9aa:0xc7ae85));
            this.proxyDoors.setMatrixAt(index,door);this.proxyFrames.setMatrixAt(index,frame);this.proxies.push({id:e.id,index,door,frame});index++;
        }
        for(let i=0;i<6;i++){const light=new THREE.PointLight(0xffe4bc,0,12,2);this.engine.scene!.add(light);this.lightPool.push(light);}
    }
    private distance(p:THREE.Vector3,entry:PassageEntry):number {
        const [x0,z0,x1,z1]=entry.bounds;
        return Math.hypot(Math.max(x0-p.x,0,p.x-x1),Math.max(z0-p.z,0,p.z-z1));
    }
    /** The concourses are pedestrian routes: nothing is streamed in for a passing vehicle. */
    setPassing(passing:boolean):void {this.passing=passing;}
    update(player:THREE.Vector3,outside:boolean):void {
        if(this.disposed)return;this.player.copy(player);this.proxyRoot.visible=outside;
        const now=performance.now();
        if(now>this.nextCheck){
            this.nextCheck=now+250;
            for(const entry of this.entries){
                const d=this.distance(player,entry),resident=this.resident.get(entry.id);
                if(resident){resident.root.visible=outside; if(d<90)resident.lastNear=now;else if(now-resident.lastNear>15000){resident.dispose();this.resident.delete(entry.id);}}
                else if(outside && !this.passing && d<45 && !this.pending.has(entry.id)){
                    this.pending.add(entry.id);
                    this.loading.enqueue('concourse:'+entry.id,entry.name,async()=>{
                        try{await this.instantiate(entry);}finally{this.pending.delete(entry.id);}
                    });
                }
            }
        }
        let proxyChanged=false;
        for(const proxy of this.proxies){const hidden=this.resident.has(proxy.id);if(proxy.hidden===hidden)continue;proxy.hidden=hidden;proxyChanged=true;this.proxyDoors!.setMatrixAt(proxy.index,hidden?this.hiddenProxy:proxy.door);this.proxyFrames!.setMatrixAt(proxy.index,hidden?this.hiddenProxy:proxy.frame);}
        if(proxyChanged && this.proxyDoors && this.proxyFrames){this.proxyDoors.instanceMatrix.needsUpdate=true;this.proxyFrames.instanceMatrix.needsUpdate=true;}
        const lights=outside?[...this.resident.values()].filter(r=>r.root.visible).flatMap(r=>r.lights).sort((a,b)=>a.distanceToSquared(player)-b.distanceToSquared(player)).slice(0,6):[];
        this.lightPool.forEach((l,i)=>{const p=lights[i];l.intensity=p && p.distanceTo(player)<22?22:0;if(p)l.position.copy(p);});
    }
    private async instantiate(entry:PassageEntry):Promise<void>{
        const data=await loadRecords<PassageData>(`/build/geographic-strip/access/${entry.id}.bin`);if(this.disposed)return;
        const art=createPassageGeometry(data),world=this.engine.physicsWorld!;art.root.userData.perfOwner='Bridge concourses';art.root.userData.perfKind='other';this.engine.scene!.add(art.root);
        const release=this.surfaces.register(art.root);
        const plan=data.collision.indices.length?planCollider({name:entry.name,shape:'trimesh',vertices:data.collision.vertices,indices:data.collision.indices instanceof Uint32Array?data.collision.indices:Uint32Array.from(data.collision.indices)},'terrain'):null;
        const body=plan?PhysicsBodyFactory.createStaticBody(world,plan.position,{shape:plan.shape,friction:.85,collisionGroup:plan.collisionGroup,collisionMask:plan.collisionMask},plan.quaternion).rigidBody:null;
        const doors:Door[]=[];const skins:THREE.Object3D[]=[];const interactions:InteractableComponent[]=[];
        if(data.lift){
            const [x,z]=data.lift;const high=data.portals[0]!.y;
            for(const level of [.18,high]){
                const button=new THREE.Mesh(new THREE.BoxGeometry(.24,.4,.12),new THREE.MeshStandardMaterial({color:0x334c52,emissive:0x50c3cb,emissiveIntensity:.35}));
                button.position.set(data.liftButton?.[0]??x+1.3,level+1.2,data.liftButton?.[1]??z);art.root.add(button);
                const target=level<1?high:.18;
                interactions.push(new InteractableComponent(world,{object3D:button,radius:2,interactable:{
                    getInteractStartDisplayName:()=>target>1?'Lift to pedestrian bridge':'Lift to street',
                    onInteractStart:()=>{const controller=this.engine.getPlayerController();if(!controller?.teleportTo)return false;controller.teleportTo(x,target+.05,z);return true;}
                }}));
            }
        }
        for(const portal of data.portals){
            const [dx,dz]=portal.direction,rotation=Math.atan2(dx,dz),nx=dz,nz=-dx;
            const width=portal.width??4.14,height=portal.height??3.1,leafWidth=width/2;
            const pair:Door[]=[];
            for(const side of [-1,1]){
                const before=new Set(this.engine.scene!.children);
                const door=new Door(this.engine,{...DEFAULT_DOOR_OPTIONS,position:new THREE.Vector3(portal.p[0]+nx*side*width/4,portal.y+height/2,portal.p[1]+nz*side*width/4),rotation,width:leafWidth,height,thickness:.1,slideDistance:side*(leafWidth+.05),slideDurationMs:650,onOpen:()=>pair.forEach(d=>d.open()),onClose:()=>pair.forEach(d=>d.close())});doors.push(door);pair.push(door);
                const leaf=this.engine.scene!.children.find(o=>!before.has(o));
                if(leaf instanceof THREE.Mesh){
                    const material=leaf.material as THREE.MeshStandardMaterial;material.color.setHex(portal.metal?0xa5aaa9:0x769191);material.transparent=!portal.metal;material.opacity=portal.metal?1:.32;material.roughness=portal.metal ? .4 : .2;material.metalness=portal.metal ? .65 : .15;material.depthWrite=!!portal.metal;
                    const trim=makeDoorTrim([[-leafWidth/2+.035,0,.075,height],[leafWidth/2-.035,0,.075,height],[0,-height/2+.05,leafWidth,.075],[0,height/2-.05,leafWidth,.075],[side*(-leafWidth/2+.23),0,.055,.7]],.12,new THREE.MeshStandardMaterial({color:data.lift||portal.metal?0x8d9393:0x665437,metalness:.7,roughness:.3}));leaf.add(trim);skins.push(trim);
                    art.root.add(leaf);
                }
            }
        }
        if(data.interior)lightInterior(art.root,this.interiorLights??=interiorLightsNode(this.engine.scene!,this.lightPool));
        this.loading.revealUntilReady(art.root);
        this.resident.set(entry.id,{data,root:art.root,doors,lights:Array.from({length:data.lights.length/3},(_,i)=>new THREE.Vector3().fromArray(data.lights,i*3)),lastNear:performance.now(),dispose:()=>{
            release();for(const i of interactions)i.dispose();for(const door of doors)door.dispose();for(const o of skins)if(o instanceof THREE.Mesh){o.geometry.dispose();(o.material as THREE.Material).dispose();}
            if(body?.isValid())world.removeRigidBody(body);art.dispose();
        }});
        console.info(`[BridgeConcourse] ${entry.name}: ${data.portals.length} entrances, one static collision mesh`);
    }
    get stats(){return {resident:this.resident.size,total:this.entries.length};}
    dispose():void {this.disposed=true;for(const mesh of [this.proxyDoors,this.proxyFrames])if(mesh){mesh.geometry.dispose();(mesh.material as THREE.Material).dispose();mesh.dispose();}this.proxyRoot.removeFromParent();for(const r of this.resident.values())r.dispose();this.resident.clear();for(const light of this.lightPool){light.removeFromParent();light.dispose();}}
}
