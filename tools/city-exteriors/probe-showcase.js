const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(75,2,1610);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
 {name:'showcase-street',eye:[-1,5,1408],target:[42,10,1385]},
 {name:'showcase-north',eye:[-15,6,1290],target:[50,10,1306]},
 {name:'mgm-mansion',eye:[40,110,1490],target:[166,7,1410]},
 {name:'mgm-street-seam',eye:[20,6,1580],target:[130,14,1580]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114],render:{...renderer.info.render}});}
release();return results;
