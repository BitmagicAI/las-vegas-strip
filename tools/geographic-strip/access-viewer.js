import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {createPassageGeometry} from '/src/work/GeographicPassageGeometry.ts';
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(innerWidth,innerHeight);renderer.setClearColor(0x9babbb);document.body.prepend(renderer.domElement);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(60,innerWidth/innerHeight,.1,5000),controls=new OrbitControls(camera,renderer.domElement);controls.minDistance=.5;controls.maxPolarAngle=Math.PI*.9;
scene.add(new THREE.HemisphereLight(0xe2f0ff,0x887257,2.2));const sun=new THREE.DirectionalLight(0xffe2b2,2);scene.add(sun,sun.target);
const $=s=>document.querySelector(s);let current,art;let bulbs=[];
const manifest=await fetch('/build/geographic-strip/access/manifest.json').then(r=>r.json());for(const p of manifest){const o=document.createElement('option');o.value=p.id;o.textContent=p.name;$('#place').append(o);}$('#place').value='bellagio-via';
function draw(){if(!document.hidden)renderer.render(scene,camera);}controls.addEventListener('change',draw);document.addEventListener('visibilitychange',draw);addEventListener('resize',()=>{renderer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();draw();});
function view(p,target){camera.position.set(...p);controls.target.set(...target);sun.position.copy(controls.target).add(new THREE.Vector3(30,70,20));sun.target.position.copy(controls.target);controls.update();draw();}
async function load(){art?.dispose();bulbs.forEach(l=>{l.removeFromParent();l.dispose();});bulbs=[];current=await fetch(`/build/geographic-strip/access/${$('#place').value}.json?v=${Date.now()}`).then(r=>r.json());art=createPassageGeometry(current);scene.add(art.root);for(const p of current.lights){const light=new THREE.PointLight(0xffe3be,25,11,2);light.position.set(...p);scene.add(light);bulbs.push(light);}$('#status').textContent=`${current.portals.length} portals · ${current.meshes.length} material batches`;$('#cutaway').checked=false;overview();}
function overview(){const b=current.bounds,x=(b[0]+b[2])/2,z=(b[1]+b[3])/2;view([x+65,60,z-45],[x,5,z]);}
$('#place').onchange=load;$('#overview').onclick=overview;
$('#entrance').onclick=()=>{const p=current.portals[0],d=p.direction;view([p.p[0]-d[0]*7,p.y+1.7,p.p[1]-d[1]*7],[p.p[0]+d[0]*12,p.y+2,p.p[1]+d[1]*12]);};
$('#arcade').onclick=()=>{if(current.id==='bellagio-via')view([-73,7.8,207.3],[-106,8.3,216.5]);else {const r=current.routes[0],p=r.at(-1);view([p[0],p[1]+1.7,p[2]],current.routes[1]?.at(-1)??r[0]);}};
$('#escalator').onclick=()=>{if(current.id==='bellagio-via')view([-49,7.8,198],[-49,2.5,216]);else overview();};
$('#exit').onclick=()=>{const p=current.portals.at(-1),d=p.direction;view([p.p[0]+d[0]*7,p.y+1.7,p.p[1]+d[1]*7],[p.p[0]-d[0]*7,p.y+2,p.p[1]-d[1]*7]);};
$('#cutaway').onchange=e=>{art.root.traverse(o=>{if(o.name==='access-plaster'||o.name==='access-glazing')o.visible=!e.target.checked;});draw();};await load();
