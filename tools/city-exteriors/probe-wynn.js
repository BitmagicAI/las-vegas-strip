const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(450,2,-1250);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'wynn-aerial',eye:[260,320,-1120],target:[670,55,-1320]},
{name:'wynn-strip',eye:[410,8,-1120],target:[650,60,-1190]},
{name:'encore-strip',eye:[510,8,-1480],target:[740,60,-1480]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
