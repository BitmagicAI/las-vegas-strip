import assert from 'node:assert/strict';
import {limitStormResolution,setStormRenderHeight,stormRenderHeight} from '../src/work/film/SceneResolution.ts';
let ratio=2,width=1920,height=1080,before,removed=false;const saved=new Map();globalThis.localStorage={setItem:(k,v)=>saved.set(k,v)};
const engine={renderer:{getPixelRatio:()=>ratio,setPixelRatio:r=>{ratio=r;},getSize:v=>v.set(width,height)},registerBeforeRender:f=>{before=f;return()=>{removed=true}}};
setStormRenderHeight(900);const release=limitStormResolution(engine);assert.equal(Math.round(width*ratio),1600);assert.equal(Math.round(height*ratio),900);
width=2560;height=1080;before();assert.equal(Math.round(width*ratio),1600);assert.equal(Math.round(height*ratio),675,'ultrawide aspect is preserved within pixel budget');
setStormRenderHeight(720);before();assert.equal(Math.round(width*ratio),1280);assert.equal(stormRenderHeight(),720);assert.equal(saved.get('afterlight:storm:render-height'),'720');
setStormRenderHeight(12);assert.equal(stormRenderHeight(),900);release();assert.equal(ratio,2);assert.ok(removed);
console.log('PASS: Retina, ultrawide, saved render size and original-resolution restoration.');
