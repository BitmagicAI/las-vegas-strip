const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(-80,2,2290);engine.editorManager.enableEditorMode();
document.querySelector('.bm-editor-header-buttons button')?.click();
let eye,target;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const results=[];
for(const v of [
 {name:'luxor-aerial',eye:[100,205,2440],target:[-240,30,2250]},
 {name:'luxor-strip',eye:[-50,5,2300],target:[-170,8,2280]},
 {name:'luxor-towers',eye:[-70,7,2130],target:[-205,20,2140]},
 {name:'luxor-north',eye:[-270,7,2040],target:[-245,12,2130]},
 {name:'park-roof-final',eye:[80,190,1380],target:[-240,30,1240]},
 {name:'mgm-courtyard-final',eye:[40,110,1490],target:[166,7,1410]}
]){eye=v.eye;target=v.target;for(let i=0;i<120;i++)await frame();await __shot(v.name);const t=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);results.push({...v,p50:t[60],p95:t[114],render:{...renderer.info.render}});}
release();return results;
