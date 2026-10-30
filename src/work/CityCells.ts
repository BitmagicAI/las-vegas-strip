import {Group} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {CollisionPack,loadCollisionPack} from './CollisionPack.js';
import {glbUrl} from './OptimizedGlb.js';
import {loadGltf} from './Prefetch.js';
import {runtimeUrl} from './RuntimeAssets.js';

// Temporary A/B switch while migration evidence is collected; published behavior is unchanged.
export const cityCellsEnabled=typeof location!=='undefined'&&['localhost','127.0.0.1'].includes(location.hostname)
    &&new URLSearchParams(location.search).get('cityCells')==='on';
interface CellFile {cell:string;file:string}
interface CellManifest {version:number;cellSize:number;cells:CellFile[];nodeOrder?:string[]}
export interface CityCollision {
    count:number;cellX:Int16Array|null;cellZ:Int16Array|null;
    trimesh(i:number,name:string):ReturnType<CollisionPack['trimesh']>;
}
async function manifest(directory:string):Promise<CellManifest>{
    const response=await fetch(runtimeUrl(directory+'/manifest.json'));
    if(!response.ok)throw new Error(`City cell manifest unavailable: ${directory}`);
    const result=await response.json() as CellManifest;
    if(result.version!==1||result.cellSize!==800)throw new Error('Unsupported city cell manifest');
    return result;
}
/** Keep physics residency on the existing 160 m records; only file packaging changes. */
class CellCollision implements CityCollision {
    readonly count:number;readonly cellX:Int16Array;readonly cellZ:Int16Array;
    private readonly owners:Uint16Array;private readonly local:Uint32Array;
    constructor(private readonly packs:Map<number,CollisionPack>){
        let count=0;for(const pack of packs.values())count+=pack.count;
        this.count=count;this.cellX=new Int16Array(count);this.cellZ=new Int16Array(count);
        this.owners=new Uint16Array(count);this.local=new Uint32Array(count);
        let at=0;
        for(const [owner,pack] of packs){
            if(!pack.cellX||!pack.cellZ)throw new Error('City collision pack lacks cells');
            for(let i=0;i<pack.count;i++,at++){
                this.cellX[at]=pack.cellX[i]!;this.cellZ[at]=pack.cellZ[i]!;this.owners[at]=owner;this.local[at]=i;
            }
        }
    }
    trimesh(i:number,name:string):ReturnType<CollisionPack['trimesh']>{return this.packs.get(this.owners[i]!)!.trimesh(this.local[i]!,name);}
}
export async function loadCellCollision():Promise<CityCollision>{
    const directory='/build/geographic-strip/collision-cells',files=(await manifest(directory)).cells;
    const packs=new Map<number,CollisionPack>();
    // Four requests overlap latency without starting all 91 decoders at once.
    for(let i=0;i<files.length;i+=4){
        const loaded=await Promise.all(files.slice(i,i+4).map(cell=>loadCollisionPack(directory+'/'+cell.file)));
        loaded.forEach((pack,k)=>packs.set(i+k,pack));
    }
    return new CellCollision(packs);
}
export async function loadCellVisuals():Promise<{scene:Group}>{
    const directory='/build/geographic-strip/cells',index=await manifest(directory),files=index.cells;
    if(!index.nodeOrder)throw new Error('City visual manifest lacks source node order');
    const scene=new Group();
    for(let i=0;i<files.length;i+=4){
        const loaded=await Promise.all(files.slice(i,i+4).map(async cell=>
            loadGltf(new GLTFLoader(),await glbUrl(directory+'/'+cell.file))));
        // Promise.all retains manifest order regardless of request completion order.
        for(const gltf of loaded)while(gltf.scene.children.length)scene.add(gltf.scene.children[0]!);
    }
    // Preserve Blender traversal order, including its natural ordering of signed cell names.
    const order=new Map<string,number>();
    for(let i=0;i<index.nodeOrder.length;i++)order.set(index.nodeOrder[i]!,i);
    // GLTFLoader sanitizes names; extras retain the exporter's exact cell/material identity.
    const key=(child:import('three').Object3D)=>`OSM ${child.userData.osmCell} ${child.userData.osmMaterial}`;
    for(const child of scene.children)if(!order.has(key(child)))throw new Error('Unknown city node '+key(child));
    scene.children.sort((a,b)=>order.get(key(a))!-order.get(key(b))!);
    return {scene};
}
