import * as THREE from 'three';
import type {PlayerController} from 'engine/PlayerController.js';
import type {HotelStreaming,KickableDoor} from './hotels/HotelStreaming.js';

/** Camera keyframes of a first-person front kick: [time s, forward m, pitch rad]. Wind-up, strike, follow-through, recover. */
const KEYS=new Float32Array([0,0,0, .09,-.05,.03, .14,.17,-.06, .24,.12,-.04, .45,0,0]);
const KICK_SECONDS=.45,IMPACT_AT=.13;
const smooth=(x:number)=>x*x*(3-2*x);

/** F (touch: KICK) kicks a closed hotel room door open: in first person the view lunges forward and jolts on impact, and the
 * door is thrown open on its hinge at the moment of impact (HotelStreaming / GuestDoor.kick). A room that is not loaded yet
 * loads first (the usual loading hold) and then bursts open. Allocation-free per frame. */
export class DoorKick {
    private held=false;private t=-1;private target:KickableDoor|null=null;private impacted=false;
    private forward=new THREE.Vector3();private from=new THREE.Vector3();
    constructor(private controller:PlayerController,private hotels:HotelStreaming){
        controller.registerCustomAction({action:'kickDoor',desktop:{keys:['KeyF']},mobile:{label:'KICK',behavior:'tap'}});
    }
    /** True while a kick is playing. */
    get kicking():boolean{return this.t>=0;}
    /** Start a kick now (the F key does this; scripted shots call it directly). */
    kick(camera:THREE.Camera,player:THREE.Vector3):void{
        if(this.t>=0)return;
        camera.getWorldDirection(this.forward);
        this.target=this.hotels.kickTarget(player,this.forward);this.from.copy(player);this.t=0;this.impacted=false;
    }
    /** Once per frame, after the camera has been updated. `blocked`: in a vehicle, on the coaster or in the lift. */
    update(dt:number,camera:THREE.Camera|null,player:THREE.Vector3|null,firstPerson:boolean,blocked:boolean):void{
        const pressed=!!this.controller.keys.kickDoor;
        if(pressed&&!this.held&&!blocked&&camera&&player)this.kick(camera,player);
        this.held=pressed;
        if(this.t<0||!camera)return;
        this.t+=dt;
        if(!this.impacted&&this.t>=IMPACT_AT){this.impacted=true;if(this.target)this.hotels.kick(this.target,this.from);this.target=null;}
        if(this.t>=KICK_SECONDS){this.t=-1;return;}
        if(!firstPerson)return;
        let i=0;while(i+3<KEYS.length-3&&KEYS[i+3]!<=this.t)i+=3;
        const t0=KEYS[i]!,t1=KEYS[i+3]!,x=smooth(Math.min(1,Math.max(0,(this.t-t0)/(t1-t0))));
        const forward=KEYS[i+1]!+(KEYS[i+4]!-KEYS[i+1]!)*x,pitch=KEYS[i+2]!+(KEYS[i+5]!-KEYS[i+2]!)*x;
        const shake=this.t>IMPACT_AT?Math.sin(this.t*95)*.012*Math.exp(-(this.t-IMPACT_AT)*16):0;
        camera.getWorldDirection(this.forward);
        camera.position.addScaledVector(this.forward,forward);camera.position.y+=shake;
        camera.rotateX(pitch);
    }
}
