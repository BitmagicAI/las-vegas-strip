import type {EngineLike} from 'types/game.js';
import type {GameEngine} from 'engine/GameEngine.js';

type FrameEngine=Pick<GameEngine,'animate'|'forceFixedDeltaTime'|'getAmbienceTime'|'getRenderedFrameCount'>;
function hasFrameLoop(engine:EngineLike):engine is EngineLike&FrameEngine {
    return 'animate' in engine && typeof engine.animate==='function'
        && 'forceFixedDeltaTime' in engine && typeof engine.forceFixedDeltaTime==='boolean'
        && typeof engine.getAmbienceTime==='function'
        && 'getRenderedFrameCount' in engine && typeof engine.getRenderedFrameCount==='function';
}

/** Suspend the engine's public frame entry point, including physics, NPCs and
 * rendering. Its pending RAF drains once without scheduling a successor. This
 * leaves the engine's independent editor/render-active and manual-pause gates
 * intact, and requires no changes to the vendored engine. */
export class BackgroundActivity {
    private readonly frameEngine:FrameEngine;
    private readonly originalAnimate:()=>void;
    private focused:boolean;
    private pageHidden=false;
    private frozen=false;
    private inactive=false;
    private halted=false;
    private freshFrame=false;
    private disposed=false;
    private pausedFrame=0;
    private listeners:{target:EventTarget;name:string;callback:EventListener}[]=[];

    constructor(engine:EngineLike,private win:Window=window,private doc:Document=document){
        if(!hasFrameLoop(engine))throw new Error('Background suspension requires Bitmagic\'s public frame-loop API');
        this.frameEngine=engine;this.originalAnimate=engine.animate;
        this.focused=doc.hasFocus();this.inactive=this.shouldSuspend();
        this.pausedFrame=engine.getRenderedFrameCount();
        engine.animate=this.animate;
        this.listen(win,'blur',()=>{this.focused=false;this.refresh();});
        this.listen(win,'focus',()=>{this.focused=doc.hasFocus();this.refresh();});
        this.listen(doc,'visibilitychange',()=>{this.focused=doc.hasFocus();this.refresh();});
        this.listen(win,'pagehide',()=>{this.pageHidden=true;this.refresh();});
        this.listen(win,'pageshow',()=>{this.pageHidden=false;this.focused=doc.hasFocus();this.refresh();});
        this.listen(doc,'freeze',()=>{this.frozen=true;this.refresh();});
        this.listen(doc,'resume',()=>{this.frozen=false;this.focused=doc.hasFocus();this.refresh();});
        this.doc.documentElement.dataset.gameActivity=this.inactive?'suspended':'active';
    }
    private listen(target:EventTarget,name:string,callback:()=>void):void{
        target.addEventListener(name,callback);this.listeners.push({target,name,callback});
    }
    private shouldSuspend():boolean{return this.doc.hidden || !this.focused || this.pageHidden || this.frozen;}
    private refresh():void{
        if(this.disposed)return;
        const inactive=this.shouldSuspend();if(inactive===this.inactive)return;
        this.inactive=inactive;this.doc.documentElement.dataset.gameActivity=inactive?'suspended':'active';
        if(inactive){
            this.pausedFrame=this.frameEngine.getRenderedFrameCount();
            console.info('[BackgroundActivity] Suspended updates and rendering');
        }else{
            // Do not feed even a short alt-tab gap into the physics integrator.
            // Keep this armed if the first call is FPS-capped or render-gated.
            this.freshFrame=true;
            console.info(`[BackgroundActivity] Resumed; ${this.frameEngine.getRenderedFrameCount()-this.pausedFrame} frames rendered while inactive`);
            // If blur/focus happened within one RAF, the existing callback owns
            // the restart. Otherwise the drained chain must be restarted once.
            if(this.halted)this.animate();
        }
    }
    private animate=():void=>{
        if(this.disposed)return;
        if(this.inactive){this.halted=true;return;}
        this.halted=false;
        const engine=this.frameEngine,ambience=engine.getAmbienceTime(),fixed=engine.forceFixedDeltaTime;
        if(this.freshFrame)engine.forceFixedDeltaTime=true;
        try{this.originalAnimate.call(engine);}
        finally{
            engine.forceFixedDeltaTime=fixed;
            if(engine.getAmbienceTime()!==ambience)this.freshFrame=false;
        }
    };
    dispose():void{
        this.disposed=true;
        for(const {target,name,callback} of this.listeners)target.removeEventListener(name,callback);
        this.listeners=[];
        if(this.frameEngine.animate===this.animate)this.frameEngine.animate=this.originalAnimate;
        delete this.doc.documentElement.dataset.gameActivity;
    }
}
