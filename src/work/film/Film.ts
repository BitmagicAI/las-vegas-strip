import * as THREE from 'three';

/**
 * Film director (local filming only; loaded by Game.ts when localStorage 'afterlight:film' is '1' on localhost).
 *
 * A TAKE is a JSON script (tools/film/takes/*.json) played on the GAME clock: under the engine's frame recorder every frame is
 * a fixed 1/60 s step, so the footage is smooth however slowly the machine captures. Nobody plays: the player is driven by a
 * virtual gamepad (left stick: walking, analog steering; buttons: throttle/brake are keys) and the first-person view is aimed
 * directly. A separate camera track can take over the camera (world, player- or jeep-relative keyframes) for cinematic shots.
 *
 *   load(take)  places the player and warms the area (wall-clock, before recording), resolves door/room targets;
 *   arm()       starts the take on the next game frame (the recorder starts right after);
 *   state()     {frame, t, step, done, warnings}; marks() the labelled frames for the cut.
 *
 * Steps run one after another; each is an object with one key:
 *   {wait: s} · {look: {yaw?|dir?:[x,z]|at?:[x,y,z], pitch?, seconds?}} · {walk: {path:[[x,z]|[x,y,z]...], run?, face?:[x,y,z], lookAhead?}}
 *   {drive: {path:[[x,z]...], speed, stop?}} · {key: 'KeyR'} · {kick: true} · {approachDoor: {}} · {enterRoom: {distance}}
 *   {view: 'first'|'third'} · {until: 'coaster-done'|'still', max: s} · {mark: 'label'} · {teleport: [x,y,z]}
 * Camera track entries: {from: s, to: s, anchor?: 'world'|'jeep'|'player', keys: [{t, pos:[x,y,z], look:[x,y,z], fov?}...]}.
 */
export interface FilmHost {
    scenarioLoad?(scenario:import('./ScenePreset.js').FilmScenario|null):Promise<void>;
    scenarioUpdate?(t:number,dt:number):void;
    /** A look-only take: time of day and weather on an ordinary camera take (no car, no crowd); null restores the city. */
    lookLoad?(look:Take['look']|null):Promise<void>;
    engine:{camera:THREE.PerspectiveCamera|null};
    teleport(x:number,y:number,z:number):void;
    position():{x:number;y:number;z:number};
    streamingBusy():boolean;
    look(yaw:number,pitch:number):void;
    view(mode:'first'|'third'):void;
    firstPerson():boolean;
    jeep():{x:number;y:number;z:number;fx:number;fy:number;fz:number;speed:number}|null;
    /** Keep a hotel floor and one of its rooms (bay, side) resident and built for a camera run; id null releases. */
    hotelPin(id:string|null,floor:number,bay:number,side:number):Promise<boolean>;
    /** Open the hotel and venue doors the camera is about to pass through (speed: the camera's, m/s; a faster camera opens
     * them from further away). */
    hotelDoors(camera:{x:number;y:number;z:number},forward:{x:number;y:number;z:number},speed:number):void;
    /** Analog throttle [0, 1] and brake [0, 1] for the jeep while a drive runs; throttle null hands it back to the pad. */
    vehicleInput(throttle:number|null,brake:number):void;
    seatJeep(x:number,y:number,z:number,heading:number):boolean;
    inVehicle():boolean;
    exitVehicle():void;
    inspect(name:string):boolean;
    landmark(key:string,view:string):unknown;
    hotel(id:string,floor:number,room:number|null,view:string|null):Promise<unknown>;
    kickDoors():{label:string;point:THREE.Vector3;approach:THREE.Vector3}[];
    prepareRoom(label:string):boolean;
    kick():void;
    coasterRiding():boolean;
    /** Distance to the first building or ground along a ray (max when nothing is hit). */
    rayDistance(ox:number,oy:number,oz:number,dx:number,dy:number,dz:number,max:number):number;
    /** Game clock and physics at 1/(60 n) s a frame while the recorder runs (n = 1 restores the engine's own stepping). */
    stepping(subframes:number):void;
    /** The Big Apple Coaster's train runs a ride on its own (no rider), `elapsed` seconds in; null parks it. */
    coaster(elapsed:number|null):void;
    /** The front car's pose (position, orientation: x right, y up, z forward) while the film's train runs. */
    coasterPose(position:THREE.Vector3,orientation:THREE.Quaternion):boolean;
    /** Keep these venues' public interiors loaded for the take (a load mid-take holds the game: a freeze); null releases. */
    venuePin(keys:string[]|null):Promise<void>;
    /** Every level of detail at full while a take loads and runs (no LOD popping on a moving camera). */
    fullDetail(on:boolean):void;
}
type Vec3=[number,number,number];
/** roll: bank about the view axis in radians (+ = rolls left, the left side of the frame dips; a right turn banks -). */
interface CameraKey {t:number;pos:Vec3;look:Vec3;fov?:number;roll?:number}
/** anchor 'coaster': keys in the front car's frame (x right, y up, z forward), the camera's up following the car (it banks
 * and loops with the track). Segments that overlap in time are blended (position, orientation and field of view, eased over
 * the overlap), so one camera can hand over from a world flight to a jeep or coaster chase and back without a cut.
 * anchor 'drone': keys in the jeep's frame (x right, y up, z forward) like 'jeep', but the frame is smoothed and the camera
 * follows its target on a critically damped spring (lag s), pulled in front of buildings; 'world' + follow: a fixed path
 * that keeps looking at the jeep. */
interface CameraSegment {from:number;to:number;anchor?:'world'|'jeep'|'player'|'drone'|'coaster';keys:CameraKey[];lag?:number;follow?:boolean;
    /** 'camera': interiors stream and visibility is decided around the camera, not the player (a camera run through a
     * building); doors: open hotel doors ahead of the camera. */
    focus?:'camera';doors?:boolean;
    /** A building source kept hidden while the segment plays (leaving a hotel through a room window, the camera is still
     * inside the tower's exterior shell for a few metres, whose walls render from both sides). */
    hide?:string}
interface Start {inspect?:string;landmark?:[string,string];hotel?:[string,number,number|null,string|null];at?:Vec3;yaw?:number;dir?:[number,number];pitch?:number;
    seat?:{at:Vec3;heading:number};view?:'first'|'third';warm?:number;door?:{near?:[number,number];label?:string};
    /** [tower id, floor, bay, side]: a hotel floor and room kept resident and built for the take (see hotelPin). */
    hotelPin?:[string,number,number,number];
    /** Venues (StripLandmarks keys) whose public interiors stay loaded for the take. */
    venues?:string[];
    /** The coaster's train is this many seconds into a ride when the take starts (negative: it sets off that much later;
     * see FilmHost.coaster). */
    coaster?:number}
export interface Take {name:string;seconds?:number;maxSeconds?:number;start:Start;steps:Record<string,unknown>[];camera?:CameraSegment[];
    scenario?:import('./ScenePreset.js').FilmScenario;
    /** Time of day and weather for a camera take: a SCENE_PRESETS name ('neon', 'storm', ...) with overrides; `area`
     * [x0,z0,x1,z1] bounds the rain field. Ignored when the take has a scenario. */
    look?:{preset:string;overrides?:Partial<import('./ScenePreset.js').ScenePreset>;area?:number[]};
    /** Recorded frames per 1/60 s (motion blur: tools/film/blend-subframes.py blends them to 60 fps); default 1. */
    subframes?:number}

const yawFor=(dx:number,dz:number)=>Math.atan2(-dx,-dz);
const wrap=(a:number)=>{while(a>Math.PI)a-=2*Math.PI;while(a<-Math.PI)a+=2*Math.PI;return a;};
const ease=(x:number)=>x<=0?0:x>=1?1:x*x*(3-2*x);
const wait=(ms:number)=>new Promise(r=>setTimeout(r,ms));

/** The virtual pad the engine's GamepadControls adopts (navigator.getGamepads is replaced while filming). */
class FilmPad {
    readonly axes=[0,0,0,0];
    readonly buttons=Array.from({length:17},()=>({pressed:false,touched:false,value:0}));
    readonly pad={id:'Afterlight film pad (standard)',index:0,connected:true,mapping:'standard',timestamp:0,axes:this.axes,buttons:this.buttons,vibrationActuator:null,hapticActuators:[]};
    private original:typeof navigator.getGamepads|null=null;
    uninstall():void {if(!this.original)return;Object.defineProperty(navigator,'getGamepads',{configurable:true,value:this.original});this.original=null;const e=new Event('gamepaddisconnected');Object.defineProperty(e,'gamepad',{value:this.pad});window.dispatchEvent(e);}
    install():void {
        if(this.original)return;this.original=navigator.getGamepads.bind(navigator);
        const pad=this.pad;Object.defineProperty(navigator,'getGamepads',{configurable:true,value:()=>[pad]});
        // GamepadControls only rescans while it already holds a pad: announce this one as a browser would.
        const e=new Event('gamepadconnected');Object.defineProperty(e,'gamepad',{value:pad});window.dispatchEvent(e);
    }
    /** Desired post-deadzone stick output (x right, y forward, each -1..1) → raw axes, inverting GamepadControls' per-axis
     * (0.12) and radial (0.15) deadzones so small steering values survive. */
    stick(x:number,y:number):void {
        const m=Math.hypot(x,y);if(m<1e-4){this.axes[0]=0;this.axes[1]=0;return;}
        const pre=Math.min(1,.15+.85*Math.min(1,m)),k=pre/m,ax=x*k,ay=y*k;
        const raw=(v:number)=>Math.abs(v)<1e-4?0:Math.sign(v)*Math.min(1,.12+.88*Math.abs(v));
        this.axes[0]=raw(ax);this.axes[1]=-raw(ay);this.pad.timestamp=performance.now();
    }
    /** Standard-layout button (0 A: jump / brake in a vehicle, 7 RT: throttle in a vehicle). */
    button(index:number,pressed:boolean):void {const b=this.buttons[index]!;b.pressed=pressed;b.touched=pressed;b.value=pressed?1:0;}
}

export class Film {
    private pad=new FilmPad();
    private take:Take|null=null;private armed=false;private frame=0;private t=0;private stepIndex=0;private stepT=0;private stepState:Record<string,number>={};
    private done=false;private warnings:string[]=[];private markList:{frame:number;label:string}[]=[];private poseLog:number[]=[];
    private yaw=0;private pitch=0;private door:{label:string;point:THREE.Vector3;approach:THREE.Vector3}|null=null;
    private keysDown=new Map<string,number>();private lastPos=new THREE.Vector3();private stuckT=0;
    private lastDt=1/60;
    private cameraFrame=-1;private heldCameraQuat=new THREE.Quaternion();private heldCameraFov=60;
    private drone={active:null as CameraSegment|null,pos:new THREE.Vector3(),vel:new THREE.Vector3(),look:new THREE.Vector3(),lookVel:new THREE.Vector3(),o:new THREE.Vector3(),fx:0,fz:1,
        /** the frame's own velocity (low-passed): fed forward so the spring smooths the key path without trailing the jeep */
        prevO:new THREE.Vector3(),oVel:new THREE.Vector3(),
        /** the aim, filtered as angles: a look-at point near the camera swung it wildly, and near-vertical views flipped its heading */
        yaw:0,pitch:0,yawVel:0,pitchVel:0,
        /** bank into the drone's own turns (eased), from the heading change of its velocity */
        roll:0,heading:0};
    /** Jeep x, z, speed, distance from the path, height and nose pitch (forward y), per driven frame (tools/film/record.mjs
     * saves it as track.json; 6 numbers a frame). */
    private trackLog:number[]=[];
    /** The camera run's streaming focus (camera position at foot height) while a 'focus: camera' segment plays. */
    private focusOn=false;private focusPoint=new THREE.Vector3();private fwd=new THREE.Vector3();
    focus():THREE.Vector3|null{return this.focusOn?this.focusPoint:null;}
    private hideSource:string|null=null;private coasterOn=false;private lastCam=new THREE.Vector3();
    hide():string|null{return this.hideSource;}
    private camPos=new THREE.Vector3();private camLook=new THREE.Vector3();private tmp=new THREE.Vector3();private savedFov=0;private camActive=false;
    private blendPos=new THREE.Vector3();private blendQuat=new THREE.Quaternion();private carPos=new THREE.Vector3();private carQuat=new THREE.Quaternion();
    constructor(private host:FilmHost){}

    async load(take:Take):Promise<Record<string,unknown>>{
        this.pad.install();this.host.stepping(1);this.host.vehicleInput(null,0);this.focusOn=false;this.hideSource=null;this.coasterOn=false;this.host.fullDetail(true);await this.host.hotelPin(null,0,0,0);this.host.coaster(null);await this.host.venuePin(null);
        this.cameraFrame=-1;this.drone.active=null;
        this.take=take;this.armed=false;this.done=false;this.frame=0;this.t=0;this.stepIndex=0;this.stepT=0;this.stepState={};this.warnings=[];this.markList=[];this.poseLog=[];this.trackLog=[];this.door=null;
        await this.host.scenarioLoad?.(take.scenario??null);
        if(!take.scenario)await this.host.lookLoad?.(take.look??null);
        const s=take.start;
        if(s.seat){this.host.seatJeep(s.seat.at[0],s.seat.at[1],s.seat.at[2],s.seat.heading);}
        else {
            // an on-foot take after a drive: leave the jeep first (teleports do not move a seated player)
            for(let i=0;i<20&&this.host.inVehicle();i++){this.host.exitVehicle();await wait(250);}
            if(s.view)this.host.view(s.view);
            if(s.inspect)this.host.inspect(s.inspect);
            else if(s.landmark)this.host.landmark(s.landmark[0],s.landmark[1]);
            else if(s.hotel)await this.host.hotel(s.hotel[0],s.hotel[1],s.hotel[2],s.hotel[3]);
            if(s.at)this.host.teleport(s.at[0],s.at[1],s.at[2]);
        }
        await this.settle();
        // places that stream in (the Eiffel deck, upper floors) may not have had a floor yet: place again once they have
        if(!s.seat&&(s.landmark||s.inspect||s.at)){
            if(s.inspect)this.host.inspect(s.inspect);else if(s.landmark)this.host.landmark(s.landmark[0],s.landmark[1]);
            if(s.at)this.host.teleport(s.at[0],s.at[1],s.at[2]);
            await this.settle();
        }
        const cam=this.host.engine.camera;
        if(s.yaw!==undefined||s.dir||s.pitch!==undefined){
            this.yaw=s.yaw??(s.dir?yawFor(s.dir[0],s.dir[1]):this.currentYaw());this.pitch=s.pitch??0;if(!s.seat)this.host.look(this.yaw,this.pitch);
        }else{this.yaw=this.currentYaw();this.pitch=cam?Math.asin(Math.max(-1,Math.min(1,cam.getWorldDirection(this.tmp).y))):0;}
        if(s.door){
            const doors=this.host.kickDoors(),p=this.host.position(),near=s.door.near??[p.x,p.z];
            doors.sort((a,b)=>Math.hypot(a.point.x-near[0],a.point.z-near[1])-Math.hypot(b.point.x-near[0],b.point.z-near[1]));
            this.door=(s.door.label?doors.find(d=>d.label===s.door!.label):doors[0])??null;
            if(!this.door)this.warnings.push('no kickable door near the start');
            else if(this.host.prepareRoom(this.door.label))await this.settle();
        }
        if(s.hotelPin){if(!await this.host.hotelPin(...s.hotelPin))this.warnings.push(`hotel pin ${s.hotelPin.join(' ')} failed`);await this.settle();}
        if(s.venues){await this.host.venuePin(s.venues);await this.settle();}
        // a camera run streams around the camera: warm the area where it starts, not just around the player
        const first=take.camera?.[0];
        if(first?.focus==='camera'&&(first.anchor??'world')==='world'&&first.keys.length){const k=first.keys[0]!.pos;this.focusPoint.set(k[0],k[1]-1.55,k[2]);this.focusOn=true;}
        await wait((s.warm??3)*1000);await this.settle();
        const p=this.host.position();this.lastPos.set(p.x,p.y,p.z);
        return {position:p,yaw:this.yaw,pitch:this.pitch,door:this.door?.label??null,warnings:this.warnings};
    }
    private async settle():Promise<void>{for(let i=0;i<240&&this.host.streamingBusy();i++)await wait(250);await wait(600);for(let i=0;i<240&&this.host.streamingBusy();i++)await wait(250);}
    private currentYaw():number{const cam=this.host.engine.camera;if(!cam)return 0;cam.getWorldDirection(this.tmp);return yawFor(this.tmp.x,this.tmp.z);}
    arm():void{this.armed=true;}
    release():void{this.pad.uninstall();this.armed=false;this.take=null;this.focusOn=false;this.hideSource=null;this.host.vehicleInput(null,0);this.host.fullDetail(false);this.host.stepping(1);if(this.camActive&&this.host.engine.camera){this.host.engine.camera.fov=this.savedFov;this.host.engine.camera.updateProjectionMatrix();}this.camActive=false;}
    state(){return {name:this.take?.name,frame:this.frame,t:this.t,dt:this.lastDt,subframes:this.take?.subframes??1,step:this.stepIndex,steps:this.take?.steps.length??0,done:this.done,warnings:this.warnings};}
    marks(){return this.markList;}
    track(){return this.trackLog;}
    /** Camera position + direction per recorded frame (x,y,z,dx,dy,dz), for checking camera work after the fact. */
    poses(){return this.poseLog;}

    /** Before the player controller runs (inputs for this frame). */
    update(dt:number):void{
        if(!this.take||!this.armed||this.done)return;
        // motion blur: the engine runs n frames per 1/60 s (the recorder pins it to 1/60 when it starts; this follows a frame later)
        const sub=this.take.subframes??1;if(sub>1)this.host.stepping(sub);
        this.frame++;this.t+=dt;this.lastDt=dt;
        this.host.scenarioUpdate?.(this.t,dt);
        // the coaster's train runs on the take's clock: `coaster` s into a ride at the start (negative: it sets off that
        // late); its own update advances it from here
        const ride=this.take.start.coaster;
        if(ride!==undefined&&!this.coasterOn&&this.t>=-ride-1e-6){this.coasterOn=true;this.host.coaster(Math.max(0,ride+this.t-dt));}
        for(const [code,until] of this.keysDown)if(this.frame>=until){document.dispatchEvent(new KeyboardEvent('keyup',{code,key:code,bubbles:true}));this.keysDown.delete(code);}
        this.pad.stick(0,0);this.pad.button(0,false);this.pad.button(7,false);
        while(this.stepIndex<this.take.steps.length){
            const step=this.take.steps[this.stepIndex]!;
            const finished=this.runStep(step,dt);
            if(!finished)break;
            this.stepIndex++;this.stepT=0;this.stepState={};
        }
        this.stepT+=dt;
        if(this.stepIndex>=this.take.steps.length&&(!this.take.seconds||this.t>=this.take.seconds))this.done=true;
        // a take never runs away: 240 s unless it says otherwise
        if(!this.done&&this.t>=(this.take.maxSeconds??240)){this.warnings.push(`take stopped at its ${this.take.maxSeconds??240} s limit (step ${this.stepIndex})`);this.done=true;}
        if(this.done&&sub>1)this.host.stepping(1);
        if(this.done){this.host.vehicleInput(null,0);this.host.coaster(null);if(this.take.scenario)this.t=Math.min(this.t,this.take.seconds??this.t);else this.host.fullDetail(false);}
    }
    /** After everything else has posed the camera (the film camera track wins). */
    applyCamera():void{
        const cam=this.host.engine.camera;if(!cam||!this.take||!this.armed)return;
        // Streaming holds can redraw many times without advancing the film clock.
        // Reapply the last pose, but never integrate drone springs or log another pose on the same tick.
        if(this.cameraFrame===this.frame){cam.position.copy(this.lastCam);cam.quaternion.copy(this.heldCameraQuat);if(cam.fov!==this.heldCameraFov){cam.fov=this.heldCameraFov;cam.updateProjectionMatrix();}cam.updateMatrixWorld(true);return;}
        this.cameraFrame=this.frame;
        const segs=this.take.camera;let seg:CameraSegment|undefined,prev:CameraSegment|undefined;
        // The wait step can finish one tick after the duration. Hold scenario framing across that boundary.
        const cameraTime=this.take.scenario?Math.min(this.t,this.take.seconds??this.t):this.t;
        if(segs)for(const c of segs)if(cameraTime>=c.from&&cameraTime<=c.to){if(seg)prev=seg;seg=c;}
        if(seg){
            if(!this.camActive){this.camActive=true;this.savedFov=cam.fov;}
            if(prev){
                // two segments overlap: ease from the earlier one to the later across the overlap
                this.cameraAt(prev,cam);this.blendPos.copy(cam.position);this.blendQuat.copy(cam.quaternion);const fov=cam.fov;
                this.cameraAt(seg,cam);const w=ease((this.t-seg.from)/Math.max(1e-6,prev.to-seg.from));
                // (slerpQuaternions copies its first argument into the target before reading the second: never pass the target)
                cam.position.lerpVectors(this.blendPos,cam.position,w);this.carQuat.copy(cam.quaternion);cam.quaternion.slerpQuaternions(this.blendQuat,this.carQuat,w);
                const f=fov+(cam.fov-fov)*w;if(Math.abs(cam.fov-f)>1e-4){cam.fov=f;cam.updateProjectionMatrix();}
                cam.updateMatrixWorld(true);
            }else this.cameraAt(seg,cam);
        }
        else if(this.camActive){this.camActive=false;cam.fov=this.savedFov;cam.updateProjectionMatrix();}
        const hold=!!this.take.scenario;
        this.focusOn=!!seg&&seg.focus==='camera'&&(!this.done||hold);this.hideSource=(!this.done||hold)&&(seg?.hide??prev?.hide)||null;
        if(this.focusOn){this.focusPoint.copy(cam.position);this.focusPoint.y-=1.55;}
        const speed=this.lastCam.distanceTo(cam.position)/Math.max(1e-4,this.lastDt);this.lastCam.copy(cam.position);this.heldCameraQuat.copy(cam.quaternion);this.heldCameraFov=cam.fov;
        if(seg?.doors&&!this.done){cam.getWorldDirection(this.fwd);this.host.hotelDoors(cam.position,this.fwd,this.frame>1?Math.min(60,speed):0);}
        if(!this.done&&this.frame%(this.take.subframes??1)===0){cam.getWorldDirection(this.tmp);this.poseLog.push(+cam.position.x.toFixed(3),+cam.position.y.toFixed(3),+cam.position.z.toFixed(3),+this.tmp.x.toFixed(4),+this.tmp.y.toFixed(4),+this.tmp.z.toFixed(4));}
    }

    private cameraAt(seg:CameraSegment,cam:THREE.PerspectiveCamera):void{
        const keys=seg.keys,local=this.t-seg.from;
        let i=0;while(i<keys.length-2&&keys[i+1]!.t<=local)i++;
        const k0=keys[Math.max(0,i-1)]!,k1=keys[i]!,k2=keys[Math.min(keys.length-1,i+1)]!,k3=keys[Math.min(keys.length-1,i+2)]!;
        const span=Math.max(1e-6,k2.t-k1.t),u=keys.length===1?0:Math.min(1,Math.max(0,(local-k1.t)/span));
        // Ease only into the first key and out of the last; Catmull-Rom keeps the speed continuous in between.
        const x=i===0&&keys.length>2?ease(u)*.5+u*.5:i===keys.length-2&&keys.length>2?ease(u)*.5+u*.5:keys.length===2?ease(u):u;
        const cr=(a:number,b:number,c:number,d:number)=>.5*((2*b)+(-a+c)*x+(2*a-5*b+4*c-d)*x*x+(-a+3*b-3*c+d)*x*x*x);
        this.camPos.set(cr(k0.pos[0],k1.pos[0],k2.pos[0],k3.pos[0]),cr(k0.pos[1],k1.pos[1],k2.pos[1],k3.pos[1]),cr(k0.pos[2],k1.pos[2],k2.pos[2],k3.pos[2]));
        this.camLook.set(cr(k0.look[0],k1.look[0],k2.look[0],k3.look[0]),cr(k0.look[1],k1.look[1],k2.look[1],k3.look[1]),cr(k0.look[2],k1.look[2],k2.look[2],k3.look[2]));
        if(seg.anchor==='drone'){const fov=k1.fov!==undefined&&k2.fov!==undefined?k1.fov+(k2.fov-k1.fov)*x:k1.fov;if(fov!==undefined&&Math.abs(cam.fov-fov)>1e-3){cam.fov=fov;cam.updateProjectionMatrix();}this.droneAt(seg,cam);return;}
        if(seg.follow){const j=this.host.jeep();if(j)this.camLook.set(j.x,j.y+1.1,j.z);}
        if(seg.anchor==='coaster'){
            if(this.host.coasterPose(this.carPos,this.carQuat)){
                this.camPos.applyQuaternion(this.carQuat).add(this.carPos);this.camLook.applyQuaternion(this.carQuat).add(this.carPos);
                cam.position.copy(this.camPos);cam.up.set(0,1,0).applyQuaternion(this.carQuat);cam.lookAt(this.camLook);
            }else{this.warnings.length<20&&this.warnings.push('coaster camera without a running train');cam.position.copy(this.camPos);cam.up.set(0,1,0);cam.lookAt(this.camLook);}
            const fov=k1.fov!==undefined&&k2.fov!==undefined?k1.fov+(k2.fov-k1.fov)*x:k1.fov;
            if(fov!==undefined&&Math.abs(cam.fov-fov)>1e-3){cam.fov=fov;cam.updateProjectionMatrix();}
            cam.updateMatrixWorld(true);return;
        }
        if(seg.anchor==='jeep'||seg.anchor==='player'){
            const j=seg.anchor==='jeep'?this.host.jeep():null,p=this.host.position();
            const ox=j?j.x:p.x,oy=j?j.y:p.y,oz=j?j.z:p.z;let fx=j?j.fx:-Math.sin(this.yaw),fz=j?j.fz:-Math.cos(this.yaw);const fl=Math.hypot(fx,fz)||1;fx/=fl;fz/=fl;
            // local: x right, y up, z forward
            const rx=-fz,rz=fx;
            const map=(v:THREE.Vector3)=>v.set(ox+v.x*rx+v.z*fx,oy+v.y,oz+v.x*rz+v.z*fz);
            map(this.camPos);map(this.camLook);
        }
        cam.position.copy(this.camPos);cam.up.set(0,1,0);cam.lookAt(this.camLook);
        if(k1.roll!==undefined||k2.roll!==undefined){const r=cr(k0.roll??0,k1.roll??0,k2.roll??0,k3.roll??0);if(r)cam.rotateZ(r);}
        const fov=k1.fov!==undefined&&k2.fov!==undefined?k1.fov+(k2.fov-k1.fov)*x:k1.fov;
        if(fov!==undefined&&Math.abs(cam.fov-fov)>1e-3){cam.fov=fov;cam.updateProjectionMatrix();}
        cam.updateMatrixWorld(true);
    }

    /** Drone: the key path in a smoothed jeep frame, chased by a damped spring, never behind a building. */
    private droneAt(seg:CameraSegment,cam:THREE.PerspectiveCamera):void{
        const j=this.host.jeep(),p=this.host.position(),d=this.drone,dt=Math.min(this.lastDt,1/20);
        const jx=j?j.x:p.x,jy=j?j.y:p.y,jz=j?j.z:p.z;let fx=j?j.fx:-Math.sin(this.yaw),fz=j?j.fz:-Math.cos(this.yaw);const fl=Math.hypot(fx,fz)||1;fx/=fl;fz/=fl;
        const first=d.active!==seg;
        if(first){d.active=seg;d.o.set(jx,jy,jz);d.fx=fx;d.fz=fz;d.prevO.copy(d.o);d.oVel.set(0,0,0);}
        else{
            // the frame follows the jeep closely in position and lazily in heading (no twitch from steering corrections)
            d.o.lerp(this.tmp.set(jx,jy,jz),1-Math.exp(-dt/.12));
            const kh=1-Math.exp(-dt/.9);d.fx+=(fx-d.fx)*kh;d.fz+=(fz-d.fz)*kh;const hl=Math.hypot(d.fx,d.fz)||1;d.fx/=hl;d.fz/=hl;
            this.tmp.subVectors(d.o,d.prevO).multiplyScalar(1/Math.max(1e-4,dt));d.oVel.lerp(this.tmp,1-Math.exp(-dt/.15));d.prevO.copy(d.o);
        }
        const rx=-d.fz,rz=d.fx,map=(v:THREE.Vector3)=>v.set(d.o.x+v.x*rx+v.z*d.fx,d.o.y+v.y,d.o.z+v.x*rz+v.z*d.fz);
        map(this.camPos);map(this.camLook);
        // Fast film actors can travel several metres while the drone origin eases forward.
        // Keep their current position in the aim point while retaining independent camera motion.
        if(this.take?.scenario)this.camLook.add(this.tmp.set(jx-d.o.x,jy-d.o.y,jz-d.o.z));
        // keep a building or the ground from coming between the jeep and the drone
        const ox=d.o.x,oy=d.o.y+1.4,oz=d.o.z,vx=this.camPos.x-ox,vy=this.camPos.y-oy,vz=this.camPos.z-oz,len=Math.hypot(vx,vy,vz);
        if(len>.5){const hit=this.host.rayDistance(ox,oy,oz,vx/len,vy/len,vz/len,len);if(hit<len){const k=Math.max(.5,hit-1.5)/len;this.camPos.set(ox+vx*k,oy+vy*k,oz+vz*k);}}
        if(first){d.pos.copy(this.camPos);d.vel.set(0,0,0);d.look.copy(this.camLook);d.lookVel.set(0,0,0);}
        else{
            // critically damped, tracking the frame's velocity (no steady trailing at speed)
            const tv=d.oVel,spring=(x:THREE.Vector3,v:THREE.Vector3,target:THREE.Vector3,lag:number)=>{
                const w=2/Math.max(.05,lag);
                v.x+=(w*w*(target.x-x.x)+2*w*(tv.x-v.x))*dt;v.y+=(w*w*(target.y-x.y)+2*w*(tv.y-v.y))*dt;v.z+=(w*w*(target.z-x.z)+2*w*(tv.z-v.z))*dt;
                x.addScaledVector(v,dt);
            };
            spring(d.pos,d.vel,this.camPos,seg.lag??.55);
        }
        // aim at the look point from where the camera actually is, as yaw/pitch: never steeper than 55 degrees down,
        // eased by a critically damped spring and capped at 80 degrees a second
        this.tmp.subVectors(this.camLook,d.pos);const hl=Math.hypot(this.tmp.x,this.tmp.z);
        const wantYaw=Math.atan2(this.tmp.x,-this.tmp.z),wantPitch=Math.max(-.96,Math.min(.7,Math.atan2(this.tmp.y,Math.max(1e-3,hl))));
        if(first){d.yaw=wantYaw;d.pitch=wantPitch;d.yawVel=0;d.pitchVel=0;}
        else{
            const w=2/(this.take?.scenario?.preset?.weather? .22:Math.max(.05,(seg.lag??.55)*.6)),cap=Math.PI*(this.take?.scenario?100:80)/180;
            const ey=wrap(wantYaw-d.yaw);d.yawVel+=(w*w*ey-2*w*d.yawVel)*dt;d.yawVel=Math.max(-cap,Math.min(cap,d.yawVel));d.yaw=wrap(d.yaw+d.yawVel*dt);
            const ep=wantPitch-d.pitch;d.pitchVel+=(w*w*ep-2*w*d.pitchVel)*dt;d.pitchVel=Math.max(-cap,Math.min(cap,d.pitchVel));d.pitch+=d.pitchVel*dt;
        }
        const cp=Math.cos(d.pitch);d.look.set(d.pos.x+Math.sin(d.yaw)*cp,d.pos.y+Math.sin(d.pitch),d.pos.z-Math.cos(d.yaw)*cp);
        // bank like a drone into its turns: atan(0.35 * v * turn rate / g), capped at 12 degrees, eased over 0.35 s
        const hs=Math.hypot(d.vel.x,d.vel.z),heading=Math.atan2(d.vel.x,-d.vel.z);
        let bank=0;if(!first&&hs>2){const rate=wrap(heading-d.heading)/Math.max(1e-4,dt);bank=-Math.atan(.35*hs*rate/9.81);bank=Math.max(-.21,Math.min(.21,bank));}
        d.heading=heading;d.roll+=(first?0:(bank-d.roll)*(1-Math.exp(-dt/.35)));if(first)d.roll=0;
        cam.position.copy(d.pos);cam.up.set(0,1,0);cam.lookAt(d.look);if(d.roll)cam.rotateZ(d.roll);cam.updateMatrixWorld(true);
    }
    private pressKey(code:string):void{document.dispatchEvent(new KeyboardEvent('keydown',{code,key:code,bubbles:true}));this.keysDown.set(code,this.frame+3);}
    private aim(yaw:number,pitch:number,dt:number,rate=1.8):void{
        const dy=wrap(yaw-this.yaw),maxStep=rate*dt;
        // critically damped approach, capped: smooth starts and stops, no whip pans
        this.yaw=wrap(this.yaw+Math.max(-maxStep,Math.min(maxStep,dy*Math.min(1,dt*3.2))));
        this.pitch+=(pitch-this.pitch)*Math.min(1,dt*3);
        if(this.host.firstPerson())this.host.look(this.yaw,this.pitch);
    }
    /** Run one step for this frame; true when it is finished. */
    private runStep(step:Record<string,unknown>,dt:number):boolean{
        const key=Object.keys(step)[0]!,arg=step[key] as Record<string,unknown>;const st=this.stepState;
        switch(key){
            case 'wait':return this.stepT>=(step.wait as number);
            case 'mark':this.markList.push({frame:this.frame,label:String(step.mark)});return true;
            case 'key':this.pressKey(String(step.key));return true;
            case 'kick':this.host.kick();this.markList.push({frame:this.frame,label:'kick'});return true;
            case 'view':this.host.view(step.view as 'first'|'third');return true;
            case 'teleport':{const p=step.teleport as Vec3;this.host.teleport(p[0],p[1],p[2]);return true;}
            case 'look':{
                const a=arg as {yaw?:number;dir?:[number,number];at?:Vec3;pitch?:number;seconds?:number};
                if(st.y0===undefined){st.y0=this.yaw;st.p0=this.pitch;const p=this.host.position();
                    st.y1=a.yaw??(a.dir?yawFor(a.dir[0],a.dir[1]):a.at?yawFor(a.at[0]-p.x,a.at[2]-p.z):this.yaw);
                    st.p1=a.pitch??(a.at?Math.atan2(a.at[1]-(p.y+1.6),Math.hypot(a.at[0]-p.x,a.at[2]-p.z)):this.pitch);}
                const sec=a.seconds??2,u=ease(Math.min(1,this.stepT/sec));
                this.yaw=wrap(st.y0!+wrap(st.y1!-st.y0!)*u);this.pitch=st.p0!+(st.p1!-st.p0!)*u;if(this.host.firstPerson())this.host.look(this.yaw,this.pitch);
                return this.stepT>=sec;
            }
            case 'walk':return this.walk(arg as {path:number[][];run?:boolean;face?:Vec3;lookAhead?:number;pitch?:number;sway?:[number,number]},dt);
            case 'approachDoor':{
                if(!this.door){this.warnings.push('approachDoor without a door');return true;}
                const a=this.door.approach,pt=this.door.point;
                const doneWalk=this.walk({path:[[a.x,a.z]],face:[pt.x,pt.y-.1,pt.z],pitch:-.04},dt,true);
                return doneWalk;
            }
            case 'enterRoom':{
                if(!this.door){this.warnings.push('enterRoom without a door');return true;}
                const a=this.door.approach,pt=this.door.point,dx=pt.x-a.x,dz=pt.z-a.z,l=Math.hypot(dx,dz)||1,dist=(arg as {distance?:number}).distance??5;
                return this.walk({path:[[pt.x+dx/l*.8,pt.z+dz/l*.8],[pt.x+dx/l*dist,pt.z+dz/l*dist]],pitch:(arg as {pitch?:number}).pitch??-.02},dt);
            }
            case 'drive':return this.drive(arg as {path:number[][];speed?:number;stop?:boolean;scale?:number},dt);
            case 'until':{
                const a=arg as {what?:string;max?:number}|string;const what=typeof a==='string'?a:a.what,max=typeof a==='string'?600:(a.max??600);
                if(this.stepT>max){this.warnings.push(`until ${what}: gave up after ${max} s`);return true;}
                if(what==='coaster-done'){if(this.host.coasterRiding())st.seen=1;return st.seen===1&&!this.host.coasterRiding();}
                if(what==='coaster-start')return this.host.coasterRiding();
                return true;
            }
            default:this.warnings.push(`unknown step ${key}`);return true;
        }
    }
    private walk(a:{path:number[][];run?:boolean;face?:Vec3;lookAhead?:number;pitch?:number;sway?:[number,number]},dt:number,arrive=false):boolean{
        const st=this.stepState,p=this.host.position();if(st.i===undefined){st.i=0;this.stuckT=0;this.lastPos.set(p.x,p.y,p.z);}
        const path=a.path;let i=st.i!;
        const px=(k:number)=>path[k]![0]!,pz=(k:number)=>path[k]![path[k]!.length===3?2:1]!;
        while(i<path.length-1&&Math.hypot(px(i)-p.x,pz(i)-p.z)<1.2)i++;st.i=i;
        const dx=px(i)-p.x,dz=pz(i)-p.z,dist=Math.hypot(dx,dz);
        if(i===path.length-1&&dist<(arrive?.25:.6)){
            if(a.face){const y=yawFor(a.face[0]-p.x,a.face[2]-p.z);this.aim(y,a.pitch??0,dt,2.4);return Math.abs(wrap(y-this.yaw))<.02;}
            return true;
        }
        // look where we are going (or at `face`), move toward the next point relative to the view
        // sway: [amplitude rad, period s] — a slow look left and right while walking (eased in over the first second)
        const sway=a.sway?a.sway[0]*Math.sin(2*Math.PI*this.stepT/a.sway[1])*Math.min(1,this.stepT):0;
        const goYaw=yawFor(dx,dz),lookYaw=(a.face?yawFor(a.face[0]-p.x,a.face[2]-p.z):goYaw)+sway;
        this.aim(lookYaw,a.pitch??0,dt);
        const rel=wrap(goYaw-this.yaw),speed=arrive&&dist<1.2?Math.max(.35,dist/1.2):1;
        // stick: y forward, x right (a positive yaw turns left)
        this.pad.stick(-Math.sin(rel)*speed,Math.cos(rel)*speed);
        if(a.run)this.holdKey('ShiftLeft');
        // stuck: no progress for 2.5 s → note it and hop to the target
        const moved=Math.hypot(p.x-this.lastPos.x,p.z-this.lastPos.z);
        if(moved>.3){this.lastPos.set(p.x,p.y,p.z);this.stuckT=0;}else if((this.stuckT+=dt)>2.5){this.warnings.push(`walk stuck at ${p.x.toFixed(1)},${p.z.toFixed(1)} (frame ${this.frame})`);this.stuckT=0;st.i=Math.min(path.length-1,i+1);}
        return false;
    }
    private holdKey(code:string):void{if(!this.keysDown.has(code))document.dispatchEvent(new KeyboardEvent('keydown',{code,key:code,bubbles:true}));this.keysDown.set(code,this.frame+2);}
    /** Drive along `path` ([x, z] or [x, z, speed] points every few metres, from tools/film/roads.py): pure pursuit with the
     * jeep's bicycle geometry and a speed-dependent lookahead, the steering lightly filtered; the speed held by pulsing the
     * throttle (RT) and brake (A) in proportion (a sigma-delta of the wanted acceleration) rather than banging them. */
    private drive(a:{path:number[][];speed?:number;stop?:boolean;scale?:number},dt:number):boolean{
        const j=this.host.jeep();if(!j){this.warnings.push('drive without a jeep');return true;}
        const st=this.stepState,path=a.path,n=path.length;if(st.i===undefined){st.i=0;st.steer=0;st.acc=0;st.bacc=0;}
        // closest point, searched forward from the last one
        let i=st.i!,best=Infinity;
        for(let k=i;k<Math.min(n,i+40);k++){const d=Math.hypot(path[k]![0]!-j.x,path[k]![1]!-j.z);if(d<best){best=d;i=k;}}
        st.i=i;
        // signed cross-track error to the segment around the closest point (positive = the jeep is left of the line)
        const s0=Math.min(i,n-2),ax=path[s0]![0]!,az=path[s0]![1]!,bx=path[s0+1]![0]!,bz=path[s0+1]![1]!,sx=bx-ax,sz=bz-az,sl=Math.hypot(sx,sz)||1;
        const cross=((j.x-ax)*sz-(j.z-az)*sx)/sl;
        this.trackLog.push(+j.x.toFixed(2),+j.z.toFixed(2),+j.speed.toFixed(2),+Math.abs(cross).toFixed(2),+j.y.toFixed(3),+j.fy.toFixed(4));
        const v=Math.max(0,j.speed),L=4+.38*v;
        let k=i,acc=0;while(k<n-1&&acc<L){acc+=Math.hypot(path[k+1]![0]!-path[k]![0]!,path[k+1]![1]!-path[k]![1]!);k++;}
        const tx=path[k]![0]!,tz=path[k]![1]!,dx=tx-j.x,dz=tz-j.z;
        const fl=Math.hypot(j.fx,j.fz)||1,fx=j.fx/fl,fz=j.fz/fl;
        // signed angle to the target, positive = to the left of the nose
        const alpha=-Math.atan2(fx*dz-fz*dx,fx*dx+fz*dz);
        // pure pursuit plus a Stanley term that pulls a lateral offset back onto the line
        // (cross > 0: the jeep is left of the line, so steer right — a negative angle)
        const delta=Math.atan2(2*2.7*Math.sin(alpha),Math.max(4,Math.hypot(dx,dz)))-Math.atan2(.9*cross,v+2);
        const cmd=Math.max(-1,Math.min(1,delta/.576));
        st.steer!+= (cmd-st.steer!)*(1-Math.exp(-dt/.08));
        const scale=a.scale??1,last=i>=n-3;
        let want=(path[i]!.length>2?path[i]![2]!:(a.speed??14))*scale;if(a.speed)want=Math.min(want,a.speed*scale);
        if(last&&a.stop!==false)want=0;
        if(last&&(a.stop===false||v<.5)){this.host.vehicleInput(null,0);return true;}
        // throttle and brake as duty cycles around the wanted speed
        const err=want-v;
        // analog throttle and brake, eased (pulsed full power rocked the chassis), around the wanted speed
        const tw=err>-.3?Math.max(0,Math.min(1,.18+.55*err)):0,bw=err<-1?Math.max(0,Math.min(1,-.35*err-.15)):0;
        st.acc!+=(tw-st.acc!)*(1-Math.exp(-dt/.25));st.bacc!+=(bw-st.bacc!)*(1-Math.exp(-dt/.2));
        // (any brake above zero cuts the engine in RapierVehicle, and an eased brake never decays to exactly 0)
        this.host.vehicleInput(st.acc!,st.bacc!<.02?0:st.bacc!);
        this.pad.button(7,false);this.pad.button(0,false);
        this.pad.stick(-st.steer!,0);
        return false;
    }
}
