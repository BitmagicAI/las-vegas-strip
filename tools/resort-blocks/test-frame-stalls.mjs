import assert from 'node:assert/strict';
import {FrameStalls} from '../../src/work/FrameStalls.ts';
import {StreamingWork} from '../../src/work/StreamingWork.ts';
let releases=[],built=false,visible=false;
const work=new StreamingWork({show:()=>visible=true,hide:()=>visible=false,failed:e=>{throw e;}},()=>{},()=>new Promise(r=>releases.push(r)));
const before=performance.now();work.enqueue('city','nearby roads and buildings',()=>{assert(visible);built=true;});
assert(!built,'Collision generation must wait for the loading paint barrier');
const stalls=new FrameStalls((a,b)=>work.activitySince(a,b));
stalls.record(before-200,performance.now(),2);assert.equal(stalls.history[0].loading,'nearby roads and buildings');
for(let i=0;i<3;i++){releases.shift()();await new Promise(r=>setImmediate(r));}
assert(built);assert(!work.busy);assert(!visible);
assert.equal(work.activitySince(before,performance.now()),'nearby roads and buildings','Finished loading remains correlated with a frame spanning its completion');
stalls.record(performance.now()+1000,performance.now()+1200,4);assert.equal(stalls.history.at(-1).loading,null);assert.match(stalls.description,/cause unknown/);
stalls.record(0,16,1);assert.equal(stalls.history.length,2);
for(let i=0;i<100;i++)stalls.record(10000+i*200,10150+i*200,2);assert.equal(stalls.history.length,40);
console.log('Paint-before-build, completed-job overlap, unknown-hitch labeling, 16 ms exclusion and bounded history passed.');
