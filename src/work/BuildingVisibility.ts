import type {StreamingWork} from './StreamingWork.js';
import * as THREE from 'three';
import manifest from './vegas-visibility.json';

type Point = { x: number; y: number; z: number };
type Zone = typeof manifest.zones[number];
export interface StreamedInteriorView {building:string;outside?:boolean;showGround:boolean;hideTower?:string}
/* Zones are tested many times a frame (every light source, twice per update), so
 * each is precompiled once into flat tables: no per-call destructuring, closures or
 * transform inversions (they were ~11 MB/s of garbage standing still).
 * ZONE row (stride 14): inverse linear a b c d, translation x z, source centre x y z,
 * cos, sin, half size x y z. VOID row (stride 5): centre x z, radius, min y, max y. */
const ZONE_STRIDE=14,VOID_STRIDE=5;
const zoneIndex=new Map<Zone,number>();
const zoneTable=new Float64Array(manifest.zones.length*ZONE_STRIDE);
const voidTable=new Float64Array(manifest.exteriorVoids.length*VOID_STRIDE);
/** zoneVoids[zoneVoidStart[i] .. zoneVoidStart[i+1]) are the voids of zone i's building. */
const zoneVoidStart=new Uint32Array(manifest.zones.length+1);
const zoneVoids=new Uint32Array(manifest.zones.length*Math.max(1,manifest.exteriorVoids.length));
manifest.exteriorVoids.forEach((v,i)=>voidTable.set([v.center[0]!,v.center[1]!,v.radius,v.minY,v.maxY],i*VOID_STRIDE));
{let n=0;manifest.zones.forEach((z,i)=>{
    zoneIndex.set(z,i);const t=z.geoTransform,[a,b,c,d]=t.linear,det=a!*d!-b!*c!,o=i*ZONE_STRIDE;
    zoneTable.set([d!/det,-b!/det,-c!/det,a!/det,t.translation[0]!,t.translation[1]!,z.sourceCenter[0]!,z.sourceCenter[1]!,z.sourceCenter[2]!,Math.cos(z.sourceYaw),Math.sin(z.sourceYaw),z.sourceSize[0]!/2,z.sourceSize[1]!/2,z.sourceSize[2]!/2],o);
    zoneVoidStart[i]=n;manifest.exteriorVoids.forEach((v,j)=>{if(v.building===z.building)zoneVoids[n++]=j;});
});zoneVoidStart[manifest.zones.length]=n;}
function containsIndex(i:number,x:number,y:number,z:number,margin:number):boolean {
    // Authored outdoor courts carve older rectangular interior zones.
    for(let k=zoneVoidStart[i]!;k<zoneVoidStart[i+1]!;k++){const v=zoneVoids[k]!*VOID_STRIDE;
        if(y>=voidTable[v+3]! && y<=voidTable[v+4]! && Math.hypot(x-voidTable[v]!,z-voidTable[v+1]!)<voidTable[v+2]!-margin)return false;}
    const o=i*ZONE_STRIDE,dx=x-zoneTable[o+4]!,dz=z-zoneTable[o+5]!;
    const lx=zoneTable[o]!*dx+zoneTable[o+1]!*dz-zoneTable[o+6]!,lz=zoneTable[o+2]!*dx+zoneTable[o+3]!*dz-zoneTable[o+8]!,ly=y-zoneTable[o+7]!;
    const co=zoneTable[o+9]!,si=zoneTable[o+10]!;
    return Math.abs(co*lx-si*lz)<=zoneTable[o+11]!+margin && Math.abs(ly)<=zoneTable[o+12]!+margin && Math.abs(si*lx+co*lz)<=zoneTable[o+13]!+margin;
}
export function contains(z: Zone, p: Point, margin = 0): boolean {return containsIndex(zoneIndex.get(z)!,p.x,p.y,p.z,margin);}
/** The first zone containing the point, as `zones.find(z=>contains(z,p,margin))` did. */
export function zoneAt(p: Point, margin = 0): Zone|undefined {
    for(let i=0;i<manifest.zones.length;i++)if(containsIndex(i,p.x,p.y,p.z,margin))return manifest.zones[i];
    return undefined;
}
export function visibilityState(player: Point, camera: Point, doorState: (id: string)=>string|null, allowPreviews = true) {
    const zone=zoneAt(player);
    // Glazed entrances reveal a bounded arrival suite before the automatic
    // doors open. Distant casinos stay culled until the player actually enters.
    const previews=new Set<string>();
    if(!zone && allowPreviews) {
        const near=manifest.portals.filter(p=>p.exterior && p.arrivals.length>0).map(p=>({p,d:Math.hypot(player.x-p.position[0]!,player.z-p.position[2]!)})).filter(v=>v.d<35 && Math.abs(player.y-v.p.position[1]!)<12).sort((a,b)=>a.d-b.d);
        for(const id of near[0]?.p.arrivals??[])previews.add(id);
    }
    const open=manifest.portals.filter(p=>{const state=doorState(p.id);return state!==null && state!=='closed';});
    let active=zone?.building;
    if (!active) {
        const nearby=open.filter(p=>p.exterior).map(p=>({p,d:Math.hypot(player.x-p.position[0]!,player.z-p.position[2]!)})).filter(p=>p.d<20).sort((a,b)=>a.d-b.d);
        active=nearby[0]?.p.buildings[0];
    }
    const cameraInside=zone && manifest.zones.some(z=>z.building===zone.building && contains(z,camera,-.3));
    const exteriorOpen=active && open.some(p=>p.exterior && p.buildings.includes(active!));
    const outside=!zone || !cameraInside || zone.windowed || !!exteriorOpen;
    const buildings=new Set<string>(active ? [active] : []);
    if (zone) for(const p of open) if(p.buildings.includes(zone.building) && Math.hypot(player.x-p.position[0]!,player.z-p.position[2]!)<12) {
        for(const b of [...p.buildings,...('adjacent' in p ? p.adjacent as string[] : [])]) buildings.add(b);
    }
    return {zone, outside, buildings,previews};
}

/** Render-only culling. Physics, doors, NPC updates and shadow proxies are independent. */
export class BuildingVisibility {
    private batches: {node: THREE.Object3D; zone?: Zone; kind: string; original: boolean}[]=[];
    private state: ReturnType<typeof visibilityState>|null=null;
    private signature='';
    private prepared=new Set<string>();
    private streamed:StreamedInteriorView|null=null;
    private outside=true;
    /** A passing vehicle never needs the arrival suite behind a glazed entrance. */
    private passing=false;
    private bypass=new URLSearchParams(location.search).get('visibility')==='all';
    constructor(root: THREE.Object3D,private loading:StreamingWork|null=null) {
        root.traverse(node=>{
            const kind=node.userData.visibilityKind;
            if(kind) this.batches.push({node,kind,zone:manifest.zones.find(z=>z.id===node.userData.visibilityZone),original:node.visible});
        });
        if(!this.batches.length) console.warn('[BuildingVisibility] Untagged level: leaving all geometry visible.');
    }
    setPassing(passing:boolean):void {this.passing=passing;}
    update(player: Point, camera: Point, doorState: (id:string)=>string|null, lights: readonly THREE.Light[], streamed:StreamedInteriorView|null=null,prepared=false) {
        if(!this.batches.length || this.bypass) return;
        const next=visibilityState({x:player.x,y:player.y+1.2,z:player.z},camera,doorState,!this.passing);
        const needed=[...next.buildings,...next.previews].filter(b=>!this.prepared.has(b) && (!streamed || streamed.showGround));
        if(!prepared && needed.length && this.loading){
            const p={...player},c={...camera};
            this.loading.enqueue('interior:'+needed.join(','),next.zone?.name??'resort interior',()=>{
                this.update(p,c,doorState,lights,streamed,true);
                for(const b of needed)this.prepared.add(b);
            });return;
        }
        this.streamed=streamed;
        this.state=next;
        const {zone,buildings,previews}=this.state;
        const outside=streamed?.outside??this.state.outside;
        this.outside=outside;
        let visible=0;
        for(const b of this.batches) {
            const own=b.zone && (streamed ? streamed.showGround && (b.zone.building===streamed.building || streamed.building==='veer' && b.zone.building==='crystals') : buildings.has(b.zone.building));
            const preview=!!b.zone && previews.has(b.zone.id);
            const roomAllowed=!zone?.room || b.zone?.id===zone.id || b.zone?.corridor;
            b.node.visible=b.original && (b.kind==='outside' ? outside : b.kind==='shell' ? outside || !!own : (preview || !!own) && !!roomAllowed);
            if(streamed?.hideTower && b.node.userData.visibilityTower===streamed.hideTower)b.node.visible=false;
            if(b.node.visible){visible++;if(prepared && b.kind==='interior')this.loading?.revealUntilReady(b.node);}
        }
        // Never change the set of lights (AGENTS.md; 2026-10-25): toggling `visible` on these level spots re-keyed every lit
        // shader in view whenever the player's zone changed (a shadow-casting spot is compiled into the shader), and the
        // engine's start-up warm-up, which reveals hidden objects, compiled for a light set the first frame then dropped.
        // They stay visible; out of sight they go dark and their shadow map stops updating.
        for(const light of lights){
            const base=(light.userData.levelIntensity??=light.intensity) as number,on=this.pointVisible(light.position);
            light.visible=true;light.intensity=on?base:0;
            const shadow=(light as THREE.Light&{shadow?:THREE.LightShadow}).shadow;
            if(light.castShadow&&shadow&&shadow.autoUpdate!==on){shadow.autoUpdate=on;if(on)shadow.needsUpdate=true;}
        }
        const key=`${streamed?`guest:${streamed.building}:${streamed.showGround}`:zone?.name??'outdoors'}|${outside}|${[...buildings].join(',')}`;
        if(key!==this.signature) {this.signature=key;console.info(`[BuildingVisibility] ${key}: ${visible}/${this.batches.length} batches visible`);}
    }
    pointVisible(p: Point): boolean {
        if(!this.state || this.bypass) return true;
        const z=zoneAt(p,.15);
        if(this.streamed)return z ? this.streamed.showGround && (z.building===this.streamed.building || this.streamed.building==='veer' && z.building==='crystals') : this.outside;
        if(!z) return this.state.outside;
        return (this.state.previews.has(z.id) || this.state.buildings.has(z.building)) && (!this.state.zone?.room || z.id===this.state.zone.id || z.corridor);
    }
    get stats(){return {enabledInteriorBatches:this.batches.filter(b=>b.kind==='interior'&&b.node.visible).length};}
    get rendersOutside():boolean{return this.bypass || this.outside;}
    dispose() {for(const b of this.batches)b.node.visible=b.original;}
}
