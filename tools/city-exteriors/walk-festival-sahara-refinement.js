// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "festival-grounds-service", "points": [[1143.7822265625, 0.25000002384185793, -3045.26416015625], [1143.6595458984375, 0.24994304180145266, -3040.88525390625], [1142.68505859375, 0.23999991416931155, -3040.884033203125], [1142.3929443359375, 0.24999847412109377, -3031.96533203125], [1146.0406494140625, 0.2500325679779053, -3031.780029296875], [1145.9874267578125, 0.25000002384185793, -3028.305908203125], [1153.8992919921875, 0.2400000333786011, -3028.048095703125], [1154.0299072265625, 0.25000288486480715, -3030.321533203125], [1183.9246826171875, 0.23999621868133547, -3029.53076171875], [1183.909912109375, 0.25001742839813235, -3027.2470703125], [1191.9405517578125, 0.25000002384185793, -3026.979248046875], [1192.10595703125, 0.2501834869384766, -3030.692626953125], [1195.6239013671875, 0.25000002384185793, -3030.630615234375], [1195.952880859375, 0.25000002384185793, -3039.45166015625], [1192.4244384765625, 0.25003173351287844, -3039.61767578125], [1192.474365234375, 0.2400000333786011, -3043.871826171875], [1143.832763671875, 0.25005927085876467, -3045.32177734375]]}, {"name": "mcdonalds-sahara-canopy-0", "points": [[1613.482177734375, 0.23996069431304934, -3104.08203125], [1617.40625, 0.23997988700866701, -3112.128662109375], [1620.147705078125, 0.24999763965606692, -3117.75048828125]]}, {"name": "mcdonalds-sahara-canopy-1", "points": [[1608.5018310546875, 0.2399472236633301, -3106.54345703125], [1612.4031982421875, 0.2502447605133057, -3114.543701171875], [1615.1480712890625, 0.24995567798614504, -3120.172119140625]]}, {"name": "mcdonalds-sahara-canopy-2", "points": [[1603.5125732421875, 0.24999632835388186, -3108.98681640625], [1607.4012451171875, 0.2504663705825806, -3116.96044921875], [1610.1524658203125, 0.25022866725921633, -3122.602294921875]]}]};
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
