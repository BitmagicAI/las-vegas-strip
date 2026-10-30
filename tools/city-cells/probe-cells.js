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
const capture=window.__cityBake;
if(capture){
 const part=[...capture.parts.values()].find(p=>p.id==='OpenStreetMap / geographic Strip');
 if(!part)throw new Error('Geographic capture missing');
 const hashes={},attributes={};
 for(const b of part.blocks)for(const [level,list] of [['high',b.high],['low',b.low],['retained',b.retained]]){
  let h=0x811c9dc5;
  const feed=a=>{const bytes=new Uint8Array(a.buffer,a.byteOffset,a.byteLength);for(const v of bytes){h^=v;h=Math.imul(h,0x01000193);}};
  for(const [mi,m] of list.entries()){
   for(const name of ['position','normal','uv','color']){
    const a=m.geometry.getAttribute(name);if(!a)continue;
    let ah=0x811c9dc5;for(const v of new Uint8Array(a.array.buffer,a.array.byteOffset,a.array.byteLength)){ah^=v;ah=Math.imul(ah,0x01000193);}
    const key=b.key+'/'+level+'/'+mi+'/'+name;
    attributes[key]=(ah>>>0).toString(16);
   }
   for(const name of ['position','normal','uv','color']){const a=m.geometry.getAttribute(name);if(a)feed(a.array);}if(m.geometry.index){
   const a=m.geometry.index.array,canonical=new Uint32Array(a.length);
   for(let i=0;i<a.length;i+=3){let r=0;if(a[i+1]<a[i+r])r=1;if(a[i+2]<a[i+r])r=2;for(let k=0;k<3;k++)canonical[i+k]=a[i+(r+k)%3];}
   feed(canonical);
  }}
  hashes[b.key+'/'+level]=(h>>>0).toString(16);
 }
 results.push({capture: capture.stats().find(p=>p.id===part.id),hashes,attributes});
}
return results;
