import * as THREE from 'three';
import {MeshStandardNodeMaterial,type Node} from 'three/webgpu';
import {uniform,mix,float,textureLoad,ivec2,int,vertexStage,vec3,positionWorld,normalWorld,sin,smoothstep,vec2,normalView,normalize} from 'three/tsl';
import {createWetSurfaceMaterial,type WetSurfaceHandle} from 'engine/weather/WetSurfaceMaterial.js';

export const sceneWetness=uniform(0);
export const sceneNeon=uniform(1);
const lookRows=new Float32Array(4096*4);
const lookTable=new THREE.DataTexture(lookRows,1,4096,THREE.RGBAFormat,THREE.FloatType);
lookTable.minFilter=lookTable.magFilter=THREE.NearestFilter;lookTable.generateMipmaps=false;lookTable.needsUpdate=true;
export function sceneSurfaceKind(name:string):number{return /window|glazing|glass/i.test(name)&&!/canopy|eiffel/i.test(name)?1:/neon|display|screen|sign|emissive|lamp|letter/i.test(name)?2:0;}
export function setSceneSurfaceRow(row:number,kind:number):void{lookRows[row*4]=kind;lookTable.needsUpdate=true;}
let wet:WetSurfaceHandle|null=null;
export function stormDrivingEnabled():boolean {
    try{return ['localhost','127.0.0.1'].includes(location.hostname)&&new URLSearchParams(location.search).get('storm')==='1';}catch{return false;}
}
export function cinematicSurfaceEnabled():boolean {
    try{return (location.hostname==='localhost'||location.hostname==='127.0.0.1')&&(stormDrivingEnabled()||localStorage.getItem('afterlight:film')==='1'||new URLSearchParams(location.search).get('film')==='1');}catch{return false;}
}
/** Reuses the engine's wet-asphalt BRDF, with the city's material-row mask so facades and lawns stay dry. */
export function applySceneSurface(material:MeshStandardNodeMaterial,asphalt:Node<'float'>,row?:Node<'int'>):void {
    if(!wet){wet=createWetSurfaceMaterial({emissive:false});wet.setWetness(1);wet.setPuddles(1);wet.setRippleAmount(1);
        wet.setLook({filmGloss:.3,surfaceDarkening:.22,envSheen:.05,rippleStrength:.30});}
    const w=asphalt.mul(sceneWetness),m=wet.material as MeshStandardNodeMaterial;
    // Keep aggregate visible between localized puddles. The previous uniform low roughness made a blue mirror sheet.
    const puddle=(m.metalnessNode as Node<'float'>).sub(.12).div(.18).clamp(0,1);
    const dry=(material.roughnessNode??float(material.roughness)) as Node<'float'>;
    const damp=mix(dry.mul(.78).clamp(.40,.69),float(.12),puddle);
    material.colorNode=material.colorNode!.mul(mix(1,puddle.mul(-.18).add(.70),w));
    material.roughnessNode=mix(dry,damp,w);
    material.metalnessNode=mix((material.metalnessNode??float(material.metalness)) as Node<'float'>,puddle.mul(.08).add(.018),w);
    // Flatten only pooled water, with moving rain rings; keep scanned aggregate between pools.
    material.normalNode=normalize(mix((material.normalNode??normalView) as Node<'vec3'>,m.normalNode as Node<'vec3'>,puddle.mul(w)));
    if(material.emissiveNode)material.emissiveNode=(material.emissiveNode as Node<'vec3'>).mul(sceneNeon);
    if(row){const kind=vertexStage(textureLoad(lookTable,ivec2(0,row),int(0))).r;const window=kind.equal(1).select(1,0);
        // Existing non-luminous facade emissions are not a substitute for architectural lighting.
        material.emissiveNode=(material.emissiveNode as Node<'vec3'>).mul(mix(1,kind.equal(2).select(1,0),sceneNeon.sub(1).clamp(0,1)));
        // Window apertures leave dark spandrels, rather than illuminating arbitrary whole wall-sized squares.
        const horizontal=normalWorld.x.abs().greaterThan(.707).select(positionWorld.z,positionWorld.x);
        const grid=vec2(horizontal.div(3.5),positionWorld.y.add(.4).div(3.35)),cell=grid.floor(),uv=grid.fract();
        const aperture=smoothstep(.12,.18,uv.x).mul(float(1).sub(smoothstep(.80,.86,uv.x))).mul(smoothstep(.22,.28,uv.y)).mul(float(1).sub(smoothstep(.80,.86,uv.y)));
        const noise=sin(cell.x.mul(12.9898).add(cell.y.mul(78.233))).mul(43758.5453).fract();
        const glow=vec3(.16,.095,.04).mul(noise.greaterThan(.66).select(noise.mul(.65).add(.35),0)).mul(aperture).mul(window).mul(sceneNeon.sub(1).max(0));
        material.emissiveNode=(material.emissiveNode as Node<'vec3'>).add(glow);
    }
    material.userData.cinematicSurface=true;
}
export function updateSceneSurface(t:number,environment:THREE.Texture|null):void {wet?.setTime(t);wet?.setEnvironment(environment);}
