let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));const results=[];
probe.teleport(1724.95,6.36,-1046.8);
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(1724.95,7.9,-1046.8);engine.camera.lookAt(1727.3,3,-1056);engine.camera.updateMatrixWorld();});
for(let i=0;i<300;i++)await frame();
await __shot('upper-landing-lookback');release();return {fixedCamera:true};
