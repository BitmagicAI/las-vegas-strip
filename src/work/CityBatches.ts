import * as THREE from 'three';
import {applySceneSurface,cinematicSurfaceEnabled,sceneSurfaceKind,setSceneSurfaceRow} from './film/SceneSurface.js';
import {MeshStandardNodeMaterial,type Node} from 'three/webgpu';
import {attribute,texture,textureLoad,uv,vec2,ivec2,int,round,dFdx,dFdy,vertexStage,sRGBTransferEOTF} from 'three/tsl';
import {makeCityAtlas,type Atlas} from './CityAtlas.js';
import {bindCityLighting} from './CityLighting.js';
import {releaseAfterUpload} from './CpuGeometryRelease.js';
import {detailNodes,pbrDetailEnabled} from './PbrDetail.js';
import {runSync} from './FrameBudget.js';
import {drawnTexture} from './ShaderSharing.js';
import {detailSetFor} from './PbrDetailSets.js';
import {floats,Scratch} from './AttributeReader.js';
import {decodeLod,sampleHash,type BakedLod} from './CityBakeLoad.js';
import {bakeCapture} from './CityBake.js';

/* Vertex layout of every city batch (32 bytes a vertex; was 88, then 32 and 40 when glossy):
 *   position  float32 ×3   world metres; float keeps seams and grounding exact
 *   normal    snorm16 ×4   xyz the normal, w the vertex's row of the surface table below (w × 32767, 2026-10-26: the
 *                          row was a float attribute of its own). Four components on purpose: three pads a 3-component
 *                          16-bit attribute itself, which rendered camouflage blotches (the Paris balloon, r185 WebGPU);
 *                          16 bits keep glossy reflections as exact as the float normals did
 *   uv        float32 ×2   source UVs; tiling repeats need float range (silhouette LODs have none)
 *   color     unorm8  ×4   sRGB-encoded material × vertex colour, decoded per vertex
 * Roughness, metalness, emission, atlas rectangle and wrap modes used to be four
 * float attributes repeated on every vertex. They are per surface, so they live
 * once in a table texture and are fetched in the vertex stage. */
const TABLE_ROWS=4096;
const tableData=new Float32Array(TABLE_ROWS*3*4);
/** Row r: texel (0,r) = roughness, metalness, wrapS repeat, wrapT repeat;
 * (1,r) = emissive rgb (premultiplied by intensity), scanned detail set + 1 (PbrDetail; 0 = none); (2,r) = atlas rect x, y, w, h. */
export const citySurfaceTable=new THREE.DataTexture(tableData,3,TABLE_ROWS,THREE.RGBAFormat,THREE.FloatType);
citySurfaceTable.name='City surface table';citySurfaceTable.minFilter=citySurfaceTable.magFilter=THREE.NearestFilter;citySurfaceTable.generateMipmaps=false;citySurfaceTable.needsUpdate=true;
const tableRows=new Map<string,number>();const rowScratch=new Float32Array(12);
function surfaceRow(m:THREE.MeshStandardMaterial,map:THREE.Texture|null,rect:readonly number[]):number {
    const s=rowScratch;s[0]=m.roughness;s[1]=m.metalness;s[2]=map?.wrapS===THREE.RepeatWrapping?1:0;s[3]=map?.wrapT===THREE.RepeatWrapping?1:0;
    s[4]=m.emissive.r*m.emissiveIntensity;s[5]=m.emissive.g*m.emissiveIntensity;s[6]=m.emissive.b*m.emissiveIntensity;s[7]=pbrDetailEnabled()?detailSetFor(m.name)+1:0;s[8]=rect[0]!;s[9]=rect[1]!;s[10]=rect[2]!;s[11]=rect[3]!;
    const kind=cinematicSurfaceEnabled()?sceneSurfaceKind(m.name):0;
    const key=s.join(',')+':'+kind;let row=tableRows.get(key);if(row!==undefined)return row;
    row=tableRows.size;if(row>=TABLE_ROWS)throw new Error('City surface table is full; raise TABLE_ROWS');
    tableData.set(s,row*12);tableRows.set(key,row);citySurfaceTable.needsUpdate=true;if(kind)setSceneSurfaceRow(row,kind);return row;
}
export function citySurfaceRows():number {return tableRows.size;}

const ROW_SCALE=32767;
const row=int(round(attribute<'vec4'>('normal','vec4').w.mul(ROW_SCALE)));
const surface=vertexStage(textureLoad(citySurfaceTable,ivec2(0,row),int(0)));
const emission=vertexStage(textureLoad(citySurfaceTable,ivec2(1,row),int(0)));
const atlasRect=vertexStage(textureLoad(citySurfaceTable,ivec2(2,row),int(0)));
const linearColor=vertexStage(sRGBTransferEOTF(attribute<'vec4'>('color','vec4').rgb)) as unknown as Node<'vec3'>;

const srgbLut=new Float32Array(256);for(let i=0;i<256;i++){const v=i/255;srgbLut[i]=v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4);}
function toSrgb8(linear:number):number {const c=Math.min(1,Math.max(0,linear));return Math.round((c<=.0031308?c*12.92:1.055*Math.pow(c,1/2.4)-.055)*255);}

/** Texture-average colour per part, so the coarse LOD keeps each building's palette. */
const lowColors=new WeakMap<THREE.BufferGeometry,{starts:Uint32Array;tint:Float32Array}>();
const mapColors=new WeakMap<THREE.Texture,THREE.Color>();
/** The average colours of every colour map under `root`, worked out off the main thread before a build that runs
 * behind play (the browser shrinks each texture to 8×8 with createImageBitmap; drawing a large texture into a canvas
 * here cost up to ~100 ms each, 1.7 s for the city). The browser's resampling may differ from drawImage's by a level or
 * two: these colours only tint the distant silhouettes. */
export async function prefetchMapColors(root:THREE.Object3D):Promise<void>{
    const maps=new Set<THREE.Texture>();
    root.traverse(o=>{if(o instanceof THREE.Mesh)for(const m of Array.isArray(o.material)?o.material:[o.material]){const map=(m as THREE.MeshStandardMaterial).map;if(map&&!mapColors.has(map)&&map.image)maps.add(map);}});
    await Promise.all([...maps].map(async map=>{
        try{
            const small=await createImageBitmap(map.image as ImageBitmapSource,{resizeWidth:8,resizeHeight:8,resizeQuality:'low'});
            const canvas=new OffscreenCanvas(8,8),context=canvas.getContext('2d')!;context.drawImage(small,0,0);small.close();
            const pixels=context.getImageData(0,0,8,8).data,c=new THREE.Color(0,0,0),p=new THREE.Color();
            for(let i=0;i<pixels.length;i+=4){p.setRGB(pixels[i]!/255,pixels[i+1]!/255,pixels[i+2]!/255,THREE.SRGBColorSpace);c.add(p);}
            if(!mapColors.has(map))mapColors.set(map,c.multiplyScalar(1/64));
        }catch{/* averageMapColor draws it when it is needed */}
    }));
}
function averageMapColor(map:THREE.Texture|null):THREE.Color {
    if(!map)return new THREE.Color(1,1,1);const cached=mapColors.get(map);if(cached)return cached;
    const canvas=document.createElement('canvas');canvas.width=canvas.height=8;const context=canvas.getContext('2d')!;context.drawImage(map.image as CanvasImageSource,0,0,8,8);const pixels=context.getImageData(0,0,8,8).data,c=new THREE.Color(0,0,0),p=new THREE.Color();for(let i=0;i<pixels.length;i+=4){p.setRGB(pixels[i]!/255,pixels[i+1]!/255,pixels[i+2]!/255,THREE.SRGBColorSpace);c.add(p);}c.multiplyScalar(1/64);mapColors.set(map,c);return c;
}

const atlases=new WeakMap<THREE.Material,THREE.Texture>();
const sharedMaterials=new Map<string,{material:MeshStandardNodeMaterial;atlas:Atlas|null;references:number}>();
const materialKeys=new WeakMap<THREE.Material,string>();
export function disposeCityMaterial(material:THREE.Material):void{
    const key=materialKeys.get(material),shared=key===undefined?undefined:sharedMaterials.get(key);
    if(shared&&--shared.references>0)return;
    if(key!==undefined){sharedMaterials.delete(key);materialKeys.delete(material);}
    atlases.get(material)?.dispose();atlases.delete(material);material.dispose();
}
/** A facade LOD shares the full-detail atlas and shader, including its lifetime. */
export function retainCityMaterial(material:THREE.Material):void {
    const key=materialKeys.get(material),shared=key===undefined?undefined:sharedMaterials.get(key);
    if(!shared)throw new Error('Only a city batch material can be retained');
    shared.references++;
}
const detailSet=int(emission.w.add(.5)).sub(1);
function surfaceMaterial(source:THREE.MeshStandardMaterial,atlas:Atlas|null,detail=true):MeshStandardNodeMaterial {
    const material=new MeshStandardNodeMaterial();material.copy(source);material.color.setHex(0xffffff);material.vertexColors=false;
    material.map=null;material.normalMap=null;material.bumpMap=null;material.userData={};material.normalNode=null;material.aoNode=null;
    material.roughnessNode=surface.x;material.metalnessNode=surface.y;material.emissiveNode=emission.rgb;
    // the table supplies these; uniform values keep three's cache key the same across the family
    material.roughness=1;material.metalness=0;material.emissive.setHex(0);material.emissiveIntensity=1;
    let color:Node<'vec3'>=linearColor;
    if(atlas){const mode=surface.zw,source=uv();const wrapped=source.clamp(0,1).mul(vec2(1).sub(mode)).add(source.fract().mul(mode));
        // the atlas is read from the drawn material, so every atlas shares one shader (ShaderSharing.drawnTexture)
        (material as unknown as {atlasMap:THREE.Texture}).atlasMap=atlas.texture;
        color=drawnTexture('atlasMap',atlas.texture).sample(atlasRect.xy.add(wrapped.mul(atlasRect.zw))).grad(dFdx(source).mul(atlasRect.zw),dFdy(source).mul(atlasRect.zw)).rgb.mul(linearColor) as unknown as Node<'vec3'>;atlases.set(material,atlas.texture);}
    material.colorNode=color;
    // scanned surface detail (PbrDetail), per table row; the coarse LOD is beyond its fade distance
    const withDetail=detail&&pbrDetailEnabled();
    if(withDetail){const d=detailNodes(detailSet as unknown as Node<'int'>,color,surface.x as unknown as Node<'float'>);
        material.colorNode=d.color;material.roughnessNode=d.roughness;material.normalNode=d.normal;material.aoNode=d.ao;}
    const cinematic=cinematicSurfaceEnabled();
    if(cinematic)applySceneSurface(material,detailSet.equal(0).select(1,0) as unknown as Node<'float'>,row);
    // Everything else in the graph is shared (the surface table, vertex attributes, PbrDetail's arrays): one node build
    // per variant instead of one per material (109 atlases, ~400 builds at start-up on 2026-10-24).
    const key=`city-surface${atlas?':atlas':''}${withDetail?':detail':''}${cinematic?':scene':''}`;
    material.customProgramCacheKey=()=>key;
    return material;
}
/** Reuse the shader/material across blocks, not just within a block. Thousands
 * of equivalent node graphs otherwise make startup compilation much slower. */
export function coarseCityMaterial(source:THREE.MeshStandardMaterial):MeshStandardNodeMaterial {
    const key=['coarse',source.side,source.fog,source.envMapIntensity].join('|');
    const shared=sharedMaterials.get(key);if(shared){shared.references++;return shared.material;}
    const material=surfaceMaterial(source,null,false);material.polygonOffset=false;
    sharedMaterials.set(key,{material,atlas:null,references:1});materialKeys.set(material,key);return material;
}

/** One source mesh of a batch and everything its vertices need. */
interface Part {mesh:THREE.Mesh;geometry:THREE.BufferGeometry;material:THREE.MeshStandardMaterial;map:THREE.Texture|null;
    matrix:THREE.Matrix4;normalMatrix:THREE.Matrix3;uvMatrix:THREE.Matrix3|null;flip:boolean;row:number;
    /** its triangles cast the city's sun shadow (userData.cityCaster, set by the loaders) */caster:boolean}
/** A batch as planned at load (2026-10-26): its source meshes in order with their per-part values, its material and
 * atlas, and no vertices. Filling it is separate: every vertex (fillBatchSteps, the near level) once the block is near,
 * or a baked subset (subsetFromPlan, the distant LOD) at load, straight from the sources. */
export interface BatchPlan {name:string;material:MeshStandardNodeMaterial;source:THREE.MeshStandardMaterial;parts:Part[];
    /** each part's first vertex and first index in the batch, then the totals (parts + 1 entries) */
    starts:Uint32Array;indexStarts:Uint32Array;
    /** each part's linear texture average (the silhouette's tint), 3 a part */
    tint:Float32Array;
    shadow:boolean;receive:boolean;mask:number}

/** Keep texture/normal-map and transparency pipelines distinct. Within a
 * pipeline, colour, emission and PBR factors are table rows, not draw calls.
 * Planned source meshes are removed from their parents (their geometry stays with the plan). */
export function planStaticBatches(meshes:THREE.Mesh[],name:string):BatchPlan[] {
    const buckets=new Map<string,{material:THREE.MeshStandardMaterial;meshes:THREE.Mesh[];shadow:boolean;receive:boolean;mask:number}>();
    for(const mesh of meshes){
        if(Array.isArray(mesh.material)||!(mesh.material instanceof THREE.MeshStandardMaterial)||mesh instanceof THREE.SkinnedMesh||mesh instanceof THREE.InstancedMesh)continue;
        const m=mesh.material;
        if(m.type!=='MeshStandardMaterial')continue;
        // Transparent objects need independent sorting; custom shaders and
        // unusual maps stay on their original rendering path.
        if(m.transparent||m.alphaTest||m.normalMap||m.bumpMap||m.aoMap||m.roughnessMap||m.metalnessMap||m.emissiveMap||m.displacementMap)continue;
        if(m.map&&(m.map.colorSpace!==THREE.SRGBColorSpace||m.map.channel!==0||
            (m.map.wrapS!==THREE.RepeatWrapping&&m.map.wrapS!==THREE.ClampToEdgeWrapping)||
            (m.map.wrapT!==THREE.RepeatWrapping&&m.map.wrapT!==THREE.ClampToEdgeWrapping)))continue;
        if(!mesh.geometry.getAttribute('position'))continue;
        mesh.updateWorldMatrix(true,false);
        const key=[m.type,m.side,m.fog,m.envMapIntensity,m.normalScale?.toArray().join(','),m.bumpScale,m.polygonOffset,m.polygonOffsetFactor,m.polygonOffsetUnits,mesh.castShadow,mesh.receiveShadow,mesh.layers.mask].join('|');
        let b=buckets.get(key);if(!b){b={material:m,meshes:[],shadow:mesh.castShadow,receive:mesh.receiveShadow,mask:mesh.layers.mask};buckets.set(key,b);}
        b.meshes.push(mesh);
    }
    const plans:BatchPlan[]=[];
    for(const [key,b] of buckets){
        const maps=b.meshes.map(m=>(m.material as THREE.MeshStandardMaterial).map);
        const materialKey=key+'|'+[...new Set(maps.map(m=>m?.uuid??'white'))].sort().join(',');
        let shared=sharedMaterials.get(materialKey);
        const atlas=shared?.atlas??makeCityAtlas(maps);
        let material:MeshStandardNodeMaterial;
        if(shared){shared.references++;material=shared.material;}else{
            material=surfaceMaterial(b.material,atlas);
            shared={material,atlas,references:1};sharedMaterials.set(materialKey,shared);materialKeys.set(material,materialKey);
        }
        const n=b.meshes.length,parts:Part[]=[],starts=new Uint32Array(n+1),indexStarts=new Uint32Array(n+1),tint=new Float32Array(n*3);
        let v=0,ix=0;
        for(let k=0;k<n;k++){
            const mesh=b.meshes[k]!,g=mesh.geometry,m=mesh.material as THREE.MeshStandardMaterial,map=m.map,count=g.getAttribute('position').count;
            // Bake the source map's UV transform so equivalent material clones can
            // batch without changing tiling or the colour space of their textures.
            const uvMatrix=map?(map.updateMatrix(),map.matrix.clone()):null,rect=atlas?.rects.get(map)??[0,0,1,1],average=averageMapColor(map);
            tint[k*3]=average.r;tint[k*3+1]=average.g;tint[k*3+2]=average.b;
            parts.push({mesh,geometry:g,material:m,map,matrix:mesh.matrixWorld.clone(),normalMatrix:new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld),
                uvMatrix,flip:!!map?.flipY,row:surfaceRow(m,map,rect),caster:!!mesh.userData.cityCaster});
            starts[k]=v;indexStarts[k]=ix;v+=count;ix+=g.index?g.index.count:count;
            mesh.removeFromParent();
        }
        starts[n]=v;indexStarts[n]=ix;
        plans.push({name:name+' / surface '+plans.length,material,source:b.material,parts,starts,indexStarts,tint,shadow:b.shadow,receive:b.receive,mask:b.mask});
    }
    return plans;
}
const vertexCount=(plan:BatchPlan)=>plan.starts[plan.parts.length]!;
const indexCount=(plan:BatchPlan)=>plan.indexStarts[plan.parts.length]!;
/** A part's normals (computed when its geometry has none, as three would) */
function partNormals(p:Part):THREE.BufferAttribute|THREE.InterleavedBufferAttribute{
    const own=p.geometry.getAttribute('normal');if(own)return own;
    const computed=p.geometry.clone();computed.computeVertexNormals();return computed.getAttribute('normal');
}
/** Writes vertex `i` of part `p` (its components already as doubles: P, N, U, O) to slot `s` of the batch arrays: the
 * world position (Vector3.applyMatrix4, perspective divide included), the normal (Matrix3 + normalize) with the surface
 * row in w, the UV (Vector2.applyMatrix3, flipped as the map is), the colour (material x vertex colour, sRGB). */
function writeVertex(p:Part,P:ArrayLike<number>,N:ArrayLike<number>,ns:number,U:ArrayLike<number>|null,O:ArrayLike<number>|null,oc:number,i:number,s:number,
    positions:Float32Array,normals:Int16Array,uvs:Float32Array|null,colors:Uint8Array,silhouette:Float32Array|null):void{
    const e=p.matrix.elements,ne=p.normalMatrix.elements,m=p.material;
    const x=P[i*3]!,y=P[i*3+1]!,z=P[i*3+2]!,w=1/(e[3]!*x+e[7]!*y+e[11]!*z+e[15]!);
    positions[s*3]=(e[0]!*x+e[4]!*y+e[8]!*z+e[12]!)*w;positions[s*3+1]=(e[1]!*x+e[5]!*y+e[9]!*z+e[13]!)*w;positions[s*3+2]=(e[2]!*x+e[6]!*y+e[10]!*z+e[14]!)*w;
    const a=N[i*ns]!,b=N[i*ns+1]!,c=N[i*ns+2]!;
    let nx=ne[0]!*a+ne[3]!*b+ne[6]!*c,ny=ne[1]!*a+ne[4]!*b+ne[7]!*c,nz=ne[2]!*a+ne[5]!*b+ne[8]!*c;const inverse=1/(Math.sqrt(nx*nx+ny*ny+nz*nz)||1);nx*=inverse;ny*=inverse;nz*=inverse;
    normals[s*4]=Math.round(nx*ROW_SCALE);normals[s*4+1]=Math.round(ny*ROW_SCALE);normals[s*4+2]=Math.round(nz*ROW_SCALE);normals[s*4+3]=p.row;
    if(uvs){
        if(U){let u=U[i*2]!,t=U[i*2+1]!;const ue=p.uvMatrix?.elements;if(ue){const u0=u;u=ue[0]!*u0+ue[3]!*t+ue[6]!;t=ue[1]!*u0+ue[4]!*t+ue[7]!;if(p.flip)t=1-t;}uvs[s*2]=u;uvs[s*2+1]=t;}
        else{uvs[s*2]=0;uvs[s*2+1]=0;}
    }
    for(let k=0;k<3;k++){
        const material=k===0?m.color.r:k===1?m.color.g:m.color.b,linear=O?material*O[i*oc+k]!:material;
        colors[s*4+k]=silhouette?toSrgb8(srgbLut[toSrgb8(linear)]!*silhouette[k]!):toSrgb8(linear);
    }
    colors[s*4+3]=255;
}

/** The near level of a batch: every vertex, written in part order (yields between parts and every 4096 vertices,
 * FrameBudget.ts, so a venue can be filled over several frames while the game runs). */
export function* fillBatchSteps(plan:BatchPlan):Generator<void,THREE.BufferGeometry> {
    const vertices=vertexCount(plan),indices=indexCount(plan),scratch=new Scratch();
    const positions=new Float32Array(vertices*3),normals=new Int16Array(vertices*4),uvs=new Float32Array(vertices*2),colors=new Uint8Array(vertices*4);
    const index=vertices>65535?new Uint32Array(indices):new Uint16Array(indices);
    for(let k=0;k<plan.parts.length;k++){
        const p=plan.parts[k]!,g=p.geometry,position=g.getAttribute('position'),count=position.count,base=plan.starts[k]!;
        const normal=partNormals(p),sourceUv=g.getAttribute('uv'),old=p.material.vertexColors?g.getAttribute('color'):undefined;
        // the source's components as doubles, converted once per array type (AttributeReader.ts)
        const P=floats(position,scratch,0),N=floats(normal,scratch,1),U=sourceUv?floats(sourceUv,scratch,2):null,O=old?floats(old,scratch,3):null;
        for(let i=0;i<count;i++){
            if((i&4095)===4095)yield;
            writeVertex(p,P,N,normal.itemSize,U,O,old?.itemSize??0,i,base+i,positions,normals,uvs,colors,null);
        }
        let ix=plan.indexStarts[k]!;
        if(g.index){const source=g.index.array;for(let j=0;j<g.index.count;j++)index[ix++]=source[j]!+base;}
        else for(let j=0;j<count;j++)index[ix++]=base+j;
        yield;
    }
    const geometry=new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.setAttribute('normal',new THREE.BufferAttribute(normals,4,true));
    geometry.setAttribute('uv',new THREE.BufferAttribute(uvs,2));geometry.setAttribute('color',new THREE.BufferAttribute(colors,4,true));
    geometry.setIndex(new THREE.BufferAttribute(index,1));geometry.computeBoundingBox();geometry.computeBoundingSphere();
    lowColors.set(geometry,{starts:plan.starts,tint:plan.tint});
    return geometry;
}
/** The drawn mesh of a plan's near level. */
export function batchMesh(plan:BatchPlan,geometry:THREE.BufferGeometry):THREE.Mesh {
    const mesh=new THREE.Mesh(geometry,plan.material);mesh.name=plan.name;mesh.castShadow=plan.shadow;mesh.receiveShadow=plan.receive;mesh.layers.mask=plan.mask;mesh.matrixAutoUpdate=false;bindCityLighting(mesh);
    return mesh;
}
/** The near level of every plan, as a group (passages, and blocks that are not lazy). */
export function batchStaticMeshes(meshes:THREE.Mesh[],name:string):THREE.Group {
    const root=new THREE.Group();root.name=name;
    for(const plan of planStaticBatches(meshes,name)){const geometry=runSync(fillBatchSteps(plan));root.add(batchMesh(plan,geometry));releaseAfterUpload(geometry);}
    return root;
}

/** Direct reads of one vertex's components, the same values three's accessors return (for a few vertices of a part;
 * whole parts go through AttributeReader.floats). */
interface One {array:ArrayLike<number>;stride:number;offset:number;scale:number;floor:number;size:number}
function one(a:THREE.BufferAttribute|THREE.InterleavedBufferAttribute):One{
    const interleaved='isInterleavedBufferAttribute' in a&&a.isInterleavedBufferAttribute;
    const array=(interleaved?(a as THREE.InterleavedBufferAttribute).data.array:(a as THREE.BufferAttribute).array) as ArrayLike<number>;
    let scale=1,floor=-Infinity;
    if(a.normalized){
        if(array instanceof Int8Array){scale=127;floor=-1;}else if(array instanceof Int16Array){scale=32767;floor=-1;}else if(array instanceof Int32Array){scale=2147483647;floor=-1;}
        else if(array instanceof Uint8Array)scale=255;else if(array instanceof Uint16Array)scale=65535;else if(array instanceof Uint32Array)scale=4294967295;
    }
    return {array,stride:interleaved?(a as THREE.InterleavedBufferAttribute).data.stride:a.itemSize,offset:interleaved?(a as THREE.InterleavedBufferAttribute).offset:0,scale,floor,size:a.itemSize};
}
/** Vertex `i` of `r` into `out` (packed, `size` components). */
function readOne(r:One,i:number,out:Float64Array):Float64Array{for(let c=0;c<r.size;c++){const v=r.array[i*r.stride+r.offset+c]!;out[c]=r.scale===1?v:Math.max(v/r.scale,r.floor);}return out;}
const _P=new Float64Array(4),_N=new Float64Array(4),_U=new Float64Array(4),_O=new Float64Array(4);

/** A FNV-1a hash of 64 evenly spaced positions of the plan's near level (the float bits it would hold), computed from
 * the sources without filling it: the bake's signature (CityBakeLoad.sampleHash). */
export function planSampleHash(plan:BatchPlan):number{
    const n=vertexCount(plan),out=new Float32Array(3),bits=new Uint32Array(out.buffer);
    let h=0x811c9dc5,k=0;
    for(let s=0;s<64;s++){
        const v=Math.floor(s*n/64);
        if(v>=n){for(let c=0;c<3;c++){h^=0;h=Math.imul(h,0x01000193);}continue;}
        while(v>=plan.starts[k+1]!)k++;
        const p=plan.parts[k]!,e=p.matrix.elements,x=readOne(one(p.geometry.getAttribute('position')),v-plan.starts[k]!,_P);
        const w=1/(e[3]!*x[0]!+e[7]!*x[1]!+e[11]!*x[2]!+e[15]!);
        out[0]=(e[0]!*x[0]!+e[4]!*x[1]!+e[8]!*x[2]!+e[12]!)*w;out[1]=(e[1]!*x[0]!+e[5]!*x[1]!+e[9]!*x[2]!+e[13]!)*w;out[2]=(e[2]!*x[0]!+e[6]!*x[1]!+e[10]!*x[2]!+e[14]!)*w;
        for(let c=0;c<3;c++){h^=bits[c]!;h=Math.imul(h,0x01000193);}
    }
    return h>>>0;
}
export function planCounts(plan:BatchPlan):{vertices:number;indices:number}{return {vertices:vertexCount(plan),indices:indexCount(plan)};}

/** A distant LOD straight from the sources (2026-10-26): `subset` names the near-level vertices it keeps (in its own
 * vertex order), `index` its triangles over them. Only those vertices are transformed, in batch order (grouped by part).
 * `silhouette`: the coarse level (no UVs; colours tinted by each part's texture average). Also returns the part of each
 * LOD vertex (for the shadow casters). */
export function subsetFromPlan(plan:BatchPlan,subset:Uint32Array,index:Uint16Array|Uint32Array,silhouette:boolean):{geometry:THREE.BufferGeometry;parts:Uint32Array} {
    const n=subset.length,order=new Float64Array(n);
    for(let s=0;s<n;s++)order[s]=subset[s]!*16777216+s;
    order.sort();
    const positions=new Float32Array(n*3),normals=new Int16Array(n*4),uvs=silhouette?null:new Float32Array(n*2),colors=new Uint8Array(n*4),parts=new Uint32Array(n);
    let k=-1,P:One|null=null,N:One|null=null,U:One|null=null,O:One|null=null,tint:Float32Array|null=null;
    for(let j=0;j<n;j++){
        const packed=order[j]!,v=Math.floor(packed/16777216),s=packed-v*16777216;
        if(k<0||v>=plan.starts[k+1]!){
            while(v>=plan.starts[k+1]!)k++;
            const p=plan.parts[k]!,g=p.geometry,old=p.material.vertexColors?g.getAttribute('color'):undefined,uv=g.getAttribute('uv');
            P=one(g.getAttribute('position'));N=one(partNormals(p));U=uv?one(uv):null;O=old?one(old):null;
            tint=silhouette?plan.tint.subarray(k*3,k*3+3):null;
        }
        const p=plan.parts[k]!,i=v-plan.starts[k]!;
        writeVertex(p,readOne(P!,i,_P),readOne(N!,i,_N),0,U?readOne(U,i,_U):null,O?readOne(O,i,_O):null,0,0,s,positions,normals,uvs,colors,tint);
        parts[s]=k;
    }
    const g=new THREE.BufferGeometry();
    g.setAttribute('position',new THREE.BufferAttribute(positions,3));g.setAttribute('normal',new THREE.BufferAttribute(normals,4,true));
    if(uvs)g.setAttribute('uv',new THREE.BufferAttribute(uvs,2));
    g.setAttribute('color',new THREE.BufferAttribute(colors,4,true));
    g.setIndex(new THREE.BufferAttribute(index,1));g.computeBoundingBox();g.computeBoundingSphere();
    return {geometry:g,parts};
}

/** The coarse (silhouette) version of a batch: vertex clustering keeps the surveyed
 * envelope, roofs and setbacks; colours are tinted by each part's texture average.
 * Built once while loading from the batch's arrays, so call it before the batch is
 * drawn (its CPU arrays are released after upload). `spacing` null keeps every vertex. */
export function coarseFromBatch(batch:THREE.BufferGeometry,spacing:number|null):THREE.BufferGeometry {return runSync(coarseFromBatchSteps(batch,spacing));}
/** coarseFromBatch as steps: yields every 8192 vertices and triangles (FrameBudget.ts). */
export function* coarseFromBatchSteps(batch:THREE.BufferGeometry,spacing:number|null):Generator<void,THREE.BufferGeometry> {
    const P=batch.getAttribute('position').array as Float32Array,C=batch.getAttribute('color').array as Uint8Array,NR=batch.getAttribute('normal').array as Int16Array,I=batch.index!.array;
    const n=P.length/3,low=lowColors.get(batch);
    // Linear vertex colour × texture average of the part it came from.
    const linear=new Float32Array(n*3);
    for(let part=0,v=0;v<n;v++){
        if((v&8191)===8191)yield;
        if(low)while(v>=low.starts[part+1]!)part++;
        const t=low?part*3:-1;
        linear[v*3]=srgbLut[C[v*4]!]!*(low?low.tint[t]!:1);linear[v*3+1]=srgbLut[C[v*4+1]!]!*(low?low.tint[t+1]!:1);linear[v*3+2]=srgbLut[C[v*4+2]!]!*(low?low.tint[t+2]!:1);
    }
    let remap:Uint32Array,clusters:number,cp:Float32Array,cc:Float32Array,cr:Int16Array;
    if(spacing===null){remap=new Uint32Array(n);for(let i=0;i<n;i++)remap[i]=i;clusters=n;cp=P.slice();cc=linear;cr=new Int16Array(n);for(let i=0;i<n;i++)cr[i]=NR[i*4+3]!;}
    else{
        // Numeric cell keys (15 bits an axis): no string keys, no per-cell arrays.
        const cells=new Map<number,number>(),sums=new Float64Array(n*6),counts=new Uint32Array(n);remap=new Uint32Array(n);cr=new Int16Array(n);clusters=0;
        for(let i=0;i<n;i++){
            if((i&8191)===8191)yield;
            const key=((Math.round(P[i*3]!/spacing)+16384)*32768+(Math.round(P[i*3+1]!/spacing)+16384))*32768+(Math.round(P[i*3+2]!/spacing)+16384);
            let id=cells.get(key);if(id===undefined){id=clusters++;cells.set(key,id);cr[id]=NR[i*4+3]!;}
            remap[i]=id;counts[id]!++;const s=id*6;sums[s]!+=P[i*3]!;sums[s+1]!+=P[i*3+1]!;sums[s+2]!+=P[i*3+2]!;sums[s+3]!+=linear[i*3]!;sums[s+4]!+=linear[i*3+1]!;sums[s+5]!+=linear[i*3+2]!;
        }
        cp=new Float32Array(clusters*3);cc=new Float32Array(clusters*3);cr=cr.slice(0,clusters);
        for(let id=0;id<clusters;id++){const k=counts[id]!,s=id*6;cp[id*3]=sums[s]!/k;cp[id*3+1]=sums[s+1]!/k;cp[id*3+2]=sums[s+2]!/k;cc[id*3]=sums[s+3]!/k;cc[id*3+1]=sums[s+4]!/k;cc[id*3+2]=sums[s+5]!/k;}
    }
    // Remap triangles; drop degenerate ones and exact duplicates (hash check, exact compare).
    const out=new Uint32Array(I.length);let t=0;const seen=new Map<number,number>();
    for(let i=0;i+2<I.length;i+=3){
        if(i%24576===24573)yield;
        let a=remap[I[i]!]!,b=remap[I[i+1]!]!,c=remap[I[i+2]!]!;if(a===b||b===c||a===c)continue;
        if(spacing!==null){const x=Math.min(a,b,c),z=Math.max(a,b,c),y=a+b+c-x-z;
            const h=(Math.imul(x,73856093)^Math.imul(y,19349663)^Math.imul(z,83492791))>>>0,prev=seen.get(h);
            if(prev!==undefined){const qa=out[prev]!,qb=out[prev+1]!,qc=out[prev+2]!,qx=Math.min(qa,qb,qc),qz=Math.max(qa,qb,qc);if(qx===x&&qz===z&&qa+qb+qc-qx-qz===y)continue;}else seen.set(h,t);}
        out[t++]=a;out[t++]=b;out[t++]=c;
    }
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(cp,3));
    g.setIndex(new THREE.BufferAttribute(clusters>65535?out.slice(0,t):Uint16Array.from(out.subarray(0,t)),1));
    g.computeVertexNormals();const fn=g.getAttribute('normal').array as Float32Array,normals=new Int16Array(clusters*4);
    for(let i=0;i<clusters;i++){normals[i*4]=Math.round(fn[i*3]!*ROW_SCALE);normals[i*4+1]=Math.round(fn[i*3+1]!*ROW_SCALE);normals[i*4+2]=Math.round(fn[i*3+2]!*ROW_SCALE);normals[i*4+3]=cr[i]!;}
    g.setAttribute('normal',new THREE.BufferAttribute(normals,4,true));
    const colors=new Uint8Array(clusters*4);for(let i=0;i<clusters;i++){colors[i*4]=toSrgb8(cc[i*3]!);colors[i*4+1]=toSrgb8(cc[i*3+1]!);colors[i*4+2]=toSrgb8(cc[i*3+2]!);colors[i*4+3]=255;}
    g.setAttribute('color',new THREE.BufferAttribute(colors,4,true));
    g.computeBoundingBox();g.computeBoundingSphere();return g;
}

/** The colour each vertex of a batch shows in the silhouette LOD (linear vertex colour x its part's texture average,
 * as coarseFromBatch and bakedLodFromBatch use), sRGB 8-bit, for the bake's capture (CityBake.ts). */
export function silhouetteColors(batch:THREE.BufferGeometry):Uint8Array {
    const C=batch.getAttribute('color').array as Uint8Array,n=C.length/4,out=new Uint8Array(n*3),low=lowColors.get(batch);
    for(let part=0,v=0;v<n;v++){
        if(low)while(v>=low.starts[part+1]!)part++;
        for(let c=0;c<3;c++)out[v*3+c]=toSrgb8(srgbLut[C[v*4+c]!]!*(low?low.tint[part*3+c]!:1));
    }
    return out;
}
if(bakeCapture)bakeCapture.silhouette=silhouetteColors;

/** A distant LOD from the bake (CityBakeLoad.ts, 2026-10-26): the baked subset of the batch's own vertices and its
 * triangles over them, instead of clustering in the browser. `silhouette`: the coarse level's layout and colours (no
 * UVs, colours tinted by each part's texture average, as coarseFromBatch); otherwise the facade level's (the batch's own
 * attributes). Null when the batch is not the one the bake was made from (stale bake): cluster then. */
export function bakedLodFromBatch(batch:THREE.BufferGeometry,baked:BakedLod|undefined,silhouette:boolean):THREE.BufferGeometry|null {
    if(!baked)return null;
    const P=batch.getAttribute('position').array as Float32Array,n=P.length/3;
    if(n!==baked.vertices||batch.index?.count!==baked.indices||sampleHash(P,n)!==baked.hash)return null;
    const {subset,index}=decodeLod(baked),count=subset.length;
    const N=batch.getAttribute('normal').array as Int16Array,C=batch.getAttribute('color').array as Uint8Array;
    const positions=new Float32Array(count*3),normals=new Int16Array(count*4),colors=new Uint8Array(count*4);
    const low=silhouette?lowColors.get(batch):undefined;
    for(let i=0;i<count;i++){
        const v=subset[i]!;
        positions[i*3]=P[v*3]!;positions[i*3+1]=P[v*3+1]!;positions[i*3+2]=P[v*3+2]!;
        for(let c=0;c<4;c++)normals[i*4+c]=N[v*4+c]!;
        if(low){
            // the part the vertex came from, for its texture average (as coarseFromBatch)
            let lo=0,hi=low.starts.length-2;while(lo<hi){const mid=(lo+hi+1)>>1;if(low.starts[mid]!<=v)lo=mid;else hi=mid-1;}
            for(let c=0;c<3;c++)colors[i*4+c]=toSrgb8(srgbLut[C[v*4+c]!]!*low.tint[lo*3+c]!);
        }else for(let c=0;c<3;c++)colors[i*4+c]=C[v*4+c]!;
        colors[i*4+3]=255;
    }
    const g=new THREE.BufferGeometry();
    g.setAttribute('position',new THREE.BufferAttribute(positions,3));g.setAttribute('normal',new THREE.BufferAttribute(normals,4,true));
    if(!silhouette){const U=batch.getAttribute('uv').array as Float32Array,uv=new Float32Array(count*2);for(let i=0;i<count;i++){uv[i*2]=U[subset[i]!*2]!;uv[i*2+1]=U[subset[i]!*2+1]!;}g.setAttribute('uv',new THREE.BufferAttribute(uv,2));}
    g.setAttribute('color',new THREE.BufferAttribute(colors,4,true));
    g.setIndex(new THREE.BufferAttribute(index,1));g.computeBoundingBox();g.computeBoundingSphere();
    return g;
}

/** Architectural LOD, built before upload. Never merge stone with glass/trim, or
 * average a facade texture into a flat colour. Keep UVs, hard edges and the source
 * normals (recomputing them rounds flat walls and changes their lighting). Small
 * coplanar details can collapse, while the surviving surfaces use the full shader.
 * Numeric spatial keys and typed linked lists avoid a JS object per vertex. */
export function facadeFromBatch(batch:THREE.BufferGeometry,spacing:number|null):THREE.BufferGeometry {return runSync(facadeFromBatchSteps(batch,spacing));}
/** facadeFromBatch as steps: yields every 4096 vertices (FrameBudget.ts). */
export function* facadeFromBatchSteps(batch:THREE.BufferGeometry,spacing:number|null):Generator<void,THREE.BufferGeometry> {
    if(spacing===null)return batch.clone();
    const P=batch.getAttribute('position') as THREE.BufferAttribute,N=batch.getAttribute('normal') as THREE.BufferAttribute;
    const C=batch.getAttribute('color') as THREE.BufferAttribute,U=batch.getAttribute('uv') as THREE.BufferAttribute,RR=N.array as Int16Array;
    const colors=C.array as Uint8Array,n=P.count,I=batch.index!.array;
    // the batch's components as doubles (AttributeReader.ts): the same values as getX/getY/getZ, without a call per
    // component; the surface row is the normal's w (RR[i*4+3])
    const scratch=new Scratch(),PR=floats(P,scratch,0),NR=floats(N,scratch,1),UR=floats(U,scratch,2);
    const heads=new Map<number,number>(),next=new Int32Array(n),representative=new Uint32Array(n),remap=new Uint32Array(n);
    const sums=new Float64Array(n*8),counts=new Uint32Array(n);let clusters=0;
    for(let i=0;i<n;i++){
        if((i&4095)===4095)yield;
        const x=PR[i*3]!,y=PR[i*3+1]!,z=PR[i*3+2]!,nx=NR[i*4]!,ny=NR[i*4+1]!,nz=NR[i*4+2]!,u=UR[i*2]!,v=UR[i*2+1]!,row=RR[i*4+3]!,ci=i*4;
        const key=((Math.round(x/spacing)+16384)*32768+(Math.round(y/spacing)+16384))*32768+(Math.round(z/spacing)+16384);
        const head=heads.get(key)??-1;let id=head;
        for(;id!==-1;id=next[id]!){
            const r=representative[id]!,rc=r*4;
            if(RR[r*4+3]===row&&colors[ci]===colors[rc]&&colors[ci+1]===colors[rc+1]&&colors[ci+2]===colors[rc+2]&&
                nx*NR[r*4]!+ny*NR[r*4+1]!+nz*NR[r*4+2]!>.98&&
                // Parallel planes can have the same finish: merging a wall with
                // its projecting trim pushes the wall through the glazing.
                Math.abs((x-PR[r*3]!)*nx+(y-PR[r*3+1]!)*ny+(z-PR[r*3+2]!)*nz)<.005&&
                Math.abs(u-UR[r*2]!)<.25&&Math.abs(v-UR[r*2+1]!)<.25)break;
        }
        if(id===-1){id=clusters++;next[id]=head;representative[id]=i;heads.set(key,id);}
        remap[i]=id;counts[id]!++;const s=id*8;
        sums[s]!+=x;sums[s+1]!+=y;sums[s+2]!+=z;sums[s+3]!+=nx;sums[s+4]!+=ny;sums[s+5]!+=nz;sums[s+6]!+=u;sums[s+7]!+=v;
    }
    const positions=new Float32Array(clusters*3),normals=new Int16Array(clusters*4),uv=new Float32Array(clusters*2),tint=new Uint8Array(clusters*4);
    for(let id=0;id<clusters;id++){
        const s=id*8,k=counts[id]!,r=representative[id]!,length=Math.hypot(sums[s+3]!,sums[s+4]!,sums[s+5]!)||1;
        for(let a=0;a<3;a++){positions[id*3+a]=sums[s+a]!/k;normals[id*4+a]=Math.round(sums[s+3+a]!/length*ROW_SCALE);tint[id*4+a]=colors[r*4+a]!;}
        normals[id*4+3]=RR[r*4+3]!;tint[id*4+3]=255;uv[id*2]=sums[s+6]!/k;uv[id*2+1]=sums[s+7]!/k;
    }
    const indices=new Uint32Array(I.length);let count=0;
    for(let i=0;i<I.length;i+=3){const a=remap[I[i]!]!,b=remap[I[i+1]!]!,c=remap[I[i+2]!]!;if(a===b||b===c||a===c)continue;indices[count++]=a;indices[count++]=b;indices[count++]=c;}
    const g=new THREE.BufferGeometry();
    g.setAttribute('position',new THREE.BufferAttribute(positions,3));g.setAttribute('normal',new THREE.BufferAttribute(normals,4,true));
    g.setAttribute('uv',new THREE.BufferAttribute(uv,2));g.setAttribute('color',new THREE.BufferAttribute(tint,4,true));
    g.setIndex(new THREE.BufferAttribute(clusters>65535?indices.slice(0,count):Uint16Array.from(indices.subarray(0,count)),1));
    g.computeBoundingBox();g.computeBoundingSphere();return g;
}

/** Concatenate compact geometries with identical attribute layouts into one. */
export function concatCompact(parts:THREE.BufferGeometry[]):THREE.BufferGeometry {
    const out=new THREE.BufferGeometry(),first=parts[0]!;let vertices=0,indices=0;
    for(const p of parts){vertices+=p.getAttribute('position').count;indices+=p.index!.count;}
    for(const name of Object.keys(first.attributes)){
        const a=first.getAttribute(name) as THREE.BufferAttribute,array=new (a.array.constructor as new(n:number)=>THREE.TypedArray)(vertices*a.itemSize);let o=0;
        for(const p of parts){const src=(p.getAttribute(name) as THREE.BufferAttribute).array;array.set(src,o);o+=src.length;}
        out.setAttribute(name,new THREE.BufferAttribute(array,a.itemSize,a.normalized));
    }
    const index=vertices>65535?new Uint32Array(indices):new Uint16Array(indices);let o=0,base=0;
    for(const p of parts){const src=p.index!.array;for(let i=0;i<src.length;i++)index[o++]=src[i]!+base;base+=p.getAttribute('position').count;}
    out.setIndex(new THREE.BufferAttribute(index,1));out.computeBoundingBox();out.computeBoundingSphere();return out;
}
