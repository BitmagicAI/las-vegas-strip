import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(innerWidth,innerHeight);renderer.setClearColor(0x142431);document.body.prepend(renderer.domElement);
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,2,22000);
const controls=new OrbitControls(camera,renderer.domElement);controls.maxPolarAngle=Math.PI*.485;controls.maxDistance=13000;controls.minDistance=25;controls.enableDamping=false;
scene.add(new THREE.HemisphereLight(0xdcecff,0x535d4f,2.4));const sun=new THREE.DirectionalLight(0xffffff,2.2);sun.position.set(1200,3000,1000);scene.add(sun);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(4600,8700),new THREE.MeshStandardMaterial({color:0x263b43,roughness:1}));ground.rotation.x=-Math.PI/2;ground.position.y=-.3;scene.add(ground);
let ready=false,renderCount=0;
function draw(){if(!document.hidden){renderer.render(scene,camera);renderCount++;if(ready)document.querySelector('#perf').textContent=`${renderer.info.render.calls} draw calls · ${renderer.info.render.triangles.toLocaleString()} triangles\nAll survey exteriors resident · render on demand`;}}
controls.addEventListener('change',draw);addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);draw();});document.addEventListener('visibilitychange',()=>{if(!document.hidden)draw();});
const {summary,buildings,roads}=await fetch('/build/strip-survey/survey.json').then(r=>{if(!r.ok)throw Error('Survey not available');return r.json();});
const colors={height:0x74cdb9,levels:0x729ddd,unknown:0xba9270};const groups={height:[],levels:[],unknown:[]};const ranges={height:[],levels:[],unknown:[]};const counts={height:0,levels:0,unknown:0};
for(let fi=0;fi<buildings.length;fi++){
 const f=buildings[fi];
 for(const polygon of f.polygons){
  const shape=new THREE.Shape(polygon[0].map(p=>new THREE.Vector2(...p)));
  for(const hole of polygon.slice(1))shape.holes.push(new THREE.Path(hole.map(p=>new THREE.Vector2(...p))));
  const geo=new THREE.ExtrudeGeometry(shape,{depth:f.height-f.base,bevelEnabled:false,steps:1,curveSegments:1});geo.rotateX(-Math.PI/2);geo.translate(0,f.base,0);geo.clearGroups();
  const faces=geo.getAttribute('position').count/3;ranges[f.kind].push({first:counts[f.kind],last:counts[f.kind]+faces,fi});counts[f.kind]+=faces;groups[f.kind].push(geo);
 }
}
const meshes=[];
for(const [kind,geos] of Object.entries(groups)){
 const geometry=mergeGeometries(geos,false);geometry.computeBoundingSphere();const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:colors[kind],roughness:.82,metalness:.08}));mesh.userData.kind=kind;scene.add(mesh);meshes.push(mesh);for(const g of geos)g.dispose();
}
const major=[],minor=[];for(const r of roads){const dest=/^(motorway|trunk|primary|secondary|tertiary)/.test(r.class)?major:minor;for(let i=1;i<r.points.length;i++)dest.push(r.points[i-1][0],.15,-r.points[i-1][1],r.points[i][0],.15,-r.points[i][1]);}
for(const [verts,color,opacity]of[[minor,0x53616a,.48],[major,0xc3b8a5,.8]]){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));scene.add(new THREE.LineSegments(g,new THREE.LineBasicMaterial({color,transparent:true,opacity})));}
const $=s=>document.querySelector(s);$('#buildings').textContent=buildings.length.toLocaleString();$('#known').textContent=`${summary.heightSource.height} recorded height tags`;$('#levels').textContent=`${summary.heightSource.levels} heights estimated from floors`;$('#unknown').textContent=`${summary.heightSource.unknown.toLocaleString()} missing heights · estimated by building use`;$('#date').textContent=summary.timestamp.slice(0,10);$('#status').textContent='Loaded entirely from local files.';
function setView(center,offset){controls.target.set(...center);camera.position.copy(controls.target).add(new THREE.Vector3(...offset));controls.update();draw();}
$('#overview').onclick=()=>setView([-650,0,500],[5600,5600,6900]);$('#central').onclick=()=>setView([-190,25,330],[850,650,1050]);$('#city').onclick=()=>setView([-230,30,995],[650,570,740]);
const select=$('#landmark');buildings.map((f,i)=>({f,i})).filter(({f})=>f.tags.name).sort((a,b)=>a.f.name.localeCompare(b.f.name)).forEach(({f,i})=>{const option=document.createElement('option');option.value=String(i);option.textContent=f.name;select.append(option);});
let marker;
function inspect(fi,fly=false){const f=buildings[fi];if(marker){scene.remove(marker);marker.geometry.dispose();marker.material.dispose();}const box=new THREE.Box3();for(const polygon of f.polygons)for(const p of polygon[0])box.expandByPoint(new THREE.Vector3(p[0],f.base,-p[1]));box.max.y=f.height;marker=new THREE.Box3Helper(box,0xfff0a7);scene.add(marker);
 const info=$('#info');info.replaceChildren();info.style.display='block';const h=document.createElement('h2');h.textContent=f.name;info.append(h);
 for(const text of [`${f.height.toFixed(1)} m · ${f.kind==='height'?'recorded height':f.kind==='levels'?'estimated from '+f.tags['building:levels']+' floors':'height unknown; '+f.heightProfile+' estimate'}`,`Base ${f.base.toFixed(1)} m · ${f.part?'building part':'building outline'}`,f.id]){const p=document.createElement('p');p.textContent=text;info.append(p);}
 const a=document.createElement('a');a.href='https://www.openstreetmap.org/'+f.id;a.target='_blank';a.textContent='View source feature ↗';info.append(a);
 if(fly){const size=box.getSize(new THREE.Vector3()),dist=Math.max(size.x,size.z,f.height)*1.8+80;setView([f.center[0],f.height*.3,-f.center[1]],[dist,dist*.65,dist]);}else draw();}
select.onchange=()=>{if(select.value!=='')inspect(Number(select.value),true);};const ray=new THREE.Raycaster();let down;
renderer.domElement.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY];});renderer.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;ray.setFromCamera(new THREE.Vector2(e.clientX/innerWidth*2-1,1-e.clientY/innerHeight*2),camera);const hit=ray.intersectObjects(meshes)[0];if(hit){const r=ranges[hit.object.userData.kind].find(r=>hit.faceIndex>=r.first&&hit.faceIndex<r.last);if(r)inspect(r.fi);}});
ready=true;setView([-190,25,330],[1250,1050,1650]);
