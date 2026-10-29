import {foliageSettings} from './FoliageSettings.js';
import {runtimeUrl} from './RuntimeAssets.js';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshStandardNodeMaterial,type Node} from 'three/webgpu';
import {lights,reference} from 'three/tsl';
import {isGeometryReleaseSuspended} from 'engine/resources/GeometryCpuRelease.js';
import {keyWithoutShadowNodes,sharedAlphaCutoff} from './ShaderSharing.js';
import {sharedInstancedMesh} from './SharedInstancing.js';
import {runSliced,runSync} from './FrameBudget.js';
import {loadPlants,type PlantList} from './Plants.js';

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
    if(source.alphaTest>0){material.alphaTest=0;material.alphaTestNode=sharedAlphaCutoff(source.alphaTest) as unknown as Node<'float'>;material.maskShadowNode=(reference('map','texture',material) as unknown as Node<'vec4'>).a.greaterThan(source.alphaTest);}
    keyWithoutShadowNodes(material);
    return material;
}
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
    /** Sliced (the city loading behind play): built within the shared frame budget and left hidden; the caller
     * compiles `group` and calls `show()`. */
    async load(sliced=false):Promise<void>{
        const loader=new GLTFLoader();
        // 363,425 lawn tufts, 8 bytes each (Plants.ts), decoded in the meshopt workers while the plants download
        const placing=loadPlants('/foliage/bellagio-placements.bin');placing.catch(()=>{});
        // public/foliage/ holds the optimized copies (tools/optimize/foliage-trees.mjs; sources in tools/foliage/models/).
        for(const file of ['tree-0','tree-1','tree-2','grass-0','grass-1'])this.assets.push((await loader.loadAsync(runtimeUrl(`/foliage/${file}.glb`))).scene);
        // The middle tree LOD's runtime copy has no textures of its own (tools/optimize/foliage-trees.mjs): its meshes take
        // tree-0's materials, which are the same Poly Haven maps.
        const near=new Map<string,THREE.Material>();
        this.assets[0]!.traverse(o=>{if(o instanceof THREE.Mesh)for(const m of Array.isArray(o.material)?o.material:[o.material])near.set(m.name,m);});
        this.assets[1]!.traverse(o=>{if(!(o instanceof THREE.Mesh))return;
            const pick=(m:THREE.Material)=>{const n=near.get(m.name);if(!n||n===m)return m;m.dispose();return n;};
            o.material=Array.isArray(o.material)?o.material.map(pick):pick(o.material);});
        for(const asset of this.assets)asset.traverse(o=>{if(o instanceof THREE.Mesh)for(const material of Array.isArray(o.material)?o.material:[o.material]){material.side=THREE.DoubleSide;if(material.transparent){material.transparent=false;material.alphaTest=.12;material.alphaToCoverage=true;material.depthWrite=true;}}});
        for(const asset of this.assets.slice(3))asset.traverse(o=>{if(o instanceof THREE.Mesh)for(const m of Array.isArray(o.material)?o.material:[o.material])if(m instanceof THREE.MeshStandardMaterial){m.roughnessMap=null;m.roughness=1;m.metalness=0;m.envMapIntensity=0;m.normalScale.set(.35,.35);m.emissive.setHex(0x526b2b);m.emissiveIntensity=.25;m.emissiveMap=m.map;}});
        const converted=new Map<THREE.Material,THREE.Material>();
        for(const asset of this.assets)asset.traverse(o=>{if(!(o instanceof THREE.Mesh))return;const swap=(m:THREE.Material)=>{if(!(m instanceof THREE.MeshStandardMaterial)||m instanceof MeshStandardNodeMaterial)return m;let lit=converted.get(m);if(!lit){const l=sunLitFoliageMaterial(m);m.dispose();this.sunLit.push(l);converted.set(m,l);lit=l;}return lit;};o.material=Array.isArray(o.material)?o.material.map(swap):swap(o.material);});
        const placements=await placing;
        this.root.name='Bellagio botanical planting';this.root.userData.perfOwner='Bellagio · trees and lawn';this.root.userData.perfKind='exterior';
        if(sliced)this.root.visible=false;this.owner.add(this.root);
        const trees=this.populate(placements.trees,this.assets.slice(0,3),40,[85,220,650],true),grass=this.populate(placements.grass,this.assets.slice(3),12,[14,36],false);
        if(sliced){await runSliced(trees);await runSliced(grass);if(!this.lightsBound)this.bindFoliageLights();}
        else{runSync(trees);runSync(grass);this.show();}
    }
    get group():THREE.Group{return this.root;}
    /** Puts the planting in and starts choosing its levels (load calls it unless sliced). */
    show():void{
        if(this.hook)return;this.root.visible=true;
        // Remove the old polygon crowns only after the replacement loaded.
        const old:THREE.Mesh[]=[];this.owner.traverse(o=>{if(o instanceof THREE.Mesh&&String(o.userData.source).startsWith('arrival-tree/'))old.push(o);});
        for(const mesh of old){mesh.removeFromParent();mesh.geometry.dispose();}
        this.previous=this.scene.onBeforeRender;const previous=this.previous;
        this.hook=(...args)=>{previous.apply(this.scene,args);if(!this.lightsBound)this.bindFoliageLights();const now=performance.now();if(this.scene.overrideMaterial||now-this.last<180||isGeometryReleaseSuspended())return;this.last=now;args[2].getWorldPosition(this.point);this.select(this.point);};
        this.scene.onBeforeRender=this.hook;
        this.unsubscribe=foliageSettings.subscribe(()=>{this.cells.forEach(c=>c.level=-1);this.select(this.point);this.last=0;});
    }
    /** Instances per `size` m cell and LOD. Steps (FrameBudget.ts): yields every 16k plants while sorting and every ~8k
     * instances while building. */
    private *populate(placed:PlantList,assets:THREE.Group[],size:number,limits:number[],trees:boolean):Generator<void,void> {
        // cells in order of first appearance, plants in placement order within each (a stable counting sort)
        const n=placed.count,cellOf=new Uint32Array(n),index=new Map<number,number>();
        for(let i=0;i<n;i++){
            if((i&16383)===16383)yield;
            const key=(Math.floor(placed.x(i)/size)+32768)*65536+Math.floor(placed.z(i)/size)+32768;
            let c=index.get(key);if(c===undefined){c=index.size;index.set(key,c);}cellOf[i]=c;
        }
        const keyOf=new Float64Array(index.size);for(const [key,c] of index)keyOf[c]=key;
        const cells=index.size,start=new Uint32Array(cells+1),order=new Uint32Array(n);
        for(let i=0;i<n;i++)start[cellOf[i]!+1]!++;
        for(let c=0;c<cells;c++)start[c+1]!+=start[c]!;
        const fill=start.slice(0,cells);
        for(let i=0;i<n;i++)order[fill[cellOf[i]!]!++]=i;
        const meshes=assets.map(asset=>{asset.updateMatrixWorld(true);const list:THREE.Mesh[]=[];asset.traverse(o=>{if(o instanceof THREE.Mesh)list.push(o);});return list;});
        const object=new THREE.Object3D(),matrix=new THREE.Matrix4();let work=0;
        for(let c=0;c<cells;c++){
            const from=start[c]!,count=start[c+1]!-from,levels:THREE.Group[]=[];
            for(let lod=0;lod<assets.length;lod++){
                const group=new THREE.Group();group.name=`${trees?'Trees':'Lawn'} ${Math.floor(keyOf[c]!/65536)-32768},${keyOf[c]!%65536-32768} LOD${lod}`;
                // Keep ground coverage across LODs; reduce blade geometry instead of tuft density.
                for(const o of meshes[lod]!){
                    const matrices=new Float32Array(count*16);
                    for(let k=0;k<count;k++){const p=order[from+k]!;object.position.set(placed.x(p),placed.y(p),placed.z(p));object.rotation.set(0,placed.yaw(p),0);object.scale.setScalar(placed.scale(p));object.updateMatrix();matrix.multiplyMatrices(object.matrix,o.matrixWorld).toArray(matrices,k*16);}
                    const mesh=sharedInstancedMesh(o.geometry,o.material,matrices,count);
                    mesh.castShadow=trees;mesh.receiveShadow=true;group.add(mesh);
                    if((work+=count)>=8192){work=0;yield;}
                }
                group.visible=lod===0;this.root.add(group);levels.push(group);
            }
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
