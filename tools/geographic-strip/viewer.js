import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {createPassageGeometry} from '/src/work/GeographicPassageGeometry.ts';
import {applyStreetMaterials} from '/src/work/GeographicStreetMaterials.ts';
import {addStreetDetailLods,extendSkylineCamera,matchHazeToSky} from '/src/work/StripAtmosphere.ts';
import {WebGPURenderer} from 'three/webgpu';
import {configureReversedDepthSorting} from '/src/work/SkylineDepth.ts';
import {SkyboxMaterialHelper} from 'engine/loaders/SkyboxMaterialHelper.js';
import {setActiveRendererType} from 'engine/RendererType.js';
const skyline=new URLSearchParams(location.search).has('skyline');
const reverseDepth=!new URLSearchParams(location.search).has('standardDepth');
const renderer=skyline?new WebGPURenderer({antialias:true,reversedDepthBuffer:reverseDepth}):new THREE.WebGLRenderer({antialias:true});if(skyline){setActiveRendererType('webgpu');await renderer.init();if(reverseDepth)configureReversedDepthSorting(renderer);}
renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(innerWidth,innerHeight);renderer.setClearColor(0xa7bdcb);document.body.prepend(renderer.domElement);
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(50,innerWidth/innerHeight,.1,22000),controls=new OrbitControls(camera,renderer.domElement);
controls.maxPolarAngle=Math.PI*.9;controls.minDistance=3;
scene.add(new THREE.HemisphereLight(0xe1eeff,0x8c785b,2.4));const sun=new THREE.DirectionalLight(0xffeddc,2);sun.position.set(1200,3000,1000);scene.add(sun);
if(skyline){
 const p=(await fetch('/src/work/world.json').then(r=>r.json())).worldProfileData;
 scene.fog=new THREE.Fog(p.fogConfig.color,p.fogConfig.near,p.fogConfig.far);
 const sky=SkyboxMaterialHelper.createMesh(await new THREE.TextureLoader().loadAsync(p.skyboxUrl),{linearTexture:false,rotationDeg:25,brightness:p.lightingConfig.skyboxIntensity});
 scene.add(sky.mesh);if(new URLSearchParams(location.search).has('noSky'))sky.mesh.visible=false;matchHazeToSky(scene,sky.mesh);extendSkylineCamera(camera);
 renderer.toneMapping=THREE.ACESFilmicToneMapping;
}
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.near=1;sun.shadow.camera.far=900;sun.shadow.camera.left=sun.shadow.camera.bottom=-140;sun.shadow.camera.right=sun.shadow.camera.top=140;sun.shadow.normalBias=.06;sun.shadow.bias=-.00015;scene.add(sun.target);
const $=s=>document.querySelector(s);let ready=false;function draw(){if(document.hidden)return;renderer.info.reset();renderer.render(scene,camera);if(ready)$('#stats').textContent=`${renderer.info.render.drawCalls??renderer.info.render.calls} draws · ${renderer.info.render.triangles.toLocaleString()} triangles`;}controls.addEventListener('change',draw);addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);draw();});document.addEventListener('visibilitychange',draw);
function view(center,offset){controls.target.set(...center);camera.position.copy(controls.target).add(new THREE.Vector3(...offset));sun.target.position.set(...center);sun.position.copy(sun.target.position).add(new THREE.Vector3(170,320,190));controls.update();draw();}
const versions=await Promise.all(['city','detailed'].map(n=>fetch(`/build/geographic-strip/${n}-version.json`).then(r=>r.json())));
const groups=await Promise.all(['city','detailed'].map(async(n,i)=>{const gltf=await new GLTFLoader().loadAsync(`/build/geographic-strip/${n}.glb?v=${versions[i].revision}`);gltf.scene.traverse(o=>{if(o.userData.visibilityKind==='interior')o.visible=false;});scene.add(gltf.scene);return gltf.scene;}));
applyStreetMaterials(groups[0],skyline && renderer.reversedDepthBuffer);groups.forEach(g=>g.traverse(o=>{if(o.isMesh){o.receiveShadow=true;o.castShadow=!o.userData.osmMaterial || /^(building|tag\/|utility|bridge-(deck|concrete|metal|roof))/.test(o.userData.osmMaterial);}}));
addStreetDetailLods(groups[0]);
$('#background').onchange=e=>{groups[0].visible=e.target.checked;draw();};$('#details').onchange=e=>{groups[1].visible=e.target.checked;draw();};
$('#whole').onclick=()=>view([-200,0,200],[5400,5600,6400]);$('#central').onclick=()=>view([-130,20,300],[750,730,900]);$('#city').onclick=()=>view([-270,25,940],[650,570,740]);$('#street').onclick=()=>view([-280,50,322],[290,-47,110]);
const passageData=await fetch('/build/geographic-strip/access/bellagio-via.json?v='+versions[0].revision).then(r=>r.json());scene.add(createPassageGeometry(passageData).root);
$('#bridge-corner').onclick=()=>view([-32,5,167],[100,80,125]);
$('#sphere').onclick=()=>view([850,7,-690],[36,22,-50]);$('#roads').onclick=()=>view([1110,.18,-720],[85,56,78]);
const wynnButton=document.createElement('button');wynnButton.textContent='Wynn / Encore streets';document.querySelector('aside').insertBefore(wynnButton,document.querySelector('aside p:last-of-type'));wynnButton.onclick=()=>view([590,0,-1470],[-360,330,280]);
const curbButton=document.createElement('button');curbButton.textContent='Curb detail';wynnButton.after(curbButton);curbButton.onclick=()=>view([546.47,.2,-1421.78],[-14,4,12]);
const arrivalButton=document.createElement('button');arrivalButton.textContent='Encore arrival roads';curbButton.after(arrivalButton);arrivalButton.onclick=()=>view([625,0,-1560],[-110,95,125]);
if(skyline){
 for(const [label,center,offset] of [['North along Strip',[300,100,-2000],[-650,180,4700]],['South along Strip',[-500,110,2000],[1100,220,-4700]]]){
  const button=document.createElement('button');button.textContent=label;arrivalButton.after(button);button.onclick=()=>view(center,offset);
 }
}
for(const [label,center,offset] of [['CityCenter distant skyline',[-270,95,940],[1700,260,2000]],['Veer distant',[-150,90,950],[160,-80,700]],['Veer close',[-150,75,950],[130,-69,120]],['Aria distant',[-340,100,890],[600,-94,400]]]){const button=document.createElement('button');button.textContent=label;arrivalButton.after(button);button.onclick=()=>view(center,offset);}
ready=true;$('#status').textContent=skyline?`20 km view · ${reverseDepth?'precision depth':'baseline depth'} · sky-matched haze`:'Local geographic build';view([-130,20,300],[750,730,900]);
