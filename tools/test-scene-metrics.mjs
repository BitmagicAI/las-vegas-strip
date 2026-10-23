import assert from 'node:assert/strict';
import * as THREE from 'three';
import {inventoryScene,renderCounters,SceneMetrics} from '../src/work/SceneMetrics.js';

// Shared assets, parent visibility and camera layers must not inflate the
// enabled count or confuse loaded geometry with actual renderer submissions.
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera();
const geometry=new THREE.BoxGeometry(),material=new THREE.MeshBasicMaterial();
const group=new THREE.Group();group.visible=false;scene.add(group);
const hidden=new THREE.Mesh(geometry,material);group.add(hidden);
const layers=new THREE.Mesh(geometry,material);layers.layers.set(3);scene.add(layers);
const instanced=new THREE.InstancedMesh(geometry,material,10);scene.add(instanced);
instanced.userData.perfOwner='Test interior';instanced.userData.perfKind='interior';
const observed=[];const inventory=inventoryScene(scene,camera,m=>observed.push(m));
assert.equal(inventory.objects,5);assert.equal(inventory.meshes,3);assert.equal(inventory.enabled,1);
assert.equal(inventory.geometries,1);assert.equal(inventory.materials,1);assert.deepEqual(observed,[instanced]);
const renderer={info:{render:{calls:50000,drawCalls:0,triangles:0}}};
assert.deepEqual(renderCounters(renderer),{calls:0,triangles:0});
assert.deepEqual(renderCounters({info:{render:{calls:7,triangles:36}}}),{calls:7,triangles:36});
let beforeCount=0,afterCount=0,sceneCount=0,updates=0;
const before=()=>beforeCount++,after=()=>afterCount++,sceneAfter=()=>sceneCount++;
instanced.onBeforeRender=before;instanced.onAfterRender=after;scene.onAfterRender=sceneAfter;
const metrics=new SceneMetrics({scene,camera,renderer},()=>updates++);
scene.onBeforeRender(renderer,scene,camera);
// Two material groups, each with ten instances: measured renderer deltas,
// not a guessed one-call-per-object or raw base-geometry triangle count.
for(let i=0;i<2;i++){
 instanced.onBeforeRender(renderer,scene,camera,geometry,material,null);
 renderer.info.render.drawCalls++;renderer.info.render.triangles+=60;
 instanced.onAfterRender(renderer,scene,camera,geometry,material,null);
}
scene.onAfterRender(renderer,scene,camera);
const row=metrics.inventory.components.find(r=>r.name==='Test interior');
assert.equal(row.drawn,1);assert.equal(row.calls,2);assert.equal(row.triangles,120);assert.equal(row.smallDrawn,1);
assert.equal(beforeCount,2);assert.equal(afterCount,2);assert.equal(sceneCount,1);assert.equal(updates,1);
assert.equal(instanced.onBeforeRender,before);assert.equal(instanced.onAfterRender,after);
assert.equal(hidden.visible,true);assert.equal(group.visible,false); // measuring cannot reveal anything
metrics.dispose();assert.equal(scene.onAfterRender,sceneAfter);
const compact=new SceneMetrics({scene,camera,renderer},()=>{});compact.detailed=false;
scene.onBeforeRender(renderer,scene,camera);scene.onAfterRender(renderer,scene,camera);
assert.equal(compact.inventory,null);assert.equal(instanced.onBeforeRender,before);
compact.dispose();geometry.dispose();material.dispose();
console.log('Scene metrics: inventory, renderer backend counters, instancing/groups, hook restoration and compact mode passed.');
