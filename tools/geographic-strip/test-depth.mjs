import assert from 'node:assert/strict';
import * as THREE from 'three';
import {WebGPURenderer} from 'three/webgpu';
import {configureSkylineDepth,configureReversedDepthSorting} from '../../src/work/SkylineDepth.ts';
import RenderList from '../../node_modules/three/src/renderers/common/RenderList.js';
// Real Three objects, without a browser/GPU: verify the compatibility adapter
// uses the complete renderer lifecycle and configures both halves before init.
let resets=0;
const engine={renderer:new WebGPURenderer({canvas:{width:16,height:16},antialias:true}),recreateRenderer(aa,type){assert.equal(type,'webgpu');resets++;this.renderer=new WebGPURenderer({canvas:{width:16,height:16},antialias:aa});}};
configureSkylineDepth(engine);
assert.equal(resets,1);assert.equal(engine.renderer.reversedDepthBuffer,true);
assert.equal(engine.renderer.backend.parameters.reversedDepthBuffer,true);
assert.equal(engine.renderer.samples,4);assert.equal(engine.renderer.initialized,false);
configureSkylineDepth(engine);assert.equal(resets,1,'Already configured renderer is retained');
// Exercise Three's ACTUAL list reversal, not only the comparator in isolation.
const renderer=engine.renderer;
const items=[{id:1,groupOrder:0,renderOrder:-1,z:.01}, // sky first
 {id:2,groupOrder:0,renderOrder:0,z:.02}, // near
 {id:3,groupOrder:0,renderOrder:0,z:.001}, // far
 {id:4,groupOrder:0,renderOrder:10,z:.01}]; // overlay last
const list=new RenderList({getNode:()=>null},new THREE.Scene());list.opaque=items.slice();list.transparent=items.slice();
list.sort(renderer._opaqueSort,renderer._transparentSort,true);
assert.deepEqual(list.opaque.map(x=>x.id),[1,2,3,4]);
assert.deepEqual(list.transparent.map(x=>x.id),[1,3,2,4]);
// Reversed float depth still separates thin facade layers across the full map.
const near=.1,far=20000;
const depth=d=>Math.fround(near*(far-d)/(d*(far-near)));
for(const distance of [10,1000,8000,15000])assert(depth(distance)>depth(distance+.06),`6 cm facade at ${distance} m`);
assert.equal(depth(near),1);assert.equal(depth(far),0);
console.log('PASS: fresh renderer setup, backend agreement, idempotency, sky/overlay/transparent order, 6 cm facade precision to 15 km');
