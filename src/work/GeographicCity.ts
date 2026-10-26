import {unmergedCasterShadows,unmergedCasterShadowsSteps} from './CityShadows.js';
import {runSliced} from './FrameBudget.js';
import {CollisionPack,loadCollisionPack} from './CollisionPack.js';
import {glbUrl} from './OptimizedGlb.js';
import {ResortBlocks} from './ResortBlocks.js';
import {StripLandmarks} from './StripLandmarks.js';
import {HighriseCity} from './HighriseCity.js';
import {SphereVenue} from './SphereVenue.js';
import {SiteLights} from './SiteLights.js';
import * as THREE from 'three';
import {WebGPURenderer} from 'three/webgpu';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {PhysicsBodyFactory} from 'engine/physics/world3d/PhysicsBodyFactory.js';
import {planCollider} from 'engine/meshlevel/MeshLevelColliders.js';
import type {EngineLike} from 'types/game.js';
import type {GroundSurfaceIndex} from './GroundSurfaceIndex.js';
import {GeographicPassages} from './GeographicPassages.js';
import {afterPaint,nextFrame,type StreamingWork} from './StreamingWork.js';
import {applyStreetMaterials} from './GeographicStreetMaterials.js';
import {CityLod} from './CityLod.js';
import {runtimeUrl} from './RuntimeAssets.js';
import {loadGltf,prefetch,takePrefetched} from './Prefetch.js';
import {appear} from './Appear.js';
import {compileSubtree} from './ShaderSharing.js';
/** A 160 m collision cell's map key. */
const cellKey=(x:number,z:number)=>(x+32768)*65536+z+32768;
/** Background silhouettes stay available across the skyline. Only collision
 * near the player is instantiated, with a larger eviction radius to avoid churn. */
export class GeographicCity {
    private root:THREE.Group|null=null;
    /** False while a background load is still building the city: update leaves the hidden root alone. */
    private shown=false;
    private lod:CityLod|null=null;
    private collision:CollisionPack|null=null;
    /** cell key -> mesh in `collision` */
    private byCell=new Map<number,number>();
    /** cell key -> its static body */
    private resident=new Map<number,ReturnType<typeof PhysicsBodyFactory.createStaticBody>['rigidBody']>();
    private releases:(()=>void)[]=[];
    private last=new THREE.Vector3(Infinity,0,Infinity);
    private credit:HTMLDivElement|null=null;
    private disposed=false;
    private passages:GeographicPassages;
    /** One fixed set of venue lights for the whole city; the venues borrow it (see SiteLights). */
    private siteLights:SiteLights;
    readonly sphere:SphereVenue;
    readonly highrises:HighriseCity;
    readonly landmarks:StripLandmarks;
    readonly resortBlocks:ResortBlocks;
    constructor(private engine:EngineLike,private surfaces:GroundSurfaceIndex,private loading:StreamingWork){this.siteLights=new SiteLights(engine.scene!);this.passages=new GeographicPassages(engine,surfaces,loading);this.sphere=new SphereVenue(engine,surfaces,loading,this.siteLights);this.highrises=new HighriseCity(engine,surfaces,loading);this.landmarks=new StripLandmarks(engine,surfaces,loading,this.siteLights);this.resortBlocks=new ResortBlocks(engine,surfaces,loading,this.siteLights);}
    /** `background` (2026-10-25): the city loads behind play. Every part loads at once, nearest `focus` first, each
     * built within the shared frame budget, compiled off the frame and dropped in when ready (FrameBudget.ts, Appear.ts). */
    async load(background=false,focus?:()=>THREE.Vector3):Promise<void>{
        const parts=Promise.all([this.passages.load(),this.sphere.load(),this.highrises.load(background),this.landmarks.load(background,focus),this.resortBlocks.load(background,focus)]);
        // the city's 74 MB come down while the landmarks above are parsed (Prefetch.ts)
        prefetch([await glbUrl('/build/geographic-strip/city.glb'),runtimeUrl('/build/geographic-strip/city-colliders.bin')]);
        if(!background)await parts;
        const collidersPath='/build/geographic-strip/city-colliders.bin',prefetched=takePrefetched(runtimeUrl(collidersPath));
        // 1,516 collision cells, 8.6 MB packed (CollisionPack.ts), decoded in the meshopt workers
        const [gltf,collision]=await Promise.all([loadGltf(new GLTFLoader(),await glbUrl('/build/geographic-strip/city.glb')),
            (prefetched??Promise.resolve(null)).then(bytes=>bytes?CollisionPack.decode(bytes):loadCollisionPack(collidersPath))]);
        this.collision=collision;
        for(let i=0;i<collision.count;i++)this.byCell.set(cellKey(collision.cellX![i]!,collision.cellZ![i]!),i);
        this.root=gltf.scene;this.root.name='OpenStreetMap / geographic Strip';
        this.releases.push(applyStreetMaterials(this.root,this.engine.renderer instanceof WebGPURenderer && this.engine.renderer.reversedDepthBuffer));
        // Buildings, tagged structures, utilities and bridges cast the sun's shadow: from their city batches' own
        // positions (CityLod, casterShadowMesh), or as proxies when no batch takes them (unmergedCasterShadows).
        this.root.traverse(o=>{if(o instanceof THREE.Mesh){
            o.castShadow=false;o.receiveShadow=true;
            const material=String(o.userData.osmMaterial??'');
            if(material.startsWith('building') || material.startsWith('tag/') || material==='utility' || ['bridge-deck','bridge-concrete','bridge-metal','bridge-roof'].includes(material))o.userData.cityCaster=true;
        }});

        if(background)this.root.visible=false;
        this.engine.scene!.add(this.root);
        this.releases.push(background?await this.surfaces.registerSliced(this.root):this.surfaces.register(this.root));
        this.lod=new CityLod(this.root,{key:m=>{
            const kind=String(m.userData.osmMaterial??''),cell=String(m.userData.osmCell??'');
            if(!cell)return null;
            const category=kind.startsWith('building')||kind.startsWith('tag/')||kind==='utility'?'buildings':'street';
            return cell+'/'+category;
        },near:240,far:2400,sliced:background,prepare:root=>compileSubtree(this.engine,root)});
        if(background){await this.lod.ready;if(this.disposed)return;await runSliced(unmergedCasterShadowsSteps(this.root));await compileSubtree(this.engine,this.root);}
        else unmergedCasterShadows(this.root);
        this.shown=true;appear(this.root);
        this.credit=document.createElement('div');
        for(const [text,url] of [['© OpenStreetMap contributors','https://www.openstreetmap.org/copyright'],['Clark County GISMO · pavement / sidewalks','https://maps.clarkcountynv.gov/arcgis/rest/services/GISMO/Pavement/MapServer'],['Liberty scan: gomeasure3d · CC BY 4.0 (adapted)','https://zenodo.org/records/10307962']]){
            const link=document.createElement('a');link.textContent=text!;link.href=url!;link.target='_blank';link.rel='noopener';link.style.color='inherit';this.credit.append(link,document.createElement('br'));
        }
        this.credit.style.cssText='position:absolute;right:16px;bottom:40px;color:#ddd;background:#17242bbb;padding:3px 6px;font:10px sans-serif;z-index:5';document.body.appendChild(this.credit);
        console.info(`[GeographicCity] ${collision.count} collision cells indexed; no far-city physics bodies`);
        console.info(`[GeographicCity] Full Strip skyline; ${this.lod.stats.blocks} city blocks use distance LOD`);
        if(background)await parts;
    }
    /** Driving past: skip the interior and concourse streaming that only a pedestrian needs. */
    setPassing(passing:boolean):void{this.landmarks.setPassing(passing);this.resortBlocks.setPassing(passing);this.sphere.setPassing(passing);this.passages.setPassing(passing);}
    /** inHotel: the hide comes from a guest tower the player is inside (its podium may hide too, see StripLandmarks). */
    update(player:THREE.Vector3,outside:boolean,hideSource?:string,inHotel=true):void{
        if(this.disposed)return;
        this.landmarks.update(player,outside,hideSource,inHotel);this.resortBlocks.update(player,outside,hideSource);this.sphere.update(player,outside);this.highrises.update(player,outside,hideSource);
        this.passages.update(player,outside);
        // (a city loading behind play keeps its root hidden until it is built and compiled)
        if(!this.root||!this.shown)return;
        this.root.visible=outside;
        // Camera remains on the detailed hotel renderer in enclosed interiors.
        if(!outside)return;
        if(player.distanceToSquared(this.last)<25*25)return;
        this.last.copy(player);
        const cx=Math.floor(player.x/160),cz=Math.floor(player.z/160),world=this.engine.physicsWorld!;
        const collision=this.collision;if(!collision)return;
        // keys of the 5 x 5 cells around the player that have collision but no body yet
        const missing=new Float64Array(25);let count=0;
        for(let x=cx-2;x<=cx+2;x++)for(let z=cz-2;z<=cz+2;z++){const key=cellKey(x,z);if(this.byCell.has(key)&&!this.resident.has(key))missing[count++]=key;}
        if(!count)return;
        // The ground under the player is already solid, so the neighbouring cells load quietly, ahead of need (a
        // vehicle at 20 m/s still has several seconds). Only a player standing on a cell with no collision yet is held.
        const own=cellKey(cx,cz),quiet=!this.byCell.has(own)||this.resident.has(own);
        this.loading.enqueue(`city-collision:${cx},${cz}`,'nearby roads and buildings',async()=>{
            let slice=performance.now();
            for(let k=0;k<count;k++){
                if(this.disposed)return;
                const key=missing[k]!;if(this.resident.has(key))continue;
                const mesh=this.byCell.get(key)!;
                const plan=planCollider(collision.trimesh(mesh,`OSM ${collision.cellX![mesh]},${collision.cellZ![mesh]}`),'terrain');
                const body=PhysicsBodyFactory.createStaticBody(world,plan.position,{shape:plan.shape,friction:.85,collisionGroup:plan.collisionGroup,collisionMask:plan.collisionMask},plan.quaternion).rigidBody;
                this.resident.set(key,body);
                // Each cell is atomic, but don't build the entire neighborhood
                // in one frame. The loading panel is painted before this job.
                if(performance.now()-slice>=6){await (quiet?nextFrame():afterPaint());slice=performance.now();}
            }
            if(this.disposed)return;
            for(const [key,body] of this.resident){const x=Math.floor(key/65536)-32768,z=key%65536-32768;if(Math.abs(x-cx)>3 || Math.abs(z-cz)>3){if(body.isValid())world.removeRigidBody(body);this.resident.delete(key);}}
        },{background:quiet});
    }
    get stats(){return {residentCells:this.resident.size,totalCells:this.collision?.count??0,lod:this.lod?.stats};}
    dispose():void{
        this.disposed=true;this.lod?.dispose();this.landmarks.dispose();this.resortBlocks.dispose();this.highrises.dispose();this.sphere.dispose();this.passages.dispose();this.siteLights.dispose();for(const release of this.releases)release();this.releases=[];
        const world=this.engine.physicsWorld;for(const body of this.resident.values())if(body.isValid())world?.removeRigidBody(body);this.resident.clear();
        this.root?.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose();}});this.root?.removeFromParent();this.credit?.remove();
    }
}
