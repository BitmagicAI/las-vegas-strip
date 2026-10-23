probe.teleport(400,2,900);engine.editorManager.enableEditorMode();document.querySelector('.bm-editor-header-buttons button')?.click();
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(340,65,1000);engine.camera.lookAt(340,16,980);engine.camera.updateMatrixWorld();});
for(let i=0;i<120;i++)await new Promise(r=>requestAnimationFrame(r));await __shot('before');
const nodes=[];scene.traverse(o=>{if(o.name.includes('grandChateau')||o.name.includes('grand-chateau'))nodes.push({name:o.name,visible:o.visible,parent:o.parent?.name});});
const removed=[];const root=scene.getObjectByName('Grand Chateau tower podium and arrival exterior / exterior');root.traverse(o=>{if(o.name.startsWith('Silhouette'))removed.push(o);});for(const o of removed)o.removeFromParent();
for(let i=0;i<60;i++)await new Promise(r=>requestAnimationFrame(r));await __shot('no-coarse');release();return {same:scene===engine.scene,nodes,removed:removed.map(o=>o.name)};
