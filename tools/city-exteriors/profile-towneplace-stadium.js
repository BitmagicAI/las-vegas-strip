let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));const results=[];
const views = [["arrival",[-825,7,1790],[-818,8,1747]],["breakfast",[-818,1.95,1752],[-811,1.5,1747]]];
const counters=()=>({pipelines:renderer._pipelines?.caches?.size??null,vertex:renderer._pipelines?.programs?.vertex?.size??null,fragment:renderer._pipelines?.programs?.fragment?.size??null,streaming:JSON.parse(JSON.stringify(probe.streaming()))});
for(let pass=0;pass<3;pass++)for(const [name,eye,target] of views){
 probe.teleport(eye[0],1,eye[2]);
 const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
 for(let i=0;i<300;i++)await frame();
 const before=counters(),times=[];let last=performance.now();
 for(let i=0;i<600;i++){await frame();const now=performance.now();times.push(now-last);last=now;}
 const after=counters();times.sort((a,b)=>a-b);
 results.push({pass,name,eye,target,p50:times[300],p95:times[570],p99:times[594],max:times[599],framesOver33:times.filter(t=>t>33.34).length,before,after});
 if(pass===2)await __shot('towneplace-profile-'+name);
 release();
}
return results;
