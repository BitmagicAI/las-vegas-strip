import {batchCityShadows} from './CityShadows.js';
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
interface CollisionCell {id:string;center:[number,number];vertices:number[];indices:number[]}
/** Background silhouettes stay available across the skyline. Only collision
 * near the player is instantiated, with a larger eviction radius to avoid churn. */
export class GeographicCity {
    private root:THREE.Group|null=null;
    private lod:CityLod|null=null;
    private cells:CollisionCell[]=[];
    private byCell=new Map<string,CollisionCell>();
    private resident=new Map<string,ReturnType<typeof PhysicsBodyFactory.createStaticBody>['rigidBody']>();
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
    async load():Promise<void>{
        const version=await fetch(runtimeUrl('/build/geographic-strip/city-version.json')).then(r=>r.json()) as {revision:string};
        await Promise.all([this.passages.load(version.revision),this.sphere.load(),this.highrises.load(),this.landmarks.load(),this.resortBlocks.load()]);
        const [gltf,response]=await Promise.all([new GLTFLoader().loadAsync(await glbUrl(`/build/geographic-strip/city.glb?v=${version.revision}`)),fetch(runtimeUrl(`/build/geographic-strip/city-colliders.json?v=${version.revision}`))]);
        if(!response.ok)throw new Error('Mapped city collision data unavailable');
        this.cells=await response.json() as CollisionCell[];
        for(const cell of this.cells)this.byCell.set(cell.id,cell);
        this.root=gltf.scene;this.root.name='OpenStreetMap / geographic Strip';
        this.releases.push(applyStreetMaterials(this.root,this.engine.renderer instanceof WebGPURenderer && this.engine.renderer.reversedDepthBuffer));
        const casters:THREE.Mesh[]=[];
        this.root.traverse(o=>{if(o instanceof THREE.Mesh){
            o.castShadow=false;o.receiveShadow=true;
            const material=String(o.userData.osmMaterial??'');
            if(material.startsWith('building') || material.startsWith('tag/') || material==='utility' || ['bridge-deck','bridge-concrete','bridge-metal','bridge-roof'].includes(material)){
                const proxy=new THREE.Mesh(o.geometry,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
                proxy.name='OSM shadow silhouette / '+o.name;proxy.layers.set(30);proxy.castShadow=true;proxy.matrix.copy(o.matrix);proxy.matrixAutoUpdate=false;casters.push(proxy);
            }
        }});
        // Share the coarse source mesh: tall distant casters remain available
        // to the focused sun without putting full-detail architecture in its pass.

        this.engine.scene!.add(this.root);
        this.releases.push(this.surfaces.register(this.root));
        for(const caster of casters)this.root.add(caster);batchCityShadows(this.root);
        this.lod=new CityLod(this.root,{key:m=>{
            const kind=String(m.userData.osmMaterial??''),cell=String(m.userData.osmCell??'');
            if(!cell)return null;
            const category=kind.startsWith('building')||kind.startsWith('tag/')||kind==='utility'?'buildings':'street';
            return cell+'/'+category;
        },near:240,far:2400});
        this.credit=document.createElement('div');
        for(const [text,url] of [['© OpenStreetMap contributors','https://www.openstreetmap.org/copyright'],['Clark County GISMO · pavement / sidewalks','https://maps.clarkcountynv.gov/arcgis/rest/services/GISMO/Pavement/MapServer'],['Liberty scan: gomeasure3d · CC BY 4.0 (adapted)','https://zenodo.org/records/10307962']]){
            const link=document.createElement('a');link.textContent=text!;link.href=url!;link.target='_blank';link.rel='noopener';link.style.color='inherit';this.credit.append(link,document.createElement('br'));
        }
        this.credit.style.cssText='position:absolute;right:16px;bottom:40px;color:#ddd;background:#17242bbb;padding:3px 6px;font:10px sans-serif;z-index:5';document.body.appendChild(this.credit);
        console.info(`[GeographicCity] ${this.cells.length} collision cells indexed; no far-city physics bodies`);
        console.info(`[GeographicCity] Full Strip skyline; ${this.lod.stats.blocks} city blocks use distance LOD`);
    }
    /** Driving past: skip the interior and concourse streaming that only a pedestrian needs. */
    setPassing(passing:boolean):void{this.landmarks.setPassing(passing);this.resortBlocks.setPassing(passing);this.sphere.setPassing(passing);this.passages.setPassing(passing);}
    /** inHotel: the hide comes from a guest tower the player is inside (its podium may hide too, see StripLandmarks). */
    update(player:THREE.Vector3,outside:boolean,hideSource?:string,inHotel=true):void{
        if(!this.root || this.disposed)return;
        this.landmarks.update(player,outside,hideSource,inHotel);this.resortBlocks.update(player,outside,hideSource);this.sphere.update(player,outside);this.highrises.update(player,outside,hideSource);
        this.root.visible=outside;
        this.passages.update(player,outside);
        // Camera remains on the detailed hotel renderer in enclosed interiors.
        if(!outside)return;
        if(player.distanceToSquared(this.last)<25*25)return;
        this.last.copy(player);
        const cx=Math.floor(player.x/160),cz=Math.floor(player.z/160),world=this.engine.physicsWorld!;
        const missing:CollisionCell[]=[];
        for(let x=cx-2;x<=cx+2;x++)for(let z=cz-2;z<=cz+2;z++){
            const cell=this.byCell.get(`${x},${z}`);if(cell&&!this.resident.has(cell.id))missing.push(cell);
        }
        if(!missing.length)return;
        // The ground under the player is already solid, so the neighbouring cells load quietly, ahead of need (a
        // vehicle at 20 m/s still has several seconds). Only a player standing on a cell with no collision yet is held.
        const own=`${cx},${cz}`,quiet=!this.byCell.has(own)||this.resident.has(own);
        this.loading.enqueue(`city-collision:${cx},${cz}`,'nearby roads and buildings',async()=>{
            let slice=performance.now();
            for(const cell of missing){
                if(this.disposed)return;
                if(this.resident.has(cell.id))continue;
                const plan=planCollider({name:'OSM '+cell.id,shape:'trimesh',vertices:cell.vertices,indices:cell.indices},'terrain');
                const body=PhysicsBodyFactory.createStaticBody(world,plan.position,{shape:plan.shape,friction:.85,collisionGroup:plan.collisionGroup,collisionMask:plan.collisionMask},plan.quaternion).rigidBody;
                this.resident.set(cell.id,body);
                // Each cell is atomic, but don't build the entire neighborhood
                // in one frame. The loading panel is painted before this job.
                if(performance.now()-slice>=6){await (quiet?nextFrame():afterPaint());slice=performance.now();}
            }
            if(this.disposed)return;
            for(const [id,body] of this.resident){const [x,z]=id.split(',').map(Number);if(Math.abs(x!-cx)>3 || Math.abs(z!-cz)>3){if(body.isValid())world.removeRigidBody(body);this.resident.delete(id);}}
        },{background:quiet});
    }
    get stats(){return {residentCells:this.resident.size,totalCells:this.cells.length,lod:this.lod?.stats};}
    dispose():void{
        this.disposed=true;this.lod?.dispose();this.landmarks.dispose();this.resortBlocks.dispose();this.highrises.dispose();this.sphere.dispose();this.passages.dispose();this.siteLights.dispose();for(const release of this.releases)release();this.releases=[];
        const world=this.engine.physicsWorld;for(const body of this.resident.values())if(body.isValid())world?.removeRigidBody(body);this.resident.clear();
        this.root?.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose();}});this.root?.removeFromParent();this.credit?.remove();
    }
}
