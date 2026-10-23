import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {finishSphereMaterials,addSphereSeats,addSphereSigns} from '/src/work/SphereVisuals.ts';
import {SphereVideo} from '/src/work/SphereVideo.ts';
const scene=new THREE.Scene();scene.background=new THREE.Color(0x0d1929);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setSize(innerWidth,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.2;document.body.append(renderer.domElement);
const camera=new THREE.PerspectiveCamera(67,innerWidth/innerHeight,.12,900);const controls=new OrbitControls(camera,renderer.domElement);controls.maxDistance=400;controls.minDistance=1;
const ambient=new THREE.HemisphereLight(0x96b3db,0x222a31,1.5);scene.add(ambient);const sun=new THREE.DirectionalLight(0xc4d9ff,2);sun.position.set(-70,140,-100);scene.add(sun);
const meta=await fetch('/build/sphere/sphere.json').then(r=>r.json());const media=await fetch('/build/sphere/media.json').then(r=>r.json());
const vids=[];for(const name of ['exterior','interior']){
 const gltf=await new GLTFLoader().loadAsync(`/build/sphere/${name}.glb?v=${Date.now()}`);finishSphereMaterials(gltf.scene);addSphereSigns(gltf.scene,meta,name);if(name==='interior')addSphereSeats(gltf.scene,meta);
 const vid=new SphereVideo('/build/sphere/'+media[name],'/build/sphere/'+media[name+'Poster']);vids.push(vid);
 gltf.scene.traverse(o=>{if(o instanceof THREE.Mesh && o.userData.spherePart===(name==='exterior'?'shell':'screen')){o.material=vid.material;}});scene.add(gltf.scene);
}
const ground=new THREE.Mesh(new THREE.PlaneGeometry(700,700),new THREE.MeshStandardMaterial({color:0x25343e,roughness:.92}));ground.rotation.x=-Math.PI/2;ground.position.y=-.3;scene.add(ground);
for(const [x,y,z] of [[0,20,-52],[-42,15,-45],[42,15,-45],[0,36,15]]){const l=new THREE.PointLight(0x78d9ff,1600,90,2);l.position.set(x,y,z);scene.add(l);}
function view(name){const v=meta.views[name];camera.position.set(...v.p);controls.target.set(...v.target);controls.update();const inside=['atrium','escalators','bowl','upper'].includes(name);ambient.intensity=inside?.35:1.5;sun.intensity=inside?0:2;vids[0].setActive(!inside);vids[1].setActive(['bowl','upper'].includes(name));document.getElementById('status').textContent=`${name} · ${meta.seats.length.toLocaleString()} shared seat instances`;}
for(const name of Object.keys(meta.views)){const b=document.createElement('button');b.textContent=name;b.onclick=()=>view(name);document.getElementById('views').append(b);}
view(new URLSearchParams(location.search).get('view')??'exterior');
const render=()=>renderer.render(scene,camera);
const visibility=()=>{renderer.setAnimationLoop(document.hidden || !document.hasFocus()?null:render);};
addEventListener('focus',visibility);addEventListener('blur',visibility);document.addEventListener('visibilitychange',visibility);visibility();render();
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
