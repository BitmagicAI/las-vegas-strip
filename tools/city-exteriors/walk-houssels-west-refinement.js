// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "houssels-west-approach-0", "points": [[2175.84521484375, 0.24999799728393557, -4105.8662109375], [2166.541015625, 0.23999991416931155, -4110.91943359375], [2165.2841796875, 0.2400000333786011, -4111.60205078125]]}, {"name": "houssels-west-approach-1", "points": [[2164.40869140625, 0.24999811649322512, -4084.328125], [2147.88916015625, 0.23931076526641848, -4091.896240234375], [2146.58935546875, 0.25000002384185793, -4092.492431640625]]}, {"name": "houssels-west-approach-2", "points": [[2154.7529296875, 0.2400000333786011, -4065.899169921875], [2140.71728515625, 0.2501722812652588, -4072.590576171875], [2139.427978515625, 0.24999990463256838, -4073.2060546875]]}, {"name": "houssels-west-approach-3", "points": [[2148.6103515625, 0.25000002384185793, -4054.2998046875], [2133.5205078125, 0.2400000333786011, -4061.986083984375], [2132.23779296875, 0.24999978542327883, -4062.63916015625]]}, {"name": "houssels-west-approach-4", "points": [[2135.690673828125, 0.24999799728393557, -4029.701416015625], [2120.644775390625, 0.2498116731643677, -4037.443603515625], [2119.36474609375, 0.24999990463256838, -4038.103759765625]]}, {"name": "houssels-west-approach-5", "points": [[2126.3603515625, 0.25000002384185793, -4011.852783203125], [2109.69384765625, 0.2501671552658081, -4019.656982421875], [2108.3994140625, 0.2400000333786011, -4020.26318359375]]}, {"name": "houssels-west-approach-6", "points": [[2120.111083984375, 0.2400000333786011, -3993.0263671875], [2106.23583984375, 0.24999954700469973, -3996.461669921875], [2104.833740234375, 0.2500452041625977, -3996.8095703125]]}, {"name": "houssels-west-approach-7", "points": [[2118.316162109375, 0.2500163555145264, -3982.311767578125], [2101.70361328125, 0.24999847412109377, -3983.78857421875], [2100.2587890625, 0.25016369819641116, -3983.917724609375]]}, {"name": "houssels-west-approach-8", "points": [[2116.59521484375, 0.2500403165817261, -3962.645263671875], [2107.657470703125, 0.250054144859314, -3962.984619140625], [2106.163818359375, 0.24999895095825198, -3963.041259765625]]}]};
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
