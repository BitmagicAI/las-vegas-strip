import {FrameStalls} from './FrameStalls.js';
import * as THREE from 'three';
import type {EngineLike} from 'types/game.js';

type Kind = 'exterior'|'interior'|'other';
interface Owner {name:string;kind:Kind}
export interface ComponentMetrics extends Owner {meshes:number;enabled:number;drawn:number;calls:number;triangles:number;smallDrawn:number;materials:number}
export interface SceneInventory {objects:number;meshes:number;enabled:number;geometries:number;materials:number;lights:number;activeLights:number;components:ComponentMetrics[]}
export interface SubmittedMesh {path:string;calls:number;triangles:number}
interface Counters {calls:number;triangles:number}

/** Three's WebGPU `calls` is lifetime render invocations, not GPU draws. */
export function renderCounters(renderer:EngineLike['renderer']):Counters {
    if(!renderer)return {calls:0,triangles:0};
    const r=renderer.info.render as {calls:number;drawCalls?:number;triangles:number};
    return {calls:r.drawCalls??r.calls,triangles:r.triangles};
}
function ownerFor(node:THREE.Object3D,parent:Owner):Owner {
    if(typeof node.userData.perfOwner==='string')return {name:node.userData.perfOwner,kind:node.userData.perfKind??'other'};
    const kind=node.userData.visibilityKind;
    if(kind)return {name:kind==='interior'?'Legacy resort interiors':'Legacy city / resort shells',kind:kind==='interior'?'interior':'exterior'};
    if(String(node.userData.source??'').startsWith('lakefront-'))return {name:'Bellagio · lakefront',kind:'exterior'};
    if(node.name.startsWith('Vegas character '))return {name:'Characters',kind:'other'};
    if(node.name==='Big Apple Coaster • OSM mapped route')return {name:'Big Apple Coaster',kind:'exterior'};
    if(node.name==='Afterlight electric charging bay')return {name:'Jeep charging bay',kind:'exterior'};
    if(node.name==='OpenStreetMap / geographic Strip')return {name:'OSM city / roads',kind:'exterior'};
    if(node.name==='Photo-referenced mapped high-rises')return {name:'Mapped high-rises',kind:'exterior'};
    return parent;
}

/** Inventory once per sample, not per frame. Enabled means parent-visible and
 * on a camera layer; it does NOT imply frustum visibility or occlusion. */
export function inventoryScene(scene:THREE.Scene,camera:THREE.Camera,onMesh?:(mesh:THREE.Mesh,row:ComponentMetrics)=>void):SceneInventory {
    const geometries=new Set<THREE.BufferGeometry>(),materials=new Set<THREE.Material>();
    const rows=new Map<string,ComponentMetrics>(),rowMaterials=new Map<ComponentMetrics,Set<THREE.Material>>();
    const result:SceneInventory={objects:0,meshes:0,enabled:0,geometries:0,materials:0,lights:0,activeLights:0,components:[]};
    function visit(node:THREE.Object3D,parentVisible:boolean,parentOwner:Owner):void {
        const visible=parentVisible&&node.visible,owner=ownerFor(node,parentOwner);
        result.objects++;
        if(node instanceof THREE.Light){result.lights++;if(visible&&node.layers.test(camera.layers)&&node.intensity>0)result.activeLights++;}
        if(node instanceof THREE.Mesh){
            result.meshes++;geometries.add(node.geometry);
            const mats=Array.isArray(node.material)?node.material:[node.material];
            let row=rows.get(owner.name);
            if(!row){row={...owner,meshes:0,enabled:0,drawn:0,calls:0,triangles:0,smallDrawn:0,materials:0};rows.set(owner.name,row);rowMaterials.set(row,new Set());}
            row.meshes++;for(const m of mats){materials.add(m);rowMaterials.get(row)!.add(m);}
            if(visible&&node.layers.test(camera.layers)&&mats.some(m=>m.visible)){result.enabled++;row.enabled++;onMesh?.(node,row);}
        }
        for(const child of node.children)visit(child,visible,owner);
    }
    visit(scene,true,{name:'Other / doors / actors',kind:'other'});
    result.geometries=geometries.size;result.materials=materials.size;
    result.components=[...rows.values()];for(const row of result.components)row.materials=rowMaterials.get(row)!.size;
    return result;
}

/** One instrumented main-camera frame on explicit request. Callbacks are removed as
 * soon as that frame ends, and all pre-existing render hooks are preserved. */
export class SceneMetrics {
    detailed=true;
    readonly stalls:FrameStalls;
    private visibilityChanged=()=>{this.lastFrame=0;};
    frame:Counters={calls:0,triangles:0};
    inventory:SceneInventory|null=null;
    frameTimes:number[]=[];renderTimes:number[]=[];updateTimes:number[]=[];
    sampledAt=0;scanMs=0;
    submitted:SubmittedMesh[]=[];
    private auditRequested=true;private lastFrame=0;private started=0;private auditing=false;
    private restored:(()=>void)[]=[];
    private scene:THREE.Scene;
    private previousBefore:THREE.Scene['onBeforeRender'];private previousAfter:THREE.Scene['onAfterRender'];
    private before:THREE.Scene['onBeforeRender'];private after:THREE.Scene['onAfterRender'];
    constructor(private engine:EngineLike,private onFrame:()=>void,loadingBetween:(from:number,to:number)=>string|null=()=>null){
        this.stalls=new FrameStalls(loadingBetween);
        if(typeof document!=='undefined')document.addEventListener('visibilitychange',this.visibilityChanged);
        this.scene=engine.scene!;this.previousBefore=this.scene.onBeforeRender;this.previousAfter=this.scene.onAfterRender;
        this.before=(...args)=>{
            this.previousBefore.apply(this.scene,args);if(args[2]!==engine.camera)return;
            const now=performance.now();
            if(this.detailed&&this.auditRequested){this.auditRequested=false;this.audit();}
            this.started=performance.now();
        };
        this.after=(...args)=>{
            this.previousAfter.apply(this.scene,args);if(args[2]!==engine.camera)return;
            const now=performance.now();this.frame=renderCounters(engine.renderer);
            if(this.lastFrame){this.stalls.record(this.lastFrame,now,now-this.started);const dt=now-this.lastFrame;if(dt<2000)this.push(this.frameTimes,dt);else this.frameTimes=[];}
            this.lastFrame=now;this.push(this.renderTimes,now-this.started);
            if(this.auditing){this.restoreHooks();this.sampledAt=Date.now();}
            this.onFrame();
        };
        this.scene.onBeforeRender=this.before;this.scene.onAfterRender=this.after;
    }
    private push(values:number[],value:number):void {values.push(value);if(values.length>240)values.shift();}
    requestAudit():void {this.auditRequested=true;}
    recordUpdate(ms:number):void {this.push(this.updateTimes,ms);}
    private audit():void {
        this.restoreHooks();this.auditing=true;const start=performance.now();
        this.submitted=[];
        this.inventory=inventoryScene(this.scene,this.engine.camera!, (mesh,row)=>{
            const before=mesh.onBeforeRender,after=mesh.onAfterRender;
            let baseline:Counters|null=null,drawn=false;
            const entry:SubmittedMesh={path:'',calls:0,triangles:0};
            const measuredBefore:THREE.Mesh['onBeforeRender']=(...args)=>{
                before.apply(mesh,args);baseline=args[2]===this.engine.camera?renderCounters(this.engine.renderer):null;
            };
            const measuredAfter:THREE.Mesh['onAfterRender']=(...args)=>{
                if(args[2]===this.engine.camera&&baseline){
                    const r=renderCounters(this.engine.renderer),calls=Math.max(0,r.calls-baseline.calls),triangles=Math.max(0,r.triangles-baseline.triangles);
                    row.calls+=calls;row.triangles+=triangles;
                    if(calls>0){
                        if(!entry.calls){const names:string[]=[];let node:THREE.Object3D|null=mesh;while(node&&node!==this.scene){if(node.name)names.unshift(node.name);node=node.parent;}entry.path=names.join(' / ')||`${mesh.type} #${mesh.id}`;this.submitted.push(entry);}
                        entry.calls+=calls;entry.triangles+=triangles;
                    }
                    if(calls>0&&!drawn){row.drawn++;drawn=true;if((mesh.geometry.index?.count??mesh.geometry.getAttribute('position')?.count??0)/3<100)row.smallDrawn++;}
                    baseline=null;
                }
                after.apply(mesh,args);
            };
            mesh.onBeforeRender=measuredBefore;mesh.onAfterRender=measuredAfter;
            this.restored.push(()=>{if(mesh.onBeforeRender===measuredBefore)mesh.onBeforeRender=before;if(mesh.onAfterRender===measuredAfter)mesh.onAfterRender=after;});
        });
        this.scanMs=performance.now()-start;
    }
    private restoreHooks():void {for(const restore of this.restored)restore();this.restored=[];this.auditing=false;}
    dispose():void {
        this.restoreHooks();
        if(typeof document!=='undefined')document.removeEventListener('visibilitychange',this.visibilityChanged);
        if(this.scene.onBeforeRender===this.before)this.scene.onBeforeRender=this.previousBefore;
        if(this.scene.onAfterRender===this.after)this.scene.onAfterRender=this.previousAfter;
    }
}
