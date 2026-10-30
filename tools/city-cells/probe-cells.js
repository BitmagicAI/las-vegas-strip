const frame=()=>new Promise(r=>requestAnimationFrame(r));
let root;
const end=performance.now()+180000;
while(performance.now()<end){root=scene.getObjectByName('OpenStreetMap / geographic Strip');if(root?.visible)break;await frame();}
if(!root?.visible)throw new Error('City root not ready');
const views=[['front',[324,5,-3057],[284,8,-3083]]];
const results=[];
for(const [name,eye,target] of views){
 probe.teleport(282,1.1,-3054);
 const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
 for(let i=0;i<180;i++)await frame();
 await __shot(name);
 let meshes=0,triangles=0;root.traverse(o=>{if(o.isMesh){meshes++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position?.count??0)/3;}});
 results.push({name,eye,target,meshes,triangles});release();
}
return results;
