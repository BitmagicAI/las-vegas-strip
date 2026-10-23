const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(60,2,644);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
 {name:'harmon-corner',eye:[-27,19,858],target:[73,16,805]},
 {name:'planet-pools',eye:[75,70,678],target:[120,13,660]},
 {name:'planet-aerial',eye:[-190,200,830],target:[205,38,657]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114],render:{...renderer.info.render}});}
release();return results;
