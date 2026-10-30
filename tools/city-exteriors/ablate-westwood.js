let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(267,1.1,-3038);
const roots=[];scene.traverse(o=>{if(o.name==='The Lexi / exterior'||o.name==='Auto Collision Experts Westwood / exterior')roots.push(o);});
if(roots.length!==2)throw Error('Expected exactly two building roots; found '+roots.length);
const saved=roots.map(o=>o.visible);let show=true;
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(237,3,-3060);engine.camera.lookAt(249,2,-3045);engine.camera.updateMatrixWorld();for(const o of roots)o.visible=show;});
const results=[];
try{
 for(let i=0;i<600;i++)await frame();
 for(const state of [true,false,false,true,false,true,true,false]){
  show=state;for(let i=0;i<90;i++)await frame();
  const times=[],draws=[],tris=[];let last=performance.now();
  for(let i=0;i<180;i++){await frame();const now=performance.now();times.push(now-last);last=now;draws.push(renderer.info.render.drawCalls);tris.push(renderer.info.render.triangles);}
  times.sort((a,b)=>a-b);draws.sort((a,b)=>a-b);tris.sort((a,b)=>a-b);
  results.push({visible:state,p50:times[90],p95:times[171],drawCalls:draws[90],triangles:tris[90]});
 }
 return {scope:'Diagnostic only: two exterior roots toggled; not original city baseline; concurrent rendering possible',roots:roots.map(o=>o.name),results};
}finally{release();roots.forEach((o,i)=>o.visible=saved[i]);}
