// Test the actual template cache with loader/physics adapters, not a copy of it.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {registerHooks} from 'node:module';
import * as THREE from 'three';
registerHooks({resolve(s,c,next){
 if(s.startsWith('engine/'))return {url:'data:text/javascript,'+encodeURIComponent(s.includes('MeshLevelSchema')?'':s.includes('PhysicsBodyFactory')?'export const PhysicsBodyFactory={createStaticBody:()=>({rigidBody:{isValid:()=>true}})};':s.includes('MeshLevelColliders')?'export const planCollider=()=>({position:{},shape:{},quaternion:{}});':'export const applyMaterialConventions=()=>{};'),shortCircuit:true};
 if(s.endsWith('.js')&&s.startsWith('.')&&fs.existsSync(new URL(s.replace('.js','.ts'),c.parentURL)))return next(s.replace('.js','.ts'),c);
 if(s.endsWith('towers.json'))return {url:new URL('../src/work/hotels/towers.json',import.meta.url).href,shortCircuit:true};
 return next(s,c);
},load(url,c,next){if(url.endsWith('towers.json'))return {format:'module',source:'export default '+fs.readFileSync(new URL(url),'utf8'),shortCircuit:true};return next(url,c);}});
const {GLTFLoader}=await import('three/addons/loaders/GLTFLoader.js');
const requests=[],disposed=[];let release=null;
GLTFLoader.prototype.loadAsync=async function(url){
 requests.push(url);if(release)await release.promise;
 const scene=new THREE.Group(),geometry=new THREE.BoxGeometry(),material=new THREE.MeshBasicMaterial();scene.add(new THREE.Mesh(geometry,material));geometry.addEventListener('dispose',()=>disposed.push(url));return {scene};
};
globalThis.fetch=async()=>({ok:true,json:async()=>({colliders:[],lights:[]})});
const {HotelTemplates}=await import('../src/work/hotels/HotelTemplates.ts');
const engine={scene:new THREE.Scene(),physicsWorld:{removeRigidBody(){}}};
const library=new HotelTemplates(engine,{register:()=>()=>{}},{revealUntilReady(){}});
await library.load();assert(requests.length>0);assert(requests.every(r=>!/-room\.|-corridor\.|-door\./.test(r)),'detailed assets fetched at startup');
assert(!requests.some(r=>r.includes('wynn-')),'remote high-rise cores must not load at startup');
await Promise.all([library.ensureCore('wynn'),library.ensureCore('wynn'),library.ensureLobby('wynn-1')]);
assert.equal(requests.filter(r=>r.includes('wynn-stair.glb')).length,1);
const upperStair=library.instantiate('wynn-stair',new THREE.Matrix4());
library.releaseLazy('wynn','wynn-1');
assert(!disposed.some(r=>r.includes('wynn-stair')),'resident upper stair must pin its core');
assert(disposed.some(r=>r.includes('wynn-1-lobby')),'unused lobby should unload');
upperStair.dispose();library.trim();
assert(disposed.some(r=>r.includes('wynn-stair')),'core must unload after delayed upper-stair eviction');
await Promise.all([library.ensureGuest('paris'),library.ensureGuest('paris')]);
assert.equal(requests.filter(r=>r.includes('paris-room.glb')).length,1,'concurrent requests must coalesce');
const pin=library.instantiate('paris-corridor',new THREE.Matrix4());
await library.ensureGuest('aria');await library.ensureGuest('vdara');library.trim();
assert(!disposed.some(r=>r.includes('paris-room')),'live floor must pin its set');
pin.dispose();library.trim();assert(disposed.some(r=>r.includes('paris-room')),'unused old set must release GPU buffers');
await library.ensureGuest('paris');assert.equal(requests.filter(r=>r.includes('paris-room.glb')).length,2,'evicted set must reload');
library.dispose();assert.equal(engine.scene.children.length,0);
// Disposal during an asynchronous load must release incoming GLBs as well.
release={promise:null,resolve:null};release.promise=new Promise(r=>release.resolve=r);
const pendingLibrary=new HotelTemplates(engine,{register:()=>()=>{}},{revealUntilReady(){}});
const wait=pendingLibrary.ensureGuest('waldorf');pendingLibrary.dispose();release.resolve();await wait;
assert(disposed.some(r=>r.includes('waldorf-room')));
console.log('Resort library: lazy startup, request coalescing, live pinning, eviction/reload, async disposal passed.');
