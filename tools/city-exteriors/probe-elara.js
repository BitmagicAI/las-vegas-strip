const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(480,2,865);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'elara-aerial',eye:[570,210,1090],target:[390,80,810]},
{name:'elara-strip',eye:[400,8,910],target:[400,85,800]},
{name:'elara-arrival',eye:[460,3,861],target:[405,12,820]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
