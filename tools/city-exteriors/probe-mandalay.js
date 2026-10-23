const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(-40,2,2680);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'mandalay-aerial',eye:[100,220,2890],target:[-280,35,2660]},
{name:'mandalay-entry',eye:[-26,5,2640],target:[-90,8,2650]},
{name:'mandalay-south',eye:[-24,5,2870],target:[-125,10,2810]},
{name:'mandalay-west',eye:[-650,100,2790],target:[-350,35,2680]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
