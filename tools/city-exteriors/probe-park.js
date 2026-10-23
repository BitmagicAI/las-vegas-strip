const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(-40,2,1300);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
 {name:'park-aerial',eye:[80,190,1380],target:[-240,30,1240]},
 {name:'park-strip',eye:[-15,5,1280],target:[-100,8,1290]},
 {name:'park-south',eye:[-140,5,1400],target:[-180,10,1340]},
 {name:'park-north',eye:[-140,5,1100],target:[-220,12,1170]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114],render:{...renderer.info.render}});}
release();return results;
