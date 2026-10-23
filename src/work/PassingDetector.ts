/** Tells a player who is driving past a building from one who is arriving at it.
 *
 * A vehicle cannot walk into a lobby, so while one is passing at speed nothing about the building's interior
 * (entrance previews, landmark and Sphere interiors, bridge concourses) needs streaming: that work is only
 * worth doing for someone on foot, or for a vehicle that has slowed to stop at an entrance. Speed is measured
 * from the player's own movement, so it works the same for the jeep, a faster vehicle and a scripted drive.
 * Entering needs a clear burst of speed and leaving needs a sustained slow-down, so the flag does not flicker
 * at junctions. */
export class PassingDetector {
    private last:{x:number;z:number;t:number}|null=null;
    private speed=0;
    private active=false;
    private slowSince=0;
    /** Metres per second at which a player on foot, or in a vehicle, counts as passing; and the speed below
     * which they stop counting (after `holdMs` of staying below it). On foot, a sprint (about 7 m/s) never counts. */
    constructor(private onFoot=9,private inVehicle=3.5,private leaveOnFoot=6,private leaveInVehicle=2,private holdMs=800){}
    /** Call once per game update. Returns whether the player is passing. */
    update(x:number,z:number,nowMs:number,driving:boolean):boolean {
        if(this.last){
            const dt=(nowMs-this.last.t)/1000,d=Math.hypot(x-this.last.x,z-this.last.z);
            // A long gap (a pause) or a jump (a teleport) says nothing about how fast the player is moving.
            if(dt>0.5||d>40)this.speed=0;
            else if(dt>0.001)this.speed+=(d/dt-this.speed)*Math.min(1,dt*4);
        }
        this.last={x,z,t:nowMs};
        const enter=driving?this.inVehicle:this.onFoot,leave=driving?this.leaveInVehicle:this.leaveOnFoot;
        if(!this.active){if(this.speed>enter){this.active=true;this.slowSince=0;}}
        else if(this.speed<leave){if(!this.slowSince)this.slowSince=nowMs;if(nowMs-this.slowSince>=this.holdMs)this.active=false;}
        else this.slowSince=0;
        return this.active;
    }
    get passing():boolean{return this.active;}
    get metresPerSecond():number{return this.speed;}
}
