const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(400,2,900);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'grand-chateau-aerial',eye:[490,220,1090],target:[340,50,955]},
{name:'grand-chateau-strip',eye:[250,8,875],target:[340,70,955]},
{name:'grand-chateau-pool',eye:[340,65,1055],target:[340,16,975]},
{name:'grand-chateau-arrival',eye:[345,3,886],target:[345,10,935]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
