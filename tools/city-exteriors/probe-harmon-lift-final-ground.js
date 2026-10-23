const frame=()=>new Promise(r=>requestAnimationFrame(r));let eye=[-41.4,8,755.2],target=[-53.4,4,742.2];const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});const rows=[];
for(const v of [
{name:'east-ground-door',eye:[73,2.4,891],target:[67.7,1.4,894.5],p:[73,1,891]},
{name:'west-landing-ground',eye:[24,10,790],target:[41,7.8,781],p:[35,7,779]}
]){eye=v.eye;target=v.target;probe.teleport(...v.p);for(let i=0;i<180;i++)await frame();await __shot(v.name);const ms=[];let last=performance.now();for(let i=0;i<180;i++){await frame();const now=performance.now();ms.push(now-last);last=now;}ms.sort((a,b)=>a-b);rows.push({...v,p50:ms[90],p95:ms[171]});}
release();return rows;
