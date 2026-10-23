const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(1665,2,-3480);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'strat-aerial',eye:[1770,160,-3390],target:[1490,25,-3505]},
{name:'strat-strip',eye:[1665,5,-3480],target:[1510,18,-3490]},
{name:'strat-south',eye:[1560,5,-3360],target:[1480,12,-3430]},
{name:'strat-north',eye:[1575,7,-3680],target:[1510,30,-3570]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
