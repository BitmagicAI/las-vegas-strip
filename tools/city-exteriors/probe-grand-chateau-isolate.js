probe.teleport(400,2,900);engine.editorManager.enableEditorMode();
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(340,65,1000);engine.camera.lookAt(340,16,980);engine.camera.updateMatrixWorld();});
for(let i=0;i<150;i++)await new Promise(r=>requestAnimationFrame(r));
engine.renderFrameNow();await new Promise(r=>setTimeout(r,500));await __shot('pool-close');
const found=[];scene.traverse(o=>{if(o.name==='Full detail / grandChateauExterior / surface 0'||o.name==='Afterlight shadow-only silhouettes')found.push(o);});for(const o of found)o.removeFromParent();
for(let i=0;i<15;i++)await new Promise(r=>requestAnimationFrame(r));renderer.setRenderTarget(null);renderer.render(scene,engine.camera);await __shot('pool-isolated');release();return {found:found.map(o=>({name:o.name,layers:o.layers.mask})),camera:engine.camera.layers.mask,position:engine.camera.position.toArray(),frames:engine.getRenderedFrameCount()};
