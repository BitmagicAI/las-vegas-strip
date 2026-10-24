import {foliageSettings} from './FoliageSettings.js';
import {glbUrl} from './OptimizedGlb.js';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshStandardNodeMaterial,type Node} from 'three/webgpu';
import {float,lights,reference} from 'three/tsl';
import {isGeometryReleaseSuspended} from 'engine/resources/GeometryCpuRelease.js';
import {runtimeUrl} from './RuntimeAssets.js';
import {sharedInstancedMesh} from './SharedInstancing.js';

/** Garden foliage keeps its own standard materials but is lit only by the sun
 * (with its shadow), the sky and the ambient term. Thousands of overlapping blades
 * and leaf cards ran the full light loop (~45 point lights) per fragment: 5-8 fps at
 * eye level in the garden. No point light reaches the planting (nearest pooled
 * light 88 m away, range at most 24 m), so the picture is identical (lawn mean
 * colour equal to 0.1 of a grey level); bindFoliageLights warns if that changes. */
function sunLitFoliageMaterial(source:THREE.MeshStandardMaterial):MeshStandardNodeMaterial {
    const material=new MeshStandardNodeMaterial();material.copy(source);material.name=source.name;
    // Leaf cut-outs go through nodes, never `alphaTest` (three r185's node copy drops it anyway).
    // The shadow pass copies each caster's `alphaTest` onto one shared shadow material, and
    // its setter bumps that material's version whenever the value switches between 0 and
    // non-zero: alternating leaves and trunks made every shadow caster rebuild its pipeline
    // key each frame (~90 a frame, ~45 MB/s of garbage). Same cut-off, same coverage edges.
    if(source.alphaTest>0){material.alphaTest=0;material.alphaTestNode=float(source.alphaTest);material.maskShadowNode=(reference('map','texture',material) as unknown as Node<'vec4'>).a.greaterThan(source.alphaTest);}
    return material;
}
interface Placement {trees:{position:[number,number,number];seed:number}[];grass:number[][]}
interface Cell {levels:THREE.Group[];box:THREE.Box3;level:number;limits:number[]}
/** Shared textured botanical assets, instanced per spatial cell and LOD. The cells share one shader build per material
 * (SharedInstancing.ts; as InstancedMeshes they cost 10 s of node builds at start-up). */
export class ResortFoliage {
    private cells:Cell[]=[];
    private unsubscribe:(()=>void)|null=null;
    private assets:THREE.Group[]=[];
    private root=new THREE.Group();
    private last=0;private point=new THREE.Vector3();
    private sunLit:MeshStandardNodeMaterial[]=[];
    private lightsBound=false;
    private previous:THREE.Scene['onBeforeRender']|null=null;
    private hook:THREE.Scene['onBeforeRender']|null=null;
    constructor(private scene:THREE.Scene,private owner:THREE.Group){}
    async load():Promise<void>{
        const loader=new GLTFLoader();
        const response=await fetch(runtimeUrl('/foliage/bellagio-placements.json'));if(!response.ok)throw Error('Foliage placements unavailable');
        const placements=await response.json() as Placement;
        for(const file of ['tree-0','tree-1','tree-2','grass-0','grass-1'])this.assets.push((await loader.loadAsync(await glbUrl(`/foliage/${file}.glb`))).scene);
        for(const asset of this.assets)asset.traverse(o=>{if(o instanceof THREE.Mesh)for(const material of Array.isArray(o.material)?o.material:[o.material]){material.side=THREE.DoubleSide;if(material.transparent){material.transparent=false;material.alphaTest=.12;material.alphaToCoverage=true;material.depthWrite=true;}}});
        for(const asset of this.assets.slice(3))asset.traverse(o=>{if(o instanceof THREE.Mesh)for(const m of Array.isArray(o.material)?o.material:[o.material])if(m instanceof THREE.MeshStandardMaterial){m.roughnessMap=null;m.roughness=1;m.metalness=0;m.envMapIntensity=0;m.normalScale.set(.35,.35);m.emissive.setHex(0x526b2b);m.emissiveIntensity=.25;m.emissiveMap=m.map;}});
        for(const asset of this.assets)asset.traverse(o=>{if(!(o instanceof THREE.Mesh))return;const swap=(m:THREE.Material)=>{if(!(m instanceof THREE.MeshStandardMaterial)||m instanceof MeshStandardNodeMaterial)return m;const lit=sunLitFoliageMaterial(m);m.dispose();this.sunLit.push(lit);return lit;};o.material=Array.isArray(o.material)?o.material.map(swap):swap(o.material);});
        this.root.name='Bellagio botanical planting';this.root.userData.perfOwner='Bellagio · trees and lawn';this.root.userData.perfKind='exterior';this.owner.add(this.root);
        this.populate(placements.trees.map(t=>[...t.position,t.seed%6283/1000,.88+(t.seed%23)/100]),this.assets.slice(0,3),40,[85,220,650],true);
        this.populate(placements.grass,this.assets.slice(3),12,[14,36],false);
        // Remove the old polygon crowns only after the replacement loaded.
        const old:THREE.Mesh[]=[];this.owner.traverse(o=>{if(o instanceof THREE.Mesh&&String(o.userData.source).startsWith('arrival-tree/'))old.push(o);});
        for(const mesh of old){mesh.removeFromParent();mesh.geometry.dispose();}
        this.previous=this.scene.onBeforeRender;const previous=this.previous;
        this.hook=(...args)=>{previous.apply(this.scene,args);if(!this.lightsBound)this.bindFoliageLights();const now=performance.now();if(this.scene.overrideMaterial||now-this.last<180||isGeometryReleaseSuspended())return;this.last=now;args[2].getWorldPosition(this.point);this.select(this.point);};
        this.scene.onBeforeRender=this.hook;
        this.unsubscribe=foliageSettings.subscribe(()=>{this.cells.forEach(c=>c.level=-1);this.select(this.point);this.last=0;});
    }
    private populate(positions:number[][],assets:THREE.Group[],size:number,limits:number[],trees:boolean):void {
        const groups=new Map<string,number[][]>();
        for(const p of positions){const key=`${Math.floor(p[0]!/size)},${Math.floor(p[2]!/size)}`;const list=groups.get(key)??[];list.push(p);groups.set(key,list);}
        const object=new THREE.Object3D(),matrix=new THREE.Matrix4();
        for(const [key,positions] of groups){
            const levels=assets.map((asset,lod)=>{
                const group=new THREE.Group();group.name=`${trees?'Trees':'Lawn'} ${key} LOD${lod}`;
                // Keep ground coverage across LODs; reduce blade geometry instead of tuft density.
                const selected=positions;
                asset.updateMatrixWorld(true);
                asset.traverse(o=>{if(!(o instanceof THREE.Mesh)||!selected.length)return;
                    const matrices=new Float32Array(selected.length*16);
                    selected.forEach((p,i)=>{object.position.set(p[0]!,p[1]!,p[2]!);object.rotation.set(0,p[3]!,0);object.scale.setScalar(p[4]!);object.updateMatrix();matrix.multiplyMatrices(object.matrix,o.matrixWorld).toArray(matrices,i*16);});
                    const mesh=sharedInstancedMesh(o.geometry,o.material,matrices,selected.length);
                    mesh.castShadow=trees;mesh.receiveShadow=true;group.add(mesh);
                });group.visible=lod===0;this.root.add(group);return group;
            });
            this.cells.push({levels,box:new THREE.Box3().setFromObject(levels[0]!),level:0,limits});
        }
    }
    /** The focused sun is created after the city loads; bind the fixed light
     * list once it exists (one material rebuild, during loading). */
    private bindFoliageLights():void {
        const sun=this.scene.getObjectByName('Afterlight focused sun');if(!(sun instanceof THREE.DirectionalLight))return;
        const list:THREE.Light[]=[sun],bounds=new THREE.Box3().setFromObject(this.root),at=new THREE.Vector3();
        this.scene.traverse(o=>{if(o instanceof THREE.HemisphereLight||o instanceof THREE.AmbientLight)list.push(o);
            else if(o instanceof THREE.PointLight&&o.parent?.name!=='PointLightPool'&&(o.distance===0||bounds.distanceToPoint(o.getWorldPosition(at))<o.distance))console.warn('[ResortFoliage] point light now reaches the garden but foliage ignores point lights:',o.name);});
        const node=lights(list);for(const m of this.sunLit){m.lightsNode=node;m.needsUpdate=true;}
        this.lightsBound=true;
    }
    select(point:THREE.Vector3):void {
        const settings=foliageSettings.get();this.root.visible=settings.enabled;if(!settings.enabled)return;
        for(const cell of this.cells){const d=cell.box.distanceToPoint(point)/settings.distanceScale;let next=cell.limits.findIndex(limit=>d<limit);if(next<0)next=cell.limits.length;
            if(next!==cell.level){const boundary=cell.limits[Math.min(next,cell.level)]!;if(cell.level<0||Math.abs(d-boundary)>=boundary*.08)cell.level=next;}
            // Re-assert every time: the engine's start-up warm-up restores visibility it
            // recorded before this cell chose its level, which left the garden empty.
            for(let i=0;i<cell.levels.length;i++){const g=cell.levels[i]!,v=i===cell.level;if(g.visible!==v)g.visible=v;}
        }
    }
    dispose():void {
        this.unsubscribe?.();this.unsubscribe=null;
        if(this.scene.onBeforeRender===this.hook&&this.previous)this.scene.onBeforeRender=this.previous;
        this.root.traverse(o=>{if(o instanceof THREE.Mesh)o.geometry.dispose();});this.root.removeFromParent();
        const textures=new Set<THREE.Texture>(),materials=new Set<THREE.Material>();
        for(const asset of this.assets)asset.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])materials.add(m);}});
        for(const m of materials){for(const value of Object.values(m))if(value instanceof THREE.Texture)textures.add(value);m.dispose();}for(const t of textures)t.dispose();this.assets=[];this.cells=[];
    }
}
