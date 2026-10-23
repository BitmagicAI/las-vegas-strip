import * as THREE from 'three';
import {isGeometryReleaseSuspended} from 'engine/GeometryCpuRelease.js';
import {batchStaticMeshes,coarseFromBatch,coarseCityMaterial,concatCompact,disposeCityMaterial,facadeFromBatch,retainCityMaterial} from './CityBatches.js';
import {releaseAfterUpload} from './CpuGeometryRelease.js';
import {bindCityLighting} from './CityLighting.js';
import {filmDetail} from './FilmDetail.js';

/** Placeholder geometry for merged source meshes (shared, empty, never drawn). */
const MERGED_SOURCE=new THREE.BufferGeometry();
export interface CityLodOptions {key:(mesh:THREE.Mesh)=>string|null; copyVisibility?:boolean;near?:number;far?:number;skyline?:boolean;coarsen?:boolean;facade?:boolean}
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
interface Block {root:THREE.Group;high:THREE.Group;low:THREE.Group;box:THREE.Box3;near:number;far:number;level:number;key:string;facade:boolean}
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
    constructor(private owner:THREE.Group,options:CityLodOptions){
        owner.updateWorldMatrix(true,true);
        const groups=new Map<string,THREE.Mesh[]>();
        owner.traverse(o=>{if(!(o instanceof THREE.Mesh)||o.layers.mask!==1||o instanceof THREE.SkinnedMesh||o instanceof THREE.InstancedMesh)return;const key=options.key(o);if(key===null)return;let g=groups.get(key);if(!g){g=[];groups.set(key,g);}g.push(o);});
        for(const [key,meshes] of groups){
            const box=new THREE.Box3();for(const m of meshes)box.expandByObject(m);
            const size=box.getSize(new THREE.Vector3());if(box.isEmpty())continue;
            const root=new THREE.Group();root.name='City block / '+key;root.userData.cityLod=true;
            if(options.copyVisibility)Object.assign(root.userData,meshes[0]!.userData);
            // Preserve component ownership in the performance panel.
            if(key.startsWith('lakefront')){root.userData.perfOwner='Bellagio · lakefront';root.userData.perfKind='exterior';}
            const originals=meshes.map(mesh=>({mesh,parent:mesh.parent!,matrix:mesh.matrix.clone(),auto:mesh.matrixAutoUpdate}));
            const high=batchStaticMeshes(meshes,'Full detail / '+key);
            if(!high.children.length)continue;
            const low=new THREE.Group();low.name='Silhouette / '+key;
            const facade=!!options.facade,retained=new THREE.Group();retained.name='Continuous surfaces / '+key;
            // Architectural LODs preserve surface boundaries; the background
            // city uses the cheaper texture-average envelope below.
            if(facade){
                // Same atlas, PBR rows and shader on both levels: texture mipmaps
                // handle distance instead of replacing the palette wholesale.
                for(const o of high.children)if(o instanceof THREE.Mesh){
                    const geometry=facadeFromBatch(o.geometry,options.coarsen===false?null:.7),material=o.material as THREE.MeshStandardMaterial;
                    retainCityMaterial(material);const mesh=new THREE.Mesh(geometry,material);mesh.name=low.name+' / surface '+low.children.length;
                    mesh.receiveShadow=o.receiveShadow;mesh.castShadow=o.castShadow;mesh.layers.mask=o.layers.mask;mesh.matrixAutoUpdate=false;bindCityLighting(mesh);low.add(mesh);releaseAfterUpload(geometry);
                }
            }else{
                const coarse:THREE.BufferGeometry[]=[];
                for(const o of high.children)if(o instanceof THREE.Mesh)coarse.push(coarseFromBatch(o.geometry,options.coarsen===false?null:Math.max(.7,Math.min(3,size.y/70))));
                if(coarse.length){const geometry=coarse.length===1?coarse[0]!:concatCompact(coarse);if(coarse.length>1)coarse.forEach(g=>g.dispose());const material=(high.children[0] as THREE.Mesh).material as THREE.MeshStandardMaterial;const mesh=new THREE.Mesh(geometry,coarseCityMaterial(material));mesh.receiveShadow=true;mesh.matrixAutoUpdate=false;bindCityLighting(mesh);low.add(mesh);releaseAfterUpload(geometry);}
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
                // A merged source is never drawn again: let its CPU geometry go (the
                // batch holds the drawable copy, GroundSurfaceIndex its own walkable
                // triangles). It is not restored on dispose.
                else mesh.geometry=MERGED_SOURCE;
            }
            // Source positions are world-space. Transform the container once.
            root.matrix.copy(owner.matrixWorld).invert();root.matrixAutoUpdate=false;root.add(high,low,retained);owner.add(root);
            const d=lodDistances(size.y,options.near,options.far,options.skyline,facade?Math.max(size.x,size.z):0);low.visible=false;this.blocks.push({root,high,low,box,...d,level:0,key,facade});
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
        for(const b of this.blocks){if(filmDetail.full)b.level=0;else if(moved||viewChanged)b.level=lodLevel(b.box.distanceToPoint(this.cameraPoint),b.near*(b.facade?viewScale:1),b.far,b.level);const high=b.level===0,low=b.level===1;if(b.high.visible!==high)b.high.visible=high;if(b.low.visible!==low)b.low.visible=low;}
    }
    /** Hide the blocks of one source (or several: a guest tower and its venue's podium, see StripLandmarks). */
    hideSource(sources?:string|readonly string[]):void {
        const list=sources===undefined?[]:typeof sources==='string'?[sources]:sources,key=list.join('|');
        if(key===this.hiddenSource)return;this.hiddenSource=key;
        for(const b of this.blocks)b.root.visible=!list.some(source=>b.key===source||b.key.endsWith('/'+source)||source==='guest-'&&b.key.startsWith(source));
    }
    get stats(){return {blocks:this.blocks.length,full:this.blocks.filter(b=>b.level===0).length,coarse:this.blocks.filter(b=>b.level===1).length,culled:this.blocks.filter(b=>b.level===2).length};}
    dispose():void {
        if(this.scene)unregister(this.scene,this);
        // Unmerged meshes go back to their parents; merged sources were released at build time.
        const sourceMeshes=new Set(this.originals.map(o=>o.mesh));
        const gs=new Set<THREE.BufferGeometry>(),ms:THREE.Material[]=[];for(const b of this.blocks){b.root.traverse(o=>{if(o instanceof THREE.Mesh&&!sourceMeshes.has(o)){gs.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:[o.material])ms.push(m);}});b.root.removeFromParent();}
        gs.forEach(g=>g.dispose());ms.forEach(disposeCityMaterial);for(const {mesh,parent,matrix,auto} of this.originals){delete mesh.userData.groundVisibilityRoot;mesh.matrix.copy(matrix);mesh.matrixAutoUpdate=auto;parent.add(mesh);}this.blocks=[];this.originals=[];
    }
}

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

export function cityLodStats(scene:THREE.Scene){const result={blocks:0,full:0,coarse:0,culled:0};for(const lod of registries.get(scene)?.items??[]){const s=lod.stats;result.blocks+=s.blocks;result.full+=s.full;result.coarse+=s.coarse;result.culled+=s.culled;}return result;}
