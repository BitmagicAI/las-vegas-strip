const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(985,2,-2350);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'circus-circus-aerial',eye:[1060,175,-2240],target:[690,30,-2410]},
{name:'circus-circus-west',eye:[985,5,-2350],target:[850,15,-2340]},
{name:'circus-circus-south',eye:[910,5,-2190],target:[875,8,-2240]},
{name:'circus-circus-north',eye:[760,8,-2600],target:[700,30,-2480]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
