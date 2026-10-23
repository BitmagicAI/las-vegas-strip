const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(75,2,1610);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
 {name:'mgm-aerial',eye:[-90,190,1800],target:[285,30,1480]},
 {name:'mgm-strip',eye:[20,6,1580],target:[130,14,1580]},
 {name:'mgm-arrival',eye:[430,7,1680],target:[425,8,1590]},
 {name:'mgm-north',eye:[65,6,1390],target:[178,12,1385]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114],render:{...renderer.info.render}});}
release();return results;
