// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "weldon-east-approach-0", "points": [[1942.2532958984375, 0.250014328956604, -3762.642333984375], [1945.39794921875, 0.25018813610076907, -3761.660400390625], [1946.77294921875, 0.23999991416931155, -3761.23095703125]]}, {"name": "weldon-east-approach-1", "points": [[1931.5, 0.25000002384185793, -3749.169189453125], [1936.0311279296875, 0.2504321575164795, -3746.7421875], [1937.2928466796875, 0.2500936031341553, -3746.06689453125]]}, {"name": "weldon-east-approach-2", "points": [[1919.5924072265625, 0.25006248950958254, -3726.488525390625], [1926.2314453125, 0.24999859333038332, -3723.516357421875], [1927.5372314453125, 0.25007894039154055, -3722.93212890625]]}, {"name": "weldon-east-approach-3", "points": [[1908.296142578125, 0.24999847412109377, -3704.971435546875], [1912.777587890625, 0.239999794960022, -3703.0185546875], [1914.083251953125, 0.25000002384185793, -3702.4501953125]]}, {"name": "weldon-east-approach-4", "points": [[1896.500244140625, 0.25009419918060305, -3682.457763671875], [1903.060791015625, 0.23999991416931155, -3680.0263671875], [1904.4617919921875, 0.2500337600708008, -3679.507080078125]]}, {"name": "weldon-east-approach-5", "points": [[1885.8885498046875, 0.24999835491180422, -3662.328369140625], [1890.3414306640625, 0.23999991416931155, -3660.197265625], [1891.6409912109375, 0.25000002384185793, -3659.5751953125]]}, {"name": "weldon-east-approach-6", "points": [[1870.470947265625, 0.23999943733215334, -3627.152587890625], [1879.4229736328125, 0.239999794960022, -3629.239990234375], [1880.81640625, 0.23999991416931155, -3629.565185546875]]}]};
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
