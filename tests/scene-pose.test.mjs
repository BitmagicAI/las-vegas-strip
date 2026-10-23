import assert from 'node:assert/strict';
import * as THREE from 'three';
import {ownScenePose,ownSceneFrame,ownSceneTranslation} from '../src/work/film/ScenePose.ts';
const scene=new THREE.Scene(),root=new THREE.Group(),bone=new THREE.Bone();scene.add(root);root.add(bone);
const flush=ownScenePose(root);root.position.set(4,0,0);bone.position.set(0,1,0);flush();
assert.deepEqual(bone.matrixWorld.elements.slice(12,15),[4,1,0]);
let calls=0;const update=bone.updateMatrixWorld.bind(bone);bone.updateMatrixWorld=f=>{calls++;update(f);};
for(let i=0;i<10;i++)scene.updateMatrixWorld(true);assert.equal(calls,0,'render passes reuse the owned pose');
root.position.x=9;bone.position.y=2;flush();assert.equal(calls,1);assert.deepEqual(bone.matrixWorld.elements.slice(12,15),[9,2,0]);
console.log('PASS: repeated render passes reuse the pose; explicit animation/physics flush updates all descendants.');

const scene2=new THREE.Scene(),moving=new THREE.Mesh();scene2.add(moving);let before,removed=false;
const release=ownSceneFrame(scene2,cb=>{before=cb;return()=>{removed=true}});
moving.position.x=11;before();assert.equal(moving.matrixWorld.elements[12],11);assert.equal(scene2.matrixWorldAutoUpdate,false);
moving.position.x=15;before();assert.equal(moving.matrixWorld.elements[12],15);release();assert.ok(removed);assert.equal(scene2.matrixWorldAutoUpdate,true);
console.log('PASS: one pre-render pose serves all passes; reset restores automatic scene updates.');

const planted=new THREE.Group(),joint=new THREE.Bone(),toe=new THREE.Bone();planted.add(joint);joint.add(toe);joint.position.y=1;toe.position.set(.1,-.7,.2);joint.rotation.set(.2,.1,.7);planted.rotation.y=.8;planted.updateMatrixWorld(true);
const reference=planted.clone(true),translate=ownSceneTranslation(planted);planted.position.set(2,.4,-7);translate(2,.4,-7);reference.position.copy(planted.position);reference.updateMatrixWorld(true);
const actual=[],expected=[];planted.traverse(o=>actual.push(...o.matrixWorld.elements));reference.traverse(o=>expected.push(...o.matrixWorld.elements));assert.equal(actual.length,expected.length);for(let i=0;i<actual.length;i++)assert.ok(Math.abs(actual[i]-expected[i])<1e-9);
console.log('PASS: planted-foot translation matches a full skeleton world-pose rebuild.');
const hidden=new THREE.Group(),hiddenChild=new THREE.Mesh();hidden.add(hiddenChild);scene2.add(hidden);hidden.visible=false;hidden.position.x=41;
let next;const restore2=ownSceneFrame(scene2,cb=>{next=cb;return()=>{}});next();assert.equal(hiddenChild.matrixWorld.elements[12],0);hidden.visible=true;next();assert.equal(hiddenChild.matrixWorld.elements[12],41,'newly visible roots are updated before rendering');restore2();
console.log('PASS: hidden scene roots defer transforms until their next visible frame.');
const skinnedRoot=new THREE.Group(),skin=new THREE.SkinnedMesh();skinnedRoot.add(skin);skinnedRoot.updateMatrixWorld(true);const moveSkin=ownSceneTranslation(skinnedRoot);skinnedRoot.position.set(3,.5,-2);moveSkin(3,.5,-2);
const identity=new THREE.Matrix4().multiplyMatrices(skin.matrixWorld,skin.bindMatrixInverse);assert.ok(identity.equals(new THREE.Matrix4()),'translated attached skin bind inverse must follow its world matrix');
console.log('PASS: attached skin binding remains consistent after cached foot-plant translation.');
