// Diagnostic only: paired visible/hidden interior cost, never a shipping preset.
const frame=()=>new Promise(r=>requestAnimationFrame(r));probe.teleport(1727,1,-1054);
let hide=false;const release=engine.registerBeforeRender(()=>{engine.camera.position.set(1787,5,-1054);engine.camera.lookAt(1735,2,-1054);engine.camera.updateMatrixWorld();scene.traverse(o=>{if(o.name==='Mardi Gras Hotel & Casino / streamed public interior')o.visible=!hide;});});
const results=[];
try{for(const state of [false,true,false]){hide=state;for(let i=0;i<180;i++)await frame();const times=[];let t=performance.now();for(let i=0;i<300;i++){await frame();const now=performance.now();times.push(now-t);t=now;}times.sort((a,b)=>a-b);results.push({interiorVisible:!hide,p50:times[150],p95:times[285]});}}finally{hide=false;scene.traverse(o=>{if(o.name==='Mardi Gras Hotel & Casino / streamed public interior')o.visible=true;});release();}return {diagnosticOnly:true,competingRenderJobs:true,results};
