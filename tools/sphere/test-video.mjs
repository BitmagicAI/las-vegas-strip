import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {stripTypeScriptTypes} from 'node:module';
// Exercise the actual playback controller with event-driven browser stubs.
// In particular, a late play() resolution must not revive a hidden video.
class Video extends EventTarget {
 paused=true; currentTime=0; dataset={}; style={}; readyState=4;
 play(){this.paused=false;return this.pending??Promise.resolve();}
 pause(){this.paused=true;}setAttribute(){}removeAttribute(){}load(){}remove(){this.removed=true;}
}
class Texture{dispose(){this.disposed=true;}}
class Material{constructor(p){Object.assign(this,p);}dispose(){this.disposed=true;}}
const window=new EventTarget(),document=new EventTarget();document.hidden=false;document.hasFocus=()=>true;document.body={append(){}};document.createElement=()=>new Video();
const THREE={TextureLoader:class{load(){return new Texture();}},VideoTexture:Texture,MeshBasicMaterial:Material};
const source=stripTypeScriptTypes(fs.readFileSync('src/work/SphereVideo.ts','utf8').replace("import * as THREE from 'three';",'').replace('export class SphereVideo','class SphereVideo'));
const SphereVideo=vm.runInNewContext(source+';SphereVideo',{THREE,window,document,console});const tick=async()=>{await Promise.resolve();await Promise.resolve();await Promise.resolve();};
const s=new SphereVideo('exosphere.mp4','poster.jpg');
s.setActive(true);await tick();assert.equal(s.video.paused,false);
window.dispatchEvent(new Event('blur'));assert.equal(s.video.paused,true);
window.dispatchEvent(new Event('focus'));await tick();assert.equal(s.video.paused,false);
document.hidden=true;document.dispatchEvent(new Event('visibilitychange'));assert.equal(s.video.paused,true);
document.hidden=false;document.dispatchEvent(new Event('visibilitychange'));await tick();assert.equal(s.video.paused,false);
s.setActive(false);assert.equal(s.video.paused,true);
let resolve;s.video.pending=new Promise(r=>resolve=r);s.setActive(true);window.dispatchEvent(new Event('blur'));resolve();await tick();assert.equal(s.video.paused,true);
window.dispatchEvent(new Event('focus'));await tick();window.dispatchEvent(new Event('pagehide'));assert.equal(s.video.paused,true);window.dispatchEvent(new Event('pageshow'));await tick();assert.equal(s.video.paused,false);
s.dispose();assert.equal(s.video.paused,true);assert.equal(s.video.removed,true);window.dispatchEvent(new Event('focus'));assert.equal(s.video.paused,true);
const broken=new SphereVideo('missing.mp4','poster.jpg');const poster=broken.material.map;broken.video.dispatchEvent(new Event('error'));broken.setActive(true);await tick();assert.equal(broken.video.paused,true);assert.equal(broken.material.map,poster);broken.dispose();
console.log('Sphere video: focus, visibility, game pause policy, page lifecycle, pending play, fallback and disposal passed.');
