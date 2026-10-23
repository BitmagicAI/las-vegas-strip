const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(980,2,-2630);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'sky-aerial',eye:[935,190,-2640],target:[1055,65,-2535]},
{name:'sky-strip',eye:[1125,6,-2510],target:[1065,45,-2520]},
{name:'sky-west',eye:[965,8,-2525],target:[1050,40,-2530]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
