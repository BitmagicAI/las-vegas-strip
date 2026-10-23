import type {StreamingWork} from '../StreamingWork.js';
import type { GroundSurfaceIndex } from '../GroundSurfaceIndex.js';
import * as THREE from 'three';
import {mapPoint} from '../geographic/Coordinates.js';
import {Door,DEFAULT_DOOR_OPTIONS} from 'engine/gameplay/doors/Door.js';
import type {DoorOptions} from 'engine/gameplay/doors/Door.js';
import type {EngineLike} from 'types/game.js';
import type {PlayerController} from 'engine/player/PlayerController.js';
import type {GameHUD} from '../GameHUD.js';
import type {StreamedInteriorView} from '../BuildingVisibility.js';
import recipes from './towers.json';
import highrises from './highrise-towers.json';
import landmarks from './landmark-towers.json';
import publicReview from '../public-resorts/review.json';
import {STORY,DOOR_X,localPoint,worldPoint,bayPoint,floorAt,insideTower,roomAt,roomId,roomNumber,roomSeed,guestVisibility,stairVisible} from './HotelLayout.js';
import type {Tower,Point,HotelSet} from './HotelLayout.js';
import {moduleMatrix,stairStopMatrix} from './HotelGeometry.js';
import {HotelTemplates} from './HotelTemplates.js';
import type {ModuleInstance,ModuleName,LightSite} from './HotelTemplates.js';
import {HotelResidency,RoomStateStore} from './HotelResidency.js';
export const HOTEL_TOWERS=[...recipes,...highrises,...landmarks] as Tower[];
const KICK_SECONDS=.34,CLOSE_SECONDS=.6,KICK_ANGLE=1.62;
/** 0→1 with a ~10% overshoot that settles back: a leaf thrown open that bounces off its stop. */
const easeOutBack=(x:number):number=>{const c1=1.5,c3=c1+1,y=x-1;return 1+c3*y*y*y+c1*y*y;};
class GuestDoor extends Door {
    /** The Blender skin's mesh (the Door's own box is invisible on room doors). Not `leaf`: engine 3.1337's Door keeps
     * its kinematic physics leaf in a private field of that name, which a subclass field would overwrite. */
    skin:THREE.Object3D|null=null;
    readonly kickable:boolean;
    private restPos=new THREE.Vector3();private hinge=new THREE.Vector3();private rotation:number;private halfWidth:number;
    /** While kicked, the skin hangs on this hinge pivot instead of the leaf, so the Door's slide (which still moves the
     * collider out of the doorway) never shows. Created per kick, released once the door has swung shut. */
    private pivot:THREE.Group|null=null;
    /** 0 still, 1 kicked open, 2 resting open, 3 swinging shut. */
    private swingPhase=0;private swingT=0;private swingSign=1;private angle=0;private closeFrom=0;private pendingKick=false;
    constructor(engine:EngineLike,options:DoorOptions,private label:string,private ready:()=>boolean,private onSwing:(door:GuestDoor)=>void){
        super(engine,options);
        this.restPos.copy(options.position);this.rotation=options.rotation;this.halfWidth=options.width/2;
        this.hinge.set(Math.cos(this.rotation),0,-Math.sin(this.rotation)).multiplyScalar(-this.halfWidth).add(this.restPos);
        this.kickable=label.startsWith('room ')||label.startsWith('apartment ');
    }
    override open():void{
        if(!this.ready())return;super.open();
        if(this.pendingKick&&this.skin?.parent){
            this.pendingKick=false;this.swingPhase=1;this.swingT=0;
            if(!this.pivot){
                const pivot=this.pivot=new THREE.Group();pivot.name='Kicked door hinge';pivot.position.copy(this.hinge);pivot.rotation.y=this.rotation;
                this.skin.parent.add(pivot);pivot.updateMatrixWorld(true);this.skin.updateMatrixWorld(true);
                for(const c of [...this.skin.children])pivot.attach(c);
            }
            this.onSwing(this);
        }
    }
    override close():void{
        super.close();
        if(this.swingPhase===1||this.swingPhase===2){this.swingPhase=3;this.swingT=0;this.closeFrom=this.angle;this.onSwing(this);}
    }
    override getInteractStartDisplayName():string{return `${this.isOpen()?'close':'open'} ${this.label}`;}
    /** Kicked from `from`: the leaf swings away from the kicker. An unloaded room loads first, then bursts open. */
    kick(from:{x:number;z:number}):boolean{
        if(!this.kickable||!this.skin||this.isOpen()||this.pendingKick)return false;
        const nx=Math.sin(this.rotation),nz=Math.cos(this.rotation);
        this.swingSign=(from.x-this.restPos.x)*nx+(from.z-this.restPos.z)*nz>=0?1:-1;
        this.pendingKick=true;this.open();return true;
    }
    /** Pose the swing for this frame. True once it no longer needs updates. */
    stepSwing(dt:number):boolean{
        const leaf=this.skin,pivot=this.pivot;if(!leaf||!pivot||this.swingPhase===0)return true;
        this.swingT+=dt;
        if(this.swingPhase===1){const x=Math.min(1,this.swingT/KICK_SECONDS);this.angle=KICK_ANGLE*easeOutBack(x);if(x>=1)this.swingPhase=2;}
        else if(this.swingPhase===3){const x=Math.min(1,this.swingT/CLOSE_SECONDS),e=x*x*(3-2*x);this.angle=this.closeFrom*(1-e);if(x>=1){this.swingPhase=0;this.angle=0;}}
        pivot.visible=leaf.visible;pivot.rotation.y=this.rotation+this.swingSign*this.angle;
        if(this.swingPhase!==0)return false;
        // Shut: hand the skin back to the leaf at its closed pose (the slide finished before the swing did).
        leaf.position.copy(this.restPos);leaf.rotation.y=this.rotation;leaf.updateMatrixWorld(true);pivot.updateMatrixWorld(true);
        for(const c of [...pivot.children])leaf.attach(c);
        pivot.removeFromParent();this.pivot=null;return true;
    }
    override dispose():void{super.dispose();this.pivot?.removeFromParent();this.pivot=null;this.skin=null;}
}
interface DoorHandle {door:GuestDoor;visuals:THREE.Object3D[];point:THREE.Vector3;closingUntil:number;
    /** Room doors: where to stand in the corridor to kick it (1.2 m out, floor level). */
    approach?:THREE.Vector3;
    /** Room doors: build the room now (a loading job) without opening the door, so a kick lands at once. */
    prepare?:()=>void}
/** A closed guest-room door the player can kick (see DoorKick). */
export type KickableDoor=DoorHandle;
interface Chunk {tower:Tower;floor:number;modules:ModuleInstance[];doors:DoorHandle[];labels:THREE.Mesh[];dispose:()=>void}
interface Room {id:string;bay:number;side:number;module:ModuleInstance;door:DoorHandle;lastNear:number;closedAt:number;visited:boolean}
interface GuestFloor extends Chunk {rooms:Map<string,Room>}

/** Only the current landing's corridor and opened rooms exist. Geometry is shared;
 * colliders/interactables, light slots and label textures have explicit lifetimes. */
export class HotelStreaming {
    private templates:HotelTemplates;
    private ground:Chunk[]=[];
    private lazyResidents=new Map<string,{lastNear:number;lobby:ModuleInstance;door:DoorHandle}>();
    private corePending=new Set<string>();
    private entries:{tower:Tower;module:ModuleInstance}[]=[];
    private closures:{tower:Tower;top:ModuleInstance;bottom:ModuleInstance}[]=[];
    private stairs=new HotelResidency<Chunk>(5,8,c=>c.dispose());
    private floors=new HotelResidency<GuestFloor>(2,10,c=>c.dispose());
    /** Kicked doors whose leaf is posed every frame (a handful at most). */
    private swinging=new Set<GuestDoor>();
    private state:RoomStateStore;
    private lightPool:THREE.PointLight[]=[];
    private now=0;
    private active:Tower|null=null;
    private currentFloor=0;
    private currentRoom:string|null=null;
    private lastInfo='';
    private status:HTMLDivElement|null=null;
    private reviewControls:HTMLDivElement|null=null;
    private disposed=false;
    private debugAt=performance.now();
    private debugText='';
    private restoreReviewRender:(()=>void)|null=null;
    /** Local filming: a floor and one room kept resident (and the room built) while a camera run passes through them,
     * so nothing loads mid-take (a load holds the game, which a recording shows as a freeze). */
    private pin:{tower:Tower;floor:number;room:string}|null=null;
    private debugRender={calls:0,triangles:0};
    constructor(private engine:EngineLike,private controller:PlayerController,private hud:GameHUD,groundSurfaces:GroundSurfaceIndex,private loading:StreamingWork,private reviewCamera?:(yaw:number,pitch?:number)=>void){
        this.templates=new HotelTemplates(engine,groundSurfaces,loading);
        let storage:Storage|null=null;try{storage=localStorage;}catch{}
        this.state=new RoomStateStore(storage);
    }
    async load():Promise<void>{
        await this.templates.load();
        if(this.disposed){this.templates.dispose();return;}
        this.ground=HOTEL_TOWERS.filter(t=>!t.lazy).map(t=>this.makeStair(t,0));
        this.entries=HOTEL_TOWERS.filter(t=>!t.lazy).map(t=>({tower:t,module:this.templates.instantiate(`${t.set}-entry`,this.matrix(t,{x:0,y:0,z:0},0,true))}));
        this.closures=HOTEL_TOWERS.filter(t=>!t.lazy).map(t=>({tower:t,
            top:this.templates.instantiate(`${t.set}-closure`,this.matrix(t,{x:0,y:0,z:0}),false),
            bottom:this.templates.instantiate(`${t.set}-closure`,this.matrix(t,{x:0,y:0,z:0}),false)}));
        for(const c of this.closures){c.top.root.visible=false;c.bottom.root.visible=false;}
        // Fixed pool avoids a changing number of renderer lights during exploration.
        for(let i=0;i<8;i++){const l=new THREE.PointLight(0xffffff,0,12,2);this.engine.scene!.add(l);this.lightPool.push(l);}
        // Interior modules see only these eight, plus sun, sky and ambient (see InteriorLighting).
        this.templates.setInteriorLights(this.lightPool);
        this.hud.createIconText('hotel-address',{anchor:'top-left',icon:'',text:''});
        if(new URLSearchParams(location.search).has('hotelDebug')){
            const scene=this.engine.scene!,previous=scene.onAfterRender;
            scene.onAfterRender=(...args)=>{
                previous.apply(scene,args);
                if(args[2]!==this.engine.camera)return;
                const render=this.engine.renderer!.info.render as {calls:number;drawCalls?:number;triangles:number};
                this.debugRender={calls:render.drawCalls??render.calls,triangles:render.triangles};
            };
            this.restoreReviewRender=()=>{scene.onAfterRender=previous;};
            this.status=document.createElement('div');this.status.id='hotel-stream-stats';
            this.status.style.cssText='position:absolute;left:18px;top:58px;color:#e5d6b9;background:#162127dd;padding:10px;font:12px monospace;pointer-events:none';document.body.appendChild(this.status);
            this.reviewControls=document.createElement('div');
            this.reviewControls.style.cssText='position:absolute;left:18px;bottom:65px;display:flex;flex-wrap:wrap;max-width:95vw;gap:6px';
            const resort=document.createElement('select');resort.id='hotel-review-property';resort.setAttribute('aria-label','Review resort');
            for(const t of HOTEL_TOWERS){const option=document.createElement('option');option.value=t.id;option.textContent=t.name;resort.appendChild(option);}
            this.reviewControls.appendChild(resort);
            if(new URLSearchParams(location.search).has('publicReview') && ['localhost','127.0.0.1'].includes(location.hostname)){
                const publicArea=document.createElement('select');publicArea.id='public-review-area';publicArea.setAttribute('aria-label','Review public area');
                for(const shot of publicReview){const option=document.createElement('option');option.value=shot.name;option.textContent=shot.name;publicArea.appendChild(option);}
                const inspect=document.createElement('button');inspect.textContent='Inspect public area';
                inspect.onclick=()=>{const shot=publicReview.find(s=>s.name===publicArea.value)!;
                    this.loading.enqueue('public-architecture-review',shot.name,()=>{
                        const x=shot.position[0]!,z=shot.position[2]!;
                        const tx=shot.target[0]!,ty=shot.target[1]!,tz=shot.target[2]!;
                        this.controller.teleportTo(x,.25,z);
                        this.reviewCamera?.(Math.atan2(x-tx,z-tz),-Math.atan2(ty-1.95,Math.hypot(tx-x,tz-z)));
                    });
                };this.reviewControls.append(publicArea,inspect);
            }
            for(const [title,room] of [['Inspect entrance','entrance'],['Inspect lobby','lobby'],['Inspect hallway','corridor'],['Inspect room','room']] as const){
                const button=document.createElement('button');button.textContent=title;button.onclick=()=>{
                    const t=HOTEL_TOWERS.find(t=>t.id===resort.value)!;
                    this.loading.enqueue('hotel-property-review',t.name,async()=>{
                        const p=await this.reviewPosition(t.id,room==='entrance'||room==='lobby'?0:t.firstGuestFloor,room==='room'?0:null,room);
                        if(p){this.controller.teleportTo(p.x,p.y,p.z);this.reviewCamera?.(p.yaw);}
                    });
                };this.reviewControls.appendChild(button);
            }
            for(const [label,step] of [['Floor up',1],['Floor down',-1],['Enter sample room',0],['Return to stairs',2],['Leave hotel',3],['Stair turn',4],['Entry door',5],['Casino',6],['Lobby far',7],['Lobby near',8],['Upper flight',9]] as const){
                const button=document.createElement('button');button.textContent=label;button.onclick=()=>{
                    if(step===3){this.controller.teleportTo(...mapPoint([-38,.25,7],'sanctuary'));return;}
                    const bookmark=new URLSearchParams(location.search).get('hotel');
                    const t=this.active??HOTEL_TOWERS.find(t=>t.id===bookmark)??HOTEL_TOWERS[0]!;
                    if(step===5){const door=this.ground.find(c=>c.tower.id===t.id)?.doors[0]?.door;if(door)door.isOpen()?door.close():door.open();return;}
                    if(step===4 || step===6 || step===7 || step===8 || step===9){
                        let local:Point;
                        if(step===4 || step===9){local=this.stairPoint(t,this.currentFloor);local.x+=step===4?-1.65:1.65;local.y+=step===4?1.85:3.14;local.z+=step===4?3.6:-1.1;}
                        else local={x:0,y:.05,z:step===7?-19:step===8?-15:-12};
                        const p=worldPoint(t,local);
                        this.loading.enqueue('hotel-review','hotel area',()=>{this.update(0,p,true);this.controller.teleportTo(p.x,p.y,p.z);});return;
                    }
                    const floor=step===1||step===-1?Math.max(0,Math.min(t.floors-1,this.currentFloor+step)):this.currentFloor;
                    this.loading.enqueue('hotel-review',step===0?'guest room':`level ${floor+1}`,async()=>{
                        const p=await this.reviewPosition(t.id,floor,step===0?0:null);
                        if(p){this.controller.teleportTo(p.x,p.y,p.z);this.reviewCamera?.(p.yaw);}
                    });
                };this.reviewControls.appendChild(button);
            }
            document.body.appendChild(this.reviewControls);
        }
        console.info(`[HotelStreaming] Ready: ${HOTEL_TOWERS.length} tower recipes; property-specific lazy guest sets; no guest rooms resident`);
    }
    get stats(){return {stairs:this.ground.length+this.stairs.entries.size,
        corridors:this.floors.entries.size,rooms:[...this.floors.entries.values()].reduce((n,f)=>n+f.value.rooms.size,0)};}
    private prefix(t:Tower):HotelSet{return t.set;}
    private matrix(t:Tower,p:Point,rotation=0,shear=false):THREE.Matrix4{
        return moduleMatrix(t,p,rotation,shear);
    }
    private stairPoint(t:Tower,floor:number):Point{return {x:(t.lean?.[0]??0)*floor*STORY,y:floor*STORY,z:(t.lean?.[1]??0)*floor*STORY};}
    private module(t:Tower,kind:'stair'|'corridor'|'room'|'cap',p:Point,rotation=0):ModuleInstance{
        return this.templates.instantiate(`${this.prefix(t)}-${kind}` as ModuleName,this.matrix(t,p,rotation,kind==='stair'));
    }
    private label(chunk:Chunk,words:string,p:Point,yaw=0,width=1.3,height=.32):void{
        const canvas=document.createElement('canvas');canvas.width=512;canvas.height=128;
        const ctx=canvas.getContext('2d')!;ctx.fillStyle=chunk.tower.kind==='apartment'?'#1b3038':'#302519';ctx.fillRect(0,0,512,128);
        const bellagioNumber=chunk.tower.set==='bellagio' && /^\d+$/.test(words);
        if(bellagioNumber){ctx.fillStyle='#beb3a0';ctx.fillRect(0,0,512,128);}
        ctx.strokeStyle=bellagioNumber?'#827359':'#ac9260';ctx.lineWidth=5;ctx.strokeRect(5,5,502,118);ctx.fillStyle=bellagioNumber?'#262321':'#efdfb5';ctx.font=bellagioNumber?'48px serif':'36px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(words,256,66,480);
        const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
        const mesh=new THREE.Mesh(new THREE.PlaneGeometry(width,height),new THREE.MeshBasicMaterial({map:texture,toneMapped:false}));
        mesh.userData.perfOwner='Guest · doors and signs';mesh.userData.perfKind='interior';
        mesh.matrixAutoUpdate=false;mesh.matrix.copy(this.matrix(chunk.tower,p,yaw));this.engine.scene!.add(mesh);chunk.labels.push(mesh);
    }
    private door(t:Tower,p:Point,yaw:number,width:number,label:string,onOpen:()=>void,ready:()=>boolean=()=>true,height=2.65):DoorHandle{
        const w=worldPoint(t,p),point=new THREE.Vector3(w.x,w.y,w.z);
        const direction=new THREE.Vector3(Math.cos(yaw),0,-Math.sin(yaw)).transformDirection(this.matrix(t,{x:0,y:0,z:0}));
        const rotation=Math.atan2(-direction.z,direction.x);
        const basis=new THREE.Vector3(Math.cos(yaw),0,-Math.sin(yaw));
        if(t.linear){const [a,b,c,d]=t.linear;basis.set(a*Math.cos(yaw)-b*Math.sin(yaw),0,c*Math.cos(yaw)-d*Math.sin(yaw));}
        const widthScale=basis.length();
        const before=new Set(this.engine.scene!.children);
        const door=new GuestDoor(this.engine,{...DEFAULT_DOOR_OPTIONS,position:point,rotation,width:width*widthScale,height,thickness:.13,slideDistance:(width+.08)*widthScale,slideDurationMs:550,onOpen,onClose:()=>{handle.closingUntil=this.now+.6;}},label,ready,d=>this.swinging.add(d));
        const visuals=this.engine.scene!.children.filter(o=>!before.has(o));
        door.skin=visuals.find(o=>o instanceof THREE.Mesh)??null;
        for(const o of visuals){o.userData.perfOwner='Guest · doors and signs';o.userData.perfKind='interior';}
        if(t.set!=='veer' && (label.startsWith('room ')||label.startsWith('apartment '))){
            // Door owns this mesh, its interaction target and the one collider.
            // Attach the shared Blender skin to it, so handles/panels move with
            // the leaf. Keep the owned material for Door.dispose to release.
            const leaf=visuals.find(o=>o instanceof THREE.Mesh);
            if(!(leaf instanceof THREE.Mesh))throw new Error('Guest door did not create its visual mesh');
            for(const mat of Array.isArray(leaf.material)?leaf.material:[leaf.material])mat.visible=false;
            const skin=this.templates.doorVisual(t.set);skin.scale.x=widthScale;leaf.add(skin);
        }
        const handle={door,point,visuals,closingUntil:0};return handle;
    }
    private chunk(tower:Tower,floor:number):Chunk{
        const chunk:Chunk={tower,floor,modules:[],doors:[],labels:[],dispose:()=>{
            for(const d of chunk.doors)d.door.dispose();for(const m of chunk.modules)m.dispose();
            for(const l of chunk.labels){l.removeFromParent();l.geometry.dispose();const mat=l.material as THREE.MeshBasicMaterial;mat.map?.dispose();mat.dispose();}
        }};return chunk;
    }
    private makeStair(t:Tower,floor:number):Chunk{
        const chunk=this.chunk(t,floor),p=this.stairPoint(t,floor);
        chunk.modules.push(this.module(t,'stair',p));
        if(floor===t.floors-1)chunk.modules.push(this.templates.instantiate(`${this.prefix(t)}-cap`,stairStopMatrix(t,p)));
        const doorPoint={x:p.x,y:p.y+1.325,z:p.z-4.98};
        if(floor===0 || floor>=t.firstGuestFloor){
            const d=this.door(t,doorPoint,0,1.78,floor===0?`${t.name} stairs`:`floor ${floor+1}`,()=>{},()=>{
                if(floor<t.firstGuestFloor || this.floors.entries.has(`${t.id}/${floor}`))return true;
                this.loading.enqueue(`floor:${t.id}/${floor}`,`${t.name} · floor ${floor+1}`,async()=>{await this.templates.ensureGuest(t.set);if(this.disposed)return;this.ensureFloor(t,floor);d.door.open();});return false;
            });
            chunk.doors.push(d);
        }else{
            // Podium/service storeys have a sealed landing rather than doors into voids.
            chunk.modules.push(this.module(t,'cap',{x:p.x,y:p.y,z:p.z-2.56}));
        }
        // Service landings have no public entrance/sign above the lobby door.
        if(floor===0 || floor>=t.firstGuestFloor){
            const bellagioEntry=floor===0 && t.set==='bellagio';
            this.label(chunk,floor===0?t.name.toUpperCase():`LEVEL ${floor+1}`,{x:p.x,y:p.y+(bellagioEntry?4.7:2.99),z:p.z-(bellagioEntry?5.60:floor===0?5.42:5.16)},Math.PI,bellagioEntry?3.4:2.55,.38);
        }
        this.label(chunk,`LEVEL ${floor+1}  /  ${floor===t.floors-1?'TOP FLOOR':'STAIRS'}`,{x:p.x-3.37,y:p.y+1.8,z:p.z-3.6},Math.PI/2,1.7,.38);
        return chunk;
    }
    private makeFloor(t:Tower,floor:number):GuestFloor{
        const chunk=this.chunk(t,floor) as GuestFloor;chunk.rooms=new Map();
        const dispose=chunk.dispose;chunk.dispose=()=>{for(const r of chunk.rooms.values())r.module.dispose();chunk.rooms.clear();dispose();};
        for(let bay=0;bay<t.bays;bay++){
            const p=bayPoint(t,floor,bay);chunk.modules.push(this.module(t,'corridor',p));
            for(const side of [-1,1]){
                const id=roomId(t,floor,bay,side),number=roomNumber(floor,bay,side),doorPoint={x:p.x+side*DOOR_X,y:p.y+1.325,z:p.z};
                const d=this.door(t,doorPoint,side*Math.PI/2,1.3,`${t.kind==='apartment'?'apartment':'room'} ${number}`,()=>{},()=>{
                    if(chunk.rooms.has(id))return true;
                    this.loading.enqueue(`room:${id}`,`${t.kind==='apartment'?'apartment':'room'} ${number}`,async()=>{await this.templates.ensureGuest(t.set);if(this.disposed)return;this.openRoom(chunk,bay,side,d);d.door.open();});return false;
                });
                const a=worldPoint(t,{x:p.x+side*(DOOR_X-1.2),y:p.y,z:p.z});d.approach=new THREE.Vector3(a.x,a.y,a.z);
                d.prepare=()=>{if(chunk.rooms.has(id))return;this.loading.enqueue(`room:${id}`,`${t.kind==='apartment'?'apartment':'room'} ${number}`,async()=>{await this.templates.ensureGuest(t.set);if(this.disposed)return;this.openRoom(chunk,bay,side,d);});};
                chunk.doors.push(d);
                this.label(chunk,number,{x:p.x+side*(t.set==='bellagio'?1.405:1.72),y:p.y+(t.set==='bellagio'?1.62:1.8),z:p.z+(t.set==='bellagio'?1.15:.92)},-side*Math.PI/2,t.set==='bellagio'?.32:.48,t.set==='bellagio'?.15:.22);
            }
        }
        // Reuse the sealed landing panel as a corridor end wall. Local scale is
        // authored in Blender; the cap is wider than the corridor, behind rooms.
        const p=bayPoint(t,floor,t.bays-1);
        if(t.set==='bellagio'){
            chunk.modules.push(this.templates.instantiate('bellagio-corridor-end',this.matrix(t,{x:p.x,y:p.y,z:p.z-2.96})));
            this.label(chunk,`GUEST ROOMS  /  LEVEL ${floor+1}`,{x:p.x,y:p.y+2.97,z:p.z-2.935},0,1.65,.16);
        }else{
            chunk.modules.push(this.module(t,'cap',{x:p.x,y:p.y,z:p.z-3.15+2.42}));
            this.label(chunk,`${this.prefix(t).toUpperCase()}  /  LEVEL ${floor+1}`,{x:p.x,y:p.y+2,z:p.z-3.04},0,2.5,.4);
        }
        console.info(`[HotelStreaming] Created corridor ${t.id}/${floor}; ${t.bays*2} doors`);return chunk;
    }
    private ensureFloor(t:Tower,floor:number):GuestFloor{
        const key=`${t.id}/${floor}`;
        const required=new Map<string,()=>GuestFloor>();
        if(this.active && this.currentFloor>=this.active.firstGuestFloor){
            const current=`${this.active.id}/${this.currentFloor}`;
            if(current!==key && this.floors.entries.has(current))required.set(current,()=>this.makeFloor(this.active!,this.currentFloor));
        }
        required.set(key,()=>this.makeFloor(t,floor));this.floors.reconcile(required,this.now);return this.floors.entries.get(key)!.value;
    }
    private openRoom(chunk:GuestFloor,bay:number,side:number,d:DoorHandle):void{
        const t=chunk.tower,id=roomId(t,chunk.floor,bay,side);if(chunk.rooms.has(id))return;
        const p=bayPoint(t,chunk.floor,bay);p.x+=side*DOOR_X;
        const module=this.module(t,'room',p,side>0?0:Math.PI);
        // Stable identity is available to future furnishing/loot variants.
        module.root.userData.roomSeed=roomSeed(id);
        chunk.rooms.set(id,{id,bay,side,module,door:d,lastNear:this.now,closedAt:0,visited:false});
        console.info(`[HotelStreaming] Created ${id}`);
    }
    private inLobby(t:Tower,p:Point):boolean {
        if(!t.lazy || t.lobbyFront===undefined || p.y<-.3 || p.y>6.7)return false;
        const front=-5.25-6*t.bays;
        return p.z>t.lobbyFront-.25 && p.z< -5.25 && Math.abs(p.x)<(p.z<front?1.9:9.3);
    }
    private async prepareCore(t:Tower):Promise<void>{
        if(!t.lazy || this.lazyResidents.has(t.id))return;
        await Promise.all([this.templates.ensureCore(t.set),this.templates.ensureLobby(t.id)]);
        if(this.disposed || this.lazyResidents.has(t.id))return;
        this.ground.push(this.makeStair(t,0));
        this.entries.push({tower:t,module:this.templates.instantiate(`${t.set}-entry`,this.matrix(t,{x:0,y:0,z:0},0,true))});
        this.closures.push({tower:t,top:this.templates.instantiate(`${t.set}-closure`,this.matrix(t,{x:0,y:0,z:0}),false),bottom:this.templates.instantiate(`${t.set}-closure`,this.matrix(t,{x:0,y:0,z:0}),false)});
        const lobby=this.templates.instantiate(`${t.id}-lobby`,this.matrix(t,{x:0,y:0,z:0}));
        const door=this.door(t,{x:0,y:2.15,z:t.lobbyFront!},0,2.5,t.name+' entrance',()=>{},()=>true,4.3);
        for(const o of door.visuals)if(o instanceof THREE.Mesh){
            // The engine door uses its own classed wood material (not necessarily
            // MeshStandardMaterial). Replace that owned material instead of silently
            // skipping the glazing when the engine chooses a node material.
            for(const material of Array.isArray(o.material)?o.material:[o.material])material.dispose();
            o.material=new THREE.MeshStandardMaterial({color:0x73959b,transparent:true,opacity:.24,depthWrite:false,metalness:.3,roughness:.2});
        }
        this.lazyResidents.set(t.id,{lastNear:this.now,lobby,door});
    }
    private evictCore(t:Tower):void {
        const r=this.lazyResidents.get(t.id);if(!r)return;
        r.lobby.dispose();r.door.door.dispose();this.lazyResidents.delete(t.id);
        for(const c of this.ground.filter(c=>c.tower.id===t.id))c.dispose();this.ground=this.ground.filter(c=>c.tower.id!==t.id);
        for(const e of this.entries.filter(c=>c.tower.id===t.id))e.module.dispose();this.entries=this.entries.filter(c=>c.tower.id!==t.id);
        for(const c of this.closures.filter(c=>c.tower.id===t.id)){c.top.dispose();c.bottom.dispose();}this.closures=this.closures.filter(c=>c.tower.id!==t.id);
        this.templates.releaseLazy(t.set,t.id);
    }
    update(dt:number,player:Point,prepared=false):void{
        for(const d of this.swinging)if(d.stepSwing(Math.min(dt,.25)))this.swinging.delete(d);
        if(!this.ground.length)return;this.now+=Math.min(dt,.25);
        const matches=HOTEL_TOWERS.map(t=>({t,p:localPoint(t,player)}));
        for(const {t,p} of matches){
            if(!t.lazy)continue;
            // (while a film run pins a tower, only that one streams: another lobby loading mid-take would hold the game)
            const near=this.pin?this.pin.tower===t:insideTower(t,p)||this.inLobby(t,p)||p.y<8 && Math.abs(p.x)<28 && p.z>(t.lobbyFront??-30)-28 && p.z<28;
            const resident=this.lazyResidents.get(t.id);
            if(near){
                if(resident)resident.lastNear=this.now;
                else if(!this.corePending.has(t.id)){
                    this.corePending.add(t.id);
                    this.loading.enqueue('tower-core:'+t.id,t.name+' entrance and stairs',async()=>{try{await this.prepareCore(t);}finally{this.corePending.delete(t.id);}});
                }
            }else if(resident && this.now-resident.lastNear>30)this.evictCore(t);
        }
        const ready=matches.filter(({t})=>!t.lazy || this.lazyResidents.has(t.id));
        const occupied=ready.find(({t,p})=>insideTower(t,p));
        const match=occupied??ready.find(({p})=>p.y>=-.5 && p.y<2 && Math.hypot(p.x,p.z+5)<12);
        this.active=match?.t??null;this.currentFloor=match?floorAt(match.t,match.p):0;
        this.currentRoom=null;
        if(match){const r=roomAt(match.t,match.p);if(r)this.currentRoom=roomId(match.t,r.floor,r.bay,r.side);}
        const pin=this.pin;
        const requiredStairs=new Map<string,()=>Chunk>();
        if(match)for(let f=Math.max(1,this.currentFloor-1);f<=Math.min(match.t.floors-1,this.currentFloor+2);f++){
            const t=match.t;requiredStairs.set(`${t.id}/${f}`,()=>this.makeStair(t,f));
        }
        // a pinned camera run climbs from the lobby to the pinned floor: every storey it passes is built before the take
        if(pin)for(let f=1;f<=Math.min(pin.tower.floors-1,pin.floor+2)&&requiredStairs.size<this.stairs.capacity;f++){
            const t=pin.tower;requiredStairs.set(`${t.id}/${f}`,()=>this.makeStair(t,f));
        }
        const requiredFloors=new Map<string,()=>GuestFloor>();
        if(pin)requiredFloors.set(`${pin.tower.id}/${pin.floor}`,()=>this.makeFloor(pin.tower,pin.floor));
        if(match && this.currentFloor>=match.t.firstGuestFloor){
            const t=match.t,f=this.currentFloor,p=match.p;
            // Preload behind the stair door while approaching the level landing.
            const landing=Math.abs(p.y-f*STORY)<.8;
            if(landing||this.currentRoom||p.z<-5)requiredFloors.set(`${t.id}/${f}`,()=>this.makeFloor(t,f));
        }
        const missing=[...requiredStairs.keys()].some(k=>!this.stairs.entries.has(k)) || [...requiredFloors.keys()].some(k=>!this.floors.entries.has(k));
        if(missing && !prepared){
            const p={...player};
            // (a pinned film run can need residency before the camera reaches the tower: no match yet)
            const t=match?.t??pin!.tower;
            this.loading.enqueue('hotel-residency',`${t.name} · level ${this.currentFloor+1}`,async()=>{if(requiredFloors.size)await this.templates.ensureGuest(t.set);if(!this.disposed)this.update(0,p,true);});
            return;
        }
        this.stairs.reconcile(requiredStairs,this.now);
        this.floors.reconcile(requiredFloors,this.now);
        const lightSites:LightSite[]=[];
        // These four small shared shells are independent of the detailed-floor
        // cache. Keep every entrance consistent while the player is in a lobby.
        for(const entry of this.entries){
            entry.module.root.visible=!occupied || (entry.tower.id===occupied.t.id && this.currentFloor<occupied.t.firstGuestFloor);
            if(entry.module.root.visible && this.active?.id===entry.tower.id)lightSites.push(...entry.module.lights);
        }
        const entrance=this.ground.find(c=>c.tower.id===this.active?.id)?.doors[0];
        for(const c of [...this.ground,...[...this.stairs.entries.values()].map(e=>e.value)]){
            const sameTower=this.active?.id===c.tower.id;
            const visible=stairVisible(c.floor,this.currentFloor,sameTower,!!occupied,!!entrance && this.doorReveals(entrance));
            this.showChunk(c,visible);
            if(visible && sameTower)for(const m of c.modules)lightSites.push(...m.lights);
        }
        // Opaque render-only boundaries cap the resident shaft, always at
        // least two storeys above the player. They never intersect the route.
        for(const c of this.closures){
            const active=c.tower.id===this.active?.id && (!!occupied || !!entrance && this.doorReveals(entrance));
            c.top.root.visible=active;c.bottom.root.visible=active;
            if(active){
                const upper=Math.min(c.tower.floors,this.currentFloor+3);
                const lower=Math.max(0,this.currentFloor-1);
                for(const [m,f] of [[c.top,upper],[c.bottom,lower]] as const){
                    // 3 cm clear of the landing slab it sits on: flush, its top (the wall's wallpaper) and the landing's
                    // stone fought on screen, the floor flickering striped as you entered the stairs (2026-10-08 film)
                    const p=this.stairPoint(c.tower,f);p.y+=m===c.bottom?-.03:.03;
                    m.root.matrix.copy(this.matrix(c.tower,p,0,true));
                    m.root.matrixWorldNeedsUpdate=true;
                }
            }
        }
        let rooms=0;
        for(const e of this.floors.entries.values()){
            // the floor above or below shows while its stair door is open: climbing the last flight toward an open
            // landing door, the corridor behind it was hidden until the player reached its floor (sky through the door)
            const c=e.value,stairDoor=Math.abs(c.floor-this.currentFloor)===1?this.stairs.entries.get(`${c.tower.id}/${c.floor}`)?.value.doors[0]:undefined;
            const visible=this.active?.id===c.tower.id && (c.floor===this.currentFloor || !!stairDoor && this.doorReveals(stairDoor));this.showChunk(c,visible);
            if(visible)for(const m of c.modules)lightSites.push(...m.lights);
            for(const [id,r] of c.rooms){
                const occupied=id===this.currentRoom,near=visible&&Math.hypot(player.x-r.door.point.x,player.z-r.door.point.z)<5 || this.pin?.room===id;
                if(occupied||near){r.lastNear=this.now;r.closedAt=0;}
                else if(this.now-r.lastNear>3 && r.door.door.isOpen())r.door.door.close();
                if(occupied&&!r.visited){const s=this.state.get(id);this.state.set(id,{...s,visited:true,visits:s.visits+1});r.visited=true;}
                const open=r.door.door.isOpen();
                if(!occupied&&!open){if(!r.closedAt)r.closedAt=this.now;if(this.now-r.closedAt>2 && this.now-r.lastNear>8){r.module.dispose();c.rooms.delete(id);continue;}}
                r.module.root.visible=visible&&(occupied||open||this.now-r.closedAt<.7);
                if(r.module.root.visible)lightSites.push(...r.module.lights);rooms++;
            }
        }
        for(const [id,r] of this.lazyResidents){
            const t=HOTEL_TOWERS.find(t=>t.id===id)!,p=localPoint(t,player);
            const visible=(!occupied || occupied.t.id===id && this.currentFloor===0) && p.y<10;
            r.lobby.root.visible=visible;for(const v of r.door.visuals)v.visible=visible;
            if(visible && (this.inLobby(t,p) || Math.hypot(p.x,p.z-t.lobbyFront!)<15))lightSites.push(...r.lobby.lights);
            if(Math.hypot(p.x,p.z-t.lobbyFront!)<3 && p.y<3 && !r.door.door.isOpen())r.door.door.open();
            // (not during a pinned film run: a camera opens it from further away, and closing it fought that every frame)
            if(!this.pin && Math.hypot(p.x,p.z-t.lobbyFront!)>8 && r.door.door.isOpen())r.door.door.close();
        }
        this.templates.trim();
        const listener=new THREE.Vector3(player.x,player.y+1.6,player.z);
        lightSites.sort((a,b)=>a.position.distanceToSquared(listener)-b.position.distanceToSquared(listener));
        for(let i=0;i<this.lightPool.length;i++){const l=this.lightPool[i]!,s=lightSites[i];l.intensity=s?.intensity??0;if(s){l.position.copy(s.position);l.color.set(s.color);l.distance=s.distance;}}
        const info=occupied?`${occupied.t.name} · ${this.currentFloor===0?'Stair lobby':`Level ${this.currentFloor+1}`}${this.currentRoom?' · '+(occupied.t.kind==='apartment'?'Apartment ':'Room ')+roomNumber(this.currentFloor,roomAt(occupied.t,occupied.p)!.bay,roomAt(occupied.t,occupied.p)!.side):''}`:'';
        if(info!==this.lastInfo){this.hud.updateIconText('hotel-address',{text:info});this.lastInfo=info;}
        if(this.status){
            if(performance.now()-this.debugAt>2000){
                let batches=0,triangles=0,lights=0;
                this.engine.scene!.traverseVisible(o=>{
                    if(o instanceof THREE.Mesh && o.userData.visibilityKind){batches++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position!.count)/3;}
                    if(o instanceof THREE.Light && o.intensity>0)lights++;
                });
                this.debugText=`draw calls ${this.debugRender.calls} | submitted triangles ${this.debugRender.triangles} | enabled level ${batches} batches / ${Math.round(triangles)} triangles | active lights ${lights} | capsule ${this.controller.getCapsuleHeight().toFixed(2)} m`;
                this.debugAt=performance.now();
            }
            this.status.textContent=`HOTEL STREAM | stair sections ${this.ground.length+this.stairs.entries.size}/${this.ground.length+5} | corridors ${this.floors.entries.size}/2 | rooms ${rooms} | physics bodies ${this.engine.physicsWorld!.getStats().rigidBodyCount} | ${this.debugText}`;
        }
    }
    /** The nearest closed guest-room door within kicking reach in front of the player (`forward`: horizontal facing). */
    kickTarget(player:Point,forward:{x:number;z:number}):KickableDoor|null{
        let best:KickableDoor|null=null,bestD=2.6*2.6;
        const fl=Math.hypot(forward.x,forward.z)||1,fx=forward.x/fl,fz=forward.z/fl;
        for(const e of this.floors.entries.values())for(const d of e.value.doors){
            if(!d.door.kickable||d.door.isOpen())continue;
            const dx=d.point.x-player.x,dz=d.point.z-player.z,d2=dx*dx+dz*dz;
            if(d2>=bestD||Math.abs(d.point.y-1.325-player.y)>1.6)continue;
            const dl=Math.sqrt(d2)||1;if((dx*fx+dz*fz)/dl<.5)continue;
            best=d;bestD=d2;
        }
        return best;
    }
    kick(target:KickableDoor,from:Point):boolean{return target.door.kick(from);}
    /** Local filming: keep `floor` of tower `id` and its room (bay, side) resident and built; null releases. Resolves
     * once the core, the corridor and the room exist (call it before a take and wait for streaming to go idle). */
    async filmPin(id:string|null,floor=0,bay=0,side=1):Promise<boolean>{
        if(id===null){this.pin=null;return true;}
        const t=HOTEL_TOWERS.find(t=>t.id===id);if(!t||floor<t.firstGuestFloor||floor>=t.floors||bay<0||bay>=t.bays)return false;
        await this.prepareCore(t);await this.templates.ensureGuest(t.set);if(this.disposed)return false;
        this.pin={tower:t,floor,room:roomId(t,floor,bay,side)};
        const c=this.ensureFloor(t,floor),d=c.doors[bay*2+(side>0?1:0)]!;this.openRoom(c,bay,side,d);
        return true;
    }
    /** The pinned room's door label ('room 301'), as GuestDoor names it. */
    private pinnedRoomLabel():string{
        const p=this.pin;if(!p)return '';const [, f, bay, side]=p.room.split('/');
        return `${p.tower.kind==='apartment'?'apartment':'room'} ${roomNumber(Number(f),Number(bay),Number(side))}`;
    }
    /** Local filming: open the doors a moving camera is about to pass through (within reach and ahead of it). Room doors
     * swing open (the kick's hinge swing, away from the camera); entrance and stair doors slide as in play. A guest
     * floor's stair door is opened from further away, so its corridor loads (in the background of the climb). */
    filmDoors(camera:Point,forward:Point,speed=0):void{
        // Only doors the camera is about to pass through: at its own height (a stair door a storey up would load that
        // floor mid-take, and a load holds the game), and of the guest rooms only the pinned one (opening the rooms it flies
        // past would load each of them).
        const pinnedRoom=this.pin?.room;
        const visit=(d:DoorHandle,reach:number,room=false,above=2.2)=>{
            if(d.door.isOpen())return;
            if(room&&(!pinnedRoom||d.door.getInteractStartDisplayName().replace(/^(open|close) /,'')!==this.pinnedRoomLabel()))return;
            const dx=d.point.x-camera.x,dy=d.point.y-1.2-camera.y,dz=d.point.z-camera.z,dist=Math.hypot(dx,dy,dz);
            if(dist>reach||dy>2.2||dy< -above||dx*forward.x+dy*forward.y+dz*forward.z<-.3)return;
            if(d.door.kickable)d.door.kick({x:camera.x,z:camera.z});else d.door.open();
        };
        // (a slide takes 0.55 s and a swing 0.34 s: a fast camera needs them started about a second ahead)
        // (a lobby is tall and a camera may swoop through it 4 m up; only floor 0's doors are in this list)
        for(const c of this.ground)for(const d of c.doors)visit(d,Math.max(5.5,1.1*speed),false,4.5);
        for(const e of this.stairs.entries.values())for(const d of e.value.doors)visit(d,Math.max(9,1.1*speed));
        for(const e of this.floors.entries.values())for(const d of e.value.doors)visit(d,Math.max(4.5,.8*speed),true);
        for(const r of this.lazyResidents.values())visit(r.door,Math.max(7,1.1*speed));
    }
    /** Pre-build the room behind a door (by its label, e.g. 'room 2101'); false when no such door is resident. */
    prepareRoom(label:string):boolean{
        for(const e of this.floors.entries.values())for(const d of e.value.doors)if(d.prepare&&d.door.getInteractStartDisplayName().replace(/^(open|close) /,'')===label){d.prepare();return true;}
        return false;
    }
    /** Closed room doors on the resident corridors, with their corridor-side kicking spot (review and filming). */
    kickableDoors():{label:string;point:THREE.Vector3;approach:THREE.Vector3}[]{
        const out:{label:string;point:THREE.Vector3;approach:THREE.Vector3}[]=[];
        for(const e of this.floors.entries.values())for(const d of e.value.doors)if(d.door.kickable&&!d.door.isOpen()&&d.approach)out.push({label:d.door.getInteractStartDisplayName().replace(/^open /,''),point:d.point,approach:d.approach});
        return out;
    }
    private showChunk(c:Chunk,visible:boolean):void{
        for(const m of c.modules)m.root.visible=visible;for(const d of c.doors)for(const v of d.visuals)v.visible=visible;for(const l of c.labels)l.visible=visible;
    }
    getView(player:Point,camera:Point):StreamedInteriorView|null{
        const lobbyTower=HOTEL_TOWERS.find(t=>this.lazyResidents.has(t.id)&&this.inLobby(t,localPoint(t,player)));
        if(lobbyTower){const p=localPoint(lobbyTower,player);return {building:lobbyTower.building,outside:p.z<lobbyTower.lobbyFront!+7,showGround:true};}
        const t=this.active;if(!t)return null;const p=localPoint(t,player);if(!insideTower(t,p))return null;
        const groundDoor=this.ground.find(c=>c.tower.id===t.id)?.doors[0];
        const corridor=this.floors.entries.get(`${t.id}/${this.currentFloor}`)?.value;
        const windowView=!!this.currentRoom || !!corridor && [...corridor.rooms.values()].some(r=>this.doorReveals(r.door));
        return guestVisibility(t,this.currentFloor,p,localPoint(t,camera),!!groundDoor && this.doorReveals(groundDoor),windowView);
    }
    private doorReveals(d:DoorHandle):boolean{return d.door.isOpen() || this.now<d.closingUntil;}
    /** Local review bookmark: prepares collision before moving the review player. */
    async reviewPosition(id:string,floor:number,bay:number|null=null,roomView:string|null=null):Promise<(Point&{yaw:number})|null>{
        const t=HOTEL_TOWERS.find(t=>t.id===id);if(!t || !Number.isInteger(floor) || floor<0 || floor>=t.floors)return null;
        await this.prepareCore(t);
        if(floor>=t.firstGuestFloor)await this.templates.ensureGuest(t.set);if(this.disposed)return null;
        let p=this.stairPoint(t,floor);p.z-=3.6;p.y+=.04;let yaw=t.yaw-(bay===null?0:Math.PI/2);
        if(t.lazy && (roomView==='entrance'||roomView==='lobby')){
            p={x:0,y:.05,z:roomView==='entrance'?t.lobbyFront!-6:-5.25-6*t.bays+2};yaw=t.yaw+Math.PI;
        }
        if(roomView==='corridor' && floor>=t.firstGuestFloor){
            this.ensureFloor(t,floor);p=bayPoint(t,floor,0);p.z+=2.6;p.y+=.05;yaw=t.yaw;
        }
        if(bay!==null && floor>=t.firstGuestFloor && bay>=0 && bay<t.bays){
            const c=this.ensureFloor(t,floor),d=c.doors[bay*2+1]!;this.openRoom(c,bay,1,d);d.door.open();
            p=bayPoint(t,floor,bay);p.x+=DOOR_X+.6;p.y+=.05;
            // Repeatable local architectural review positions, clear of furniture.
            if(t.set==='bellagio' && (roomView==='bedroom'||roomView==='bathroom')){
                p.x+=roomView==='bedroom'?2.85:1.06;p.z+=roomView==='bedroom'?.78:-.77;
                yaw=t.yaw+(roomView==='bedroom'?-1.20:0);
            }
        }
        const w=worldPoint(t,p);this.update(0,w,true);return {...w,yaw};
    }
    dispose():void{
        this.restoreReviewRender?.();
        this.disposed=true;for(const t of HOTEL_TOWERS)if(t.lazy)this.evictCore(t);this.floors.dispose();this.stairs.dispose();for(const c of this.ground)c.dispose();this.ground=[];
        for(const entry of this.entries)entry.module.dispose();this.entries=[];
        for(const c of this.closures){c.top.dispose();c.bottom.dispose();}this.closures=[];
        for(const l of this.lightPool){l.removeFromParent();l.dispose();}this.lightPool=[];this.templates.dispose();this.status?.remove();this.reviewControls?.remove();
    }
}
