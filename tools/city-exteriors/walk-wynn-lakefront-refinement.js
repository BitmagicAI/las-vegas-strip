// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "north-lower", "points": [[551.2675645513317, 0.7, -1169.5486616712801], [548.6865645513317, 0.7, -1173.73646167128], [546.1055645513318, 0.7, -1177.9242616712802], [543.5245645513318, 0.7, -1182.1120616712801]]}, {"name": "north-upper", "points": [[551.2675645513317, 5.9, -1169.5486616712801], [548.6865645513317, 5.9, -1173.73646167128], [546.1055645513318, 5.9, -1177.9242616712802], [543.5245645513318, 5.9, -1182.1120616712801]]}, {"name": "sw-lower", "points": [[546.3023228815186, 0.7, -1126.0967107326644], [547.4119228815186, 0.7, -1129.0867107326644], [548.5215228815186, 0.7, -1132.0767107326644], [549.6311228815186, 0.7, -1135.0667107326644]]}, {"name": "sw-upper", "points": [[546.3023228815186, 5.9, -1126.0967107326644], [547.4119228815186, 5.9, -1129.0867107326644], [548.5215228815186, 5.9, -1132.0767107326644], [549.6311228815186, 5.9, -1135.0667107326644]]}]};
const waitReady=async()=>{const end=performance.now()+120000;while(probe.streaming().busy){if(performance.now()>end)throw new Error('Area not ready');await frame();}};
const allResults=[],doorEvents=[];
const {getInteractionManager}=await import('/dist/engine/engine/InteractionManager.js');
const openNearby=async()=>{
 const p=probe.position();let opened=false;
 for(const c of getInteractionManager().registry.values()){
  const d=c.getInteractable(),o=c.getObject3D(),q=o.getWorldPosition(o.position.clone());
  if(typeof d.isOpen==='function'&&!d.isOpen()&&Math.hypot(q.x-p.x,q.z-p.z)<3&&Math.abs(q.y-p.y)<3){
   const accepted=d.onInteractStart();doorEvents.push({position:[q.x,q.y,q.z],accepted});opened=true;
  }
 }
 if(opened)for(let i=0;i<60;i++)await frame();
};
for(const route of meta.routes){
const points=route.points,walk=points.concat(points.slice(0,-1).reverse());
probe.teleport(points[0][0],points[0][1]+1.0,points[0][2]);
for(let i=0;i<240;i++)await frame();await waitReady();
const press=on=>document.dispatchEvent(new KeyboardEvent(on?'keydown':'keyup',{code:'KeyW',key:'w',bubbles:true,cancelable:true}));
const results=[];
try{
 for(let k=1;k<walk.length;k++){
  const goal=walk[k];let reached=false;const start=performance.now(),origin=probe.position(),timeout=10000+1000*Math.hypot(goal[0]-origin.x,goal[2]-origin.z)/1.5;
  while(performance.now()-start<timeout){
   const p=probe.position(),dx=goal[0]-p.x,dz=goal[2]-p.z;
   if(Math.hypot(dx,dz)<.10){reached=Math.abs(p.y-goal[1])<.45;break;}
   probe.look(Math.atan2(-dx,-dz),0);await openNearby();press(true);await frame();
  }
  press(false);if(k===points.length-1){await waitReady();const p=probe.position(),q=points[points.length-2];probe.look(Math.atan2(p.x-q[0],p.z-q[2]),0);for(let i=0;i<6;i++)await frame();await __shot('walk-endpoint-'+allResults.length);}results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await waitReady();const p=probe.position(),q=points[1];probe.look(Math.atan2(p.x-q[0],p.z-q[2]),0);for(let i=0;i<6;i++)await frame();await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {doorEvents,routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
