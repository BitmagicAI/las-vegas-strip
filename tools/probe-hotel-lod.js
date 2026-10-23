const frame=()=>new Promise(resolve=>requestAnimationFrame(resolve));
const settle=async(n=90)=>{for(let i=0;i<n;i++)await frame();};
const blocks=[];
scene.traverse(o=>{if(o.userData.cityLod&&/vanderpump/.test(o.name))blocks.push(o);});
const bounds=blocks.map(b=>{const g=b.children[0].children.find(m=>m.isMesh).geometry;return {name:b.name,min:g.boundingBox.min.toArray(),max:g.boundingBox.max.toArray()};});
probe.teleport(-50,2,180);
engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let cameraEye=[-145,65,350],mode='natural';
const previous=scene.onBeforeRender;
scene.onBeforeRender=function(...args){previous.apply(this,args);if(scene.overrideMaterial)return;if(mode!=='natural')for(const b of blocks){b.children[0].visible=mode==='full';b.children[1].visible=mode==='coarse';}};
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...cameraEye);engine.camera.lookAt(83,18,102);engine.camera.updateMatrixWorld();});
const states=()=>blocks.map(b=>({name:b.name,high:b.children[0].visible,low:b.children[1].visible,highTriangles:b.children[0].children.reduce((n,m)=>n+(m.geometry?.index?.count??0)/3,0),lowTriangles:b.children[1].children.reduce((n,m)=>n+(m.geometry?.index?.count??0)/3,0)}));
const views=[];
for(const state of ['natural','full','coarse']){mode=state;await settle();await __shot('cromwell-'+state);views.push({mode,state:states(),render:{...renderer.info.render}});}
mode='natural';const distances=[];
for(const x of [-100,-150,-250,-450,-650,-850,-1100]){cameraEye=[x,38,140];await settle(25);distances.push({eye:cameraEye.slice(),states:states()});}
mode='natural';cameraEye=[-145,65,350];await settle(120);
const times=[];let last=performance.now();for(let i=0;i<150;i++){await frame();const now=performance.now();times.push(now-last);last=now;}times.sort((a,b)=>a-b);
const performanceSample={median:times[75],p95:times[142],max:times[149],render:{...renderer.info.render}};
release();scene.onBeforeRender=previous;
return {bounds,views,distances,performanceSample};
