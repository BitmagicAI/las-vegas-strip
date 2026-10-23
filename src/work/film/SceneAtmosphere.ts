import {limitStormResolution} from './SceneResolution.js';
import {ownSceneFrame} from './ScenePose.js';
import SSRNode from 'three/addons/tsl/display/SSRNode.js';
import {stormDrivingEnabled} from './SceneSurface.js';
import * as THREE from 'three';
import type {GameEngine} from 'engine/GameEngine.js';
import type {ResolvedBloomConfig} from 'engine/core/PostFxPipeline.js';
import type {WeatherConfig} from 'types/game.js';
import {RainHeightField} from 'engine/world/weather/RainHeightField.js';
import {RainVFXGpu,DEFAULT_RAIN_VFX_GPU_OPTIONS,type ComputeCapableRenderer} from 'engine/world/weather/RainVFXGpu.js';
import {RainVFXWebGl,DEFAULT_RAIN_VFX_WEBGL_OPTIONS} from 'engine/world/weather/RainVFXWebGl.js';
import {isWebGpuActive} from 'engine/render/backend/RendererType.js';
import {sceneWetness,sceneNeon,updateSceneSurface} from './SceneSurface.js';
import {weatherFor,type ScenePreset,type RouteKey} from './ScenePreset.js';

/** Engine internals the film borrows by name. Engine 3.1337 moved them out of GameEngine into its private post-FX owner
 * (engine/core/PostFxPipeline.ts) and weather owner (engine/world/weather/WeatherEngineBridge.ts). */
interface Internals {
    postFx:{bloomConfig:ResolvedBloomConfig|null;setBloom(config:ResolvedBloomConfig|null):void;bloomPipeline:{outputNode?:import('three/webgpu').Node}|null};
    weather:{getConfig():WeatherConfig|null;system:{dispose():void}|null};
}
const internals=(engine:GameEngine)=>engine as unknown as Internals;

const sleep=(ms:number)=>new Promise<void>(resolve=>setTimeout(resolve,ms));
function stormSky(daylight:ScenePreset['daylight']):THREE.CanvasTexture {
    const c=document.createElement('canvas');c.width=512;c.height=256;const ctx=c.getContext('2d')!,im=ctx.createImageData(c.width,c.height);
    const hash=(x:number,y:number,z:number)=>{const v=Math.sin(x*127.1+y*311.7+z*74.7)*43758.5453;return v-Math.floor(v);};
    const noise=(x:number,y:number,z:number)=>{const ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z);let X=x-ix,Y=y-iy,Z=z-iz;X=X*X*(3-2*X);Y=Y*Y*(3-2*Y);Z=Z*Z*(3-2*Z);let v=0;for(let a=0;a<2;a++)for(let b=0;b<2;b++)for(let d=0;d<2;d++)v+=hash(ix+a,iy+b,iz+d)*(a?X:1-X)*(b?Y:1-Y)*(d?Z:1-Z);return v;};
    for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){
        const a=x/c.width*Math.PI*2,b=y/c.height*Math.PI,dx=Math.sin(b)*Math.cos(a),dy=Math.cos(b),dz=Math.sin(b)*Math.sin(a);
        let cloud=0,amp=.55,f=3;for(let i=0;i<5;i++){cloud+=noise(dx*f,dy*f*.72,dz*f)*amp;f*=2.1;amp*=.49;}
        const horizon=Math.exp(-Math.abs(dy)*5),v=Math.max(0,cloud-.22),k=(y*c.width+x)*4;
        const day=daylight==='day',dusk=daylight==='dusk';
        im.data[k]=(day?75:dusk?65:24)+v*(day?130:45)+horizon*(dusk?85:14);im.data[k+1]=(day?110:dusk?55:34)+v*(day?120:53)+horizon*20;im.data[k+2]=(day?145:dusk?65:53)+v*(day?90:62)+horizon*25;im.data[k+3]=255;
    }
    ctx.putImageData(im,0,0);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.mapping=THREE.EquirectangularReflectionMapping;t.name='Local cinematic storm sky';return t;
}
/** Reversible scene-only look; uses engine rain with the mesh-level height index and film clock. */
export class SceneAtmosphere {
    private releaseResolution:(()=>void)|null=null;
    private releasePose:(()=>void)|null=null;
    private original:{background:THREE.Scene['background'];environment:THREE.Texture|null;fog:THREE.Scene['fog'];fogNode:THREE.Scene['fogNode'];environmentIntensity:number;backgroundIntensity:number;exposure:number}|null=null;
    private lights=new Map<THREE.Light,{color:THREE.Color;intensity:number}>();
    private lightStates:{light:THREE.Light;color:THREE.Color;intensity:number}[]=[];
    private skies=new Map<THREE.Object3D,boolean>();
    private sky:THREE.CanvasTexture|null=null;
    private field:RainHeightField|null=null;
    private gpu:RainVFXGpu|null=null;
    private gl:RainVFXWebGl|null=null;
    private center=new THREE.Vector3();
    private preset:ScenePreset|null=null;
    private priorWeather:WeatherConfig|null=null;
    private flash=0;
    private priorBloom:ResolvedBloomConfig|null=null;
    readonly floods:THREE.SpotLight[]=[];
    readonly lamps:THREE.PointLight[]=[];
    private bolts:THREE.LineSegments|null=null;
    private boltGeo:THREE.BufferGeometry|null=null;
    private boltMat:THREE.LineBasicMaterial|null=null;
    constructor(private engine:GameEngine,private heightAt:(x:number,z:number)=>number){
        // Allocate the light set once, before any take is warmed or compiled. Presets only change intensity.
        for(let i=0;i<8;i++){const l=new THREE.PointLight(i<2?0xc7e1ff:0xa72eff,0,i<2?42:35,2);l.name='Cinematic light '+i;this.lamps.push(l);engine.scene!.add(l);}
        for(let i=0;i<12;i++){const l=new THREE.SpotLight(i<2?0xd5e4ff:0xffc079,0,260,.45,.65,1.6);l.name='Cinematic architectural flood '+i;this.floods.push(l);engine.scene!.add(l,l.target);}
    }
    async apply(preset:ScenePreset,route:readonly RouteKey[]):Promise<void>{
        this.restore();const scene=this.engine.scene!,renderer=this.engine.renderer!;
        this.original={background:scene.background,environment:scene.environment,fog:scene.fog,fogNode:scene.fogNode,environmentIntensity:scene.environmentIntensity,backgroundIntensity:scene.backgroundIntensity,exposure:renderer.toneMappingExposure};
        this.preset=preset;const fx=internals(this.engine).postFx;this.priorBloom=fx.bloomConfig;fx.setBloom({enabled:true,strength:.34,radius:.42,threshold:1.05});this.priorWeather=internals(this.engine).weather.getConfig();
        scene.traverse(o=>{if(o instanceof THREE.Light&&!this.lamps.includes(o as THREE.PointLight)&&!this.floods.includes(o as THREE.SpotLight))this.lights.set(o,{color:o.color.clone(),intensity:o.intensity});if(/skybox/i.test(o.name)){this.skies.set(o,o.visible);if(preset.daylight!=='original')o.visible=false;}});
        for(const [light,state] of this.lights)this.lightStates.push({light,...state});
        if(preset.daylight!=='original'){
            this.sky=stormSky(preset.daylight);scene.background=this.sky;scene.environment=this.sky;scene.environmentIntensity=preset.daylight==='night'?.4:1.0;
            scene.fogNode=null;scene.fog=new THREE.FogExp2(0x080e1b,preset.weather==='storm'?.00135:.0005);renderer.toneMappingExposure=.90;
        }
        sceneWetness.value=preset.wetness;sceneNeon.value=preset.neon;
        if(preset.weather!=='clear'){
            // Public API owns SSR composition. Its stock terrain adapter only supports VXL; replace the rain owner
            // with the same engine rain components below, using this mesh level's heights and exact recording time.
            this.engine.applyWeatherConfig(weatherFor(preset));
            // Gameplay keeps puddle reflections, with a half-resolution ray-march. Capture remains full resolution.
            if(stormDrivingEnabled()){const visited=new Set<import('three/webgpu').Node>();const visit=(node:import('three/webgpu').Node)=>{if(visited.has(node))return;visited.add(node);if(node instanceof SSRNode)node.resolutionScale=.5;for(const child of node.getChildren())visit(child);};const output=internals(this.engine).postFx.bloomPipeline?.outputNode;if(output)visit(output);}
            const weather=internals(this.engine).weather;weather.system?.dispose();weather.system=null;
            this.field=new RainHeightField();let x0=Infinity,x1=-Infinity,z0=Infinity,z1=-Infinity;
            for(const p of route){x0=Math.min(x0,p.x);x1=Math.max(x1,p.x);z0=Math.min(z0,p.z);z1=Math.max(z1,p.z);}
            this.field.start({minX:x0-65,maxX:x1+65,minY:-3,maxY:200,minZ:z0-65,maxZ:z1+65});
            // Cache only this route's rain heights, so the 768² rain bake does not issue half a million scene queries.
            const W=160,H=160,heights=new Float32Array(W*H),dx=(x1-x0+130)/W,dz=(z1-z0+130)/H;
            for(let j=0;j<H;j++){for(let i=0;i<W;i++)heights[j*W+i]=this.heightAt(x0-65+(i+.5)*dx,z0-65+(j+.5)*dz);if(j%4===0)await sleep(0);}
            const cached=(x:number,z:number)=>heights[Math.max(0,Math.min(H-1,Math.floor((z-z0+65)/dz)))*W+Math.max(0,Math.min(W-1,Math.floor((x-x0+65)/dx)))]!;
            while(!this.field.isReady){this.field.step(cached);await sleep(0);}
            if(isWebGpuActive()){this.gpu=new RainVFXGpu(scene,this.field,{...DEFAULT_RAIN_VFX_GPU_OPTIONS,maxDrops:18000,radius:38,columnHeight:28,streakLength:.75,streakWidth:.012,splashSize:.13,opacity:.19});this.gpu.syncField(this.field);this.gpu.setIntensity(preset.rain);}
            else{this.gl=new RainVFXWebGl(scene,{...DEFAULT_RAIN_VFX_WEBGL_OPTIONS,maxDrops:8000});this.gl.setIntensity(preset.rain);}
        }
        this.makeLightning(route);this.update(0,0,0);
        if(stormDrivingEnabled()){this.releasePose=ownSceneFrame(scene,callback=>this.engine.registerBeforeRender(callback));this.releaseResolution=limitStormResolution(this.engine);}
    }
    private makeLightning(route:readonly RouteKey[]):void{
        const first=route[0]!,v=new Float32Array(30*6);let x=first.x-550,y=640,z=first.z-900;
        for(let i=0;i<30;i++){const j=i*6;v[j]=x;v[j+1]=y;v[j+2]=z;x+=Math.sin(i*8.31)*22;y-=15+Math.sin(i)*5;z+=Math.cos(i*3.31)*12;v[j+3]=x;v[j+4]=y;v[j+5]=z;}
        this.boltGeo=new THREE.BufferGeometry();this.boltGeo.setAttribute('position',new THREE.BufferAttribute(v,3));
        this.boltMat=new THREE.LineBasicMaterial({color:0xc5dcff,transparent:true,opacity:0,depthWrite:false,toneMapped:false});this.bolts=new THREE.LineSegments(this.boltGeo,this.boltMat);this.bolts.frustumCulled=false;this.engine.scene!.add(this.bolts);
    }
    update(t:number,dt:number,flash:number):void{
        const p=this.preset;if(!p||!this.original)return;this.flash=flash;
        const night=p.daylight==='night',day=p.daylight==='day',scene=this.engine.scene!;
        for(let i=0;i<this.lightStates.length;i++){const s=this.lightStates[i]!,l=s.light;
            if(l instanceof THREE.DirectionalLight){l.intensity=(night?.14:day?2.1:s.intensity*.55)+flash*3.0;l.color.setHex(night?0x8fa7d9:day?0xf3f4ed:0xffb776);}
            else if(l instanceof THREE.HemisphereLight||l instanceof THREE.AmbientLight){l.intensity=night?.48:day?1.6:s.intensity*.85;l.color.setHex(night?0x718bbc:0xd2dbea);}
        }
        if(p.daylight==='original')for(let i=0;i<this.lightStates.length;i++){const s=this.lightStates[i]!,l=s.light;l.color.copy(s.color);l.intensity=s.intensity;}
        scene.backgroundIntensity=(night?.32:1)+flash*2;sceneWetness.value=p.wetness;sceneNeon.value=p.neon;updateSceneSurface(t,scene.environment);
        if(this.boltMat)this.boltMat.opacity=flash;
        const cam=this.engine.camera;if(cam){cam.getWorldPosition(this.center);this.gpu?.setFrameState(this.center,5,-2);this.gpu?.computeStep(this.engine.renderer as unknown as ComputeCapableRenderer,dt,t);this.gl?.update(dt,t,this.center,5,-2,this.heightAt);}
    }
    restore():void{
        this.releasePose?.();this.releasePose=null;this.releaseResolution?.();this.releaseResolution=null;
        this.gpu?.dispose();this.gpu=null;this.gl?.dispose();this.gl=null;this.field?.dispose();this.field=null;
        this.bolts?.removeFromParent();this.bolts=null;this.boltGeo?.dispose();this.boltGeo=null;this.boltMat?.dispose();this.boltMat=null;
        if(this.original){const s=this.engine.scene!,o=this.original;this.engine.applyWeatherConfig(this.priorWeather);s.background=o.background;s.environment=o.environment;s.fog=o.fog;s.fogNode=o.fogNode;s.environmentIntensity=o.environmentIntensity;s.backgroundIntensity=o.backgroundIntensity;this.engine.renderer!.toneMappingExposure=o.exposure;}
        for(const [l,s] of this.lights){l.color.copy(s.color);l.intensity=s.intensity;}this.lights.clear();this.lightStates.length=0;for(const [o,v] of this.skies)o.visible=v;this.skies.clear();
        for(const l of this.lamps)l.intensity=0;for(const l of this.floods)l.intensity=0;if(this.original)internals(this.engine).postFx.setBloom(this.priorBloom);this.sky?.dispose();this.sky=null;this.preset=null;this.original=null;sceneWetness.value=0;sceneNeon.value=1;
    }
}
