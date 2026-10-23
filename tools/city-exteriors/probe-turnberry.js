const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(1800,2,-2700);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'turnberry-aerial',eye:[1800,190,-2530],target:[1800,55,-2790]},
{name:'turnberry-south',eye:[1795,6,-2680],target:[1800,50,-2770]},
{name:'turnberry-north',eye:[1795,30,-2920],target:[1795,45,-2800]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
