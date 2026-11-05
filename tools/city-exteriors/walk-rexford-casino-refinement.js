// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "rexford-ellen-courtyard", "points": [[2081.8848, 0.2397575616836548, -3821.7719], [2066.5077, 0.25006058216094973, -3822.6117], [2067.1075, 0.25011887550354006, -3833.5953], [2063.6677, 0.2399472236633301, -3840.2928], [2067.1075, 0.25052263736724856, -3833.5953], [2066.0169, 0.23920359611511233, -3813.6251], [2064.3187, 0.25017120838165285, -3802.7014], [2060.7148, 0.2400000333786011, -3800.8952]]}, {"name": "casino-center-1520", "points": [[1812.3046, 0.3398988485336304, -4083.2679], [1802.323, 0.23996009826660158, -4083.8733], [1798.0309, 0.25003805160522463, -4084.1337], [1799.4191, 0.24997820854187014, -4082.2461], [1798.5595, 0.24976553916931155, -4068.0722], [1796.1819, 0.25000002384185793, -4065.2109]]}, {"name": "rexford-ellen-courtyard-stairs0", "points": [[2061.3874, 0.25034918785095217, -3840.7178], [2061.7719, 3.2499999046325683, -3847.7573], [2067.713, 3.249997043609619, -3847.4329], [2067.0668, 3.2399181365966796, -3835.6005]]}, {"name": "rexford-ellen-courtyard-stairs1", "points": [[2057.705, 0.24959328174591067, -3804.4647], [2057.3178, 3.2400001525878905, -3797.3753], [2065.0563, 3.250159168243408, -3796.9526], [2065.8034, 3.2500328063964843, -3810.6322]]}, {"name": "casino-center-1520-stairs0", "points": [[1797.0294, 0.2500521183013916, -4079.1852], [1796.5633, 3.2399982452392577, -4071.4993], [1794.6668, 3.250262641906738, -4071.6144], [1794.2248, 3.2399977684020995, -4064.3277]]}]};
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
