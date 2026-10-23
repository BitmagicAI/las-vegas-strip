export interface FrameStall {at:number;durationMs:number;renderSubmissionMs:number;loading:string|null}
/** Constant work per frame, bounded history; no scene scans or timer polling. */
export class FrameStalls {
    readonly history:FrameStall[]=[];
    constructor(private loadingBetween:(from:number,to:number)=>string|null){}
    record(from:number,to:number,renderSubmissionMs:number):void {
        if(to-from<100)return;
        this.history.push({at:to,durationMs:to-from,renderSubmissionMs,loading:this.loadingBetween(from,to)});
        if(this.history.length>40)this.history.shift();
    }
    get description():string {
        const last=this.history[this.history.length-1];
        if(!last)return 'none ≥100 ms';
        return `${Math.round(last.durationMs)} ms · ${last.loading?'during loading: '+last.loading:'no tracked loading (cause unknown)'}`;
    }
}
