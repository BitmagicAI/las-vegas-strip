import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
import {MeshBasicNodeMaterial} from 'three/webgpu';
import {vec3} from 'three/tsl';
import {extendSkylineCamera,matchHazeToSky,addStreetDetailLods} from '../../src/work/StripAtmosphere.ts';

const profile=JSON.parse(fs.readFileSync('src/work/world.json')).worldProfileData;
const camera=new THREE.PerspectiveCamera(60,1,.1,1000),projection=camera.projectionMatrix.clone();
extendSkylineCamera(camera);
assert.equal(camera.near,.1,'Room-scale near clipping must be preserved');
assert(!projection.equals(camera.projectionMatrix));
// Cover diagonals across the entire mapped ground, not just a central spawn.
const corners=[[-2350,0,-4400],[2550,0,-4400],[-2350,0,4300],[2550,0,4300]].map(p=>new THREE.Vector3(...p));
for(const a of corners)for(const b of corners){
 const distance=a.distanceTo(b);assert(distance<camera.far);
 const t=THREE.MathUtils.smoothstep(distance,profile.fogConfig.near,profile.fogConfig.far);
 assert(t<.5,'Even the longest map diagonal must retain its skyline');
}
assert.equal(profile.vegetationRenderDistance,560,'Do not expand small scenery with haze distance');
const scene=new THREE.Scene();scene.fog=new THREE.Fog('#aeb9c4',800,20000);
const material=new MeshBasicNodeMaterial();material.colorNode=vec3(.4,.5,.6);
const sky=new THREE.Mesh(new THREE.SphereGeometry(500),material);
const restore=matchHazeToSky(scene,sky);assert(scene.fogNode);restore();assert.equal(scene.fogNode,undefined);

const root=new THREE.Group();root.position.set(30,1,20);root.rotation.y=.3;
const rail=new THREE.Mesh(new THREE.BoxGeometry(60,2,3),new THREE.MeshBasicMaterial());
rail.userData.osmMaterial='bridge-metal';rail.position.set(900,6,-400);rail.rotation.y=.5;root.add(rail);
const building=new THREE.Mesh(new THREE.BoxGeometry(40,120,40),new THREE.MeshBasicMaterial());building.userData.osmMaterial='building-tagged';root.add(building);
const proxy=rail.clone();proxy.userData={};proxy.layers.set(30);root.add(proxy);
root.updateMatrixWorld(true);const before=rail.matrixWorld.clone();
assert.equal(addStreetDetailLods(root),1);root.updateMatrixWorld(true);
assert(rail.matrixWorld.elements.every((v,i)=>Math.abs(v-before.elements[i])<1e-8),'LOD must not move roads/bridge details');
const lod=rail.parent;assert(lod instanceof THREE.LOD);
camera.position.copy(lod.getWorldPosition(new THREE.Vector3()));camera.updateMatrixWorld();lod.update(camera);assert(rail.visible);
camera.position.x+=4000;camera.updateMatrixWorld();lod.update(camera);assert(!rail.visible);
assert(building.visible && building.parent===root);assert(proxy.visible && proxy.parent===root);
camera.position.copy(lod.getWorldPosition(new THREE.Vector3()));camera.updateMatrixWorld();lod.update(camera);assert(rail.visible,'Detail returns when editor/game camera approaches');
console.log('PASS: entire-map camera range, restrained haze, unchanged near plane/scenery budget, sky fog lifecycle, LOD transforms/return/shadow isolation');
