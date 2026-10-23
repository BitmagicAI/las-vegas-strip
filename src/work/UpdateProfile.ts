/** Opt-in CPU timings for local gameplay diagnosis: ?updateProfile. */
class UpdateProfile {
    readonly enabled=typeof location!=='undefined' && ['localhost','127.0.0.1'].includes(location.hostname) && new URLSearchParams(location.search).has('updateProfile');
    private samples=new Map<string,number[]>();
    private panel:HTMLPreElement|null=null;
    private since=0;
    private frames=0;
    private measuredAt=0;
    start():number{return this.enabled?performance.now():0;}
    end(name:string,start:number):void{
        if(!this.enabled)return;
        const samples=this.samples.get(name)??[];
        samples.push(performance.now()-start);this.samples.set(name,samples);
    }
    frame(dt:number):void{
        if(!this.enabled)return;
        if(!this.measuredAt)this.measuredAt=performance.now();
        this.frames++;
        this.since+=dt;if(this.since<3)return;
        if(!this.panel){this.panel=document.createElement('pre');this.panel.id='update-profile';this.panel.style.cssText='position:absolute;right:18px;top:115px;background:#101820ee;color:#fff;padding:12px;font:12px monospace;pointer-events:none';document.body.append(this.panel);}
        const now=performance.now();
        const lines=[`GAMEPLAY CPU ms — mean / p95 / max · ${(this.frames*1000/(now-this.measuredAt)).toFixed(1)} FPS`];
        for(const [name,values] of this.samples){
            values.sort((a,b)=>a-b);
            lines.push(`${name.padEnd(22)} ${(values.reduce((a,b)=>a+b,0)/values.length).toFixed(2)} / ${values[Math.floor(values.length*.95)]!.toFixed(2)} / ${values[values.length-1]!.toFixed(2)}`);
        }
        this.panel.textContent=lines.join('\n');this.samples.clear();this.since=0;this.frames=0;this.measuredAt=now;
    }
    dispose():void{this.panel?.remove();this.panel=null;this.samples.clear();this.since=0;this.frames=0;this.measuredAt=0;}
}
export const updateProfile=new UpdateProfile();
