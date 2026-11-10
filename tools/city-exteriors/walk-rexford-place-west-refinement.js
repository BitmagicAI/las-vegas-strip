// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "rexford-place-west-approach-0", "points": [[2067.001708984375, 0.2503175973892212, -4114.8427734375], [2063.970703125, 0.2399993181228638, -4116.4296875], [2062.693603515625, 0.250056529045105, -4117.09912109375]]}, {"name": "rexford-place-west-approach-1", "points": [[2056.534423828125, 0.24990382194519045, -4094.93310546875], [2053.49609375, 0.25028040409088137, -4096.4150390625], [2052.21240234375, 0.2400000333786011, -4097.041015625]]}, {"name": "rexford-place-west-approach-2", "points": [[2050.478271484375, 0.25025966167449953, -4082.7392578125], [2047.48779296875, 0.2400000333786011, -4084.337890625], [2046.2255859375, 0.2500144481658936, -4085.012939453125]]}, {"name": "rexford-place-west-approach-3", "points": [[2039.9656982421875, 0.2499722480773926, -4063.183837890625], [2036.8680419921875, 0.2502295017242432, -4064.59375], [2035.567138671875, 0.25004842281341555, -4065.186767578125]]}, {"name": "rexford-place-west-approach-4", "points": [[2025.87646484375, 0.24999966621398928, -4030.3427734375], [2022.6357421875, 0.25024368762969973, -4031.304443359375], [2021.249267578125, 0.24999978542327883, -4031.717041015625]]}, {"name": "rexford-place-west-approach-5", "points": [[2022.2491455078125, 0.2399995565414429, -4018.505126953125], [2018.947998046875, 0.24999954700469973, -4019.333251953125], [2017.559814453125, 0.24999978542327883, -4019.681396484375]]}, {"name": "rexford-place-west-approach-6", "points": [[2018.578125, 0.2501288890838623, -3996.475341796875], [2015.1943359375, 0.24976887702941897, -3996.616943359375], [2013.765625, 0.2500293493270874, -3996.6767578125]]}, {"name": "rexford-place-west-approach-7", "points": [[2017.1676025390625, 0.25000002384185793, -3983.818359375], [2013.7845458984375, 0.239999794960022, -3983.9306640625], [2012.344970703125, 0.25010850429534914, -3983.978271484375]]}, {"name": "rexford-place-west-approach-8", "points": [[2015.080078125, 0.25002517700195315, -3944.423583984375], [2011.68408203125, 0.25027217864990237, -3944.586669921875], [2010.25537109375, 0.2500328063964844, -3944.6552734375]]}, {"name": "rexford-place-west-approach-9", "points": [[2015.8802490234375, 0.25017585754394533, -3960.8837890625], [2012.4993896484375, 0.25006809234619143, -3960.95703125], [2011.070556640625, 0.2501030206680298, -3960.988037109375]]}, {"name": "rexford-place-west-approach-10", "points": [[2034.4400634765625, 0.2502126932144165, -4050.645751953125], [2031.3934326171875, 0.2499177694320679, -4052.169921875], [2030.1163330078125, 0.2501638174057007, -4052.806640625]]}]};
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
