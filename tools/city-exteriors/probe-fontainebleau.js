const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(1000,2,-2440);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'fontainebleau-aerial',eye:[880,180,-2240],target:[1240,40,-2430]},
{name:'fontainebleau-west',eye:[990,5,-2450],target:[1150,15,-2450]},
{name:'fontainebleau-south',eye:[1180,5,-2220],target:[1200,16,-2300]},
{name:'fontainebleau-north',eye:[1100,5,-2570],target:[1200,16,-2480]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
