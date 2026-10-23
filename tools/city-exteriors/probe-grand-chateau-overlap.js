probe.teleport(400,2,900);engine.editorManager.enableEditorMode();
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(340,65,1055);engine.camera.lookAt(340,16,975);engine.camera.updateMatrixWorld();});
for(let i=0;i<180;i++)await new Promise(r=>requestAnimationFrame(r));
const result=[];scene.traverse(o=>{if(!o.isMesh)return;let visible=true;for(let p=o;p;p=p.parent)if(!p.visible)visible=false;if(!visible)return;const b=o.geometry.boundingBox;if(!b)return;const q=b.clone().applyMatrix4(o.matrixWorld);if(q.min.x<=340&&q.max.x>=340&&q.min.z<=980&&q.max.z>=980&&q.min.y<30){result.push({name:o.name,parent:o.parent.name,min:q.min.toArray(),max:q.max.toArray(),mat:(Array.isArray(o.material)?o.material:[o.material]).map(m=>({name:m.name,water:!!m.userData.realisticWater}))});}});
await __shot('pool-debug');release();return result;
