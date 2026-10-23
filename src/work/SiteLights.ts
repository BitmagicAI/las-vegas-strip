import * as THREE from 'three';

export interface LightSite {x:number;y:number;z:number;color:number;intensity:number;distance:number}

/** A fixed set of point lights shared by every streamed venue (landmark interiors, the Sphere).
 *
 * three.js hashes the id of every visible light into the shader cache key of every lit material, so adding,
 * removing or hiding a single light makes the renderer rebuild every lit shader in view on the next frame
 * (tens of milliseconds each: a multi-second freeze on the Strip, 15 to 86 programs per change). These lights
 * are created once at boot, stay visible for the life of the game and are switched on by intensity only, the
 * same rule the engine's point-light pool, HotelStreaming and GeographicPassages follow. Never create, remove
 * or set `visible` on a light after boot; move one of these instead. */
export class SiteLights {
    private lights:THREE.PointLight[]=[];
    private offers=new Map<string,readonly LightSite[]>();
    private dirty=true;
    private focus={x:Infinity,y:Infinity,z:Infinity};
    constructor(parent:THREE.Object3D,readonly count=4){
        for(let i=0;i<count;i++){
            const light=new THREE.PointLight(0xffffff,0,18,2);
            light.name='Shared venue light '+(i+1);light.castShadow=false;
            parent.add(light);this.lights.push(light);
        }
    }
    /** The pool's lights, for a fixed interior light list (see InteriorLighting). */
    get pointLights():readonly THREE.PointLight[]{return this.lights;}
    /** Replace the sites an owner currently wants lit; an empty list withdraws the owner. */
    offer(owner:string,sites:readonly LightSite[]):void {
        const had=this.offers.get(owner);
        if(sites.length){if(had!==sites){this.offers.set(owner,sites);this.dirty=true;}}
        else if(had){this.offers.delete(owner);this.dirty=true;}
    }
    /** Light the offered sites nearest to `focus`; every other light in the pool goes dark by intensity. */
    apply(focus:{x:number;y:number;z:number}):void {
        // Nothing to redo while the offers are unchanged and the player has barely moved.
        if(!this.dirty&&Math.hypot(focus.x-this.focus.x,focus.y-this.focus.y,focus.z-this.focus.z)<2)return;
        this.dirty=false;this.focus={x:focus.x,y:focus.y,z:focus.z};
        const ranked:{site:LightSite;d:number}[]=[];
        for(const sites of this.offers.values())for(const site of sites)ranked.push({site,d:Math.hypot(site.x-focus.x,site.y-focus.y,site.z-focus.z)});
        ranked.sort((a,b)=>a.d-b.d);
        for(let i=0;i<this.lights.length;i++){
            const light=this.lights[i]!,pick=ranked[i]?.site;
            if(!pick){light.intensity=0;continue;}
            light.position.set(pick.x,pick.y,pick.z);light.color.setHex(pick.color);light.intensity=pick.intensity;light.distance=pick.distance;
        }
    }
    /** The pool itself, for tests and the local review probe. */
    get pool():readonly THREE.PointLight[]{return this.lights;}
    get lit():number{return this.lights.filter(l=>l.intensity>0).length;}
    dispose():void {
        for(const light of this.lights){light.removeFromParent();light.dispose();}
        this.lights=[];this.offers.clear();this.dirty=true;
    }
}
