// Summarize fresh-browser runs; local timings are not published-CDN acceptance evidence.
import fs from 'node:fs';
import path from 'node:path';
const root=process.argv[2]??'.bitmagic/city-cells';
const rows=[];
for(const name of fs.readdirSync(root).filter(n=>/^load-(before|after)-\d+$/.test(n)).sort()){
 const file=path.join(root,name,'results.json');if(!fs.existsSync(file))continue;
 const m=JSON.parse(fs.readFileSync(file)).find(r=>r.loadMetrics)?.loadMetrics;
 if(!m)throw new Error(`Missing load metrics: ${name}`);
 rows.push({run:name,readySeconds:m.readyAt/1000,frameP95After:m.framesAfterReady.p95,frameMaxAfter:m.framesAfterReady.max,
  frameP99Before:m.framesBeforeReady.p99,longTaskMaxBefore:Math.max(0,...m.longTasksBeforeReady.map(([,d])=>d)),
  requests:m.resources.length,transferBytes:m.resources.reduce((n,r)=>n+r.bytes,0)});
}
const median=values=>{const v=values.slice().sort((a,b)=>a-b);return v.length?v.length%2?v[v.length>>1]:(v[v.length/2-1]+v[v.length/2])/2:null;};
const summary={};
for(const kind of ['before','after']){
 const r=rows.filter(r=>r.run.includes(kind));
 summary[kind]={runs:r.length,medianReadySeconds:median(r.map(v=>v.readySeconds)),medianFrameP95After:median(r.map(v=>v.frameP95After)),maxFrameAfter:r.length?Math.max(...r.map(v=>v.frameMaxAfter)):null};
}
console.log(JSON.stringify({scope:'Local fresh-browser WebGPU, same camera, default ultra quality. Not published-CDN proof; shared-machine variability applies.',summary,rows},null,2));
