const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(805,2,-1930);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'resorts-world-aerial',eye:[890,175,-1760],target:[590,42,-2000]},
{name:'resorts-world-west',eye:[805,5,-1930],target:[680,16,-1950]},
{name:'resorts-world-south',eye:[630,5,-1740],target:[590,16,-1820]},
{name:'resorts-world-north',eye:[775,5,-2130],target:[650,16,-2100]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
