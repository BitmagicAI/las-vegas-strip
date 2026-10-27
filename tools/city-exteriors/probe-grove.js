const frame=()=>new Promise(r=>requestAnimationFrame(r));const results=[];
for(const [name,eye,target] of [['north',[2024,3,1159],[2027,2,1175]],['east',[2066,3,1181],[2047,2,1181]],['south',[2030,4,1209],[2030,2,1189]]]){
 probe.teleport(eye[0],1,eye[2]);
 const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
 for(let i=0;i<300;i++)await frame();await __shot('grove-'+name);
 const times=[];let last=performance.now();for(let i=0;i<180;i++){await frame();const now=performance.now();times.push(now-last);last=now;}times.sort((a,b)=>a-b);release();results.push({name,eye,target,p50:times[90],p95:times[171]});
}return results;
