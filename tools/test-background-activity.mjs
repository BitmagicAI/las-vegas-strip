import assert from 'node:assert/strict';
import {BackgroundActivity} from '../src/work/BackgroundActivity.ts';

function fixture(initialFocus=true){
 const win=new EventTarget(),doc=new EventTarget();
 let focus=initialFocus,queue=new Map(),serial=0,now=0,last=0,ambience=0,renders=0,updates=0;
 doc.hidden=false;doc.hasFocus=()=>focus;doc.documentElement={dataset:{}};
 const deltas=[];
 const engine={
  forceFixedDeltaTime:false,renderActive:true,capNext:false,manualPause:false,
  getAmbienceTime:()=>ambience,getRenderedFrameCount:()=>renders,
  animate(){
   queue.clear();queue.set(++serial,()=>this.animate());
   if(!this.renderActive || this.capNext){this.capNext=false;return;}
   const raw=Math.min((now-last)/1000,.1);last=now;ambience+=raw;
   const dt=this.forceFixedDeltaTime?1/60:raw;
   if(!this.manualPause){updates++;deltas.push(dt);}renders++;
  },
 };
 const original=engine.animate,activity=new BackgroundActivity(engine,win,doc);
 return {engine,activity,doc,deltas,original,
  frame(ms=17){now+=ms;const pending=[...queue.values()];queue.clear();for(const cb of pending)cb();},
  start(){engine.animate();},
  focus(value){focus=value;win.dispatchEvent(new Event(value?'focus':'blur'));},
  hidden(value){doc.hidden=value;doc.dispatchEvent(new Event('visibilitychange'));},
  event(target,name){(target==='win'?win:doc).dispatchEvent(new Event(name));},
  stats:()=>({renders,updates,pending:queue.size,ambience}),
 };
}
let checks=0;
const f=fixture();f.start();f.frame();assert.equal(f.stats().pending,1);
// Alt-tab with the page still visible: one already-scheduled callback drains;
// no simulation, GPU draw or replacement callback occurs in the background.
f.focus(false);const paused=f.stats();f.frame(400);f.frame(60_000);
assert.equal(f.stats().renders,paused.renders);assert.equal(f.stats().updates,paused.updates);assert.equal(f.stats().ambience,paused.ambience);assert.equal(f.stats().pending,0);checks+=4;
f.focus(true);assert.equal(f.stats().pending,1);assert.equal(f.deltas.at(-1),1/60);assert(!f.engine.forceFixedDeltaTime);checks+=3;
// Hidden wins over a focus notification. A visibility event while another app
// owns focus must not restart rendering either.
f.hidden(true);f.frame();const h=f.stats();f.focus(true);assert.equal(f.stats().pending,0);
f.focus(false);f.hidden(false);assert.equal(f.stats().pending,0);f.frame(4000);assert.equal(f.stats().renders,h.renders);checks+=3;
f.focus(true);assert.equal(f.stats().pending,1);
// Rapid blur/focus before the scheduled RAF never creates parallel loops.
for(let i=0;i<10;i++){f.focus(false);f.focus(true);assert.equal(f.stats().pending,1);f.frame();}checks+=10;
// A short background gap and a capped first wake frame must still use 1/60
// when simulation next ticks, without changing the user's recording setting.
f.focus(false);f.frame(250);f.engine.capNext=true;f.focus(true);f.frame();assert.equal(f.deltas.at(-1),1/60);checks++;
f.engine.forceFixedDeltaTime=true;f.focus(false);f.frame();f.focus(true);assert(f.engine.forceFixedDeltaTime);checks++;
// This gate is separate from manual pause and creator's render-active gate.
f.engine.forceFixedDeltaTime=false;f.engine.manualPause=true;f.engine.renderActive=false;f.focus(false);f.frame();const p=f.stats();f.focus(true);f.frame();
assert(f.engine.manualPause);assert(!f.engine.renderActive);assert.equal(f.stats().renders,p.renders);assert.equal(f.stats().updates,p.updates);checks+=4;
f.engine.renderActive=true;f.frame();assert.equal(f.stats().updates,p.updates);checks++;
f.engine.manualPause=false;f.frame();assert(f.stats().updates>p.updates);checks++;
for(const [off,on,target] of [['pagehide','pageshow','win'],['freeze','resume','doc']]){
 f.event(target,off);f.frame();assert.equal(f.stats().pending,0);f.event(target,on);assert.equal(f.stats().pending,1);checks+=2;
}
f.activity.dispose();assert.equal(f.engine.animate,f.original);assert.equal(f.doc.documentElement.dataset.gameActivity,undefined);f.focus(false);f.frame();assert.equal(f.stats().pending,1);checks+=3;
// A background-loaded page must wait for focus without a phantom first draw.
const cold=fixture(false);cold.start();cold.frame();assert.equal(cold.stats().renders,0);assert.equal(cold.stats().pending,0);cold.focus(true);assert.equal(cold.stats().renders,1);assert.equal(cold.stats().pending,1);cold.activity.dispose();checks+=4;
console.log({checks,backgroundFrames:0,backgroundUpdates:0,singleLoopResume:'passed',pauseAndEditorState:'preserved',lifecycleAndCleanup:'passed'});
