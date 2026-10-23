const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(1325,2,-2890);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'sahara-aerial',eye:[1200,165,-2850],target:[1480,28,-2960]},
{name:'sahara-strip',eye:[1315,5,-2970],target:[1450,14,-2990]},
{name:'sahara-arrival',eye:[1325,5,-2890],target:[1380,8,-2910]},
{name:'sahara-east',eye:[1640,7,-2890],target:[1510,40,-2920]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
