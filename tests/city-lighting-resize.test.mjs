// City surfaces after a resize (src/work/CityLighting.ts): three's ClusteredLightsNode rebuilds its cluster buffers when
// the drawing buffer changes size, and a shader compiled before keeps reading the old ones (2026-10-26: every lamp pool
// and headlight of a storm recording went dark once the recorder resized the renderer). A bound material carries the
// cluster grid in its program key from binding on, and a resize gives it a new key and a rebuild; nothing else does.
// Run: node --import ./tools/ts-register.mjs tests/city-lighting-resize.test.mjs
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {MeshStandardNodeMaterial,WebGPURenderer} from 'three/webgpu';
import {bindCityLighting} from '../src/work/CityLighting.ts';

const material=new MeshStandardNodeMaterial({color:0x808080});
/** The key three would give the material without the grid. */
const own=(m)=>m.constructor.prototype.customProgramCacheKey.call(m);
const mesh=new THREE.Mesh(new THREE.BoxGeometry(),material),scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera();
scene.add(mesh);
bindCityLighting(mesh);
// keyed before any draw: the start-up warm-up compiles without calling onBeforeRender
assert.equal(material.customProgramCacheKey(),`${own(material)}|grid0`,'the grid is in the key from binding on');

// a stand-in WebGPU renderer: the frame counter, the drawing buffer and the scene's light list are all the callback reads
const size={x:1920,y:1143};
const renderer=Object.create(WebGPURenderer.prototype);
Object.assign(renderer,{backend:{isWebGPUBackend:true},info:{frame:0},lighting:{getNode:()=>({getLights:()=>[]})},
    getDrawingBufferSize:(target)=>target.set(size.x,size.y)});
const draw=()=>{renderer.info.frame++;mesh.onBeforeRender(renderer,scene,camera,mesh.geometry,material,null);};

draw();const version=material.version;
assert.equal(material.customProgramCacheKey(),`${own(material)}|grid0`,'the first size is the first grid');
assert.ok(material.lightsNode,'the clustered light list is set');
for(let i=0;i<5;i++)draw();
assert.equal(material.version,version,'drawing at the same size never rebuilds');

size.y=1080;draw(); // the recorder's 1920x1080
assert.equal(material.customProgramCacheKey(),`${own(material)}|grid1`,'a resize is a new grid');
assert.equal(material.version,version+1,'and rebuilds the material once');
draw();draw();
assert.equal(material.version,version+1,'once');

// a material bound later, after the resize, starts on the current grid
const late=new MeshStandardNodeMaterial(),lateMesh=new THREE.Mesh(new THREE.BoxGeometry(),late);
bindCityLighting(lateMesh);
assert.equal(late.customProgramCacheKey(),`${own(late)}|grid1`,'a material bound after a resize starts on the current grid');
console.log('PASS: city surfaces carry the cluster grid in their program key and rebuild once per resize');
