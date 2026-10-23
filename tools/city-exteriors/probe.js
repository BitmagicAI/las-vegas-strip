const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(60,2,644);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
 {name:'planet-aerial',eye:[-190,200,830],target:[205,38,657]},
 {name:'planet-north',eye:[9,7,565],target:[65,10,553]},
 {name:'planet-center',eye:[-3,5,650],target:[60,15,650]},
 {name:'planet-south',eye:[0,5,740],target:[65,10,710]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114],render:{...renderer.info.render}});}
release();return results;
