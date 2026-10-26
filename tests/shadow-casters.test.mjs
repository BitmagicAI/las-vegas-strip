import assert from 'node:assert/strict';import * as T from 'three';
// Run: node --import ./tools/ts-register.mjs tests/shadow-casters.test.mjs
const {AfterlightShadows}=await import('../src/work/AfterlightShadows.ts');
const scene=new T.Scene(),level=new T.Group(),sourceSun=new T.DirectionalLight(0xffb46c,2);sourceSun.name='DirectionalLight';sourceSun.position.set(5,1,-2);scene.add(sourceSun,sourceSun.target,level);
const original=new T.Mesh(new T.BoxGeometry(),new T.MeshBasicMaterial());original.castShadow=true;level.add(original);
const system=new AfterlightShadows(scene,level),p=new T.Vector3(-42,0,0);system.update(p);scene.updateMatrixWorld(true);system.sun.shadow.updateMatrices(system.sun);
assert.equal(original.castShadow,false);assert.equal(sourceSun.visible,false);assert.equal(sourceSun.layers.mask,0);assert.equal(system.sun.intensity,2);assert.equal(system.sun.shadow.mapSize.width,4096);assert.equal(system.sun.shadow.camera.right-system.sun.shadow.camera.left,64);
const camera=system.sun.shadow.camera,frustum=new T.Frustum().setFromProjectionMatrix(new T.Matrix4().multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse));
const sunward=sourceSun.position.clone().normalize();assert(frustum.containsPoint(p.clone().addScaledVector(sunward,650)),'Distant upstream tall caster must remain inside the shadow depth');assert(frustum.containsPoint(p),'Player must stay inside shadow frustum');
assert(system.proxies.children.every(m=>m.layers.mask===(1<<30)&&m.castShadow),'Proxies must be shadow-only');assert(system.small.some(s=>!s.mesh.visible),'Distant small objects must be excluded');
const mainCamera=new T.PerspectiveCamera();mainCamera.layers.enable(1);assert(system.proxies.children.every(m=>!m.layers.test(mainCamera.layers)),'Engine main-camera layers 0 and 1 must not reveal proxies');
assert(!scene.children.some(o=>o.name==='Player foot contact shadow'));system.dispose();assert.equal(sourceSun.intensity,2);assert.equal(sourceSun.visible,true);assert.equal(sourceSun.layers.mask,1);console.log('PASS: fine texel density, 650 m upstream caster, nearby small-object culling, shadow-only layers, single sun, cleanup.');
