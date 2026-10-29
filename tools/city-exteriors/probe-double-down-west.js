const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(2014,1,1167);
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(2007,4,1172);engine.camera.lookAt(2034,2.5,1166);engine.camera.updateMatrixWorld();});
for(let i=0;i<240;i++)await frame();await __shot('doubleDown-west');release();return {position:probe.position(),resident:probe.resident()};
