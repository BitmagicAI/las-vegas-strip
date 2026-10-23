const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(70,2,-580);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'mirage-aerial',eye:[120,220,-410],target:[-180,25,-600]},
{name:'mirage-strip',eye:[80,8,-550],target:[-150,35,-580]},
{name:'mirage-arrival',eye:[-15,4,-610],target:[-120,20,-590]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
