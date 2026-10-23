import * as THREE from 'three';
import type {LightsNode} from 'three/webgpu';
import {lights} from 'three/tsl';
import {lightInterior} from './InteriorLighting.js';

/** Objects that move through the city near the camera (the jeep, the player, NPCs, the charging bay)
 * are lit by sun, sky, ambient and the eight point lights that matter most around the player, instead of
 * every point light in the scene. With the full list (~43), the jeep filling the screen cost ~38 ms of GPU
 * a frame (26 fps standing next to it at spawn, 60 fps once seated, when the camera sits behind it).
 *
 * The eight are stand-ins that are NOT in the scene graph, so no other material's light list changes (the
 * light-set rule): every frame they copy position, colour, intensity, range and decay from the scene's most
 * influential point lights around the focus. A light keeps its slot while it stays in the top eight, so the
 * set only changes at the weak end (no visible popping). Allocation-free per frame. */
export class NearbyLights {
    readonly proxies:THREE.PointLight[]=[];
    private node:LightsNode|null=null;
    private slots:(THREE.PointLight|null)[];
    private score:Float64Array;
    private pending:THREE.Object3D[]=[];
    constructor(private scene:THREE.Scene,private renderer:{lighting:{getNode(scene:THREE.Scene):{getLights():THREE.Light[]}}},readonly count=8,private additional:readonly THREE.Light[]=[]){
        for(let i=0;i<count;i++){const l=new THREE.PointLight(0xffffff,0,0,2);l.name='Nearby stand-in light '+(i+1);l.matrixAutoUpdate=false;this.proxies.push(l);}
        this.slots=new Array<THREE.PointLight|null>(count).fill(null);this.score=new Float64Array(count);
    }
    /** Use the nearby list for every lit material under `root` (now, or once the sun exists). */
    apply(root:THREE.Object3D):void {const node=this.lightsNode();if(node)lightInterior(root,node,false);else this.pending.push(root);}
    private lightsNode():LightsNode|null {
        if(this.node)return this.node;
        const sun=this.scene.getObjectByName('Afterlight focused sun');if(!(sun instanceof THREE.DirectionalLight))return null;
        const list:THREE.Light[]=[sun];this.scene.traverse(o=>{if((o instanceof THREE.HemisphereLight||o instanceof THREE.AmbientLight)&&o.visible)list.push(o);});
        this.node=lights([...list,...this.proxies,...this.additional]);return this.node;
    }
    private influence(light:THREE.PointLight,focus:THREE.Vector3):number {
        if(light.intensity<=0)return 0;
        const e=light.matrixWorld.elements,dx=e[12]!-focus.x,dy=e[13]!-focus.y,dz=e[14]!-focus.z,d2=dx*dx+dy*dy+dz*dz;
        // Range 0 is unlimited in three; otherwise allow a few metres beyond it for objects around the focus.
        if(light.distance>0){const r=light.distance+12;if(d2>r*r)return 0;}
        return light.intensity/Math.max(1,d2);
    }
    /** Call once per frame with the player's position. */
    update(focus:THREE.Vector3):void {
        if(this.pending.length&&this.lightsNode()){for(const root of this.pending)this.apply(root);this.pending.length=0;}
        if(!this.node)return;
        const all=this.renderer.lighting.getNode(this.scene).getLights(),slots=this.slots,score=this.score;
        // Keep current lights that still matter; free the rest.
        for(let i=0;i<slots.length;i++){const l=slots[i];score[i]=l?this.influence(l,focus):0;if(score[i]===0)slots[i]=null;}
        // Offer every other point light to the weakest slot.
        for(const light of all){
            if(!(light instanceof THREE.PointLight)||light.castShadow)continue;
            let taken=false;for(let i=0;i<slots.length;i++)if(slots[i]===light){taken=true;break;}if(taken)continue;
            const s=this.influence(light,focus);if(s===0)continue;
            let weakest=0;for(let i=1;i<slots.length;i++)if(score[i]!<score[weakest]!)weakest=i;
            if(s>score[weakest]!){slots[weakest]=light;score[weakest]=s;}
        }
        for(let i=0;i<slots.length;i++){
            const p=this.proxies[i]!,l=slots[i];
            if(!l){p.intensity=0;continue;}
            p.color.copy(l.color);p.intensity=l.intensity;p.distance=l.distance;p.decay=l.decay;
            p.matrixWorld.copy(l.matrixWorld);p.matrix.copy(l.matrixWorld);
        }
    }
}
