// Background streaming jobs: work the player does not need yet runs without holding the game or showing the
// loading panel; work the player needs now still holds and shows it, and can override a queued background job.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
// The module uses requestAnimationFrame; give it a deterministic one that the test steps by hand.
let frames=[];globalThis.requestAnimationFrame=cb=>{frames.push(cb);return frames.length;};
const stepFrame=async()=>{const run=frames;frames=[];for(const cb of run)cb(performance.now());for(let i=0;i<5;i++)await Promise.resolve();};
fs.mkdirSync('build',{recursive:true});
fs.writeFileSync('build/streaming-work-test-module.mjs',ts.transpileModule(fs.readFileSync('src/work/StreamingWork.ts','utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText);
const {StreamingWork}=await import('../build/streaming-work-test-module.mjs?'+Date.now());
console.info=()=>{};
const make=()=>{const events=[];const work=new StreamingWork({show:(l,n)=>events.push('show:'+n),hide:()=>events.push('hide'),failed:e=>events.push('failed')},b=>events.push('hold:'+b),undefined,()=>events.push('settle'));return {work,events};};

// 1. A background job: no hold, no panel, not busy, runs in a frame of its own, leaves a history entry.
{const {work,events}=make();let ran=false;
 work.enqueue('city-collision:0,0','roads',()=>{ran=true;},{background:true});
 assert.deepEqual(events,[],'nothing is held or shown');assert.equal(work.busy,false);assert.equal(ran,false,'not run inside the frame that asked');
 await stepFrame();assert.equal(ran,true);assert.deepEqual(events,[]);assert.equal(work.busy,false);
 const t=work.history.at(-1);assert.equal(t.background,true);assert.equal(t.heldMs,0);assert.ok(t.ranMs>=0);
 assert.equal(work.activitySince(t.at-1,t.at+t.ranMs+1),'roads','background work still correlates with a stall');}

// 2. A held job queued behind a background job: the game is held straight away, the panel shows when its turn comes.
{const {work,events}=make();const order=[];
 work.enqueue('a','ahead',async()=>{order.push('a');},{background:true});
 work.enqueue('b','needed',()=>{order.push('b');});
 assert.deepEqual(events,['hold:true'],'a needed job holds the game immediately');assert.equal(work.busy,true);
 await stepFrame();assert.deepEqual(order,['a']);assert.ok(events.includes('show:0'),'the panel is shown for the held job');
 for(let i=0;i<14&&work.busy;i++)await stepFrame();
 assert.deepEqual(order,['a','b']);assert.equal(work.busy,false);assert.equal(events.at(-1),'hold:false');
 assert.equal(events.filter(e=>e==='hold:true').length,1);assert.equal(events.filter(e=>e==='hold:false').length,1);}

// 3. Needed after all: queueing the same key again without the flag upgrades the waiting job to a held one.
{const {work,events}=make();let ran=false;
 work.enqueue('c','collision',()=>{ran=true;},{background:true});assert.equal(work.busy,false);
 work.enqueue('c','collision',()=>assert.fail('the duplicate must not run'));
 assert.equal(work.busy,true,'upgraded');assert.deepEqual(events,['hold:true']);
 for(let i=0;i<14&&work.busy;i++)await stepFrame();assert.equal(ran,true);assert.equal(work.history.at(-1).background,false);assert.equal(events.at(-1),'hold:false');}

// 4. A background-only queue never touches the hold: releasing a hold that was not taken would re-enable a disabled body.
{const {work,events}=make();
 work.enqueue('x','one',()=>{},{background:true});work.enqueue('y','two',async()=>{await new Promise(r=>setImmediate(r));},{background:true});
 for(let i=0;i<4;i++){await stepFrame();await new Promise(r=>setImmediate(r));}
 assert.equal(work.history.length,2);assert.deepEqual(events,[],'no hold, no panel, no hide for background-only work');}

// 5. A failing background job reports once, clears the queue and holds nothing.
{const {work,events}=make();
 work.enqueue('bad','broken',()=>{throw Error('fixture');},{background:true});await stepFrame();
 assert.deepEqual(events,['failed']);assert.equal(work.busy,false);}

// 6. Held jobs behave exactly as before.
{const {work,events}=make();let built=false;
 work.enqueue('floor','corridor',()=>{built=true;});
 assert.deepEqual(events,['hold:true','show:0']);assert.equal(built,false,'paint barrier first');
 for(let i=0;i<14&&work.busy;i++)await stepFrame();
 assert.equal(built,true);assert.deepEqual(events,['hold:true','show:0','settle','show:1','show:2','hide','hold:false']);}
console.log('streaming-background: ok');
