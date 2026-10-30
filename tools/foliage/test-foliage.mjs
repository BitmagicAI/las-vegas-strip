import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as T from 'three';
import {MeshStandardNodeMaterial} from 'three/webgpu';
import {ResortFoliage} from '../../src/work/ResortFoliage.ts';
import {PlantList,loadPlants} from '../../src/work/Plants.ts';
import {runSync} from '../../src/work/FrameBudget.ts';
import {foliageSettings,FoliageSettingsStore,FOLIAGE_SETTINGS_KEY} from '../../src/work/FoliageSettings.ts';
/** [x, y, z, yaw, scale] per plant -> a PlantList in the bytes tools/optimize/pack-data.mjs writes (a 1 cm grid from 0). */
function plantList(plants){
    const data=new Uint8Array(plants.length*8),dv=new DataView(data.buffer);
    plants.forEach(([x,y,z,yaw,scale],i)=>{[x,y,z].forEach((v,a)=>dv.setUint16(i*8+a*2,Math.round(v*100),true));dv.setUint8(i*8+6,Math.round(yaw*128/Math.PI)&255);dv.setUint8(i*8+7,Math.round(scale*255/2));});
    return new PlantList(plants.length,new Float32Array([0,0,0]),new Float32Array([.01,.01,.01]),0,2/255,data);
}
const scene=new T.Scene(),owner=new T.Group();scene.add(owner);
const foliage=new ResortFoliage(scene,owner);
// sharedInstancedMesh takes node materials only; load() converts the GLBs' materials before populating
const asset=new T.Group();asset.add(new T.Mesh(new T.BoxGeometry(1,6,1).translate(0,3,0),new MeshStandardNodeMaterial()));
runSync(foliage.populate(plantList([[0,.51,0,0,1],[3,.51,3,1,.9],[82,.51,0,2,1]]),[asset,asset,asset],40,[85,220,650],true));
const grove=foliage.cells[0].levels[0].children[0];
assert.equal(foliage.cells.length,2);assert.equal(grove.geometry.instanceCount,2);
assert.equal(foliage.cells[0].levels[0].children.length,1,'One material draws the whole grove in one call');
const second=grove.geometry.getAttribute('instanceColumn3').data.array.subarray(16+12,16+15);
assert.deepEqual([...second].map(v=>Math.round(v*100)/100),[3,.51,3],'Plants keep their places and their order within a cell');
for(const [x,level] of [[0,0],[140,1],[350,2],[900,3],[0,0]]){foliage.select(new T.Vector3(x,0,0));assert.equal(foliage.cells[0].level,level);assert.equal(foliage.cells[0].levels.filter(g=>g.visible).length,level===3?0:1);}
const grass=JSON.parse(fs.readFileSync('public/foliage/bellagio-placements.json'));assert(grass.grass.length>1000);assert(grass.grass.every(p=>p[1]===.512&&p[4]>0&&p[4]<2));assert(grass.trees.every(t=>t.crownRadius===4));
// The game loads only the packed copy: decode it as Plants.ts does and hold it to the JSON it is packed from.
const fetched=globalThis.fetch;globalThis.fetch=async()=>new Response(fs.readFileSync('public/foliage/bellagio-placements.bin'));
const packed=await loadPlants('/foliage/bellagio-placements.bin');globalThis.fetch=fetched;
assert.equal(packed.trees.count,grass.trees.length);assert.equal(packed.grass.count,grass.grass.length);
const off=(list,i,[x,y,z])=>Math.max(Math.abs(list.x(i)-x),Math.abs(list.y(i)-y),Math.abs(list.z(i)-z));
let far=0,scaleOff=0;grass.trees.forEach((t,i)=>{far=Math.max(far,off(packed.trees,i,t.position));});
grass.grass.forEach((p,i)=>{far=Math.max(far,off(packed.grass,i,p));scaleOff=Math.max(scaleOff,Math.abs(packed.grass.scale(i)-p[4]));});
assert(far<.01&&scaleOff<.002,`bellagio-placements.bin differs from its JSON (${far.toFixed(4)} m, scale ${scaleOff.toFixed(4)}): node tools/optimize/pack-data.mjs`);
foliageSettings.set({enabled:false});foliage.select(new T.Vector3());assert.equal(foliage.root.visible,false);
foliageSettings.set({enabled:true,distanceScale:.25});foliage.select(new T.Vector3(350,0,0));assert.equal(foliage.root.visible,true);assert.equal(foliage.cells[0].level,3);
foliageSettings.set({distanceScale:2});foliage.select(new T.Vector3(350,0,0));assert.equal(foliage.cells[0].level,1);
foliageSettings.set({distanceScale:1});
let saved=null;const storage={getItem:()=>saved,setItem:(key,value)=>{assert.equal(key,FOLIAGE_SETTINGS_KEY);saved=value;}};
const prefs=new FoliageSettingsStore(storage);prefs.set({enabled:false,distanceScale:.75});
assert.deepEqual(new FoliageSettingsStore(storage).get(),{enabled:false,distanceScale:.75});
saved='bad json';assert.deepEqual(new FoliageSettingsStore(storage).get(),{enabled:true,distanceScale:1});
prefs.set({distanceScale:Infinity});assert.equal(prefs.get().distanceScale,1);
prefs.set({distanceScale:999});assert.equal(prefs.get().distanceScale,2);
const blocked=new FoliageSettingsStore({getItem(){throw Error('blocked')},setItem(){throw Error('quota')}});blocked.set({enabled:false});assert.equal(blocked.get().enabled,false);
console.log('Foliage visibility, distance, persistence, invalid storage and blocked storage passed.');
foliage.dispose();assert.equal(owner.children.length,0);
console.log(`Instancing, 5 LOD transitions, cleanup, ${grass.trees.length} tree placements and ${grass.grass.length} grass placements passed.`);
const bladeManifest=JSON.parse(fs.readFileSync('tools/foliage/models/grass-manifest.json'));
assert.equal(bladeManifest.kind,'mown-grass');
assert(bladeManifest.lods[0].triangles<=72 && bladeManifest.lods[1].triangles<=8,'Lawn must not regress to heavyweight scrub');
assert(grass.grass.every(p=>p[4]>=.85&&p[4]<=1.05),'No oversized perimeter band');
