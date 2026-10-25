import type {Object3D} from 'three';
export interface StreamingProgress {
    show(label:string,completed:number,total:number):void;
    hide():void;
    failed(error:unknown):void;
}
/** Two animation frames guarantee a paint opportunity before synchronous work.
 * Keep the indicator through the first render too (GPU uploads can block it). */
export function afterPaint():Promise<void>{
    return new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve())));
}
/** One animation frame: lets quiet work start in a frame of its own, and lets a long job hand the frame back. */
export function nextFrame():Promise<void>{
    return new Promise(resolve=>requestAnimationFrame(()=>resolve()));
}
/** What one streaming job cost the player: the whole game is held for `heldMs` (0 for a background job, which
 * runs for `ranMs` without holding anything). Kept for the last 200 jobs (the local review probe and the console read it). */
export interface StreamingJobTiming {key:string;label:string;at:number;queuedMs:number;prepareMs:number;revealMs:number;heldMs:number;ranMs:number;background:boolean;}
export interface StreamingOptions {
    /** Run quietly: no loading panel and the game keeps running. For work the player does not need yet, such as
     * collision a few seconds ahead of a moving vehicle. The work must slice itself (yield with `nextFrame()`),
     * because nothing stands between it and the next frame. Queueing the same key again without this flag turns a
     * waiting job into a normal, held one, which is how "needed now" overrides "ahead of need". */
    background?:boolean;
}
interface Job {label:string;prepare:()=>void|Promise<void>;queuedAt:number;background:boolean}
export class StreamingWork {
    private jobs=new Map<string,Job>();
    private running=false;
    /** A job that holds the game is queued or running. Background jobs never set this. */
    private holding=false;
    private disposed=false;
    private active:{label:string;at:number}|null=null;
    private unculled=new Set<Object3D>();
    /** Roots revealed by the running held job, pre-compiled before its first frames. */
    private revealed:Object3D[]=[];
    private heldSince=0;
    /** Timings of finished jobs, oldest first (capped). */
    readonly history:StreamingJobTiming[]=[];
    /** `precompile` builds the shaders and pipelines of a held job's revealed roots off the frame (Game: the renderer's
     * compileAsync), so its first frames draw them instead of building them one by one (2026-10-25: a teleport to the
     * Venetian streamed three interiors and stalled ~4 s on 41 pipelines). */
    constructor(private progress:StreamingProgress,private hold:(busy:boolean)=>void,private paint=afterPaint,private settle:()=>void=()=>{},
        private precompile:(roots:readonly Object3D[])=>Promise<void>=()=>Promise.resolve()){}
    /** True while the game is held for a job (the loading panel is up). Background work does not count. */
    get busy():boolean{return this.holding;}
    /** Correlation only: overlap does not prove the loading job caused a hitch. Background jobs count too. */
    activitySince(from:number,to:number):string|null {
        if(this.active&&this.active.at<=to)return this.active.label;
        for(let i=this.history.length-1;i>=0;i--){const t=this.history[i]!;if(t.at<=to&&t.at+t.ranMs>=from)return t.label;}
        return null;
    }
    enqueue(key:string,label:string,prepare:()=>void|Promise<void>,options:StreamingOptions={}):void {
        if(this.disposed)return;
        const background=options.background===true,queued=this.jobs.get(key);
        if(queued){
            // Needed now after all: the queued background job becomes a normal one.
            if(queued.background&&!background){queued.background=false;this.beginHold();}
            return;
        }
        this.jobs.set(key,{label,prepare,queuedAt:performance.now(),background});
        if(!background)this.beginHold();
        if(!this.running){this.running=true;void this.drain();}
    }
    private beginHold():void {
        if(this.holding)return;
        this.holding=true;this.heldSince=performance.now();this.hold(true);
    }
    /** Upload only newly revealed modules, even before a sliding door has
     * finished opening. Never reveal hidden resorts or change their residency. */
    revealUntilReady(root:Object3D):void {
        if(!this.holding)return;
        root.traverse(node=>{if(node.frustumCulled){this.unculled.add(node);node.frustumCulled=false;}});
        this.revealed.push(root);
    }
    private restoreCulling():void {for(const node of this.unculled)node.frustumCulled=true;this.unculled.clear();}
    private record(key:string,job:Job,started:number,prepareMs:number,revealStart:number,end:number):void {
        const quiet=job.background;
        const t:StreamingJobTiming={key,label:job.label,at:started,queuedMs:started-job.queuedAt,prepareMs,revealMs:quiet?0:end-revealStart,heldMs:quiet?0:end-started,ranMs:end-started,background:quiet};
        this.history.push(t);if(this.history.length>200)this.history.shift();
        console.info(quiet
            ?`[StreamingWork] ${key} "${job.label}": background, ran ${t.ranMs.toFixed(0)} ms without holding the game (waited ${t.queuedMs.toFixed(0)} ms in the queue)`
            :`[StreamingWork] ${key} "${job.label}": prepare ${prepareMs.toFixed(0)} ms, first frames ${t.revealMs.toFixed(0)} ms, game held ${t.heldMs.toFixed(0)} ms (waited ${t.queuedMs.toFixed(0)} ms in the queue)`);
    }
    private async drain():Promise<void>{
        try {
            for(const [key,job] of this.jobs){
                const started=performance.now();this.active={label:job.label,at:started};
                if(job.background){
                    // Quiet path: no panel, no hold. The job may be upgraded to a held one while it waits for its frame.
                    await nextFrame();if(this.disposed)return;
                    if(job.background){
                        const prepareStart=performance.now();
                        await job.prepare();if(this.disposed)return;
                        this.jobs.delete(key);
                        this.record(key,job,started,performance.now()-prepareStart,0,performance.now());
                        continue;
                    }
                }
                this.progress.show(`Loading… ${job.label}`,0,2);
                await this.paint();if(this.disposed)return;
                const prepareStart=performance.now();
                await job.prepare();if(this.disposed)return;
                const prepareMs=performance.now()-prepareStart;
                this.settle();
                if(this.revealed.length){await this.precompile(this.revealed.splice(0));if(this.disposed)return;}
                this.progress.show(`Loading… ${job.label}`,1,2);
                // The normal renderer uploads/compiles only this visible scene.
                // Do not warm every hidden resort or un-cull the whole city.
                const revealStart=performance.now();
                await this.paint();if(this.disposed)return;
                this.progress.show('Loading… ready',2,2);
                await this.paint();
                this.jobs.delete(key);
                this.record(key,job,started,prepareMs,revealStart,performance.now());
            }
        } catch(error){this.progress.failed(error);this.jobs.clear();}
        finally {
            this.active=null;this.running=false;
            if(this.holding){
                console.info(`[StreamingWork] queue drained: game held ${(performance.now()-this.heldSince).toFixed(0)} ms in total`);
                this.holding=false;this.heldSince=0;this.restoreCulling();this.progress.hide();this.hold(false);
            }
        }
    }
    dispose():void {this.disposed=true;this.holding=false;this.jobs.clear();this.restoreCulling();this.progress.hide();this.hold(false);}
}
