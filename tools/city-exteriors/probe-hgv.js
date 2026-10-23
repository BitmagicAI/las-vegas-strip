const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(980,2,-2630);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'hgv-aerial',eye:[900,160,-2460],target:[1100,35,-2640]},
{name:'hgv-strip',eye:[965,6,-2640],target:[1090,30,-2640]},
{name:'hgv-south',eye:[1100,6,-2500],target:[1090,25,-2630]},
{name:'hgv-east',eye:[1240,70,-2600],target:[1100,25,-2640]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
