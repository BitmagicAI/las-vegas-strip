import * as THREE from 'three';
import type {Node} from 'three/webgpu';
import {abs,cameraPosition,cameraViewMatrix,faceDirection,float,int,length,materialColor,materialRoughness,max,mix,normalWorldGeometry,normalize,positionWorld,select,sign,smoothstep,texture,uniformArray,vec2,vec3,vec4} from 'three/tsl';
import {activeDeviceQualityTier} from 'engine/quality/DeviceQuality.js';
import {PBR_PARAMS,PBR_SETS,detailSetFor} from './PbrDetailSets.js';
import {runtimeUrl} from './RuntimeAssets.js';

/**
 * Photoreal surface detail from scanned CC0 materials (Poly Haven; downloaded to build/pbr/, packed by
 * tools/pbr/pack-strips.py into three 15-layer texture arrays: albedo, normal (OpenGL), AO/roughness/metal).
 *
 * Every surface keeps its own authored colour: the scan lays its light/dark and hue variation over it (normalised by the
 * scan's mean colour, so the average stays put), plus relief, cavity AO and roughness variation, at the real-world scale
 * of the material. It is projected in world space along the surface's dominant axis (roads and roofs from above, walls
 * from the side), so it needs no UVs, and fades out between 60 and 240 m (the city LOD's near range) where the mip chain
 * has already averaged it away. Which scan a surface gets comes from its material name (PbrDetailSets.ts):
 *   - city batches (CityBatches): a column of the surface table, so thousands of facades share one shader;
 *   - every other exterior asset: when its GLB loads (`gltfUrlHooks` in GltfDecoders), as node inputs on the plain
 *     material, which three's WebGPU renderer copies into the node material it builds for it.
 * High and ultra tiers only; `?pbr=off` turns it off for A/B checks.
 */
let arrays:{albedo:THREE.DataArrayTexture;normal:THREE.DataArrayTexture;arm:THREE.DataArrayTexture}|null=null;
const P0=uniformArray(PBR_SETS.map(s=>{const p=PBR_PARAMS[s];return new THREE.Vector4(p[0],p[1],p[2],p[3]);}),'vec4');
const P1=uniformArray(PBR_SETS.map(s=>{const p=PBR_PARAMS[s];return new THREE.Vector4(p[4],p[5],0,0);}),'vec4');
const MEAN=uniformArray(PBR_SETS.map(()=>new THREE.Vector4(.5,.5,.5,0)),'vec4');

export function pbrDetailEnabled():boolean{return arrays!==null;}

async function loadStrip(url:string,size:number,colorSpace:THREE.ColorSpace,upload:(t:THREE.Texture)=>void):Promise<THREE.DataArrayTexture>{
    const layers=PBR_SETS.length;
    const bitmap=await createImageBitmap(await (await fetch(url)).blob(),{colorSpaceConversion:'none',premultiplyAlpha:'none'});
    const canvas=new OffscreenCanvas(size,size*layers),context=canvas.getContext('2d',{willReadFrequently:true})!;
    context.drawImage(bitmap,0,0);bitmap.close();
    const data=new Uint8Array(context.getImageData(0,0,size,size*layers).data.buffer);
    canvas.width=canvas.height=1;
    const t=new THREE.DataArrayTexture(data,size,size,layers);
    t.format=THREE.RGBAFormat;t.type=THREE.UnsignedByteType;t.colorSpace=colorSpace;
    t.wrapS=t.wrapT=THREE.RepeatWrapping;t.minFilter=THREE.LinearMipmapLinearFilter;t.magFilter=THREE.LinearFilter;
    t.generateMipmaps=true;t.anisotropy=8;t.name='PBR detail / '+url.split('/').pop();t.needsUpdate=true;
    // upload now and drop the 60 MB CPU copy (nothing big stays on the JS heap)
    upload(t);(t.image as {data:Uint8Array|null}).data=null;
    return t;
}

/** Load the three arrays once, before the city batches and assets build their materials. `upload` puts a texture on the
 * GPU right away (renderer.initTexture). Does nothing below the high tier or with `?pbr=off`. */
export async function loadPbrDetail(upload:(t:THREE.Texture)=>void):Promise<void>{
    if(arrays)return;
    const tier=activeDeviceQualityTier();
    if(tier!=='high'&&tier!=='ultra')return;
    if(new URLSearchParams(location.search).get('pbr')==='off')return;
    try{
        const info=await (await fetch(runtimeUrl('/build/pbr/strips/sets.json'))).json() as {size:number;sets:string[];meanLinear:number[][]};
        if(info.sets.join()!==PBR_SETS.join())throw new Error('build/pbr/strips is out of date: run python3 tools/pbr/pack-strips.py');
        const [albedo,normal,arm]=await Promise.all([
            loadStrip(runtimeUrl('/build/pbr/strips/albedo.webp'),info.size,THREE.SRGBColorSpace,upload),
            loadStrip(runtimeUrl('/build/pbr/strips/normal.webp'),info.size,THREE.NoColorSpace,upload),
            loadStrip(runtimeUrl('/build/pbr/strips/arm.webp'),info.size,THREE.NoColorSpace,upload)]);
        info.meanLinear.forEach((m,i)=>(MEAN.array[i] as THREE.Vector4).set(m[0]!,m[1]!,m[2]!,0));
        arrays={albedo,normal,arm};
        console.info(`[PbrDetail] ${PBR_SETS.length} scanned materials at ${info.size}px`);
    }catch(error){console.warn('[PbrDetail] scanned materials unavailable; surfaces stay as authored',error);}
}

export interface DetailNodes {color:Node<'vec3'>;roughness:Node<'float'>;normal:Node<'vec3'>;ao:Node<'float'>}

const LUMA=vec3(.2126,.7152,.0722);
/** The detail for a surface: `set` is an int node (an index into PBR_SETS, -1 for none), `base` its colour and
 * `roughness` its roughness. `normal` is in view space (a material's normalNode). */
export function detailNodes(set:Node<'int'>,base:Node<'vec3'>,roughness:Node<'float'>):DetailNodes{
    const a=arrays!;
    const has=set.greaterThanEqual(int(0)),layer=max(set as unknown as Node<"float">,int(0) as unknown as Node<"float">) as unknown as Node<"int">;
    const p0=P0.element(layer) as unknown as Node<'vec4'>,p1=P1.element(layer) as unknown as Node<'vec4'>,mean=(MEAN.element(layer) as unknown as Node<'vec4'>).xyz;
    // dominant-axis world projection; tangent frames are right-handed with green = up on walls (OpenGL normal maps)
    const n=normalWorldGeometry,an=abs(n),p=positionWorld;
    const top=an.y.greaterThan(max(an.x,an.z)),alongX=an.x.greaterThan(an.z);
    const sy=sign(n.y),sx=sign(n.x),sz=sign(n.z);
    const uv=select(top,vec2(p.x.mul(sy),p.z),select(alongX,vec2(p.z.mul(sx).negate(),p.y.negate()),vec2(p.x.mul(sz),p.y.negate()))).div(p0.x).toVar();
    const T=select(top,vec3(sy,0,0),select(alongX,vec3(0,0,sx.negate()),vec3(sz,0,0)));
    const B=select(top,vec3(0,0,-1),vec3(0,1,0));
    const fade=select(has,float(1).sub(smoothstep(60,240,length(p.sub(cameraPosition)))),float(0)).toVar();
    const albedo=texture(a.albedo,uv).depth(layer).rgb.toVar();
    const tangent=texture(a.normal,uv).depth(layer).rgb.mul(2).sub(1).toVar();
    const arm=texture(a.arm,uv).depth(layer).rgb.toVar();
    // colour: the scan's variation around its mean laid over the surface's own colour, plus a share of the scan's own
    // colour at the surface's brightness
    const varied=base.mul(mix(vec3(1),albedo.div(max(mean,vec3(.02))),p0.z.mul(fade)));
    const scan=albedo.mul(base.dot(LUMA).div(max(mean.dot(LUMA),.02)));
    const color=mix(varied,scan,p0.y.mul(fade));
    // relief: perturb the geometric normal (flipped on back faces) along the projection's axes
    const s=p0.w.mul(fade);
    const world=normalize(T.mul(tangent.x.mul(s)).add(B.mul(tangent.y.mul(s))).add(n.mul(max(tangent.z,.2)))).mul(faceDirection);
    return {
        color:color as unknown as Node<'vec3'>,
        roughness:mix(roughness,arm.g,p1.x.mul(fade)) as unknown as Node<'float'>,
        normal:cameraViewMatrix.mul(vec4(world,0)).xyz.normalize() as unknown as Node<'vec3'>,
        ao:mix(float(1),arm.r,p1.y.mul(fade)) as unknown as Node<'float'>,
    };
}

/** Assets loaded whole (not through the city batches) whose surfaces get no detail: interiors, hotel modules, people,
 * vehicles and foliage keep their authored look. */
const SKIP_URL=/interior|lobby|\/hotels\/|\/interiors\/|vehicle|foliage|character|uthana|player|npc/i;
const done=new WeakSet<THREE.Material>();

/** Give the opaque standard materials of a just-loaded exterior asset their scanned detail (by material name). The
 * material stays a plain MeshStandardMaterial for all game code; the node inputs only reach the WebGPU renderer, and one
 * shader serves every material on the same scan (`customProgramCacheKey`), since colour, maps and roughness come from
 * the material's own properties. */
export function applyPbrDetail(root:THREE.Object3D,url:string):void{
    if(!arrays||SKIP_URL.test(url))return;
    root.traverse(o=>{
        if(!(o instanceof THREE.Mesh)||o instanceof THREE.SkinnedMesh)return;
        for(const m of Array.isArray(o.material)?o.material:[o.material]){
            if(done.has(m))continue;done.add(m);
            if(!(m instanceof THREE.MeshStandardMaterial)||(m as {isNodeMaterial?:boolean}).isNodeMaterial||m.transparent||m.alphaTest>0||m.opacity<1)continue;
            const set=detailSetFor(m.name);if(set<0)continue;
            const d=detailNodes(int(set) as unknown as Node<'int'>,materialColor.rgb as unknown as Node<'vec3'>,materialRoughness as unknown as Node<'float'>);
            const target=m as unknown as Record<string,unknown>;
            target.colorNode=vec4(d.color,(materialColor as unknown as Node<'vec4'>).a);target.roughnessNode=d.roughness;
            if(!m.normalMap&&!m.bumpMap)target.normalNode=d.normal;
            if(!m.aoMap)target.aoNode=d.ao;
            const key='pbr-detail:'+set+(m.normalMap||m.bumpMap?':own-normal':'')+(m.aoMap?':own-ao':'');
            m.customProgramCacheKey=()=>key;
            m.userData.pbrDetail=PBR_SETS[set];m.needsUpdate=true;
        }
    });
}
