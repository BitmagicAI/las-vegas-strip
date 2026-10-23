import assert from 'node:assert/strict';
import * as THREE from 'three';
import {GroveLod} from '../../src/work/GroveLod.ts';
const scene=new THREE.Scene(),owner=new THREE.Group();scene.add(owner);
for(let i=0;i<3;i++){const m=new THREE.Mesh(new THREE.BoxGeometry(2,2,2));m.userData.source=`arrival-tree/0,0/${i}`;owner.add(m);}
const original=scene.onBeforeRender,lod=new GroveLod(owner),camera=new THREE.PerspectiveCamera();
for(const [distance,level] of [[10,0],[150,1],[350,2],[800,3],[350,2],[150,1],[10,0]]){
 await new Promise(r=>setTimeout(r,190));camera.position.set(distance,0,0);camera.updateMatrixWorld();scene.onBeforeRender(null,scene,camera);
 assert.deepEqual(owner.children.map(g=>g.visible),[0,1,2].map(i=>i===level));
}
lod.dispose();assert.equal(scene.onBeforeRender,original);console.log('Grove LOD: near, medium, far, culled and return transitions pass; hook restored.');
