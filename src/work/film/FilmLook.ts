import * as THREE from 'three';
import type {GameEngine} from 'engine/GameEngine.js';
import type {GroundSurfaceIndex} from '../GroundSurfaceIndex.js';
import {SceneAtmosphere} from './SceneAtmosphere.js';
import {SceneStreetLights} from './SceneStreetLights.js';
import {SCENE_PRESETS,type ScenePreset} from './ScenePreset.js';

export interface LookRequest {preset:string;overrides?:Partial<ScenePreset>;area?:readonly number[]}

/**
 * Time of day and weather for the city: the night sky and fog, lit windows and signs (sceneNeon), wet streets
 * (sceneWetness), rain around the camera, floodlights on the Eiffel Tower, the Bellagio facade and the Paris balloon, and
 * street spill near the camera. Film takes ask for it with `look` (tools/film, src/work/film/Film.ts); a game layer can
 * reuse `atmosphere`, `streetLights` and `architectureFloods` for its own scenes. Every light is allocated in the
 * constructor and presets only change intensities and positions (AGENTS.md: never change the light set at runtime).
 */
export class FilmLook {
    readonly atmosphere:SceneAtmosphere;
    readonly streetLights:SceneStreetLights;
    private preset:ScenePreset|null=null;private elapsed=0;private camera=new THREE.Vector3();
    constructor(private engine:GameEngine,ground:GroundSurfaceIndex){
        this.atmosphere=new SceneAtmosphere(engine,(x,z)=>ground.height(x,z,30,-3)??0);
        this.streetLights=new SceneStreetLights(this.atmosphere.lamps.slice(0,7));
    }
    get active():boolean{return this.preset!==null;}
    /** Applies a SCENE_PRESETS name plus overrides; `area` [x0,z0,x1,z1] bounds the rain field (the rain follows the
     * camera). The crowd stays out (population 0). null restores the city's own look. */
    async look(look:LookRequest|null):Promise<void>{
        this.reset();if(!look)return;
        const p:ScenePreset={...(SCENE_PRESETS[look.preset]??SCENE_PRESETS.neon!),...(look.overrides??{}),population:0};
        const a=look.area??[-400,-800,400,900];
        await this.atmosphere.apply(p,[{t:0,x:a[0]!,y:0,z:a[1]!},{t:1,x:a[2]!,y:0,z:a[3]!}]);
        this.preset=p;this.elapsed=0;
    }
    /** Fixed floods on the Eiffel Tower, the Bellagio facade and the Paris balloon (floods 2-11; 0 and 1 are left to a
     * vehicle's headlights). */
    architectureFloods(power:number):void{
        const floods=this.atmosphere.floods;
        // Warm uplights actually illuminate iron/stone; opaque architecture receives no emissive boost.
        for(let i=2;i<6;i++){const l=floods[i]!,a=(i-2)*Math.PI*.5+Math.PI*.25;l.position.set(74.5+Math.cos(a)*35,5,400.5+Math.sin(a)*35);l.target.position.set(74.5,105,400.5);l.distance=230;l.angle=.34;l.intensity=11000*power;}
        for(let i=6;i<10;i++){const l=floods[i]!;l.position.set(-170-(i-6)*43,5,390+(i-6)*6);l.target.position.set(-260-(i-6)*32,80,310);l.distance=240;l.angle=.43;l.intensity=14000*power;}
        // Paris balloon: light the existing blue/gold surface, not the entire resort material.
        for(let i=10;i<12;i++){const l=floods[i]!,side=i===10?-1:1;l.position.set(42+side*21,12,535);l.target.position.set(42,31,511.5);l.distance=75;l.angle=.53;l.penumbra=.8;l.color.setHex(0xb5d6ff);l.intensity=2500*power;}
    }
    /** Every frame while a look is on. */
    render(dt:number):void{
        const p=this.preset;if(!p)return;
        this.elapsed+=dt;const power=p.daylight==='night'?p.neon/4:0;
        // no vehicle: headlights and fill stay dark; street spill follows the camera
        this.atmosphere.floods[0]!.intensity=0;this.atmosphere.floods[1]!.intensity=0;this.atmosphere.lamps[7]!.intensity=0;
        this.architectureFloods(power);
        const camera=this.engine.camera;if(camera){camera.getWorldPosition(this.camera);this.streetLights.update(this.camera,power);}
        for(const l of this.atmosphere.lamps)l.updateMatrixWorld();
        this.atmosphere.update(this.elapsed,dt,0);
    }
    reset():void{this.atmosphere.restore();this.preset=null;this.elapsed=0;}
}
