// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "weldon-west-approach-0", "points": [[1928.35400390625, 0.35005965232849123, -3769.613037109375], [1918.418701171875, 0.25000002384185793, -3773.669677734375], [1917.0947265625, 0.25008716583251955, -3774.21044921875]]}, {"name": "weldon-west-approach-1", "points": [[1916.249267578125, 0.3498645067214966, -3746.684326171875], [1909.0540771484375, 0.2504358530044556, -3750.2392578125], [1907.7708740234375, 0.2400000333786011, -3750.87255859375]]}, {"name": "weldon-west-approach-2", "points": [[1905.8341064453125, 0.3499974250793457, -3727.001220703125], [1895.668212890625, 0.25048294067382815, -3730.947509765625], [1894.275390625, 0.2400000333786011, -3731.48876953125]]}, {"name": "weldon-west-approach-3", "points": [[1893.5528564453125, 0.3397068023681641, -3703.478271484375], [1885.5111083984375, 0.24999680519104006, -3707.387939453125], [1884.2149658203125, 0.25006201267242434, -3708.017578125]]}, {"name": "weldon-west-approach-4", "points": [[1881.9990234375, 0.3501663446426392, -3681.520263671875], [1873.1212158203125, 0.25019397735595705, -3685.766357421875], [1871.771728515625, 0.24999966621398928, -3686.41162109375]]}]};
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
  press(false);if(k===points.length-1){await waitReady();await __shot('walk-frontage-'+allResults.length);}results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await waitReady();await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {doorEvents,routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
