/** Compact recipes only. Never enumerate all rooms at startup. Units are metres. */
export interface Point { x: number; y: number; z: number }
export type HotelSet = 'polo'|'linq'|'vanderpump'|'bellagio'|'veer'|'paris'|'caesars'|'cosmopolitan'|'flamingo'|'horseshoe'|'planet-hollywood'|'aria'|'vdara'|'waldorf'|'bellagio-spa'|'mirage'|'treasure-island'|'park-mgm'|'luxor'|'mandalay-bay'|'horseshoe-east'|'encore'|'wynn'|'rio'|'palazzo'|'venetian'|'westgate'|'signature'|'trump'|'mgm-grand'|'new-york'|'w-las-vegas'|'harrahs'|'sky'|'fontainebleau'|'turnberry-place'|'turnberry-towers'|'allure'|'circus-circus'|'strat'|'sahara'|'grand-chateau'|'resorts-world'|'panorama'|'martin'|'springhill'|'elara'|'hgv-boulevard'|'palms';
export interface Tower {
    id: string; name: string; building: string;
    origin: [number, number, number]; yaw: number;
    floors: number; firstGuestFloor: number; bays: number;
    kind: 'room' | 'apartment';
    /** Explicit property set; future hotels must author/select their own assets. */
    set: HotelSet;
    roomDepth?: number;
    lazy?: boolean;
    lobbyFront?: number;
    source?: string;
    /** Horizontal map fit; shared by render meshes, collision, and local queries. */
    linear?: [number,number,number,number];
    /** Horizontal drift per metre of height; stairs follow continuously by shear. */
    lean?: [number, number];
    curve?: number;
}
export const STORY = 3.6;
export const BAY = 6;
export const FIRST_BAY_Z = -8.1;
export const DOOR_X = 1.85;
export const ROOM_DEPTH = 5.4;
/** Property-specific room envelopes; Bellagio's photo-referenced King is deeper. */
export function roomDepth(t:Tower):number { return t.roomDepth ?? (t.set==='bellagio'?8.1:ROOM_DEPTH); }
export function localPoint(t: Tower, p: Point): Point {
    const x=p.x-t.origin[0], z=p.z-t.origin[2], c=Math.cos(t.yaw), s=Math.sin(t.yaw);
    // Indexed reads, not destructuring: this runs per tower every frame.
    if(t.linear){const l=t.linear,a=l[0],b=l[1],c=l[2],d=l[3],det=a*d-b*c;return {x:(d*x-b*z)/det,y:p.y-t.origin[1],z:(a*z-c*x)/det};}
    return {x:c*x-s*z,y:p.y-t.origin[1],z:s*x+c*z};
}
export function worldPoint(t: Tower, p: Point): Point {
    const c=Math.cos(t.yaw),s=Math.sin(t.yaw);
    if(t.linear){const l=t.linear;return {x:t.origin[0]+l[0]*p.x+l[1]*p.z,y:t.origin[1]+p.y,z:t.origin[2]+l[2]*p.x+l[3]*p.z};}
    return {x:t.origin[0]+c*p.x+s*p.z,y:t.origin[1]+p.y,z:t.origin[2]-s*p.x+c*p.z};
}
export function floorAt(t: Tower, p: Point): number { return Math.max(0,Math.min(t.floors-1,Math.floor((p.y+.12)/STORY))); }
export function roomId(t: Tower, floor: number, bay: number, side: number): string { return `${t.id}/${floor}/${bay}/${side}`; }
export function roomNumber(floor: number, bay: number, side: number): string { return `${floor+1}${String(bay*2+(side>0?2:1)).padStart(2,'0')}`; }
export function bayPoint(t: Tower, floor: number, bay: number): Point {
    const z=FIRST_BAY_Z-bay*BAY;
    return {x:(t.curve??0)*z*z+(t.lean?.[0]??0)*floor*STORY,y:floor*STORY,z:z+(t.lean?.[1]??0)*floor*STORY};
}
export function roomAt(t: Tower, p: Point): {floor:number;bay:number;side:number}|null {
    const floor=floorAt(t,p);
    if(floor<t.firstGuestFloor || p.y-floor*STORY>3.58)return null;
    // Only the active floor's few bays are examined, never the entire tower.
    for(let bay=0;bay<t.bays;bay++){
        const q=bayPoint(t,floor,bay),x=p.x-q.x;
        if(Math.abs(p.z-q.z)<BAY/2 && Math.abs(x)>DOOR_X && Math.abs(x)<DOOR_X+roomDepth(t))
            return {floor,bay,side:x>0?1:-1};
    }
    return null;
}
export function insideTower(t: Tower,p: Point,margin=0):boolean {
    if(p.y<-.5 || p.y>t.floors*STORY+.2)return false;
    const sx=p.x-(t.lean?.[0]??0)*p.y, sz=p.z-(t.lean?.[1]??0)*p.y;
    if(Math.abs(sx)<3.7+margin && sz>-5.15-margin && sz<5.15+margin)return true;
    const floor=floorAt(t,p),q=bayPoint(t,floor,Math.max(0,Math.min(t.bays-1,Math.round((FIRST_BAY_Z-p.z)/BAY))));
    return floor>=t.firstGuestFloor && Math.abs(p.x-q.x)<DOOR_X+roomDepth(t)+.05+margin && p.z< -4.7+margin && p.z> FIRST_BAY_Z+BAY/2-t.bays*BAY-margin;
}
export function roomSeed(id:string):number {let h=2166136261;for(const ch of id)h=Math.imul(h^ch.charCodeAt(0),16777619);return h>>>0;}

/** Proximity is for residency only. Crossing a preload radius cannot change the
 * public lobby or reveal service floors above its entrance. */
export function stairVisible(floor:number,currentFloor:number,sameTower:boolean,inside:boolean,entranceOpen:boolean):boolean {
    if(!inside)return floor===0 || (sameTower && entranceOpen && floor<=2);
    return sameTower && floor>=currentFloor-1 && floor<=currentFloor+2;
}

/** Only real openings reveal another space; a chase camera crossing a shaft
 * wall must not enable an entire city. Undefined outside delegates to the
 * public-floor portal policy at the ground entrance. */
export function guestVisibility(t:Tower,floor:number,player:Point,camera:Point,groundOpen:boolean,windowView:boolean){
    if(!insideTower(t,player))return null;
    const entranceCamera=camera.y<STORY && camera.z<-4.7 && Math.abs(camera.x)<3.7;
    const showGround=floor===0 && (groundOpen || entranceCamera);
    return {building:t.building,outside:windowView?true:showGround?undefined:false,showGround,
        hideTower:windowView?(t.lazy?t.source:t.building==='veer'?t.id:t.building):undefined};
}
