let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));const results=[];
probe.teleport(1741,.3,-1061);
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(1741,2.4,-1061);engine.camera.lookAt(1741,.05,-1054);engine.camera.updateMatrixWorld();});
for(let i=0;i<300;i++)await frame();
await __shot('pool-t0');
for(let i=0;i<180;i++)await frame();
await __shot('pool-t3');release();return {fixedCamera:true,frameInterval:180};
