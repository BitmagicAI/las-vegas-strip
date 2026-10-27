const frame=()=>new Promise(r=>requestAnimationFrame(r));probe.teleport(2066,1,1181);
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(2066,3,1181);engine.camera.lookAt(2047,2,1181);engine.camera.updateMatrixWorld();});
for(let i=0;i<300;i++)await frame();await __shot('grove-east');release();return {position:probe.position(),resident:probe.resident()};
