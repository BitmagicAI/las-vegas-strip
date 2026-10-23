const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(120,2,-1460);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'trump-aerial',eye:[220,240,-1310],target:[32,70,-1510]},
{name:'trump-south',eye:[25,8,-1400],target:[32,65,-1510]},
{name:'trump-north',eye:[30,12,-1640],target:[32,65,-1510]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
