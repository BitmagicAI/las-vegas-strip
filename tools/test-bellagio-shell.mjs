import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
import {geometryScene} from './hotel-test-geometry.mjs';

// Test the exported runtime geometry, with back-face culling, not the original
// uncut Blender file. A back wall behind a missing facade is also a failure.
const root=geometryScene('build/hotels/staged-vegas.glb'),meshes=[];
root.traverse(o=>{if(o.isMesh && o.parent.userData.visibilityTower==='bellagio')meshes.push(o);});
const ray=new THREE.Raycaster();ray.far=26;let checks=0;
for(const side of [-1,1])for(let bay=0;bay<24;bay++){
 const u=side*(10+(bay+.5)*3.54),front=-159+18*(Math.abs(u)/95)**2;
 for(const y of [12,20,32,45,58,70,78]){
  // Begin beyond the portico roofs so foreground architecture cannot mask a
  // missing tower facade or be mistaken for the facade being tested.
  ray.set(new THREE.Vector3(front+3,y,-18+u),new THREE.Vector3(-1,0,0));
  const hit=ray.intersectObjects(meshes,false)[0];
  assert(hit,`Missing exterior at bay ${side}/${bay}, height ${y}`);
  assert(Math.abs(hit.point.x-front)<1.4,`See-through facade at ${side}/${bay}/${y}: ${hit.point.x} vs ${front}`);
  assert.notEqual(hit.object.parent.userData.visibilityKind,'interior','Facade must render outdoors with all guest chunks absent');
  checks++;
 }
}
const report={checks,frontFacingFacade:'passed',outdoorVisibility:'passed',streamedRoomShellOwnership:'passed'};
fs.writeFileSync('build/hotels/bellagio-shell-repair/runtime-geometry-test.json',JSON.stringify(report,null,2));console.log(report);
