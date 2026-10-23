import type {EngineLike} from 'types/game.js';
import type {ResortBlocks} from './ResortBlocks.js';
/** Local-only architectural review controls. All movement uses the normal input
 * and physics path; no replacement renderer or fake performance measurements. */
export class ResortBlockReview {
    private render={calls:0,triangles:0};private restoreRender:()=>void;private lastUi=0;private previousFreeMouse=false;
    private pendingKey:{key:string;code:string}|null=null;private heldKey:{key:string;code:string}|null=null;
    private root=document.createElement('div');private status=document.createElement('pre');private samples:number[]=[];private last=0;private until=0;private pendingWalk=false;private walk=false;private selected='cosmo';private shot='entrance';private settle=0;
    constructor(private engine:EngineLike,private blocks:ResortBlocks,private go:(key:string,view:string)=>void,private position:()=>{x:number;y:number;z:number},private busy:()=>boolean,placeJeep?:()=>void){
        // Review buttons must not steer the pointer-locked camera while capturing
        // a fixed comparison view. This helper only exists with ?resortReview=1.
        this.previousFreeMouse=engine.getPointerLockManager?.()?.getFreeMouseMode()??false;
        engine.getPointerLockManager?.()?.setFreeMouseMode(true);
        const scene=engine.scene!,previous=scene.onAfterRender;
        scene.onAfterRender=(...args)=>{previous.apply(scene,args);if(args[2]!==engine.camera)return;const r=engine.renderer!.info.render as {calls:number;drawCalls?:number;triangles:number};this.render={calls:r.drawCalls??r.calls,triangles:r.triangles};};
        this.restoreRender=()=>{scene.onAfterRender=previous;};
        this.root.id='resort-block-review';this.root.style.cssText='position:absolute;left:18px;bottom:90px;z-index:90;background:#10252ee8;color:#eee;padding:12px;border:1px solid #88b7b4;font:12px system-ui;max-width:430px';
        const select=document.createElement('select');select.setAttribute('aria-label','Resort area');
        for(const [key,label] of [['cosmo','Exterior / main entrance'],['cosmoL1','Level 1 · casino'],['cosmoL2','Level 2 · gallery / bridges'],['cosmoL3','Level 3 · restaurants'],['cosmoL4','Level 4 · Boulevard Pool'],['cosmoL14','Level 14 · Chelsea Pool'],['bellagioBlock','Bellagio · main arrival'],['bellagioLobby','Bellagio · lobby'],['bellagioGarden','Bellagio · pools'],['bellagioConservatory','Bellagio · conservatory'],['bellagioPromenade','Bellagio · casino promenade'],['parisBlock','Paris · exterior / terraces'],['parisDining','Paris · restaurants'],['parisPool','Paris · pool terrace']]){const o=document.createElement('option');o.value=key!;o.textContent=label!;select.append(o);}
        const requested=new URLSearchParams(location.search).get('landmark');
        if(requested&&[...select.options].some(o=>o.value===requested))this.selected=requested;
        select.value=this.selected;select.onchange=()=>{this.selected=select.value;};this.root.append(select);
        for(const [label,view] of [['Visit level','entrance'],['Pool view','deck'],['Tower and pool','tower-pool'],['Pool aerial','pool-aerial'],['Tower base','tower-base'],['Observation deck','observation'],['Lift cabin','lift-cabin'],['Stair ascent','stairs'],['Block aerial','aerial'],['Street frontage','frontage'],['Covered arrival','arrival'],['Garden foliage','foliage'],['Arrival aerial','arrival-aerial'],['Arrival inside','arrival-inside'],['Arrival facades','facades'],['Facade aerial','facades-aerial'],['Pool stairs','pool-stairs'],['Pool connection','pool-bridge'],['Lakefront aerial','lakefront'],['Lake promenade','shore'],['Bridge entry','bridge'],['Bridge stairs','bridge-stairs'],['Garage aerial','garage'],['Garage entrance','garage-entry'],['Sign stairs','sign-stairs']]){const b=document.createElement('button');b.textContent=label!;b.onclick=()=>{this.stop();this.shot=view!;this.go(this.selected,this.shot);this.samples=[];this.settle=performance.now()+3500;};this.root.append(b);}
        if(placeJeep){const b=document.createElement('button');b.textContent='Place garage test jeep';b.onclick=()=>{if(!this.busy())placeJeep();};this.root.append(b);}
        const walk=document.createElement('button');walk.textContent='Walk forward 5 seconds';walk.onclick=()=>{this.pendingWalk=true;};this.root.append(walk);
        for(const [label,key,code] of [['Interact (E)','e','KeyE'],['Ride lift (L)','l','KeyL'],['Pause menu','Escape','Escape']]){const b=document.createElement('button');b.textContent=label!;b.onclick=()=>{this.pendingKey={key:key!,code:code!};};this.root.append(b);}
        const stop=document.createElement('button');stop.textContent='Stop walking';stop.onclick=()=>this.stop();this.root.append(stop);
        const hide=document.createElement('button');hide.textContent='Hide review controls';hide.onclick=()=>{this.root.style.display='none';this.stop();};this.root.append(hide);
        this.status.id='resort-block-stats';this.root.append(this.status);document.body.append(this.root);
    }
    private releaseKey(){if(this.heldKey){document.dispatchEvent(new KeyboardEvent('keyup',{...this.heldKey,bubbles:true}));this.heldKey=null;}}
    private stop(){this.walk=false;this.pendingWalk=false;this.pendingKey=null;this.releaseKey();document.dispatchEvent(new KeyboardEvent('keyup',{key:'w',code:'KeyW',bubbles:true}));}
    update():void{
        this.releaseKey();
        if(this.pendingKey&&!this.busy()){const key=this.pendingKey;this.heldKey=key;this.pendingKey=null;document.dispatchEvent(new KeyboardEvent('keydown',{...key,bubbles:true}));if(key.key==='Escape')setTimeout(()=>{if(this.heldKey===key)this.releaseKey();},250);}
        const now=performance.now();if(this.pendingWalk&&!this.busy()){this.pendingWalk=false;this.walk=true;this.until=now+5000;document.dispatchEvent(new KeyboardEvent('keydown',{key:'w',code:'KeyW',bubbles:true}));}
        if(this.walk&&now>=this.until)this.stop();
        if(!this.busy()&&now>this.settle&&this.last>0&&now-this.last<250){this.samples.push(now-this.last);if(this.samples.length>300)this.samples.shift();}this.last=now;
        if(now-this.lastUi<250)return;this.lastUi=now;
        const a=[...this.samples].sort((a,b)=>a-b),p=this.position();
        this.status.textContent=JSON.stringify({area:this.selected,view:this.shot,position:[p.x,p.y,p.z].map(v=>+v.toFixed(2)),busy:this.busy(),walking:this.walk,frames:a.length,p50Ms:a[Math.floor(a.length*.5)]?.toFixed(1),p95Ms:a[Math.floor(a.length*.95)]?.toFixed(1),drawCalls:this.render.calls,triangles:this.render.triangles,...this.blocks.stats},null,1);
    }
    dispose(){this.stop();this.restoreRender();this.root.remove();this.engine.getPointerLockManager?.()?.setFreeMouseMode(this.previousFreeMouse);}
}
