// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "rexford-place-east-approach-0", "points": [[2110.6953125, 0.2502767086029053, -4137.869140625], [2113.750732421875, 0.25003626346588137, -4136.44580078125], [2115.045166015625, 0.2500297069549561, -4135.84130859375]]}, {"name": "rexford-place-east-approach-1", "points": [[2099.40966796875, 0.2399995565414429, -4116.5791015625], [2102.553466796875, 0.24980964660644533, -4115.333984375], [2103.892333984375, 0.2500678539276123, -4114.8037109375]]}, {"name": "rexford-place-east-approach-2", "points": [[2094.53662109375, 0.24999954700469973, -4106.505859375], [2097.552001953125, 0.25043060779571535, -4104.96044921875], [2098.824951171875, 0.2400000333786011, -4104.30810546875]]}, {"name": "rexford-place-east-approach-3", "points": [[2084.663818359375, 0.2399995565414429, -4089.181640625], [2087.6123046875, 0.25005128383636477, -4087.546875], [2088.863525390625, 0.2400000333786011, -4086.852783203125]]}, {"name": "rexford-place-east-approach-4", "points": [[2072.718994140625, 0.2501514196395874, -4075.324462890625], [2075.839599609375, 0.24982359409332278, -4074.076171875], [2077.176513671875, 0.25000002384185793, -4073.541015625]]}, {"name": "rexford-place-east-approach-5", "points": [[2066.767578125, 0.24999954700469973, -4055.240478515625], [2069.687255859375, 0.25041534900665285, -4053.5830078125], [2070.931396484375, 0.2400000333786011, -4052.87646484375]]}, {"name": "rexford-place-east-approach-6", "points": [[2056.055908203125, 0.3506381750106812, -4044.700439453125], [2059.108642578125, 0.23999967575073244, -4043.24169921875], [2060.397705078125, 0.2400000333786011, -4042.624267578125]]}, {"name": "rexford-place-east-approach-7", "points": [[2050.4462890625, 0.2503103256225586, -4015.87353515625], [2053.748779296875, 0.2400000333786011, -4015.093017578125], [2055.150634765625, 0.2500370979309082, -4014.76171875]]}, {"name": "rexford-place-east-approach-8", "points": [[2047.24609375, 0.24999990463256838, -4002.849609375], [2050.526611328125, 0.25000002384185793, -4002.150146484375], [2051.93408203125, 0.24999990463256838, -4001.85009765625]]}, {"name": "rexford-place-east-approach-9", "points": [[2044.7611083984375, 0.2399995565414429, -3976.04150390625], [2048.160888671875, 0.24999942779541018, -3975.901123046875], [2049.589599609375, 0.250048303604126, -3975.84228515625]]}, {"name": "rexford-place-east-approach-10", "points": [[2043.8599853515625, 0.2399995565414429, -3963.22314453125], [2047.2540283203125, 0.250237250328064, -3963.041015625], [2048.6826171875, 0.24999680519104006, -3962.96435546875]]}]};
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
