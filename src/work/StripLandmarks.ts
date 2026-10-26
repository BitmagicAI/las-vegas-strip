import {applyLawnMaterial} from './LawnMaterial.js';
import {filmDetail} from './FilmDetail.js';
import {glbUrl} from './OptimizedGlb.js';
import {interiorLightsNode,lightInterior} from './InteriorLighting.js';
import type {LightsNode} from 'three/webgpu';
import {ResortFoliage} from './ResortFoliage.js';
import {makeDoorTrim} from './DoorTrim.js';
import {unmergedCasterShadows,unmergedCasterShadowsSteps} from './CityShadows.js';
import {runSliced} from './FrameBudget.js';
import {type CollisionPack,loadCollisionPack} from './CollisionPack.js';
import {loadRecords} from './PackedRecords.js';
import {GroveLod} from './GroveLod.js';
import {CityLod} from './CityLod.js';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {Door,DEFAULT_DOOR_OPTIONS} from 'engine/gameplay/doors/Door.js';
import {PhysicsBodyFactory} from 'engine/physics/world3d/PhysicsBodyFactory.js';
import {planCollider} from 'engine/meshlevel/MeshLevelColliders.js';
import {GameState,getGameStateManager} from 'engine/core/GameStateManager.js';
import type {EngineLike} from 'types/game.js';
import type {GroundSurfaceIndex} from './GroundSurfaceIndex.js';
import type {StreamingWork} from './StreamingWork.js';
import {disposeSphereRoot} from './SphereVisuals.js';
import type {SiteLights,LightSite} from './SiteLights.js';
import {runtimeUrl} from './RuntimeAssets.js';
import {loadGltf,prefetch} from './Prefetch.js';
import {appear} from './Appear.js';
import {compileSubtree} from './ShaderSharing.js';
type Body=ReturnType<typeof PhysicsBodyFactory.createStaticBody>['rigidBody'];
/** a point, as the record file gives it (PackedRecords.ts: a typed array of three) */
type XYZ=Float32Array&readonly [number,number,number];
interface Zone {origin:XYZ;yaw:number;width:number;depth:number;height:number}
interface Portal {p:XYZ;yaw:number;width:number;height:number;name:string}
interface Meta {exteriorOnly?:boolean;hotelSources?:string[];structural?:boolean;exteriorCollision?:string;outside?:boolean;levelY?:number;preloadDistance?:number;key:string;name:string;building?:string;bounds:Float32Array&readonly [number,number,number,number];portals:Portal[];/** x, y, z per point */accessPoints?:Float32Array;zones:Zone[];lights:{p:XYZ;color:number;power:number;range:number}[];views:Record<string,{eye:XYZ;target:XYZ}>;/** x, y, z, yaw per seat */seats?:Float32Array;wheel?:{center:XYZ;radius:number;yaw:number;cabins:number}}
interface Resident {/** top of the venue's podium meshes (-Infinity without one) */podiumTop:number;meta:Meta;exterior:THREE.Group;interior:THREE.Group|null;body:Body|null;exteriorBody:Body|null;exteriorLoaded:boolean;doors:Door[];leaves:THREE.Mesh[];sites:LightSite[];releaseExterior:()=>void;releaseInterior:(()=>void)|null;pending:boolean;lastNear:number;retryAfter:number;nearPortals:Set<number>;details:THREE.Object3D[]}
class ArrivalDoor extends Door {
    constructor(engine:EngineLike,options:ConstructorParameters<typeof Door>[1],private ready:()=>boolean){super(engine,options);}
    override open():void{if(this.ready())super.open();}
}
const BASE='/build/strip-landmarks/';
/** Permanent skyline envelopes; on-demand public interiors and hotel modules.
 * No venue allocates a full set of rooms or thousands of individual seat objects. */
export class StripLandmarks {
    private venues:Resident[]=[];
    private lods=new Map<Resident,CityLod>();
    private groves:GroveLod[]=[];
    private foliage:ResortFoliage[]=[];
    private disposed=false;
    private nextCheck=0;
    private passing=false;
    private lastWheelTime=0;
    private wheelAngle=0;
    private rim:THREE.Group|null=null;
    private cabins:{root:THREE.Group;start:THREE.Vector3}[]=[];
    /** The four lights every interior borrows. Created once; never added, removed or hidden afterwards (see SiteLights). */
    constructor(private engine:EngineLike,private surfaces:GroundSurfaceIndex,private loading:StreamingWork,private lights:SiteLights,private base=BASE){}
    /** While passing at speed, interiors are not streamed in; collision for the exterior still is. */
    setPassing(passing:boolean):void {this.passing=passing;}
    /** `sliced` (the city loading behind play, 2026-10-25): exteriors load nearest `focus` first, each built over
     * several frames within the shared loading budget (FrameBudget.ts), compiled off the frame and only then shown,
     * dropping in from the sky (Appear.ts). Without it everything is built at once, as before. */
    async load(sliced=false,focus?:()=>THREE.Vector3):Promise<void>{
        const all=await loadRecords<Meta[]>(this.base+'venues.bin');
        let meta=all;
        if(focus){const f=focus(),d=(m:Meta)=>Math.hypot((m.bounds[0]+m.bounds[2])/2-f.x,(m.bounds[1]+m.bounds[3])/2-f.z);meta=[...all].sort((a,b)=>d(a)-d(b));}
        // every exterior downloads ahead of the serial parse below (Prefetch.ts)
        prefetch(await Promise.all(meta.map(m=>glbUrl(this.base+m.key+'-exterior.glb'))));
        // Limit concurrent parsing so startup doesn't briefly double every asset's memory.
        for(const m of meta){
            const gltf=await loadGltf(new GLTFLoader(),await glbUrl(this.base+m.key+'-exterior.glb'));
            if(this.disposed){disposeSphereRoot(gltf.scene);return;}
            const exterior=gltf.scene;exterior.name=m.name+' / exterior';exterior.userData.perfOwner=m.name+' · exterior';exterior.userData.perfKind='exterior';this.finish(exterior,false);if(m.key==='bellagioBlock')applyLawnMaterial(exterior);if(sliced)exterior.visible=false;this.engine.scene!.add(exterior);
            // Podiums, shells, guest and mapped towers cast the sun's shadow: from their city batches (CityLod) or as
            // proxies when no batch takes them (unmergedCasterShadows, after the LOD below).
            const details:THREE.Object3D[]=[];
            exterior.traverse(o=>{if(o.userData.detail)details.push(o);if(o instanceof THREE.Mesh && !o.userData.detail && /podium|mall-shell|arena-shell|campanile|guest-|tower\/|lakefront-(pavilions|rotundas|village-shell)/.test(String(o.userData.source)))o.userData.cityCaster=true;});
            let podiumTop=-Infinity;const box=new THREE.Box3();
            exterior.traverse(o=>{if(o instanceof THREE.Mesh&&/podium/.test(String(o.userData.source))){box.setFromObject(o);podiumTop=Math.max(podiumTop,box.max.y);}});
            const v:Resident={podiumTop,meta:m,exterior,interior:null,body:null,exteriorBody:null,exteriorLoaded:false,doors:[],leaves:[],sites:m.lights.map(l=>({x:l.p[0],y:l.p[1],z:l.p[2],color:l.color,intensity:l.power,distance:l.range})),releaseExterior:sliced?await this.surfaces.registerSliced(exterior):this.surfaces.register(exterior),releaseInterior:null,pending:false,lastNear:0,retryAfter:0,nearPortals:new Set(),details};if(!sliced)this.venues.push(v);this.createDoors(v);
            if(m.key==='bellagioBlock'){v.exteriorBody=this.body(await this.collision(m.exteriorCollision??m.key+'-exterior-collision.json'),m.name);v.exteriorLoaded=true;}
            if(m.wheel)this.setupWheel(v);
            // The High Roller moves independently; its stationary resort still batches like other buildings.
            const lod=new CityLod(exterior,{facade:true,sliced,prepare:root=>compileSubtree(this.engine,root),key:o=>{
                const source=String(o.userData.source??'');
                if(m.wheel&&source.startsWith('wheel-'))return null;
                if(source.startsWith('arrival-tree/'))return null;
                // A guest tower, or a mapped tower drawn here (tower/<its source>): its own block, hidden from its own rooms.
                if(source.startsWith('guest-')||source.startsWith('tower/'))return source;
                if(typeof o.userData.spatialCell==='string')return m.key+':'+o.userData.spatialCell;
                if(source.startsWith('lakefront-'))return 'lakefront-village';
                return m.key;
            }});
            this.lods.set(v,lod);
            if(!sliced)unmergedCasterShadows(exterior);
            if(sliced){
                await lod.ready;if(this.disposed)return;
                await runSliced(unmergedCasterShadowsSteps(exterior));
                await compileSubtree(this.engine,exterior);
                exterior.visible=true;this.venues.push(v);appear(exterior);
            }
        }
        for(const v of this.venues)if(v.meta.key==='bellagioBlock'){const foliage=new ResortFoliage(this.engine.scene!,v.exterior);try{await foliage.load(sliced);if(this.disposed){foliage.dispose();return;}if(sliced){await compileSubtree(this.engine,foliage.group);foliage.show();appear(foliage.group);}this.foliage.push(foliage);}catch(error){foliage.dispose();console.warn('[ResortFoliage] Keeping existing planting because assets could not load',error);}}
        for(const v of this.venues)this.groves.push(new GroveLod(v.exterior));
        console.info(`[StripLandmarks] ${this.venues.length} exteriors ready; public interiors and guest hotels remain streamed.`);
    }
    private finish(root:THREE.Group,inside:boolean):void{
        root.traverse(o=>{if(!(o instanceof THREE.Mesh))return;o.castShadow=false;o.receiveShadow=true;
            // glTF splits multi-material tree meshes into children; extras remain on their parent.
            if(!o.userData.source){let parent=o.parent;while(parent&&parent!==root){if(String(parent.userData.source??'').startsWith('arrival-tree/')){o.userData.source=parent.userData.source;break;}parent=parent.parent;}}

            for(const m of Array.isArray(o.material)?o.material:[o.material]){m.side=THREE.DoubleSide;if(m instanceof THREE.MeshStandardMaterial){m.envMapIntensity=inside?.24:.6;if(m.transparent)m.depthWrite=false;if(inside){m.fog=false;if(m.emissive.r+m.emissive.g+m.emissive.b<.001){m.emissive.copy(m.color).multiplyScalar(.09);m.emissiveMap=m.map;}}}}
        });
    }
    private createDoors(v:Resident):void{
        for(const p of v.meta.portals){
            const pair:Door[]=[];
            for(const side of [-1,1]){
                const w=p.width/2,co=Math.cos(p.yaw),si=Math.sin(p.yaw),before=new Set(this.engine.scene!.children);
                const door=new ArrivalDoor(this.engine,{...DEFAULT_DOOR_OPTIONS,position:new THREE.Vector3(p.p[0]+co*side*w/2,p.p[1]+p.height/2,p.p[2]-si*side*w/2),rotation:p.yaw,width:w-.02,height:p.height,thickness:.12,slideDistance:side*(w+.04),slideDurationMs:650,onOpen:()=>pair.forEach(d=>d.open()),onClose:()=>pair.forEach(d=>d.close())},()=>!!v.interior);
                pair.push(door);v.doors.push(door);
                const leaf=this.engine.scene!.children.find(o=>!before.has(o));if(!(leaf instanceof THREE.Mesh))continue;leaf.userData.perfOwner='Public entrance doors';leaf.userData.perfKind='exterior';
                const mat=leaf.material as THREE.MeshStandardMaterial;mat.color.setHex(0x8eabb6);mat.transparent=true;mat.opacity=.2;mat.depthWrite=false;mat.metalness=.2;mat.roughness=.16;
                const frame=new THREE.MeshStandardMaterial({color:0x384952,metalness:.65,roughness:.28});
                leaf.add(makeDoorTrim([[-w/2,0,.07,p.height],[w/2,0,.07,p.height],[0,-p.height/2,w,.08],[0,p.height/2,w,.08],[-side*.55,0,.045,.8]],.16,frame));v.leaves.push(leaf);
            }
        }
    }
    /** A venue's collision mesh (named by its JSON source; the game loads the packed .bin, CollisionPack.ts). */
    private collision(file:string):Promise<CollisionPack>{return loadCollisionPack(this.base+file.replace(/\.json$/,'.bin'));}
    private body(pack:CollisionPack,name:string):Body|null {
        if(!pack.triangleCount(0))return null;const p=planCollider(pack.trimesh(0,name),'terrain');return PhysicsBodyFactory.createStaticBody(this.engine.physicsWorld!,p.position,{shape:p.shape,friction:.85,collisionGroup:p.collisionGroup,collisionMask:p.collisionMask},p.quaternion).rigidBody;
    }
    private async loadInterior(v:Resident):Promise<void>{
        if(v.meta.exteriorOnly)return;
        const [gltf,data]=await Promise.all([new GLTFLoader().loadAsync(await glbUrl(this.base+v.meta.key+'-interior.glb')),this.collision(v.meta.key+'-interior-collision.json')]);
        if(this.disposed){disposeSphereRoot(gltf.scene);return;}
        const root=gltf.scene;root.name=v.meta.name+' / streamed public interior';root.userData.perfOwner=v.meta.name+' · interior';root.userData.perfKind='interior';this.finish(root,true);
        // Lit by sun, sky, ambient and the four shared venue lights only (see InteriorLighting).
        lightInterior(root,this.interiorLights??=interiorLightsNode(this.engine.scene!,this.lights.pointLights));this.engine.scene!.add(root);v.interior=root;v.body=this.body(data,root.name);v.releaseInterior=this.surfaces.register(root);
        if(v.meta.seats)this.addSeats(root,v.meta.seats);
        // At most four real lights light the nearest fixtures, borrowed from the shared pool in update();
        // decorative luminous meshes do the rest. Never create lights here: a light added to or removed from
        // the scene rebuilds every lit shader in view.
        this.loading.revealUntilReady(root);
    }
    private addSeats(root:THREE.Group,seats:Float32Array):void {
        const mat=new THREE.MeshStandardMaterial({color:0x323638,roughness:.75,emissive:0x080a0b}),steel=new THREE.MeshStandardMaterial({color:0x424341,roughness:.45,metalness:.5});
        const parts:[[number,number,number],[number,number,number],THREE.Material][]=[[[0,0,0],[.48,.12,.46],mat],[[0,.32,-.19],[.49,.66,.12],mat],[[0,-.21,0],[.1,.36,.24],steel],[[.27,.18,0],[.07,.06,.44],steel]];
        const object=new THREE.Object3D(),offset=new THREE.Vector3();
        for(const [local,size,material] of parts){const count=seats.length/4,mesh=new THREE.InstancedMesh(new THREE.BoxGeometry(...size),material,count);mesh.name='Arena shared seat part';for(let i=0;i<count;i++){object.rotation.set(0,seats[i*4+3]!,0);offset.set(...local).applyEuler(object.rotation);object.position.set(seats[i*4]!,seats[i*4+1]!,seats[i*4+2]!).add(offset);object.updateMatrix();mesh.setMatrixAt(i,object.matrix);}mesh.instanceMatrix.needsUpdate=true;mesh.computeBoundingSphere();root.add(mesh);}
    }
    private inZone(point:THREE.Vector3,z:Zone,margin=0):boolean {const dx=point.x-z.origin[0],dz=point.z-z.origin[2],c=Math.cos(z.yaw),s=Math.sin(z.yaw),x=c*dx-s*dz,t=s*dx+c*dz;return Math.abs(x)<z.width/2+margin && t>-margin && t<z.depth+margin && point.y>z.origin[1]-.6 && point.y<z.origin[1]+z.height+.4;}
    getView(player:THREE.Vector3,camera:THREE.Vector3):{building:string;outside:boolean;showGround:boolean}|null{
        for(const v of this.venues){if(!v.interior)continue;const inside=v.meta.zones.some(z=>this.inZone(player,z))&&v.meta.zones.some(z=>this.inZone(camera,z));if(!inside)continue;
            const nearGlass=v.meta.portals.some(p=>Math.hypot(player.x-p.p[0],player.y-p.p[1],player.z-p.p[2])<14 || Math.hypot(camera.x-p.p[0],camera.y-p.p[1],camera.z-p.p[2])<14);
            return {building:v.meta.building??v.meta.key,outside:v.meta.outside??nearGlass,showGround:false};
        }return null;
    }
    private wheelAxis=new THREE.Vector3();
    /** Local filming: venues whose public interiors stay loaded (and never unload) while a take flies through them. */
    private pinned=new Set<string>();
    async filmPin(keys:string[]|null):Promise<void>{
        this.pinned=new Set(keys??[]);
        for(const v of this.venues){
            if(!this.pinned.has(v.meta.key))continue;
            if(!v.exteriorLoaded){const c=await this.collision(v.meta.exteriorCollision??v.meta.key+'-exterior-collision.json');if(this.disposed)return;v.exteriorBody=this.body(c,v.meta.name);v.exteriorLoaded=true;}
            if(!v.interior&&!v.pending){v.pending=true;try{await this.loadInterior(v);}finally{v.pending=false;}}
            v.lastNear=performance.now();
        }
    }
    private interiorLights:LightsNode|null=null;
    /** Local filming: open a venue's street-portal doors a moving camera is about to fly through (play opens them within
     * 3.5 m, too late for a camera at 10 m/s); they close again once the camera is 8 m past, as in play. */
    filmDoors(camera:{x:number;y:number;z:number},forward:{x:number;y:number;z:number},speed=0):void{
        for(const v of this.venues.values()){
            if(!v.interior)continue;
            for(let i=0;i<v.meta.portals.length;i++){
                const p=v.meta.portals[i]!,dx=p.p[0]-camera.x,dz=p.p[2]-camera.z,dist=Math.hypot(dx,dz);
                if(dist<Math.max(10,1.2*speed)&&Math.abs(camera.y-p.p[1])<4&&dx*forward.x+dz*forward.z>0&&!v.nearPortals.has(i)){v.nearPortals.add(i);v.doors[i*2]?.open();}
            }
        }
    }
    update(player:THREE.Vector3,outside:boolean,hideSource?:string,inHotel=true):void {
        if(this.disposed)return;const now=performance.now(),check=now>this.nextCheck;if(check)this.nextCheck=now+350;
        const playing=getGameStateManager().getCurrentState()===GameState.PLAYING;
        for(const v of this.venues){
            // Runs every frame for every venue: plain loops, no destructuring, mapped or spread arrays.
            const m=v.meta,bounds=m.bounds,d=Math.hypot(Math.max(bounds[0]-player.x,0,player.x-bounds[2]),Math.max(bounds[1]-player.z,0,player.z-bounds[3]));
            let portalDistance=Infinity,inside=false;
            for(const p of m.portals)portalDistance=Math.min(portalDistance,Math.hypot(player.x-p.p[0],player.y-p.p[1],player.z-p.p[2]));
            const access=m.accessPoints;if(access)for(let i=0;i<access.length;i+=3)portalDistance=Math.min(portalDistance,Math.hypot(player.x-access[i]!,player.y-access[i+1]!,player.z-access[i+2]!));
            for(const z of m.zones)if(this.inZone(player,z)){inside=true;break;}
            const verticalNear=m.levelY===undefined||Math.abs(player.y-m.levelY)<7;
            const publicVisible=inside||verticalNear&&portalDistance<42;
            v.exterior.visible=outside||publicVisible||!!m.structural&&d===0;if(v.interior)v.interior.visible=publicVisible;const leavesVisible=publicVisible||outside&&portalDistance<140;for(const o of v.leaves)o.visible=leavesVisible;
            // Inside this venue's own guest tower below its podium roof (a stair storey inside the podium, the LINQ's
            // level 3 inside its 17 m podium): the podium is hidden too, or its roof slices through the floors in view.
            // (The Cromwell's podium is 7.0 m, under its level-3 floor at 7.44: its rooms keep the podium in view.)
            // (a venue without `building` must not match an absent hide: undefined===undefined hid every one of its guest
            // towers in play, the Cromwell's and the LINQ's among them)
            const hide=hideSource!==undefined&&hideSource===m.building?'guest-':hideSource;
            const lowGuest=inHotel&&!!hide&&hide.startsWith('guest-')&&!!m.hotelSources?.includes(hide)&&player.y<v.podiumTop-.3;
            this.lods.get(v)?.hideSource(lowGuest?[hide!,m.key]:hide);
            if(check&&!this.lods.has(v))for(const n of v.details)n.visible=filmDetail.full||d<750;
            if(check&&!this.lods.has(v))v.exterior.traverse(o=>{if(o instanceof THREE.Mesh && hideSource && (o.userData.source===hideSource || String(o.userData.source).endsWith('/'+hideSource) || hideSource===m.building && String(o.userData.source).startsWith('guest-') || lowGuest && /podium/.test(String(o.userData.source))))o.visible=false;else if(o instanceof THREE.Mesh && !o.userData.detail)o.visible=true;});
            if(verticalNear&&portalDistance<90||inside||this.pinned.has(m.key))v.lastNear=now;
            if(check&&!v.pending&&now>v.retryAfter){
                const exteriorNeeded=d<90&&!v.exteriorLoaded,interiorNeeded=!m.exteriorOnly&&(inside||!this.passing&&portalDistance<(m.preloadDistance??38))&&!v.interior&&(m.levelY!==undefined?verticalNear:player.y<40);
                if(exteriorNeeded||interiorNeeded){v.pending=true;this.loading.enqueue('landmark:'+m.key,m.name,async()=>{try{
                    if(exteriorNeeded){const c=await this.collision(m.exteriorCollision??m.key+'-exterior-collision.json');if(!this.disposed){v.exteriorBody=this.body(c,m.name);v.exteriorLoaded=true;}}
                    if(interiorNeeded&&!this.disposed)await this.loadInterior(v);
                }catch(e){v.retryAfter=performance.now()+10000;console.error('[StripLandmarks]',m.key,e);}finally{v.pending=false;}},{background:!interiorNeeded&&d>=30});}
                else if(!inside&&(portalDistance>135||m.levelY!==undefined&&Math.abs(player.y-m.levelY)>12)&&now-v.lastNear>20000){this.unload(v);if(m.key!=='bellagioBlock'&&d>150&&v.exteriorBody?.isValid()){this.engine.physicsWorld!.removeRigidBody(v.exteriorBody);v.exteriorBody=null;v.exteriorLoaded=false;}}
            }
            if(playing)for(let i=0;i<m.portals.length;i++){const p=m.portals[i]!,dist=Math.hypot(player.x-p.p[0],player.z-p.p[2]);if(dist<3.5&&Math.abs(player.y-p.p[1])<2&&v.interior&&!v.nearPortals.has(i)){v.nearPortals.add(i);v.doors[i*2]?.open();}else if(dist>8&&v.nearPortals.delete(i))v.doors[i*2]?.close();}
            if(check)this.lights.offer('landmark:'+this.base+m.key,v.interior&&publicVisible?v.sites:[]);
        }
        if(check)this.lights.apply(player);
        if(playing&&outside&&this.rim){const dt=this.lastWheelTime?Math.min(.1,(now-this.lastWheelTime)/1000):0;
            // (filming: held at its authored pose, the one a camera path through its spokes was checked against)
            this.wheelAngle=filmDetail.full?0:this.wheelAngle+dt*Math.PI*2/1800;const w=this.venues.find(v=>v.meta.wheel)?.meta.wheel;if(w){this.rim.quaternion.setFromAxisAngle(this.wheelAxis.set(Math.sin(w.yaw),0,Math.cos(w.yaw)),this.wheelAngle);for(const {root,start} of this.cabins)root.position.copy(start).applyQuaternion(this.rim.quaternion).sub(start);}}this.lastWheelTime=now;
    }
    private setupWheel(v:Resident):void{
        const w=v.meta.wheel!,c=new THREE.Vector3().fromArray(w.center),rim=new THREE.Group();rim.name='High Roller rotating rim';rim.position.copy(c);v.exterior.add(rim);this.rim=rim;
        const nodes=[...v.exterior.children];for(const o of nodes){if(o.userData.source==='wheel-rim'){o.position.sub(c);rim.add(o);}}
        for(let i=0;i<w.cabins;i++){const root=new THREE.Group(),a=i*Math.PI*2/w.cabins,start=new THREE.Vector3(w.radius*Math.cos(a)*Math.cos(w.yaw),w.radius*Math.sin(a),-w.radius*Math.cos(a)*Math.sin(w.yaw));root.name='High Roller upright cabin '+i;v.exterior.add(root);for(const o of nodes)if(o.userData.source==='wheel-cabin-'+i)root.add(o);this.cabins.push({root,start});}
    }
    review(key:string,view='entrance'):{position:THREE.Vector3;yaw:number;pitch:number}|null {const p=key==='bellagioBlock'&&view==='foliage'?{eye:Float32Array.of(-87,2.21,584),target:Float32Array.of(-92,3.5,576)}:this.venues.find(v=>v.meta.key===key)?.meta.views[view];if(!p)return null;const eye=new THREE.Vector3().fromArray(p.eye),d=new THREE.Vector3().fromArray(p.target).sub(eye);return {position:eye.add(new THREE.Vector3(0,-1.7,0)),yaw:Math.atan2(-d.x,-d.z),pitch:-Math.atan2(d.y,Math.hypot(d.x,d.z))};}
    private unload(v:Resident):void{v.doors.forEach(d=>d.close());v.nearPortals.clear();v.releaseInterior?.();v.releaseInterior=null;if(v.body?.isValid())this.engine.physicsWorld!.removeRigidBody(v.body);v.body=null;if(v.interior)disposeSphereRoot(v.interior);v.interior=null;this.lights.offer('landmark:'+this.base+v.meta.key,[]);}
    get stats(){return {residentInteriors:this.venues.filter(v=>v.interior).map(v=>v.meta.key),physicsBodies:this.venues.reduce((n,v)=>n+Number(!!v.body)+Number(!!v.exteriorBody)+v.doors.length,0)};}
    dispose():void{this.disposed=true;for(const g of this.groves.reverse())g.dispose();this.groves=[];for(const f of this.foliage.reverse())f.dispose();this.foliage=[];for(const lod of this.lods.values())lod.dispose();this.lods.clear();for(const v of this.venues){this.unload(v);v.doors.forEach(d=>d.dispose());v.leaves.forEach(l=>l.children.forEach(c=>disposeSphereRoot(c)));v.releaseExterior();if(v.exteriorBody?.isValid())this.engine.physicsWorld!.removeRigidBody(v.exteriorBody);disposeSphereRoot(v.exterior);}this.venues=[];this.cabins=[];this.rim=null;}
}
