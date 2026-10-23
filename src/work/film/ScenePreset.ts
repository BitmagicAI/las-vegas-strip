import type {WeatherConfig} from 'types/game.js';

/** Local cinematic layer. These values never write world.json or the level assets. */
export interface ScenePreset {
    daylight:'original'|'day'|'dusk'|'night';
    weather:'clear'|'rain'|'storm';
    rain:number;
    wetness:number;
    neon:number;
    population:number;
    seed:number;
}
export interface RouteKey {t:number;x:number;y:number;z:number;drift?:number}
export interface FilmScenario {
    preset:ScenePreset;
    route:RouteKey[];
    vehicle:string;
    lightning:number[];
}
export const SCENE_PRESETS:Record<string,ScenePreset>={
    original:{daylight:'original',weather:'clear',rain:0,wetness:0,neon:1,population:0,seed:1010},
    daylight:{daylight:'day',weather:'clear',rain:0,wetness:0,neon:1,population:0,seed:1010},
    neon:{daylight:'night',weather:'clear',rain:0,wetness:.25,neon:3,population:0,seed:1010},
    storm:{daylight:'night',weather:'storm',rain:1,wetness:1,neon:4,population:72,seed:1010},
};
export function weatherFor(p:ScenePreset):WeatherConfig {
    return {precipitation:p.weather==='clear'?'none':'rain',intensity:p.rain,wetness:p.wetness,
        wind:{x:5,z:-2},puddles:1,reflections:'ssr',reflectionStrength:.28,reflectionHighlight:1.15,
        reflectionStreak:1.4,reflectionDistance:45,filmGloss:.3,surfaceDarkening:.22,envSheen:.05,
        rippleStrength:.30,spray:true,trailStrength:.25};
}
/** Stateless sampling makes path, events and camera repeatable at any recording frame rate. */
export function sampleRoute(keys:readonly RouteKey[],t:number,out:Float64Array):void {
    let i=0;while(i<keys.length-2&&keys[i+1]!.t<t)i++;
    const a=keys[i]!,b=keys[Math.min(i+1,keys.length-1)]!,p=keys[Math.max(0,i-1)]!,n=keys[Math.min(i+2,keys.length-1)]!;
    const span=Math.max(.001,b.t-a.t),u=Math.max(0,Math.min(1,(t-a.t)/span)),u2=u*u,u3=u2*u;
    if(a.x===b.x&&a.y===b.y&&a.z===b.z){out[0]=a.x;out[1]=a.y;out[2]=a.z;out[3]=out[4]=out[5]=0;out[6]=a.drift??0;return;}
    for(let c=0;c<3;c++){
        const k=c===0?'x':c===1?'y':'z';
        const va=(b[k]-p[k])/Math.max(.001,b.t-p.t)*span,vb=(n[k]-a[k])/Math.max(.001,n.t-a.t)*span;
        out[c]=(2*u3-3*u2+1)*a[k]+(u3-2*u2+u)*va+(-2*u3+3*u2)*b[k]+(u3-u2)*vb;
        out[c+3]=((6*u2-6*u)*a[k]+(3*u2-4*u+1)*va+(-6*u2+6*u)*b[k]+(3*u2-2*u)*vb)/span;
    }
    out[6]=(a.drift??0)+((b.drift??0)-(a.drift??0))*u;
}
