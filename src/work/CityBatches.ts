import * as THREE from 'three';
import {applySceneSurface,cinematicSurfaceEnabled,sceneSurfaceKind,setSceneSurfaceRow} from './film/SceneSurface.js';
import {MeshStandardNodeMaterial,type Node} from 'three/webgpu';
import {attribute,texture,textureLoad,uv,vec2,ivec2,int,dFdx,dFdy,vertexStage,sRGBTransferEOTF} from 'three/tsl';
import {makeCityAtlas,type Atlas} from './CityAtlas.js';
import {bindCityLighting} from './CityLighting.js';
import {releaseAfterUpload} from './CpuGeometryRelease.js';
import {detailNodes,pbrDetailEnabled} from './PbrDetail.js';
import {drawnTexture} from './ShaderSharing.js';
import {detailSetFor} from './PbrDetailSets.js';

/* Vertex layout of every city batch (32 bytes a vertex, 40 when glossy; was 88):
 *   position       float32 ×3   world metres; float keeps seams and grounding exact
 *   normal         snorm8  ×3   padded to 4 bytes on upload; float32 for glossy/metal buckets
 *   uv             float32 ×2   source UVs; tiling repeats need float range
 *   color          unorm8  ×4   sRGB-encoded material × vertex colour, decoded per vertex
 *   batchMaterial  float32 ×1   row of the shared surface table below
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

const row=int(attribute<'float'>('batchMaterial','float'));
const surface=vertexStage(textureLoad(citySurfaceTable,ivec2(0,row),int(0)));
const emission=vertexStage(textureLoad(citySurfaceTable,ivec2(1,row),int(0)));
const atlasRect=vertexStage(textureLoad(citySurfaceTable,ivec2(2,row),int(0)));
const linearColor=vertexStage(sRGBTransferEOTF(attribute<'vec4'>('color','vec4').rgb)) as unknown as Node<'vec3'>;

const srgbLut=new Float32Array(256);for(let i=0;i<256;i++){const v=i/255;srgbLut[i]=v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4);}
function toSrgb8(linear:number):number {const c=Math.min(1,Math.max(0,linear));return Math.round((c<=.0031308?c*12.92:1.055*Math.pow(c,1/2.4)-.055)*255);}

/** Texture-average colour per part, so the coarse LOD keeps each building's palette. */
const lowColors=new WeakMap<THREE.BufferGeometry,{starts:Uint32Array;tint:Float32Array}>();
const mapColors=new WeakMap<THREE.Texture,THREE.Color>();
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

const _p=new THREE.Vector3(),_n=new THREE.Vector3(),_uv=new THREE.Vector2(),_normalMatrix=new THREE.Matrix3();
interface Part {mesh:THREE.Mesh;material:THREE.MeshStandardMaterial;map:THREE.Texture|null}

/** Keep texture/normal-map and transparency pipelines distinct. Within a
 * pipeline, colour, emission and PBR factors are table rows, not draw calls.
 * Merged source meshes are removed from their parents. */
export function batchStaticMeshes(meshes:THREE.Mesh[],name:string):THREE.Group {
    const root=new THREE.Group();root.name=name;
    const buckets=new Map<string,{material:THREE.MeshStandardMaterial;parts:Part[];shadow:boolean;receive:boolean;mask:number}>();
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
        let b=buckets.get(key);if(!b){b={material:m,parts:[],shadow:mesh.castShadow,receive:mesh.receiveShadow,mask:mesh.layers.mask};buckets.set(key,b);}
        b.parts.push({mesh,material:m,map:m.map});
    }
    for(const [key,b] of buckets){
        const maps=b.parts.map(p=>p.map);
        const materialKey=key+'|'+[...new Set(maps.map(m=>m?.uuid??'white'))].sort().join(',');
        let shared=sharedMaterials.get(materialKey);
        const atlas=shared?.atlas??makeCityAtlas(maps);
        // 8-bit normals are ~0.4 degrees off: invisible on matte facades, visible in
        // glossy reflections, so glossy or metal buckets keep float normals. (snorm16
        // normals render camouflage blotches on three r185 WebGPU: the Paris balloon.)
        const precise=b.parts.some(p=>p.material.roughness<.3||p.material.metalness>.5);
        let vertices=0,indices=0;for(const p of b.parts){const g=p.mesh.geometry,n=g.getAttribute('position').count;vertices+=n;indices+=g.index?g.index.count:n;}
        const positions=new Float32Array(vertices*3),normals=precise?new Float32Array(vertices*3):new Int8Array(vertices*3),uvs=new Float32Array(vertices*2),colors=new Uint8Array(vertices*4),rows=new Float32Array(vertices);
        const index=vertices>65535?new Uint32Array(indices):new Uint16Array(indices),scale=precise?1:127;
        const starts=new Uint32Array(b.parts.length+1),tint=new Float32Array(b.parts.length*3);
        let v=0,ix=0;
        b.parts.forEach((p,partIndex)=>{
            const g=p.mesh.geometry,m=p.material,position=g.getAttribute('position') as THREE.BufferAttribute,count=position.count;
            let normal=g.getAttribute('normal') as THREE.BufferAttribute|undefined,computed:THREE.BufferGeometry|null=null;
            if(!normal){computed=g.clone();computed.computeVertexNormals();normal=computed.getAttribute('normal') as THREE.BufferAttribute;}
            const sourceUv=g.getAttribute('uv') as THREE.BufferAttribute|undefined,old=m.vertexColors?g.getAttribute('color') as THREE.BufferAttribute|undefined:undefined,matrix=p.mesh.matrixWorld;
            _normalMatrix.getNormalMatrix(matrix);
            // Bake the source map's UV transform so equivalent material clones can
            // batch without changing tiling or the colour space of their textures.
            const uvMatrix=p.map?(p.map.updateMatrix(),p.map.matrix):null,flip=!!p.map?.flipY;
            const rect=atlas?.rects.get(p.map)??[0,0,1,1],materialRow=surfaceRow(m,p.map,rect);
            const average=averageMapColor(p.map);starts[partIndex]=v;tint[partIndex*3]=average.r;tint[partIndex*3+1]=average.g;tint[partIndex*3+2]=average.b;
            for(let i=0;i<count;i++,v++){
                _p.fromBufferAttribute(position,i).applyMatrix4(matrix);positions[v*3]=_p.x;positions[v*3+1]=_p.y;positions[v*3+2]=_p.z;
                _n.fromBufferAttribute(normal,i).applyMatrix3(_normalMatrix).normalize();normals[v*3]=precise?_n.x:Math.round(_n.x*scale);normals[v*3+1]=precise?_n.y:Math.round(_n.y*scale);normals[v*3+2]=precise?_n.z:Math.round(_n.z*scale);
                if(sourceUv){_uv.fromBufferAttribute(sourceUv,i);if(uvMatrix){_uv.applyMatrix3(uvMatrix);if(flip)_uv.y=1-_uv.y;}uvs[v*2]=_uv.x;uvs[v*2+1]=_uv.y;}
                colors[v*4]=toSrgb8(m.color.r*(old?old.getX(i):1));colors[v*4+1]=toSrgb8(m.color.g*(old?old.getY(i):1));colors[v*4+2]=toSrgb8(m.color.b*(old?old.getZ(i):1));colors[v*4+3]=255;
                rows[v]=materialRow;
            }
            const base=v-count;
            if(g.index)for(let j=0;j<g.index.count;j++)index[ix++]=g.index.getX(j)+base;
            else for(let j=0;j<count;j++)index[ix++]=base+j;
            computed?.dispose();p.mesh.removeFromParent();
        });
        starts[b.parts.length]=v;
        const geometry=new THREE.BufferGeometry();
        geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.setAttribute('normal',new THREE.BufferAttribute(normals,3,!precise));
        geometry.setAttribute('uv',new THREE.BufferAttribute(uvs,2));geometry.setAttribute('color',new THREE.BufferAttribute(colors,4,true));geometry.setAttribute('batchMaterial',new THREE.BufferAttribute(rows,1));
        geometry.setIndex(new THREE.BufferAttribute(index,1));geometry.computeBoundingBox();geometry.computeBoundingSphere();
        lowColors.set(geometry,{starts,tint});
        let material:MeshStandardNodeMaterial;
        if(shared){shared.references++;material=shared.material;}else{
            material=surfaceMaterial(b.material,atlas);
            shared={material,atlas,references:1};sharedMaterials.set(materialKey,shared);materialKeys.set(material,materialKey);
        }
        const mesh=new THREE.Mesh(geometry,material);mesh.name=name+' / surface '+root.children.length;mesh.castShadow=b.shadow;mesh.receiveShadow=b.receive;mesh.layers.mask=b.mask;mesh.matrixAutoUpdate=false;bindCityLighting(mesh);root.add(mesh);
        releaseAfterUpload(geometry);
    }
    return root;
}

/** The coarse (silhouette) version of a batch: vertex clustering keeps the surveyed
 * envelope, roofs and setbacks; colours are tinted by each part's texture average.
 * Built once while loading from the batch's arrays, so call it before the batch is
 * drawn (its CPU arrays are released after upload). `spacing` null keeps every vertex. */
export function coarseFromBatch(batch:THREE.BufferGeometry,spacing:number|null):THREE.BufferGeometry {
    const P=batch.getAttribute('position').array as Float32Array,C=batch.getAttribute('color').array as Uint8Array,R=batch.getAttribute('batchMaterial').array as Float32Array,I=batch.index!.array;
    const n=P.length/3,low=lowColors.get(batch);
    // Linear vertex colour × texture average of the part it came from.
    const linear=new Float32Array(n*3);
    for(let part=0,v=0;v<n;v++){
        if(low)while(v>=low.starts[part+1]!)part++;
        const t=low?part*3:-1;
        linear[v*3]=srgbLut[C[v*4]!]!*(low?low.tint[t]!:1);linear[v*3+1]=srgbLut[C[v*4+1]!]!*(low?low.tint[t+1]!:1);linear[v*3+2]=srgbLut[C[v*4+2]!]!*(low?low.tint[t+2]!:1);
    }
    let remap:Uint32Array,clusters:number,cp:Float32Array,cc:Float32Array,cr:Float32Array;
    if(spacing===null){remap=new Uint32Array(n);for(let i=0;i<n;i++)remap[i]=i;clusters=n;cp=P.slice();cc=linear;cr=R.slice();}
    else{
        // Numeric cell keys (15 bits an axis): no string keys, no per-cell arrays.
        const cells=new Map<number,number>(),sums=new Float64Array(n*6),counts=new Uint32Array(n);remap=new Uint32Array(n);cr=new Float32Array(n);clusters=0;
        for(let i=0;i<n;i++){
            const key=((Math.round(P[i*3]!/spacing)+16384)*32768+(Math.round(P[i*3+1]!/spacing)+16384))*32768+(Math.round(P[i*3+2]!/spacing)+16384);
            let id=cells.get(key);if(id===undefined){id=clusters++;cells.set(key,id);cr[id]=R[i]!;}
            remap[i]=id;counts[id]!++;const s=id*6;sums[s]!+=P[i*3]!;sums[s+1]!+=P[i*3+1]!;sums[s+2]!+=P[i*3+2]!;sums[s+3]!+=linear[i*3]!;sums[s+4]!+=linear[i*3+1]!;sums[s+5]!+=linear[i*3+2]!;
        }
        cp=new Float32Array(clusters*3);cc=new Float32Array(clusters*3);cr=cr.slice(0,clusters);
        for(let id=0;id<clusters;id++){const k=counts[id]!,s=id*6;cp[id*3]=sums[s]!/k;cp[id*3+1]=sums[s+1]!/k;cp[id*3+2]=sums[s+2]!/k;cc[id*3]=sums[s+3]!/k;cc[id*3+1]=sums[s+4]!/k;cc[id*3+2]=sums[s+5]!/k;}
    }
    // Remap triangles; drop degenerate ones and exact duplicates (hash check, exact compare).
    const out=new Uint32Array(I.length);let t=0;const seen=new Map<number,number>();
    for(let i=0;i+2<I.length;i+=3){
        let a=remap[I[i]!]!,b=remap[I[i+1]!]!,c=remap[I[i+2]!]!;if(a===b||b===c||a===c)continue;
        if(spacing!==null){const x=Math.min(a,b,c),z=Math.max(a,b,c),y=a+b+c-x-z;
            const h=(Math.imul(x,73856093)^Math.imul(y,19349663)^Math.imul(z,83492791))>>>0,prev=seen.get(h);
            if(prev!==undefined){const qa=out[prev]!,qb=out[prev+1]!,qc=out[prev+2]!,qx=Math.min(qa,qb,qc),qz=Math.max(qa,qb,qc);if(qx===x&&qz===z&&qa+qb+qc-qx-qz===y)continue;}else seen.set(h,t);}
        out[t++]=a;out[t++]=b;out[t++]=c;
    }
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(cp,3));
    g.setIndex(new THREE.BufferAttribute(clusters>65535?out.slice(0,t):Uint16Array.from(out.subarray(0,t)),1));
    g.computeVertexNormals();const fn=g.getAttribute('normal').array as Float32Array,normals=new Int8Array(fn.length);for(let i=0;i<fn.length;i++)normals[i]=Math.round(fn[i]!*127);
    g.setAttribute('normal',new THREE.BufferAttribute(normals,3,true));
    const colors=new Uint8Array(clusters*4);for(let i=0;i<clusters;i++){colors[i*4]=toSrgb8(cc[i*3]!);colors[i*4+1]=toSrgb8(cc[i*3+1]!);colors[i*4+2]=toSrgb8(cc[i*3+2]!);colors[i*4+3]=255;}
    g.setAttribute('color',new THREE.BufferAttribute(colors,4,true));g.setAttribute('batchMaterial',new THREE.BufferAttribute(cr,1));
    g.computeBoundingBox();g.computeBoundingSphere();return g;
}

/** Architectural LOD, built before upload. Never merge stone with glass/trim, or
 * average a facade texture into a flat colour. Keep UVs, hard edges and the source
 * normals (recomputing them rounds flat walls and changes their lighting). Small
 * coplanar details can collapse, while the surviving surfaces use the full shader.
 * Numeric spatial keys and typed linked lists avoid a JS object per vertex. */
export function facadeFromBatch(batch:THREE.BufferGeometry,spacing:number|null):THREE.BufferGeometry {
    if(spacing===null)return batch.clone();
    const P=batch.getAttribute('position') as THREE.BufferAttribute,N=batch.getAttribute('normal') as THREE.BufferAttribute;
    const C=batch.getAttribute('color') as THREE.BufferAttribute,U=batch.getAttribute('uv') as THREE.BufferAttribute,R=batch.getAttribute('batchMaterial') as THREE.BufferAttribute;
    const colors=C.array as Uint8Array,n=P.count,I=batch.index!.array;
    const heads=new Map<number,number>(),next=new Int32Array(n),representative=new Uint32Array(n),remap=new Uint32Array(n);
    const sums=new Float64Array(n*8),counts=new Uint32Array(n);let clusters=0;
    for(let i=0;i<n;i++){
        const x=P.getX(i),y=P.getY(i),z=P.getZ(i),nx=N.getX(i),ny=N.getY(i),nz=N.getZ(i),u=U.getX(i),v=U.getY(i),row=R.getX(i),ci=i*4;
        const key=((Math.round(x/spacing)+16384)*32768+(Math.round(y/spacing)+16384))*32768+(Math.round(z/spacing)+16384);
        const head=heads.get(key)??-1;let id=head;
        for(;id!==-1;id=next[id]!){
            const r=representative[id]!,rc=r*4;
            if(R.getX(r)===row&&colors[ci]===colors[rc]&&colors[ci+1]===colors[rc+1]&&colors[ci+2]===colors[rc+2]&&
                nx*N.getX(r)+ny*N.getY(r)+nz*N.getZ(r)>.98&&
                // Parallel planes can have the same finish: merging a wall with
                // its projecting trim pushes the wall through the glazing.
                Math.abs((x-P.getX(r))*nx+(y-P.getY(r))*ny+(z-P.getZ(r))*nz)<.005&&
                Math.abs(u-U.getX(r))<.25&&Math.abs(v-U.getY(r))<.25)break;
        }
        if(id===-1){id=clusters++;next[id]=head;representative[id]=i;heads.set(key,id);}
        remap[i]=id;counts[id]!++;const s=id*8;
        sums[s]!+=x;sums[s+1]!+=y;sums[s+2]!+=z;sums[s+3]!+=nx;sums[s+4]!+=ny;sums[s+5]!+=nz;sums[s+6]!+=u;sums[s+7]!+=v;
    }
    const positions=new Float32Array(clusters*3),normals=N.array instanceof Float32Array?new Float32Array(clusters*3):new Int8Array(clusters*3);
    const uv=new Float32Array(clusters*2),tint=new Uint8Array(clusters*4),rows=new Float32Array(clusters),precise=normals instanceof Float32Array;
    for(let id=0;id<clusters;id++){
        const s=id*8,k=counts[id]!,r=representative[id]!,length=Math.hypot(sums[s+3]!,sums[s+4]!,sums[s+5]!)||1;
        for(let a=0;a<3;a++){positions[id*3+a]=sums[s+a]!/k;const value=sums[s+3+a]!/length;normals[id*3+a]=precise?value:Math.round(value*127);tint[id*4+a]=colors[r*4+a]!;}
        tint[id*4+3]=255;uv[id*2]=sums[s+6]!/k;uv[id*2+1]=sums[s+7]!/k;rows[id]=R.getX(r);
    }
    const indices=new Uint32Array(I.length);let count=0;
    for(let i=0;i<I.length;i+=3){const a=remap[I[i]!]!,b=remap[I[i+1]!]!,c=remap[I[i+2]!]!;if(a===b||b===c||a===c)continue;indices[count++]=a;indices[count++]=b;indices[count++]=c;}
    const g=new THREE.BufferGeometry();
    g.setAttribute('position',new THREE.BufferAttribute(positions,3));g.setAttribute('normal',new THREE.BufferAttribute(normals,3,!precise));
    g.setAttribute('uv',new THREE.BufferAttribute(uv,2));g.setAttribute('color',new THREE.BufferAttribute(tint,4,true));g.setAttribute('batchMaterial',new THREE.BufferAttribute(rows,1));
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
