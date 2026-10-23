const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(1630,2,-2400);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'place-aerial',eye:[1810,205,-2380],target:[1515,50,-2395]},
{name:'place-east',eye:[1670,6,-2395],target:[1530,40,-2395]},
{name:'place-south',eye:[1515,10,-2220],target:[1515,35,-2410]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
