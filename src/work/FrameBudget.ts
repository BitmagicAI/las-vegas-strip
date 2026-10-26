/** Main-thread time for loading work, shared by everything that builds the city (2026-10-25, the owner: "load only
 * the minimal assets, then already drop the player in ... this assumes that we don't have constant stalling").
 *
 * Long loops (merging meshes into city batches, the ground index, LOD building) call `await frameBudget.slice()` every
 * few thousand items: it returns at once while the current frame's share is left, and otherwise waits for the next
 * animation frame. Before play the share is large (nothing is drawn but the loading screen); in play it is a few
 * milliseconds, so the city keeps arriving without holding a frame. One budget for all callers, so two loaders running
 * at once cannot each take a whole share. */
const LOADING_MS=40,PLAYING_MS=5;
class Budget {
    private frameStart=0;
    private share=LOADING_MS;
    private waiting:Promise<void>|null=null;
    private release:(()=>void)|null=null;
    constructor(){
        if(typeof requestAnimationFrame==='undefined')return;
        const tick=(t:number)=>{
            this.frameStart=performance.now();
            if(this.release){const r=this.release;this.release=null;this.waiting=null;r();}
            void t;requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    }
    /** In play the share drops to a few milliseconds a frame. */
    playing(on:boolean):void{this.share=on?PLAYING_MS:LOADING_MS;}
    /** Milliseconds of loading work allowed per frame. */
    get perFrame():number{return this.share;}
    /** True when the current frame's share is used up (callers that cannot await check this). */
    get spent():boolean{return performance.now()-this.frameStart>this.share;}
    /** Resolves now while the frame's share lasts, else at the next animation frame. */
    slice():Promise<void>|void{
        if(!this.spent)return;
        if(typeof requestAnimationFrame==='undefined')return;
        this.waiting??=new Promise<void>(resolve=>{this.release=resolve;});
        return this.waiting;
    }
}
export const frameBudget=new Budget();

/** Long work written once as a generator that `yield`s every few thousand items: run it to completion here... */
export function runSync<T>(steps:Generator<unknown,T>):T{let r=steps.next();while(!r.done)r=steps.next();return r.value;}
/** ...or spread over frames within the shared budget. */
export async function runSliced<T>(steps:Generator<unknown,T>):Promise<T>{
    let r=steps.next();
    while(!r.done){await frameBudget.slice();r=steps.next();}
    return r.value;
}
