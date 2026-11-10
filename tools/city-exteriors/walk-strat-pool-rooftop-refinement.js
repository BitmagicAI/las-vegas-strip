// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "strat-pool-deck route 0", "points": [[1376, 26.25, -3438], [1376, 26.25, -3428], [1376, 26.25, -3415]]}, {"name": "strat-pool-deck route 1", "points": [[1438, 26.25, -3434], [1448, 26.25, -3434], [1455, 26.25, -3421]]}, {"name": "strat-pool-deck route 2", "points": [[1384, 26.25, -3438], [1388, 26.25, -3438], [1392, 26.25, -3438]]}, {"name": "strat-thrill-rides route 0", "points": [[1599.885332299083, 268, -3496.4427625774088], [1599.3473201503734, 268, -3490.980233560957], [1597.753959209399, 268, -3485.7276264711863], [1595.1664814435544, 268, -3480.88679605286], [1591.6843221723063, 268, -3476.6437727041853], [1587.441298823632, 268, -3473.1616134329374], [1582.6004684053055, 268, -3470.574135667093], [1577.3478613155346, 268, -3468.9807747261184], [1571.885332299083, 268, -3468.4427625774088]]}, {"name": "strat-thrill-rides route 1", "points": [[1571.885332299083, 268, -3468.4427625774088], [1566.4228032826315, 268, -3468.9807747261184], [1561.1701961928607, 268, -3470.574135667093], [1556.3293657745342, 268, -3473.1616134329374], [1552.0863424258598, 268, -3476.6437727041853], [1548.6041831546117, 268, -3480.88679605286], [1546.0167053887671, 268, -3485.7276264711863], [1544.4233444477927, 268, -3490.980233560957], [1543.885332299083, 268, -3496.4427625774088]]}, {"name": "strat-thrill-rides route 2", "points": [[1543.885332299083, 268, -3496.4427625774088], [1544.4233444477927, 268, -3501.9052915938605], [1546.0167053887671, 268, -3507.157898683631], [1548.6041831546117, 268, -3511.9987291019575], [1552.0863424258598, 268, -3516.2417524506322], [1556.3293657745342, 268, -3519.72391172188], [1561.1701961928607, 268, -3522.3113894877247], [1566.4228032826315, 268, -3523.904750428699], [1571.885332299083, 268, -3524.4427625774088]]}, {"name": "strat-thrill-rides route 3", "points": [[1571.885332299083, 268, -3524.4427625774088], [1577.3478613155346, 268, -3523.904750428699], [1582.6004684053055, 268, -3522.3113894877247], [1587.441298823632, 268, -3519.72391172188], [1591.6843221723063, 268, -3516.2417524506322], [1595.1664814435544, 268, -3511.9987291019575], [1597.753959209399, 268, -3507.157898683631], [1599.3473201503734, 268, -3501.9052915938605], [1599.885332299083, 268, -3496.4427625774088]]}]};
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
  press(false);if(k===points.length-1){await waitReady();await __shot('walk-endpoint-'+allResults.length);}results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await waitReady();await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {doorEvents,routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
