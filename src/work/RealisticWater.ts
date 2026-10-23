import {stormDrivingEnabled} from './film/SceneSurface.js';
import * as THREE from 'three';
import {MeshPhysicalNodeMaterial,NodeMaterial,RenderTarget,type LightsNode,type Renderer} from 'three/webgpu';
import {Fn,cameraPosition,cameraViewMatrix,cos,dot,float,fwidth,length,max,mix,normalize,positionWorld,pow,reflect,reflector,sin,smoothstep,texture,uniform,vec2,vec3,vec4} from 'three/tsl';
import {activeDeviceQualityTier} from 'engine/quality/DeviceQuality.js';
import {interiorLightsNode} from './InteriorLighting.js';
import {clipWaterReflection} from './WaterReflectionClip.js';

/**
 * Realistic water for every water surface the assets carry (the Bellagio lake, the resort pools and fountain basins, the
 * level's interior pools): their flat, static materials are replaced at load (GltfDecoders' parse hook) by a physical
 * water material:
 *  - moving surface: a sum of directional waves evaluated per pixel in world space (deep-water dispersion, so long waves
 *    travel faster), each wave fading out with distance before it can shimmer;
 *  - reflections: near-mirror roughness and water's specular response (ior 1.33: ~2 % straight down, mirror-like at
 *    grazing angles), so the sunset sky, the sun glint and, with the renderer's screen-space reflections, the buildings
 *    appear on it;
 *  - body colour: deep green-blue for the lake, clear turquoise for pools; a little brighter where the view looks down
 *    into it than at grazing angles.
 * Lit by the sun, sky and ambient only (a fixed list, the light-set rule): point lights add nothing visible on open water
 * and would cost the full loop on a surface that can fill the screen. Time comes from the engine's render ambience clock:
 * it keeps moving in the editor and honors the frame recorder's fixed step and inactive-tab suspension.
 */
type WaterKind='lake'|'pool'|'canal';
/** Water material names in the assets (scan of every runtime GLB, 2026-10-08). 'Strip / lake-underwater' is the basin. */
export function waterKind(name:string):WaterKind|null{
    if(/^Strip \/ lake-water$/.test(name))return 'lake';
    if(name==='Strip / canal-water')return 'canal';
    if(/^Strip \/ (paris-)?water$/.test(name)||/^(?:Strip \/ )?[a-z][a-z0-9-]*_(water|pool)$/.test(name)||name==='mirage_water')return 'pool';
    return null;
}
/** [direction x, direction z, wavelength m, amplitude m] per wave. */
const WAVES:Record<WaterKind,Float32Array>={
    // a calm lake (the owner: the first version read as aliased noise, "not like water")
    // slopes of 1-2 %: the reflected window grids stay readable, wobbling instead of scattering
    lake:Float32Array.of(1,.25,7.5,.012,-.6,1,4.2,.008,.8,-.7,2.6,.005,-.2,-1,1.55,.0032,.95,.4,.95,.002,-.85,.55,.6,.0014,.3,.95,.38,.0009),
    pool:Float32Array.of(1,.3,2.8,.012,-.5,1,1.6,.009,.7,-.8,.9,.006,-.9,-.3,.55,.004,.2,.98,.33,.0025),
    canal:Float32Array.of(.85,.31,4.7,.009,-.41,.97,2.37,.005,.71,-.63,1.13,.0027,-.92,-.27,.57,.0014,.34,.91,.29,.00065),
};
const BODY:Record<WaterKind,[THREE.ColorRepresentation,THREE.ColorRepresentation]>={lake:['#0f3c44','#1b5a62'],pool:['#0e5f6e','#2aa3b2'],canal:['#125358','#277b77']};
const waterTime=uniform(0);

/** World-space normal of the moving surface (a TSL node). */
function waveNormal(kind:WaterKind,minWavelength=0){
    return Fn(()=>{
        const p=positionWorld,dist=length(p.sub(cameraPosition));
        const dx=float(0).toVar(),dz=float(0).toVar();
        const waves=WAVES[kind];
        for(let i=0;i<waves.length;i+=4){
            const x=waves[i]!,z=waves[i+1]!,lambda=waves[i+2]!,a=waves[i+3]!;
            if(lambda!<minWavelength)continue;
            const l=Math.hypot(x!,z!),ux=x!/l,uz=z!/l,k=2*Math.PI/lambda!,omega=Math.sqrt(9.81*k);
            const phase=p.x.mul(ux*k).add(p.z.mul(uz*k)).add(waterTime.mul(omega)).add((x!*13.7+z!*5.3)%6.28);
            // fade a wave out before it gets under ~4 pixels a wavelength, measured on screen (fwidth of its phase), so
            // grazing views, where distance alone says nothing, cannot alias either; plus a gentle distance fade
            const fade=float(1).sub(smoothstep(lambda!*40,lambda!*120,dist)).mul(float(1).sub(smoothstep(.8,1.6,fwidth(phase))));
            const slope=cos(phase).mul(a!*k).mul(fade);
            dx.addAssign(slope.mul(ux));dz.addAssign(slope.mul(uz));
            // a second, crossing train of the same wave breaks up the parallel ridges
            const phase2=p.x.mul(-uz*k*.83).add(p.z.mul(ux*k*.83)).add(waterTime.mul(omega*.91)).add(1.7);
            const slope2=sin(phase2).mul(a!*k*.45).mul(fade);
            dx.addAssign(slope2.mul(-uz));dz.addAssign(slope2.mul(ux));
        }
        return normalize(vec3(dx.negate(),1,dz.negate()));
    })();
}
const sunDirection=uniform(new THREE.Vector3(.4,.2,-.9));
const sunColor=uniform(new THREE.Color(1,.7,.42));
/** The lake's planar reflection scale (of the drawing buffer); a mirrored render of the scene while the lake is in view. */
const LAKE_REFLECTION_SCALE=.5;
/** `?water=nomirror` keeps the lake on the plain water material (A/B and cost checks). */
const MIRROR_ALLOWED=typeof location==='undefined'||new URLSearchParams(location.search).get('water')!=='nomirror';

function waterMaterial(kind:WaterKind,name:string):MeshPhysicalNodeMaterial{
    const m=new MeshPhysicalNodeMaterial();
    m.name=`${name} (realistic water)`;m.userData.realisticWater=kind;
    m.roughness=kind==='lake'?.035:.025;m.metalness=0;m.ior=1.333;m.specularIntensity=1;
    const deep=new THREE.Color(BODY[kind][0]),shallow=new THREE.Color(BODY[kind][1]);
    const n=waveNormal(kind);
    m.normalNode=cameraViewMatrix.mul(vec4(n,0)).xyz.normalize();
    // looking down into the water shows more of its body; at grazing angles it is all reflection
    const view=normalize(cameraPosition.sub(positionWorld));
    m.colorNode=mix(vec3(deep.r,deep.g,deep.b),vec3(shallow.r,shallow.g,shallow.b),smoothstep(.15,.85,view.y));
    return m;
}

/** The lake: a planar mirror of the scene (the hotels, the Eiffel Tower, the sky) broken up by the waves, with water's
 * Fresnel response, the low sun's glint and a deep green-blue body. Unlit (no light list): it draws its own sun. */
function lakeMaterial(mesh:THREE.Mesh,name:string,kind:WaterKind='lake'):NodeMaterial{
    const m=new NodeMaterial();m.name=`${name} (realistic water, mirror)`;m.userData.realisticWater=kind;m.userData.mirror=true;
    const mirror=reflector({resolutionScale:LAKE_REFLECTION_SCALE});
    // the mirror plane: the lake's own surface, facing up (a child of the mesh, so it follows wherever the asset is placed)
    mesh.geometry.computeBoundingBox();const b=mesh.geometry.boundingBox!;
    mirror.target.position.set((b.min.x+b.max.x)/2,b.max.y,(b.min.z+b.max.z)/2);mirror.target.rotation.x=-Math.PI/2;mesh.add(mirror.target);
    const n=waveNormal(kind),toEye=cameraPosition.sub(positionWorld),eye=normalize(toEye);
    // the mirror image is bent by the long swell only: the ripples' slopes scattered it into a leopard pattern of the
    // reflected window grid near the camera; a reflected ray turns by twice the tilt whatever the distance, so no 1/dist
    // Screen UV displacement is only a few pixels, not several percent of the image.
    // Large offsets fold the hotel's repeated windows into rapidly changing zebra bands.
    const distortion=waveNormal(kind,2).xz.mul(kind==='canal'?.10:.12);
    const uvMirror=mirror.uvNode!.add(distortion);mirror.uvNode=uvMirror;
    // micro-ripples make the lake a slightly rough mirror: a soft 9-tap disc (3 px) instead of a razor-sharp image, so a
    // reflected tower's window grid wobbles as soft stripes rather than hard zebra bands
    const texel=uniform(new THREE.Vector2(1/1920,1/1080)),taps:{value:THREE.Texture}[]=[];
    let blurred=mirror.rgb.mul(.2);
    for(let i=0;i<8;i++){const a=i*Math.PI/4+.39,tap=texture(mirror.value,uvMirror.add(vec2(Math.cos(a)*3,Math.sin(a)*3).mul(texel)));taps.push(tap as unknown as {value:THREE.Texture});blurred=blurred.add(tap.rgb.mul(.1));}
    RealisticWater.mirrors.push({base:mirror.reflector as unknown as MirrorBase,plane:mirror.target,material:m,camera:new THREE.PerspectiveCamera(),target:null,taps,texel,kind});
    const deep=new THREE.Color(BODY[kind][0]),shallow=new THREE.Color(BODY[kind][1]);
    m.colorNode=Fn(()=>{
        const cosT=max(dot(eye,n),0);
        // Air/water Fresnel: about 2% head-on, approaching a mirror at grazing angles.
        const reflectance=mix(float(.0204),float(1),pow(float(1).sub(cosT),5));
        const glint=pow(max(dot(eye,reflect(sunDirection.negate(),n)),0),128).mul(sunColor).mul(2);
        const body=mix(vec3(deep.r,deep.g,deep.b),vec3(shallow.r,shallow.g,shallow.b),smoothstep(.12,.85,eye.y)).mul(float(.55).add(max(dot(sunDirection,n),0).mul(.35)));
        return mix(body,blurred.add(glint),reflectance);
    })();
    return m;
}

interface MirrorBase {updateBefore:(frame:unknown)=>unknown;textureNode:{value:THREE.Texture}}
interface Mirror {kind:WaterKind;base:MirrorBase;plane:THREE.Object3D;material:THREE.Material;camera:THREE.PerspectiveCamera;target:RenderTarget|null;
    /** the blur's extra samples of the mirror image, and the size of one of its texels */
    taps:{value:THREE.Texture}[];texel:{value:THREE.Vector2}}
/** Meshes lying wholly below a mirrored water surface (the lake bed): seen by the view camera, skipped by the mirror. */
export const BELOW_WATER_LAYER=3;
const _p=new THREE.Vector3(),_n=new THREE.Vector3(),_c=new THREE.Vector3(),_look=new THREE.Vector3(),_t=new THREE.Vector3(),_m=new THREE.Matrix4(),_size=new THREE.Vector2();
/** How far the mirror renders (m): the reflected skyline beyond it is the sky, which the clear colour already gives. Cuts the
 * mirror pass's draw calls roughly in half at the sanctuary. */
const MIRROR_FAR=1400;
const reflectPoint=(q:THREE.Vector3)=>q.addScaledVector(_n,-2*_t.subVectors(q,_p).dot(_n));

/** The mirror image for the view camera, rendered by hand: three's ReflectorNode bends the near plane onto the water with
 * a projection trick that assumes a standard depth buffer, and this game renders with a reversed one (SkylineDepth), which
 * clips away everything. Both lakes and canals use a reversed-depth-aware oblique clip plane, so bank undersides
 * and submerged hardware cannot leak into the mirrored scene. The sun's shadow map is not re-rendered. */
function renderMirror(mirror:Mirror,frame:{renderer:Renderer;scene:THREE.Scene;camera:THREE.Camera}):void{
    const {renderer,scene,camera}=frame;
    _m.extractRotation(mirror.plane.matrixWorld);_n.set(0,0,1).applyMatrix4(_m).normalize();_p.setFromMatrixPosition(mirror.plane.matrixWorld);
    _c.setFromMatrixPosition(camera.matrixWorld);
    if(_t.subVectors(_c,_p).dot(_n)<=0)return;   // under the water: nothing to mirror
    const v=mirror.camera;
    v.copy(camera as THREE.PerspectiveCamera,false);
    // Camera.copy omits this flag in r185; set it before editing the projection,
    // otherwise Renderer silently rebuilds the matrix and loses our clipping plane.
    Reflect.set(v,'_reversedDepth',camera.reversedDepth);
    // reflect the eye, the point it looks at and its up vector across the plane
    _look.set(0,0,-1).applyMatrix4(_m.extractRotation(camera.matrixWorld)).add(_c);
    v.position.copy(_c);reflectPoint(v.position);
    v.up.set(0,1,0).applyMatrix4(_m).reflect(_n);
    v.lookAt(reflectPoint(_look));
    // same lens (so the image lines up with the view), shorter range: x/y of the projection do not depend on the far plane
    v.far=Math.min(v.far,mirror.kind==='canal'?650:MIRROR_FAR);v.updateProjectionMatrix();v.updateMatrixWorld();
    clipWaterReflection(v,_p.y+.015);
    v.layers.mask=camera.layers.mask&~(1<<BELOW_WATER_LAYER);
    renderer.getDrawingBufferSize(_size);
    // full resolution while filming (every frame is a final frame), half in play
    const scale=RealisticWater.everyFrame?1:LAKE_REFLECTION_SCALE;
    const w=Math.max(1,Math.round(_size.x*scale)),h=Math.max(1,Math.round(_size.y*scale));
    if(!mirror.target){
        mirror.target=new RenderTarget(w,h,{type:THREE.HalfFloatType,samples:4});
        mirror.target.texture.name='Lake mirror';
        mirror.target.texture.generateMipmaps=true;
        mirror.target.texture.minFilter=THREE.LinearMipmapLinearFilter;
    }
    else if(mirror.target.width!==w||mirror.target.height!==h)mirror.target.setSize(w,h);
    const shadow=RealisticWater.sunShadow(),auto=shadow?.autoUpdate,needs=shadow?.needsUpdate;
    if(shadow){shadow.autoUpdate=false;shadow.needsUpdate=false;}
    const rt=renderer.getRenderTarget(),mrt=renderer.getMRT(),autoClear=renderer.autoClear;
    mirror.material.visible=false;
    try{
        renderer.setMRT(null);renderer.setRenderTarget(mirror.target);renderer.autoClear=true;
        renderer.render(scene,v);
    }finally{
        renderer.setMRT(mrt);renderer.setRenderTarget(rt);renderer.autoClear=autoClear;mirror.material.visible=true;
        if(shadow){shadow.autoUpdate=auto!;shadow.needsUpdate=needs!;}
    }
    mirror.base.textureNode.value=mirror.target.texture;
    for(const tap of mirror.taps)tap.value=mirror.target.texture;
    mirror.texel.value.set(1/w,1/h);
    RealisticWater.reflectionFrames++;
}

export class RealisticWater {
    /** Lake mirrors, rendered by renderMirror for the view camera only. */
    static mirrors:Mirror[]=[];
    static sunShadow():THREE.DirectionalLightShadow|null{return RealisticWater.sun?.shadow??null;}
    private static patched=new WeakSet<object>();
    private static sun:THREE.DirectionalLight|null=null;
    /** The main view camera (the only one the lake mirrors for). */
    static camera:THREE.Camera|null=null;
    /** Full-resolution reflections for filming. Play/editor still refresh every displayed frame. */
    static everyFrame=false;
    static frame=0;
    static reflectionFrames=0;
    static get time():number{return waterTime.value;}
    private static materials:MeshPhysicalNodeMaterial[]=[];
    private static outdoorLights:LightsNode|null=null;
    static converted=0;
    /** Replace the water materials under `root` (each loaded asset gets its own instances, so an interior's light list
     * never reaches the lake). Called for every parsed GLB. */
    static adopt(root:THREE.Object3D):void{
        let mine:Map<string,MeshPhysicalNodeMaterial>|null=null;let lakeTop:number|null=null;
        root.traverse(o=>{
            if(!(o instanceof THREE.Mesh))return;
            const swap=(src:THREE.Material):THREE.Material=>{
                const kind=waterKind(src.name);if(!kind)return src;
                RealisticWater.converted++;
                // the lake mirrors the scene on the ultra tier (an extra, half-resolution render while it is in view)
                if((kind==='lake'||kind==='canal')&&MIRROR_ALLOWED&&!stormDrivingEnabled()&&activeDeviceQualityTier()==='ultra'){
                    src.dispose();root.updateMatrixWorld(true);const top=new THREE.Box3().setFromObject(o).max.y;lakeTop=lakeTop===null?top:Math.max(lakeTop,top);
                    return lakeMaterial(o,src.name,kind);
                }
                mine??=new Map();let w=mine.get(src.name);
                if(!w){w=waterMaterial(kind,src.name);mine.set(src.name,w);RealisticWater.materials.push(w);src.dispose();}
                o.receiveShadow=true;return w;
            };
            o.material=Array.isArray(o.material)?o.material.map(swap):swap(o.material);
        });
        if(lakeTop!==null){
            const box=new THREE.Box3();let n=0;
            root.traverse(o=>{if(o instanceof THREE.Mesh&&!(o.material as THREE.Material).userData?.mirror&&box.setFromObject(o).max.y<=lakeTop!+.02){o.layers.set(BELOW_WATER_LAYER);n++;}});
            console.info(`[RealisticWater] lake mirror; ${n} meshes below the water are left out of the reflection`);
        }
    }
    /** Once before rendering, with absolute ambience seconds (not the paused simulation delta). */
    static update(time:number,scene:THREE.Scene|null,camera:THREE.Camera|null=null):void{
        waterTime.value=time;RealisticWater.camera=camera;RealisticWater.frame++;
        if(scene&&!RealisticWater.sun){
            const sun=scene.getObjectByName('Afterlight focused sun');
            if(sun instanceof THREE.DirectionalLight){
                RealisticWater.sun=sun;
                sunDirection.value.subVectors(sun.position,sun.target.position).normalize();
                sunColor.value.copy(sun.color).multiplyScalar(Math.max(.4,sun.intensity));
            }
        }
        // the view camera sees the lake bed; the mirror camera does not
        if(camera&&RealisticWater.mirrors.length)camera.layers.enable(BELOW_WATER_LAYER);
        for(const mirror of RealisticWater.mirrors){
            // static level parents are not re-walked by the scene's matrix update: keep the plane's world matrix current
            mirror.plane.updateWorldMatrix(true,false);
            if(RealisticWater.patched.has(mirror.base))continue;RealisticWater.patched.add(mirror.base);
            // only the view camera gets a mirror (another camera, such as the sun's shadow camera, would swap the texture)
            mirror.base.updateBefore=(frame:unknown)=>{
                const f=frame as {renderer:Renderer;scene:THREE.Scene;camera:THREE.Camera};
                // screenUV samples an image from this exact camera pose. Reusing the previous
                // image on alternate frames makes it jump whenever the camera turns or moves.
                if(f.camera===RealisticWater.camera)renderMirror(mirror,f);
                return undefined;
            };
        }
        // pools reflect the actual sky at full strength (the scene's environment light is kept dim on purpose)
        if(scene?.environment)for(const m of RealisticWater.materials)if(!m.envMap){m.envMap=scene.environment;m.envMapIntensity=1.35;m.needsUpdate=true;}
        if(scene&&RealisticWater.materials.length){
            // sun, sky and ambient (a fixed list), once the focused sun exists; interiors may have set their own
            if(!RealisticWater.outdoorLights&&scene.getObjectByName('Afterlight focused sun'))RealisticWater.outdoorLights=interiorLightsNode(scene,[]);
            const node=RealisticWater.outdoorLights;
            if(node)for(const m of RealisticWater.materials)if(!m.lightsNode){m.lightsNode=node;m.needsUpdate=true;}
        }
    }
}
