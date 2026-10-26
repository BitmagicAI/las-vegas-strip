import * as THREE from 'three';
import type {EngineLike} from 'types/game.js';

/** One shader for every ordinary surface, whichever texture slots its asset filled (2026-10-25: the owner's
 * rule that surfaces differing only in vertex buffers and textures must not compile again).
 *
 * three keys a material's shader by which texture slots are set, so an untextured, a colour-mapped and a normal-mapped
 * standard material are three shaders (108 plain materials in view at spawn fell into seven such combinations). Here a
 * material without a colour map gets a white one and one without a normal map a flat one, so they share one shader.
 * Exact: white × colour is the colour, and a flat normal map through three's derivative tangent frame returns the
 * geometric normal (TangentUtils: the tangents are zero where the UVs have no slope). The defaults use the sampler
 * settings of nearly every map in the assets (repeat, trilinear), which are part of the key too.
 *
 * Applied when a material is first drawn (three's render-object lookup), after every load-time pass that reads texture
 * slots: city batching skips normal-mapped materials and averages colour maps, PbrDetail and SphereVisuals check them.
 * Code that reads a slot later can tell a default from a real map with `isDefaultTexture`. Skipped: bump-mapped and
 * flat-shaded materials, node materials that compute their own colour or normal, and geometry without UVs. */
function texture(data:Uint8Array|Uint16Array,type:THREE.TextureDataType,colorSpace:THREE.ColorSpace,name:string):THREE.DataTexture{
    const t=new THREE.DataTexture(data,1,1,THREE.RGBAFormat,type);
    t.colorSpace=colorSpace;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.magFilter=THREE.LinearFilter;t.minFilter=THREE.LinearMipmapLinearFilter;
    t.name=name;t.needsUpdate=true;
    // Shared by every plain material for the whole session: an unloading venue that disposes its materials' maps must not
    // destroy them (WebGPU then rejects every draw that still samples them: "Destroyed texture ... used in a submit").
    t.dispose=()=>{};
    return t;
}
const half=THREE.DataUtils.toHalfFloat;
const WHITE=texture(new Uint8Array([255,255,255,255]),THREE.UnsignedByteType,THREE.SRGBColorSpace,'Default colour (white)');
// half float, so the flat normal is exactly (0, 0, 1) after three's ×2−1 (8-bit 128 would tilt it by 1/255)
const FLAT=texture(new Uint16Array([half(.5),half(.5),half(1),half(1)]),THREE.HalfFloatType,THREE.NoColorSpace,'Default normal (flat)');

export function isDefaultTexture(t:THREE.Texture|null|undefined):boolean{return t===WHITE||t===FLAT;}

const CANONICAL=new Set(['MeshStandardMaterial','MeshPhysicalMaterial','MeshStandardNodeMaterial','MeshPhysicalNodeMaterial']);
function canonicalize(object:THREE.Object3D,material:THREE.Material):void{
    if(!CANONICAL.has(material.type))return;
    const m=material as THREE.MeshStandardMaterial&{colorNode?:unknown;normalNode?:unknown};
    if(m.flatShading||m.bumpMap||m.colorNode||m.normalNode)return;
    if(!(object as THREE.Mesh).geometry?.getAttribute('uv'))return;
    if(!m.map)m.map=WHITE;
    if(!m.normalMap)m.normalMap=FLAT;
}

/** Install before the first frame. `?canonical=off` on localhost leaves materials as loaded (A/B checks). */
export function canonicalMaterialsOnFirstDraw(engine:EngineLike):void{
    if(typeof location!=='undefined'&&['localhost','127.0.0.1'].includes(location.hostname)&&new URLSearchParams(location.search).get('canonical')==='off')return;
    const objects=(engine.renderer as unknown as {_objects?:{get:(object:THREE.Object3D,material:THREE.Material,...rest:unknown[])=>unknown}})._objects;
    if(!objects?.get)throw new Error('Unsupported three renderer: no render-object lookup to canonicalize materials at');
    const get=objects.get.bind(objects),seen=new WeakSet<THREE.Material>();
    objects.get=(object,material,...rest)=>{
        if(!seen.has(material)){seen.add(material);canonicalize(object,material);}
        return get(object,material,...rest);
    };
}
