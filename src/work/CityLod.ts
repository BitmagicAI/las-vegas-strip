import * as THREE from 'three';
import {isGeometryReleaseSuspended} from 'engine/resources/GeometryCpuRelease.js';
import {bakedLodFromBatch,batchMesh,coarseFromBatchSteps,coarseCityMaterial,concatCompact,disposeCityMaterial,facadeFromBatchSteps,fillBatchSteps,planCounts,planSampleHash,planStaticBatches,prefetchMapColors,retainCityMaterial,subsetFromPlan,type BatchPlan} from './CityBatches.js';
import {runSliced,runSync} from './FrameBudget.js';
import {releaseAfterUpload} from './CpuGeometryRelease.js';
import {bindCityLighting} from './CityLighting.js';
import {filmDetail} from './FilmDetail.js';
import {bakeCapture} from './CityBake.js';
import {cityLodBake,decodeLod,type BakedLod} from './CityBakeLoad.js';
import {casterShadowMesh} from './CityShadows.js';
/** How many batches took their LOD from the bake and how many were clustered in the browser (stale or missing bake). */
export const bakeUse={baked:0,clustered:0};
/** `?lodLevel=0|1` on localhost: every block at that level (comparing LODs). */
const forcedLevel=typeof location!=='undefined'&&['localhost','127.0.0.1'].includes(location.hostname)?Number(new URLSearchParams(location.search).get('lodLevel')??-1):-1;
const originalsSet=(list:{mesh:THREE.Mesh}[])=>new Set(list.map(o=>o.mesh));
/** Near detail on approach (2026-10-26, the owner: "Yes please do 1-4 now"): a block with a baked LOD loads as that LOD
 * alone, straight from its sources, and fills its full-detail batches only when the camera comes within its near range
 * (nearest first, within the frame budget); a block left far behind for EVICT_MS drops them again. Off while filming
 * (every take needs everything at once) and for blocks without a valid bake. */
let lazyNear=true;
export function setCityNearDetail(mode:'lazy'|'eager'):void{lazyNear=mode==='lazy';}
const EVICT_MS=20000,EVICT_FACTOR=1.6;

/** Placeholder geometry for merged source meshes (shared, empty, never drawn). */
const MERGED_SOURCE=new THREE.BufferGeometry();
export interface CityLodOptions {key:(mesh:THREE.Mesh)=>string|null; copyVisibility?:boolean;near?:number;far?:number;skyline?:boolean;coarsen?:boolean;facade?:boolean;
    /** Build the blocks over several frames within the shared loading budget (FrameBudget.ts); `ready` resolves when done. */
    sliced?:boolean;
    /** Compile a block's near level before it is shown (ShaderSharing.compileSubtree). */
    prepare?:(root:THREE.Object3D)=>Promise<unknown>}
/** Hotels include broad, low podiums: height alone switched Cromwell across the
 * street. Facade owners supply their footprint and keep a distant silhouette. */
export function lodDistances(height:number,near?:number,far?:number,skyline=false,footprint=0):{near:number;far:number}{
    // A whole resort's yard may span half a kilometre. Cap the footprint's
    // contribution so its tiny fittings do not stay at full detail for kilometres.
    return {near:near??(footprint>0?Math.max(550,Math.min(1800,height*6),Math.min(650,footprint*6)):Math.max(180,Math.min(900,height*5))),far:skyline||height>45||footprint>0?Infinity:far??Math.max(1200,height*55)};
}
export function lodLevel(distance:number,near:number,far:number,current:number):number {
    const n=near*(current===0?1.12:.88),f=far*(current===2?.88:1.12);return distance>f?2:distance>n?1:0;
}
interface Block {root:THREE.Group;high:THREE.Group;low:THREE.Group;box:THREE.Box3;near:number;far:number;level:number;key:string;facade:boolean;
    /** the batch materials this block holds a reference to (released on dispose) */materials:THREE.Material[];
    /** lazy blocks: the plans their near level is filled from, whether it is, and since when it has been far */
    plans:BatchPlan[]|null;nearBuilt:boolean;farSince:number;distance:number}
/** The bake's batch fits this plan: same vertex and index counts and the same sampled positions. */
function fits(plan:BatchPlan,baked:BakedLod|undefined):baked is BakedLod{
    if(!baked)return false;const c=planCounts(plan);
    return c.vertices===baked.vertices&&c.indices===baked.indices&&planSampleHash(plan)===baked.hash;
}
/** Caster triangles of a near level: the index ranges of the parts that cast. */
function nearCasters(plan:BatchPlan,index:ArrayLike<number>):Uint32Array{
    let n=0;for(let k=0;k<plan.parts.length;k++)if(plan.parts[k]!.caster)n+=plan.indexStarts[k+1]!-plan.indexStarts[k]!;
    const out=new Uint32Array(n);let o=0;
    for(let k=0;k<plan.parts.length;k++)if(plan.parts[k]!.caster)for(let i=plan.indexStarts[k]!;i<plan.indexStarts[k+1]!;i++)out[o++]=index[i]!;
    return out;
}
/** Caster triangles of baked LODs (several when a silhouette concatenates them): those whose first vertex came from a
 * casting part, numbered in the concatenated geometry. */
function lodCasters(lods:{plan:BatchPlan;geometry:THREE.BufferGeometry;parts:Uint32Array}[]):Uint32Array{
    let n=0;
    for(const {plan,geometry,parts} of lods){const index=geometry.index!.array;for(let t=0;t+2<index.length;t+=3)if(plan.parts[parts[index[t]!]!]!.caster)n+=3;}
    const out=new Uint32Array(n);let o=0,base=0;
    for(const {plan,geometry,parts} of lods){const index=geometry.index!.array;for(let t=0;t+2<index.length;t+=3)if(plan.parts[parts[index[t]!]!]!.caster){out[o++]=index[t]!+base;out[o++]=index[t+1]!+base;out[o++]=index[t+2]!+base;}base+=parts.length;}
    return out;
}
const shadowIndex=(list:Uint32Array,vertices:number)=>vertices>65535?list:Uint16Array.from(list);

/** The unit of work is a whole block or tower, never an individual window.
 * Selection is throttled and also runs from the active editor camera. */
export class CityLod {
    private blocks:Block[]=[];
    private originals:{mesh:THREE.Mesh;parent:THREE.Object3D;matrix:THREE.Matrix4;auto:boolean}[]=[];
    private last=0;
    private hiddenSource:string|undefined;
    private cameraPoint=new THREE.Vector3();
    private lastPoint=new THREE.Vector3(Infinity,Infinity,Infinity);
    private lastViewScale=1;
    private scene:THREE.Scene|null=null;
    private wanted=new Set<Block>();
    private building:Block|null=null;
    private disposed=false;
    private prepare:CityLodOptions['prepare'];
    /** Resolves when every block is built: at once, unless the options asked for `sliced`. */
    readonly ready:Promise<void>;
    constructor(private owner:THREE.Group,options:CityLodOptions){
        this.prepare=options.prepare;
        if(options.sliced)this.ready=prefetchMapColors(owner).then(()=>runSliced(this.build(owner,options)));
        else{runSync(this.build(owner,options));this.ready=Promise.resolve();}
    }
    private *build(owner:THREE.Group,options:CityLodOptions):Generator<void,void>{
        owner.updateWorldMatrix(true,true);
        const groups=new Map<string,THREE.Mesh[]>();
        owner.traverse(o=>{if(!(o instanceof THREE.Mesh)||o.layers.mask!==1||o instanceof THREE.SkinnedMesh||o instanceof THREE.InstancedMesh)return;const key=options.key(o);if(key===null)return;let g=groups.get(key);if(!g){g=[];groups.set(key,g);}g.push(o);});
        const lodBake=cityLodBake(),coarsen=options.coarsen!==false;
        for(const [key,meshes] of groups){
            const box=new THREE.Box3();for(const m of meshes)box.expandByObject(m);
            const size=box.getSize(new THREE.Vector3());if(box.isEmpty())continue;
            const root=new THREE.Group();root.name='City block / '+key;root.userData.cityLod=true;
            if(options.copyVisibility)Object.assign(root.userData,meshes[0]!.userData);
            // Preserve component ownership in the performance panel.
            if(key.startsWith('lakefront')){root.userData.perfOwner='Bellagio · lakefront';root.userData.perfKind='exterior';}
            const originals=meshes.map(mesh=>({mesh,parent:mesh.parent!,matrix:mesh.matrix.clone(),auto:mesh.matrixAutoUpdate}));
            const plans=planStaticBatches(meshes,'Full detail / '+key);
            if(!plans.length)continue;
            yield;
            const high=new THREE.Group();high.name='Full detail / '+key;
            const low=new THREE.Group();low.name='Silhouette / '+key;
            const facade=!!options.facade,retained=new THREE.Group();retained.name='Continuous surfaces / '+key;
            const materials:THREE.Material[]=plans.map(p=>p.material);
            // The baked LOD of each batch (CityBakeLoad.ts) when there is one for exactly this batch.
            const baked=plans.map((plan,k)=>lodBake&&coarsen?lodBake.batch(owner.name,key,k):undefined);
            const lazy=lazyNear&&!bakeCapture&&plans.every((plan,k)=>fits(plan,baked[k]));
            if(lazy){
                // The LOD alone, from the sources: only its vertices are transformed. The near level waits (select).
                bakeUse.baked+=plans.length;
                const lods=plans.map((plan,k)=>{const {subset,index}=decodeLod(baked[k]!);return {plan,...subsetFromPlan(plan,subset,index,!facade)};});
                if(facade){
                    // Same atlas, PBR rows and shader on both levels: texture mipmaps
                    // handle distance instead of replacing the palette wholesale.
                    for(const lod of lods){
                        const {plan,geometry,parts}=lod;
                        if(!geometry.index!.count){geometry.dispose();continue;}   // simplified away entirely (meshopt Prune)
                        retainCityMaterial(plan.material);materials.push(plan.material);
                        const mesh=new THREE.Mesh(geometry,plan.material);mesh.name=low.name+' / surface '+low.children.length;
                        mesh.receiveShadow=plan.receive;mesh.castShadow=plan.shadow;mesh.layers.mask=plan.mask;mesh.matrixAutoUpdate=false;bindCityLighting(mesh);low.add(mesh);
                        const casters=casterShadowMesh(geometry,shadowIndex(lodCasters([lod]),parts.length),'City shadow / LOD / '+key);if(casters)low.add(casters);
                        releaseAfterUpload(geometry);
                    }
                }else{
                    const geometry=lods.length===1?lods[0]!.geometry:concatCompact(lods.map(l=>l.geometry));
                    const casters=lodCasters(lods),base=geometry.getAttribute('position').count;
                    if(lods.length>1)lods.forEach(l=>l.geometry.dispose());
                    if(geometry.index!.count){
                        const material=coarseCityMaterial(plans[0]!.source);materials.push(material);
                        const mesh=new THREE.Mesh(geometry,material);mesh.receiveShadow=true;mesh.matrixAutoUpdate=false;bindCityLighting(mesh);low.add(mesh);
                        const shadow=casterShadowMesh(geometry,shadowIndex(casters,base),'City shadow / LOD / '+key);if(shadow)low.add(shadow);
                        releaseAfterUpload(geometry);
                    }else geometry.dispose();
                }
            }else{
                // Everything now: the near level, its casters (always drawn, as the merged casters were) and the LOD
                // from the bake when it fits, clustered otherwise.
                const batches:THREE.Mesh[]=[];
                for(const plan of plans){
                    const geometry=yield* fillBatchSteps(plan),mesh=batchMesh(plan,geometry);high.add(mesh);batches.push(mesh);
                    const casters=casterShadowMesh(geometry,shadowIndex(nearCasters(plan,geometry.index!.array),planCounts(plan).vertices),'City shadow / '+key);if(casters)root.add(casters);
                }
                if(facade){
                    for(const [k,o] of batches.entries()){
                        const fromBake=coarsen?bakedLodFromBatch(o.geometry,baked[k],false):null;if(fromBake)bakeUse.baked++;else bakeUse.clustered++;
                        const geometry=fromBake??(yield* facadeFromBatchSteps(o.geometry,coarsen?.7:null)),material=o.material as THREE.MeshStandardMaterial;
                        retainCityMaterial(material);materials.push(material);const mesh=new THREE.Mesh(geometry,material);mesh.name=low.name+' / surface '+low.children.length;
                        mesh.receiveShadow=o.receiveShadow;mesh.castShadow=o.castShadow;mesh.layers.mask=o.layers.mask;mesh.matrixAutoUpdate=false;bindCityLighting(mesh);low.add(mesh);releaseAfterUpload(geometry);
                    }
                }else{
                    const coarse:THREE.BufferGeometry[]=[];
                    for(const [k,o] of batches.entries()){
                        const fromBake=coarsen?bakedLodFromBatch(o.geometry,baked[k],true):null;if(fromBake)bakeUse.baked++;else bakeUse.clustered++;
                        coarse.push(fromBake??(yield* coarseFromBatchSteps(o.geometry,coarsen?Math.max(.7,Math.min(3,size.y/70)):null)));
                    }
                    if(coarse.length){const geometry=coarse.length===1?coarse[0]!:concatCompact(coarse);if(coarse.length>1)coarse.forEach(g=>g.dispose());const material=coarseCityMaterial(plans[0]!.source);materials.push(material);const mesh=new THREE.Mesh(geometry,material);mesh.receiveShadow=true;mesh.matrixAutoUpdate=false;bindCityLighting(mesh);low.add(mesh);releaseAfterUpload(geometry);}
                }
                for(const o of batches)releaseAfterUpload(o.geometry);
            }
            // Unmergeable architecture keeps its own pipeline across facade
            // levels; other blocks and water retain their existing near range.
            for(const original of originals){
                const mesh=original.mesh;
                mesh.userData.groundVisibilityRoot=root;
                if(mesh.parent){
                    mesh.updateWorldMatrix(true,false);mesh.matrix.copy(mesh.matrixWorld);mesh.matrixAutoUpdate=false;
                    // Preserve the existing range-culling of water. Keeping a
                    // remote canal mirror active adds an entire city render even
                    // when that tiny surface is hidden behind another building.
                    const water=Array.isArray(mesh.material)?mesh.material.some(m=>m.userData.realisticWater):mesh.material.userData.realisticWater;
                    (facade&&!water?retained:high).add(mesh);this.originals.push(original);
                }
                // A merged source is not drawn again. Filled now, its CPU geometry can go (the batch holds the drawable
                // copy, GroundSurfaceIndex its own walkable triangles); a lazy block keeps it to fill its near level.
                // It is not restored on dispose.
                else if(!lazy)mesh.geometry=MERGED_SOURCE;
            }
            // Source positions are world-space. Transform the container once.
            root.matrix.copy(owner.matrixWorld).invert();root.matrixAutoUpdate=false;root.add(high,low,retained);owner.add(root);
            const d=lodDistances(size.y,options.near,options.far,options.skyline,facade?Math.max(size.x,size.z):0);low.visible=false;
            this.blocks.push({root,high,low,box,...d,level:0,key,facade,materials,plans:lazy?plans:null,nearBuilt:!lazy,farSince:0,distance:0});
            if(bakeCapture){const children=(g:THREE.Group)=>g.children.filter((o):o is THREE.Mesh=>o instanceof THREE.Mesh);
                const spacing=!coarsen?null:facade?.7:Math.max(.7,Math.min(3,size.y/70));
                bakeCapture.block(owner,{key,box,near:d.near,far:d.far,facade,spacing,userData:options.copyVisibility?{...meshes[0]!.userData}:{},high:children(high).filter(m=>!originalsSet(originals).has(m)),low:children(low),
                    retained:originals.filter(o=>o.mesh.parent).map(o=>o.mesh),merged:originals.filter(o=>!o.mesh.parent).map(o=>o.mesh)});}
            yield;
        }
        // A scene hook is needed because editor navigation bypasses Game.update.
        let parent:THREE.Object3D|null=owner;while(parent&&!(parent instanceof THREE.Scene))parent=parent.parent;
        if(parent instanceof THREE.Scene){this.scene=parent;register(this.scene,this);}
    }
    select(camera:THREE.Camera,now=performance.now()):void {
        if(now-this.last<180||isGeometryReleaseSuspended())return;this.last=now;
        camera.getWorldPosition(this.cameraPoint);const moved=this.cameraPoint.distanceToSquared(this.lastPoint)>=1;if(moved)this.lastPoint.copy(this.cameraPoint);
        // Zoomed editor views need the same detail as moving closer. A 70-degree
        // vertical FOV is the baseline; wide views never shorten the safe range.
        const viewScale=(camera as THREE.PerspectiveCamera).isPerspectiveCamera?Math.max(1,camera.projectionMatrix.elements[5]!/1.428148):1;
        const viewChanged=Math.abs(viewScale-this.lastViewScale)>.001;this.lastViewScale=viewScale;
        // Even when the camera has not moved, re-assert what each level shows: the engine's
        // start-up warm-up restores visibility it recorded before the first selection.
        for(const b of this.blocks){
            if(moved||viewChanged)b.distance=b.box.distanceToPoint(this.cameraPoint);
            if(filmDetail.full)b.level=0;else if(forcedLevel>=0)b.level=forcedLevel;else if(moved||viewChanged)b.level=lodLevel(b.distance,b.near*(b.facade?viewScale:1),b.far,b.level);
            let high=b.level===0,low=b.level===1;
            if(b.plans){
                // a lazy block shows its LOD until its near level is filled, and drops that level when long out of range
                if(high&&!b.nearBuilt){high=false;low=true;this.wanted.add(b);}
                if(b.nearBuilt&&b.level!==0&&b.distance>b.near*EVICT_FACTOR){if(!b.farSince)b.farSince=now;else if(now-b.farSince>EVICT_MS)this.evict(b);}
                else b.farSince=0;
            }
            if(b.high.visible!==high)b.high.visible=high;if(b.low.visible!==low)b.low.visible=low;
        }
        this.pump();
    }
    /** Fill the nearest wanted block's near level next (one at a time, within the frame budget). */
    private pump():void{
        if(this.building||!this.wanted.size||this.disposed)return;
        let next:Block|null=null;for(const b of this.wanted)if(b.nearBuilt||b.level!==0)this.wanted.delete(b);else if(!next||b.distance<next.distance)next=b;
        if(!next)return;
        this.wanted.delete(next);this.building=next;const b=next,group=new THREE.Group();
        runSliced(this.fillNear(b,group)).then(()=>this.prepare?.(group)).then(()=>{
            if(this.disposed||!b.plans){disposeNear(group);return;}
            for(const o of [...group.children])b.high.add(o);
            b.nearBuilt=true;b.farSince=0;
        }).catch(error=>console.error('[CityLod] near detail failed',b.key,error)).finally(()=>{this.building=null;this.last=0;});
    }
    private *fillNear(b:Block,group:THREE.Group):Generator<void,void>{
        for(const plan of b.plans!){
            const geometry=yield* fillBatchSteps(plan),mesh=batchMesh(plan,geometry);mesh.userData.cityNear=true;group.add(mesh);
            const casters=casterShadowMesh(geometry,shadowIndex(nearCasters(plan,geometry.index!.array),planCounts(plan).vertices),'City shadow / '+b.key);
            if(casters){casters.userData.cityNear=true;group.add(casters);}
            releaseAfterUpload(geometry);
        }
    }
    /** Drop a lazy block's near level (its GPU buffers); the plans keep the sources to fill it again. */
    private evict(b:Block):void{
        const filled=b.high.children.filter(o=>o instanceof THREE.Mesh&&o.userData.cityNear===true);
        for(const o of filled){o.removeFromParent();(o as THREE.Mesh).geometry.dispose();}
        b.nearBuilt=false;b.farSince=0;
    }
    /** Hide the blocks of one source (or several: a guest tower and its venue's podium, see StripLandmarks). */
    hideSource(sources?:string|readonly string[]):void {
        const list=sources===undefined?[]:typeof sources==='string'?[sources]:sources,key=list.join('|');
        if(key===this.hiddenSource)return;this.hiddenSource=key;
        for(const b of this.blocks)b.root.visible=!list.some(source=>b.key===source||b.key.endsWith('/'+source)||source==='guest-'&&b.key.startsWith(source));
    }
    get stats(){return {blocks:this.blocks.length,full:this.blocks.filter(b=>b.level===0).length,coarse:this.blocks.filter(b=>b.level===1).length,culled:this.blocks.filter(b=>b.level===2).length,
        nearFilled:this.blocks.filter(b=>b.nearBuilt).length,lazy:this.blocks.filter(b=>b.plans).length};}
    dispose():void {
        this.disposed=true;
        if(this.scene)unregister(this.scene,this);
        // Unmerged meshes go back to their parents; merged sources were released at build time (or are dropped with the plans).
        const sourceMeshes=new Set(this.originals.map(o=>o.mesh));
        const gs=new Set<THREE.BufferGeometry>();
        for(const b of this.blocks){b.root.traverse(o=>{if(o instanceof THREE.Mesh&&!sourceMeshes.has(o))gs.add(o.geometry);});b.root.removeFromParent();b.materials.forEach(disposeCityMaterial);b.plans=null;}
        gs.forEach(g=>g.dispose());for(const {mesh,parent,matrix,auto} of this.originals){delete mesh.userData.groundVisibilityRoot;mesh.matrix.copy(matrix);mesh.matrixAutoUpdate=auto;parent.add(mesh);}this.blocks=[];this.originals=[];
    }
}
function disposeNear(group:THREE.Group):void{group.traverse(o=>{if(o instanceof THREE.Mesh)o.geometry.dispose();});}

const registries=new WeakMap<THREE.Scene,{items:Set<CityLod>;previous:THREE.Scene['onBeforeRender'];hook:THREE.Scene['onBeforeRender']}>();
function register(scene:THREE.Scene,lod:CityLod):void {
    let r=registries.get(scene);if(!r){const previous=scene.onBeforeRender,items=new Set<CityLod>();const hook:THREE.Scene['onBeforeRender']=(...args)=>{
        previous.apply(scene,args);
        // WebGPU recursively renders this same scene from each shadow camera
        // with an override material. Those passes must never choose the city's
        // visible LOD (or a long frame can switch to the sun's position).
        if(scene.overrideMaterial)return;
        for(const item of items)item.select(args[2]);
    };r={items,previous,hook};registries.set(scene,r);scene.onBeforeRender=hook;}r.items.add(lod);
}
function unregister(scene:THREE.Scene,lod:CityLod):void {const r=registries.get(scene);if(!r)return;r.items.delete(lod);if(!r.items.size){if(scene.onBeforeRender===r.hook)scene.onBeforeRender=r.previous;registries.delete(scene);}}

export function cityLodStats(scene:THREE.Scene){const result={blocks:0,full:0,coarse:0,culled:0,nearFilled:0,lazy:0};for(const lod of registries.get(scene)?.items??[]){const s=lod.stats;result.blocks+=s.blocks;result.full+=s.full;result.coarse+=s.coarse;result.culled+=s.culled;result.nearFilled+=s.nearFilled;result.lazy+=s.lazy;}return result;}
