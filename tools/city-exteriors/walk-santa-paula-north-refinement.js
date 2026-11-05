// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "santa-paula-north-stairs-0", "points": [[2019.970703125, 0.2400000333786011, -3890.04052734375], [2013.91015625, 3.2500056266784667, -3890.224609375], [2003.13232421875, 3.2499984741210937, -3890.552001953125]]}, {"name": "santa-paula-north-stairs-1", "points": [[2010.3709716796875, 0.24805166721343996, -3874.106201171875], [2004.3406982421875, 3.250022792816162, -3874.36572265625], [2001.2666015625, 3.250132942199707, -3874.498046875]]}, {"name": "santa-paula-north-stairs-2", "points": [[2024.5458984375, 0.2399995565414429, -3848.170166015625], [2018.50732421875, 3.2499999046325683, -3848.50244140625], [2000.5003662109375, 3.2500943183898925, -3849.494140625]]}, {"name": "santa-paula-north-stairs-3", "points": [[2016.38037109375, 0.23999967575073244, -3831.078369140625], [2010.3056640625, 3.2501248359680175, -3831.322509765625], [1999.5174560546875, 3.250100040435791, -3831.754638671875]]}, {"name": "santa-paula-north-stairs-4", "points": [[2021.6307373046875, 0.2399995565414429, -3807.425048828125], [2015.5850830078125, 3.2500003814697265, -3807.5361328125], [1998.3243408203125, 3.2501014709472655, -3807.85498046875]]}, {"name": "santa-paula-north-stairs-5", "points": [[2005.7283935546875, 0.24145188331604006, -3791.59423828125], [1999.693359375, 3.2499999046325683, -3791.833251953125], [1997.095703125, 3.2500423431396483, -3791.936279296875]]}]};
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
