const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(1750,2,-2300);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
{name:'westgate-aerial',eye:[1660,190,-2130],target:[1920,40,-2240]},
{name:'westgate-paradise',eye:[1740,6,-2260],target:[1910,40,-2290]},
{name:'westgate-east',eye:[2140,12,-2250],target:[1940,40,-2270]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114]});}
release();return results;
