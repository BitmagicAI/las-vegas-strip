import type {StreamingWork} from '../StreamingWork.js';
import {glbUrl} from '../OptimizedGlb.js';
import type { GroundSurfaceIndex } from '../GroundSurfaceIndex.js';
import * as THREE from 'three';
import type {LightsNode} from 'three/webgpu';
import {interiorLightsNode,lightInterior} from '../InteriorLighting.js';
import {interiorKey} from '../InteriorKeyLight.js';
import {colliderVertices} from './HotelGeometry.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {PhysicsBodyFactory} from 'engine/physics/PhysicsBodyFactory.js';
import {planCollider} from 'engine/meshlevel/MeshLevelColliders.js';
import {applyMaterialConventions} from 'engine/meshlevel/MeshLevel.js';
import type {MeshLevelData,MeshLevelCollider} from 'engine/meshlevel/MeshLevelSchema.js';
import type {EngineLike} from 'types/game.js';
import type {HotelSet} from './HotelLayout.js';
import recipes from './towers.json';
export type ModuleName=`${HotelSet}-${'stair'|'corridor'|'room'|'cap'|'entry'|'closure'|'door'|'corridor-end'}`|`${string}-lobby`;
const REVISION='door-panels-6';
const CORE=['stair','cap','entry','closure'] as const;
const GUEST=['corridor','room','door'] as const;
export interface LightSite {position:THREE.Vector3;color:string;intensity:number;distance:number}
export interface ModuleInstance {root:THREE.Group;lights:LightSite[];dispose:()=>void;colliders:number}

/** Shared mesh resources are disposed only with the library, never with a clone. */
export class HotelTemplates {
    private interiorLights:LightsNode|null=null;
    /** Interior modules (all but the street-facing entries) use sun, sky, ambient and the hotel's own
     * light pool only (see InteriorLighting). Called once the pool exists; applies to loaded and future modules. */
    setInteriorLights(pool:readonly THREE.Light[]):void {
        this.interiorLights=interiorLightsNode(this.engine.scene!,pool);
        for(const [name,base] of this.bases)this.lightModule(name,base);
    }
    private lightModule(name:ModuleName,base:THREE.Group):void {if(this.interiorLights&&!name.endsWith('-entry'))lightInterior(base,this.interiorLights);}
    private bases=new Map<ModuleName,THREE.Group>();
    private metadata=new Map<ModuleName,MeshLevelData>();
    private pending=new Map<ModuleName,Promise<void>>();
    private references=new Map<ModuleName,number>();
    private recent:HotelSet[]=[];
    private releasedLazy=new Set<ModuleName>();
    private disposed=false;
    constructor(private engine:EngineLike,private groundSurfaces:GroundSurfaceIndex,private loading:StreamingWork){}
    private async fetchModule(name:ModuleName):Promise<void>{
        this.releasedLazy.delete(name);
        if(this.bases.has(name))return;
        const existing=this.pending.get(name);if(existing)return existing;
        const request=(async()=>{
            const url=`/build/hotels/${name}`;
            const [gltf,response]=await Promise.all([
                new GLTFLoader().loadAsync(await glbUrl(`${url}.glb?v=${REVISION}`)),
                fetch(`${url}.mesh-level.json?v=${REVISION}`)
            ]);
            if(!response.ok){this.releaseResources([gltf.scene]);throw new Error(`Cannot load hotel metadata ${name}: ${response.status}`);}
            const meta=await response.json() as MeshLevelData;
            if(this.disposed){this.releaseResources([gltf.scene]);return;}
            applyMaterialConventions(gltf.scene);this.lightModule(name,gltf.scene);this.bases.set(name,gltf.scene);this.metadata.set(name,meta);
        })();
        this.pending.set(name,request);
        try{await request;}finally{this.pending.delete(name);}
    }
    async load():Promise<void>{
        // Only lightweight entry / stair shells at boot. Detailed guest sets are
        // fetched while the painted loading indicator holds player simulation.
        const sets=[...new Set(recipes.map(t=>t.set as HotelSet))];
        for(const set of sets)await Promise.all(CORE.map(kind=>this.fetchModule(`${set}-${kind}`)));
    }
    async ensureCore(set:HotelSet):Promise<void>{await Promise.all(CORE.map(kind=>this.fetchModule(`${set}-${kind}`)));}
    async ensureLobby(id:string):Promise<void>{await this.fetchModule(`${id}-lobby`);}
    releaseLazy(set:HotelSet,id:string):void{
        const names=[...this.bases.keys()].filter(n=>n===`${id}-lobby` || CORE.some(k=>n===`${set}-${k}`));
        for(const n of names)this.releasedLazy.add(n);
        this.trim();
    }
    async ensureGuest(set:HotelSet):Promise<void>{
        this.recent=this.recent.filter(s=>s!==set);this.recent.push(set);
        const names:ModuleName[]=GUEST.filter(k=>set!=='veer'||k!=='door').map((k):ModuleName=>`${set}-${k}`);
        if(set==='bellagio')names.push('bellagio-corridor-end');
        await Promise.all(names.map(n=>this.fetchModule(n)));
        this.trim();
    }
    /** At most two unused detailed property sets; live floors pin their set. */
    trim():void{
        for(const n of this.releasedLazy){
            if((this.references.get(n)??0)>0 || this.pending.has(n))continue;
            const base=this.bases.get(n);if(base)this.releaseResources([base]);
            this.bases.delete(n);this.metadata.delete(n);this.references.delete(n);this.releasedLazy.delete(n);
        }
        for(const set of this.recent.slice(0,-2)){
            const names=[...this.bases.keys()].filter(n=>n.startsWith(set+'-')&&!CORE.some(k=>n===`${set}-${k}`));
            if(names.some(n=>(this.references.get(n)??0)>0)||[...this.pending.keys()].some(n=>n.startsWith(set+'-')))continue;
            this.releaseResources(names.map(n=>this.bases.get(n)!));
            for(const n of names){this.bases.delete(n);this.metadata.delete(n);this.references.delete(n);}
            this.recent=this.recent.filter(s=>s!==set);
        }
    }
    doorVisual(set:HotelSet):THREE.Group{return this.bases.get(`${set}-door`)!.clone(true);}
    instantiate(name:ModuleName,matrix:THREE.Matrix4,staticGround=true):ModuleInstance {
        const base=this.bases.get(name);if(!base)throw new Error(`Hotel template not prepared: ${name}`);
        this.references.set(name,(this.references.get(name)??0)+1);
        const root=base.clone(true);root.matrixAutoUpdate=false;root.matrix.copy(matrix);
        root.name='Streamed '+name;root.userData.perfOwner='Guest · '+name;root.userData.perfKind=name.endsWith('-entry')?'exterior':'interior';this.engine.scene!.add(root);
        // (each clone casts for the interiors' overhead key light while it is on; the template itself is never in the scene)
        if(!name.endsWith('-entry'))interiorKey.register(root);
        this.loading.revealUntilReady(root);
        const releaseGround=staticGround?this.groundSurfaces.register(root):()=>{};
        const meta=this.metadata.get(name)!,world=this.engine.physicsWorld!;
        const bodies=meta.colliders.map(c=>{
            const vertices=colliderVertices(c),out:number[]=[],p=new THREE.Vector3();
            for(let i=0;i<vertices.length;i+=3){p.set(vertices[i]!,vertices[i+1]!,vertices[i+2]!).applyMatrix4(matrix);out.push(p.x,p.y,p.z);}
            const record:MeshLevelCollider=c.shape==='trimesh'?{name:c.name,shape:'trimesh',vertices:out,indices:c.indices}:{name:c.name,shape:'convexHull',vertices:out};
            const plan=planCollider(record,'terrain');
            return PhysicsBodyFactory.createStaticBody(world,plan.position,{shape:plan.shape,friction:.85,collisionGroup:plan.collisionGroup,collisionMask:plan.collisionMask},plan.quaternion).rigidBody;
        });
        const lights:LightSite[]=meta.lights.filter(l=>l.type==='point').map(l=>({position:new THREE.Vector3(...l.position).applyMatrix4(matrix),color:l.color,intensity:l.intensity,distance:l.type==='point'?l.distance:10}));
        return {root,lights,colliders:bodies.length,dispose:()=>{this.references.set(name,(this.references.get(name)??1)-1);releaseGround();root.removeFromParent();for(const b of bodies)if(b.isValid())world.removeRigidBody(b);}};
    }
    private releaseResources(roots:THREE.Group[]):void {
        const geometries=new Set<THREE.BufferGeometry>(),materials=new Set<THREE.Material>(),textures=new Set<THREE.Texture>();
        for(const root of roots)root.traverse(o=>{if(o instanceof THREE.Mesh){geometries.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:[o.material])materials.add(m);}});
        for(const m of materials)for(const value of Object.values(m))if(value instanceof THREE.Texture)textures.add(value);
        for(const g of geometries)g.dispose();for(const m of materials)m.dispose();for(const t of textures)t.dispose();
    }
    dispose():void {this.disposed=true;this.releaseResources([...this.bases.values()]);this.bases.clear();this.metadata.clear();this.references.clear();}
}
