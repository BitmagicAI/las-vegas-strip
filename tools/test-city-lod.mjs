// Run: node --import ./tools/ts-register.mjs tools/test-city-lod.mjs
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {CityLod,lodDistances,lodLevel} from '../src/work/CityLod.ts';
import {batchStaticMeshes,coarseFromBatch,citySurfaceTable,disposeCityMaterial as releaseMaterial} from '../src/work/CityBatches.ts';
import {GroundSurfaceIndex} from '../src/work/GroundSurfaceIndex.ts';
const scene=new THREE.Scene(),root=new THREE.Group();scene.add(root);root.position.set(10,0,0);
const a=new THREE.Mesh(new THREE.BoxGeometry(10,4,10),new THREE.MeshStandardMaterial({color:0xff0000,roughness:.2,metalness:.8}));a.position.set(0,2,0);root.add(a);
const b=new THREE.Mesh(new THREE.BoxGeometry(4,8,4),new THREE.MeshStandardMaterial({color:0x00ff00,roughness:.9}));b.position.set(20,4,0);root.add(b);
const pane=new THREE.Mesh(new THREE.BoxGeometry(1,1,.1),new THREE.MeshStandardMaterial({transparent:true,opacity:.3}));pane.position.set(30,2,0);root.add(pane);root.updateMatrixWorld(true);const paneMatrix=pane.matrixWorld.clone();
const surfaces=new GroundSurfaceIndex();surfaces.register(root);assert.equal(surfaces.height(10,0,20,0),4);
const sourceIndexCount=a.geometry.index.count+b.geometry.index.count;const lod=new CityLod(root,{key:()=> 'test'});assert.equal(lod.stats.blocks,1);
const high=root.getObjectByName('Full detail / test');assert.equal(high.children.length,2,'different PBR colors share a draw, transparent panes retain sorting');assert.equal(pane.parent,high);root.updateMatrixWorld(true);assert.deepEqual(pane.matrixWorld.elements,paneMatrix.elements,'unmerged surface keeps its world transform');
assert.equal(high.children[0].geometry.index.count,sourceIndexCount);
{// Compact layout: float positions/uvs, 8/16-bit normals, 8-bit sRGB colour, one table row per vertex.
const g=high.children[0].geometry,at=n=>g.getAttribute(n);
assert.ok(at('position').array instanceof Float32Array&&at('uv').array instanceof Float32Array);
assert.ok(!at('normal').normalized&&at('normal').array instanceof Float32Array,'a glossy/metal bucket keeps float normals');{const m=batchStaticMeshes([new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial({roughness:.9}))],'matte').children[0];assert.ok(m.geometry.getAttribute('normal').normalized&&m.geometry.getAttribute('normal').array instanceof Int8Array,'matte buckets use 8-bit normals');releaseMaterial(m.material);}
assert.ok(at('color').normalized&&at('color').array instanceof Uint8Array&&at('color').itemSize===4);
assert.deepEqual(Object.keys(g.attributes).sort(),['batchMaterial','color','normal','position','uv']);
const rowOf=v=>at('batchMaterial').getX(v),t=citySurfaceTable.image.data,ra=rowOf(0),rb=rowOf(g.getAttribute('position').count-1);
assert.notEqual(ra,rb,'different PBR factors are different table rows');
assert.ok(Math.abs(t[ra*12]-.2)<1e-6&&Math.abs(t[ra*12+1]-.8)<1e-6,'row holds roughness and metalness');
assert.ok(Math.abs(at('color').getX(0)-1)<1e-6&&at('color').getY(0)===0,'red stays red (sRGB-encoded)');
assert.equal(a.geometry.getAttribute('position'),undefined,'merged source geometry is released to the placeholder');}
assert.equal(surfaces.height(10,0,20,0),4,'exact source grounding survives batching');
root.visible=false;assert.equal(surfaces.height(10,0,20,0),undefined,'parent visibility still gates grounding');root.visible=true;
assert.equal(lodDistances(160).far,Infinity);assert.ok(Number.isFinite(lodDistances(8).far));
assert.equal(lodLevel(205,200,1200,0),0);assert.equal(lodLevel(230,200,1200,0),1);assert.equal(lodLevel(180,200,1200,1),1);assert.equal(lodLevel(170,200,1200,1),0);
assert.equal(lodLevel(1400,200,1200,1),2);assert.equal(lodLevel(100000,800,Infinity,1),1);
const camera=new THREE.PerspectiveCamera();camera.position.set(600,0,0);lod.select(camera,1000);assert.equal(lod.stats.coarse,1);assert.equal(surfaces.height(10,0,20,0),4,'editor LOD does not remove player grounding');camera.position.x=4000;lod.select(camera,1200);assert.equal(lod.stats.culled,1);camera.position.x=10;lod.select(camera,1400);assert.equal(lod.stats.full,1);
const sphereMesh=batchStaticMeshes([new THREE.Mesh(new THREE.SphereGeometry(20,64,48),new THREE.MeshStandardMaterial())],'sphere').children[0],sphere=sphereMesh.geometry;releaseMaterial(sphereMesh.material);const low=coarseFromBatch(sphere,2);assert.ok(low.index.count<sphere.index.count/2);for(const x of low.getAttribute('position').array)assert.ok(Number.isFinite(x));assert.ok(low.getAttribute('normal').array instanceof Int8Array);assert.equal(low.getAttribute('batchMaterial').getX(0),sphere.getAttribute('batchMaterial').getX(0));
let selected=0;const select=lod.select.bind(lod);lod.select=()=>{selected++;};scene.overrideMaterial=new THREE.MeshBasicMaterial();scene.onBeforeRender(null,scene,camera);assert.equal(selected,0,'shadow/override passes cannot change view LOD');scene.overrideMaterial.dispose();scene.overrideMaterial=null;scene.onBeforeRender(null,scene,camera);assert.equal(selected,1,'main and editor views update LOD');lod.select=select;
lod.dispose();assert.equal(a.parent,null,'merged sources are not restored: their geometry was released');assert.equal(pane.parent,root);assert.equal(pane.matrixAutoUpdate,true);root.updateMatrixWorld(true);assert.deepEqual(pane.matrixWorld.elements,paneMatrix.elements);assert.equal(scene.onBeforeRender.name,'onBeforeRender');
console.log('PASS: batch material factors, transformed bounds, exact grounding, hidden parents, scale-aware distance, hysteresis, clustering and disposal');

const {batchCityShadows}=await import('../src/work/CityShadows.ts');
const shadowRoot=new THREE.Group();scene.add(shadowRoot);let shadowTriangles=0;
for(let i=0;i<10;i++){const m=new THREE.Mesh(new THREE.BoxGeometry(2,4,2),new THREE.MeshBasicMaterial());m.position.x=i*3;m.layers.set(30);m.castShadow=true;shadowRoot.add(m);shadowTriangles+=m.geometry.index.count/3;}
batchCityShadows(shadowRoot);assert.equal(shadowRoot.children.length,1);assert.equal(shadowRoot.children[0].geometry.index.count/3,shadowTriangles);assert.equal(shadowRoot.children[0].layers.mask,1<<30);
const {makeDoorTrim}=await import('../src/work/DoorTrim.ts');const trim=makeDoorTrim([[-1,0,.075,3.1],[1,0,.075,3.1],[0,-1.5,2.07,.075],[0,1.5,2.07,.075],[.8,0,.055,.7]],.12,new THREE.MeshStandardMaterial());assert.equal(trim.geometry.index.count,5*36);assert.equal(trim.geometry.groups.length,0);
console.log('PASS: exact shadow triangle batching and moving door trim');
const {disposeCityMaterial}=await import('../src/work/CityBatches.ts');
const sharedA=batchStaticMeshes([new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial({color:0xaa0000}))],'a');
const sharedB=batchStaticMeshes([new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial({color:0x00aa00}))],'b');
assert.equal(sharedA.children[0].material,sharedB.children[0].material,'separate city blocks share one shader/material');
let disposed=0;sharedA.children[0].material.addEventListener('dispose',()=>disposed++);disposeCityMaterial(sharedA.children[0].material);assert.equal(disposed,0,'one block eviction must retain another block material');disposeCityMaterial(sharedB.children[0].material);assert.equal(disposed,1,'last owner releases shared material');
console.log('PASS: cross-block shader sharing and reference-counted disposal');

// A color buffer is dormant when vertexColors=false; physical materials need
// their own shader features and must remain unmerged.
const untouched=new THREE.Group(),physical=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshPhysicalMaterial({clearcoat:1}));untouched.add(physical);
const inactiveColor=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial({color:0xffffff}));
inactiveColor.geometry.setAttribute('color',new THREE.Float32BufferAttribute(new Float32Array(24*3),3));untouched.add(inactiveColor);
const correct=batchStaticMeshes([physical,inactiveColor],'material compatibility');assert.equal(physical.parent,untouched);assert.equal(correct.children.length,1);assert.equal(correct.children[0].geometry.getAttribute('color').getX(0),1);
console.log('PASS: unsupported physical materials and inactive vertex colors preserve appearance');

const {CityDetailRanges,cityEntranceDetails}=await import('../src/work/CityDetailRanges.ts');
const detailScene=new THREE.Scene(),transformed=new THREE.Group();transformed.position.set(20,0,40);detailScene.add(transformed);
const leaf=new THREE.Mesh(new THREE.BoxGeometry(2,3,.1),new THREE.MeshStandardMaterial());leaf.name='door_test_pivot';leaf.position.set(10,1.5,2);transformed.add(leaf);
const tower=new THREE.Mesh(new THREE.BoxGeometry(30,160,30),new THREE.MeshStandardMaterial());detailScene.add(tower);
const details=cityEntranceDetails(detailScene);assert.deepEqual(details,[leaf]);detailScene.updateMatrixWorld(true);const originalWorld=leaf.matrixWorld.clone();
const detailRange=new CityDetailRanges(detailScene,details);detailScene.updateMatrixWorld(true);assert.deepEqual(leaf.matrixWorld.elements,originalWorld.elements);
const rangeParent=leaf.parent;camera.position.set(1000,0,0);detailRange.select(camera,1000);assert.equal(rangeParent.visible,false);assert.equal(tower.visible,true);
leaf.visible=false;camera.position.set(30,0,42);detailRange.select(camera,1300);assert.equal(rangeParent.visible,true);assert.equal(leaf.visible,false,'range culling cannot reveal a gameplay-hidden door');
leaf.position.x+=2;detailScene.updateMatrixWorld(true);assert.equal(leaf.getWorldPosition(new THREE.Vector3()).x,32,'moving leaves retain local animation');
detailRange.dispose();assert.equal(leaf.parent,transformed);assert.equal(leaf.position.x,12);assert.equal(leaf.visible,false);
console.log('PASS: small-detail cell culling preserves tower visibility, transforms, animated leaves and gameplay hiding');

const lateRanges=new CityDetailRanges(detailScene,[]);lateRanges.watchDoorParent(transformed);
const lateDoor=new THREE.Group();lateDoor.name='door_async_pivot';lateDoor.add(new THREE.Mesh(new THREE.BoxGeometry(2,3,.1),new THREE.MeshStandardMaterial()));
transformed.add(lateDoor);lateDoor.position.set(500,2,0); // Fit happens after childadded.
await Promise.resolve();camera.position.set(0,0,0);lateRanges.select(camera,2000);
assert.notEqual(lateDoor.parent,transformed);assert.equal(lateDoor.parent.visible,false,'late fitted door joins correct distant cell');
assert.equal(lateDoor.getWorldPosition(new THREE.Vector3()).x,520);
lateRanges.dispose();assert.equal(lateDoor.parent,transformed);
const afterDispose=new THREE.Group();afterDispose.name='door_after_dispose_pivot';transformed.add(afterDispose);await Promise.resolve();assert.equal(afterDispose.parent,transformed);
console.log('PASS: asynchronously loaded doors register once after fitting, and dispose removes subscription');

// Hotel silhouettes retain material boundaries, flat-wall normals, UVs and atlas
// ownership. The old position-only clustering blended these overlapping layers.
{
const {facadeFromBatch}=await import('../src/work/CityBatches.ts');
const facadeRoot=new THREE.Group();scene.add(facadeRoot);
const stone=new THREE.Mesh(new THREE.PlaneGeometry(100,40,200,80),new THREE.MeshStandardMaterial({color:0xd2ae7b,roughness:.87}));
const window=new THREE.Mesh(new THREE.PlaneGeometry(100,40,200,80),new THREE.MeshStandardMaterial({color:0x152539,roughness:.15,metalness:.6}));window.position.z=.12;
const trim=new THREE.Mesh(new THREE.PlaneGeometry(100,40,200,80),new THREE.MeshStandardMaterial({color:0xffffff,roughness:.87}));trim.position.z=.24;
const back=new THREE.Mesh(new THREE.PlaneGeometry(100,40,200,80),new THREE.MeshStandardMaterial({color:0xd2ae7b,roughness:.87}));back.rotation.y=Math.PI;back.position.z=-.1;
const matchingTrim=trim.clone();matchingTrim.position.z=.32;
facadeRoot.add(stone,window,trim,back,matchingTrim);
for(const mesh of facadeRoot.children)mesh.material.envMapIntensity=.731;
const glass=new THREE.Mesh(new THREE.PlaneGeometry(10,20),new THREE.MeshStandardMaterial({transparent:true,opacity:.25}));facadeRoot.add(glass);
const water=new THREE.Mesh(new THREE.PlaneGeometry(8,8),new THREE.MeshPhysicalMaterial());water.material.userData.realisticWater='pool';facadeRoot.add(water);
const facadeLod=new CityLod(facadeRoot,{key:()=> 'hotel',facade:true});
const fullHotel=facadeRoot.getObjectByName('Full detail / hotel'),lowHotel=facadeRoot.getObjectByName('Silhouette / hotel');
const fullMesh=fullHotel.children[0],lowMesh=lowHotel.children[0];
assert.equal(fullMesh.material,lowMesh.material,'hotel levels share exactly the same textured/PBR shader');
assert.ok(lowMesh.geometry.index.count<fullMesh.geometry.index.count*.8,'dense facade tessellation still reduces');
assert.equal(water.parent,fullHotel,'remote water retains its existing LOD culling instead of adding offscreen reflection passes');
assert.equal(glass.parent.name,'Continuous surfaces / hotel','custom/transparent surfaces do not vanish at the facade switch');
const fg=fullMesh.geometry,lg=lowMesh.geometry,fp=fg.getAttribute('position'),lp=lg.getAttribute('position');
const fc=fg.getAttribute('color'),lc=lg.getAttribute('color'),ln=lg.getAttribute('normal'),lu=lg.getAttribute('uv');
const palette=new Set();for(let i=0;i<fc.count;i++)palette.add(fc.getX(i)+','+fc.getY(i)+','+fc.getZ(i));
for(let i=0;i<lc.count;i++){
 assert.ok(palette.has(lc.getX(i)+','+lc.getY(i)+','+lc.getZ(i)),'no blended white/beige/glass vertex tint');
 assert.ok(Math.abs(ln.getZ(i))>.999,'opposite flat faces keep their own normals');
 assert.ok(lu.getX(i)>=0&&lu.getX(i)<=1&&lu.getY(i)>=0&&lu.getY(i)<=1,'UVs survive simplification');
 const z=lp.getZ(i);assert.ok([0,.12,.24,.32,-.1].some(source=>Math.abs(z-source)<1e-5),'parallel planes, including identical-colour wall/trim, stay at their original depths');
}
assert.ok(lg.getAttribute('normal').array instanceof Float32Array,'glossy facade precision survives');
assert.deepEqual(facadeFromBatch(fg,null).getAttribute('uv').array,fg.getAttribute('uv').array,'coarsening disabled keeps source mapping');
const distances=lodDistances(40,undefined,undefined,false,100);assert.equal(distances.near,600);assert.equal(distances.far,Infinity);
assert.equal(lodDistances(30,undefined,undefined,false,500).near,650,'broad low resort grounds cannot force kilometre-wide full detail');
assert.ok(lodDistances(160,undefined,undefined,false,160).near>lodDistances(160).near,'large towers retain detail longer too');
camera.fov=70;camera.updateProjectionMatrix();camera.position.set(0,0,400);facadeLod.select(camera,2200);assert.equal(facadeLod.stats.full,1,'low hotel stays detailed across the boulevard');
camera.position.z=1000;facadeLod.select(camera,2500);assert.equal(facadeLod.stats.coarse,1);
camera.fov=30;camera.updateProjectionMatrix();facadeLod.select(camera,2800);assert.equal(facadeLod.stats.full,1,'stationary editor zoom restores detail');
let facadeDisposed=0;fullMesh.material.addEventListener('dispose',()=>facadeDisposed++);facadeLod.dispose();assert.equal(facadeDisposed,1,'shared high/low material disposes only once');assert.equal(glass.parent,facadeRoot);
console.log('PASS: hotel material/normal/UV continuity, retained transparent surfaces, geometry reduction, footprint ranges, stationary zoom and shared atlas lifetime');
}
