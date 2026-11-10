let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const eye=[-46,7.8,741.5],target=[-53.4,7.4,742.2];
const frame=()=>new Promise(r=>requestAnimationFrame(r));probe.teleport(eye[0],eye[1]-1.7,eye[2]);
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
for(let i=0;i<900;i++)await frame();let deadline=performance.now()+120000;while(probe.streaming().busy){if(performance.now()>deadline)throw Error('streaming timeout');await frame();}
for(let i=0;i<60;i++)await frame();await __shot('cosmo-upper');
const rows=[],startAudit={...window.__shaderAudit?.().totals},initialPrograms=renderer.info.memory.programs;let prev=await frame();
for(let i=0;i<900;i++){let t=await frame();rows.push([t-prev,window.__liftCpu.get(prev)||0,renderer.info.render.drawCalls,renderer.info.render.triangles,probe.streaming().busy]);window.__liftCpu.delete(prev);prev=t;}
release();const quant=(col,p)=>{const a=rows.map(r=>r[col]).sort((a,b)=>a-b);return a[Math.floor(a.length*p)];};
return {eye,target,samples:rows.length,p50:quant(0,.5),p95:quant(0,.95),cpuP50:quant(1,.5),cpuP95:quant(1,.95),drawsP50:quant(2,.5),trianglesP50:quant(3,.5),initialPrograms,finalPrograms:renderer.info.memory.programs,streamingFrames:rows.filter(r=>r[4]).length,startAudit,endAudit:{...window.__shaderAudit?.().totals},rows};
