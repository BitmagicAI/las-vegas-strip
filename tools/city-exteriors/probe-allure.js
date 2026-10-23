const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(1350,2,-3090);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'allure-aerial',eye:[1350,180,-2970],target:[1240,55,-3125]},
{name:'allure-south',eye:[1250,6,-3065],target:[1250,45,-3120]},
{name:'allure-north',eye:[1250,6,-3200],target:[1250,40,-3125]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
