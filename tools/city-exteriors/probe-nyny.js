const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(-35,2,1510);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'nyny-aerial',eye:[90,110,1640],target:[-160,25,1510]},
{name:'nyny-strip',eye:[-10,5,1520],target:[-65,10,1520]},
{name:'nyny-north',eye:[-65,5,1400],target:[-110,8,1440]},
{name:'nyny-garage',eye:[-400,5,1560],target:[-320,10,1540]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
