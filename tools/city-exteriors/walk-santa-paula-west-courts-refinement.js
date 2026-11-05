// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "santa-paula-west-approach-0", "points": [[1966.14990234375, 0.24999167919158938, -3741.975830078125], [1965.2225341796875, 0.25065221786499026, -3741.995849609375], [1963.9940185546875, 0.24999954700469973, -3742.0224609375]]}, {"name": "santa-paula-west-approach-1", "points": [[1965.9102783203125, 0.25000002384185793, -3732.380859375], [1965.015625, 0.25000002384185793, -3732.400146484375], [1963.7816162109375, 0.25001718997955324, -3732.4267578125]]}, {"name": "santa-paula-west-approach-2", "points": [[1965.6961669921875, 0.25000002384185793, -3722.785400390625], [1964.80859375, 0.23999991416931155, -3722.804443359375], [1963.61767578125, 0.2501558303833008, -3722.830322265625]]}, {"name": "santa-paula-west-approach-3", "points": [[1960.37060546875, 0.2500226736068726, -3708.06201171875], [1959.4642333984375, 0.25000002384185793, -3708.096923828125], [1958.2303466796875, 0.2500245809555054, -3708.14404296875]]}, {"name": "santa-paula-west-approach-4", "points": [[1959.9862060546875, 0.2501079082489014, -3698.071533203125], [1959.0821533203125, 0.25007262229919436, -3698.10595703125], [1957.847900390625, 0.24950351715087893, -3698.15478515625]]}, {"name": "santa-paula-west-approach-5", "points": [[1955.0440673828125, 0.239999794960022, -3672.975341796875], [1955.075439453125, 0.2499879837036133, -3673.923583984375], [1955.1160888671875, 0.2400000333786011, -3675.157470703125]]}, {"name": "santa-paula-west-approach-6", "points": [[1945.246826171875, 0.23999848365783694, -3673.3515625], [1945.2763671875, 0.2500006198883057, -3674.24658203125], [1945.3170166015625, 0.23999991416931155, -3675.48046875]]}, {"name": "santa-paula-west-approach-7", "points": [[1935.4462890625, 0.25015571117401125, -3673.62548828125], [1935.4774169921875, 0.25015058517456057, -3674.569580078125], [1935.51806640625, 0.239999794960022, -3675.80322265625]]}, {"name": "santa-paula-west-approach-8", "points": [[1938.0606689453125, 0.239999794960022, -3667.413818359375], [1937.132080078125, 0.2500446081161499, -3667.448486328125], [1935.898193359375, 0.25000002384185793, -3667.49462890625]]}, {"name": "santa-paula-west-approach-9", "points": [[1937.697265625, 0.25000002384185793, -3658.86669921875], [1936.8131103515625, 0.2501107692718506, -3658.8994140625], [1935.61328125, 0.2500790596008301, -3658.9443359375]]}, {"name": "santa-paula-west-approach-10", "points": [[1964.700927734375, 0.2500293493270874, -3633.337646484375], [1963.8056640625, 0.2501025438308716, -3633.371337890625], [1962.5609130859375, 0.24999942779541018, -3633.417724609375]]}, {"name": "santa-paula-west-approach-11", "points": [[1933.866943359375, 0.2500245809555054, -3636.327392578125], [1932.9254150390625, 0.2500003814697266, -3636.355224609375], [1931.7237548828125, 0.25004401206970217, -3636.390869140625]]}, {"name": "santa-paula-west-approach-12", "points": [[1933.6063232421875, 0.24997725486755373, -3627.89697265625], [1932.702880859375, 0.23999991416931155, -3627.923583984375], [1931.468994140625, 0.25029399394989016, -3627.960205078125]]}, {"name": "santa-paula-west-approach-13", "points": [[1933.3748779296875, 0.250089430809021, -3619.4658203125], [1932.427978515625, 0.2500630855560303, -3619.49365234375], [1931.194091796875, 0.25000002384185793, -3619.5302734375]]}, {"name": "santa-paula-west-approach-14", "points": [[1913.832275390625, 0.23999991416931155, -3636.698974609375], [1912.8988037109375, 0.25000002384185793, -3636.731689453125], [1911.6539306640625, 0.2501001596450806, -3636.775634765625]]}, {"name": "santa-paula-west-approach-15", "points": [[1913.477294921875, 0.23999967575073244, -3626.7431640625], [1912.548095703125, 0.25005080699920657, -3626.776123046875], [1911.314208984375, 0.2400000333786011, -3626.819580078125]]}, {"name": "santa-paula-west-approach-16", "points": [[1913.0927734375, 0.25011982917785647, -3616.7890625], [1912.2515869140625, 0.25010409355163576, -3616.818603515625], [1910.9527587890625, 0.25003316402435305, -3616.8642578125]]}]};
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
