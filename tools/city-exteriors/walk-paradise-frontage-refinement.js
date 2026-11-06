// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "Paradise building 1 approach and return", "points": [[1773.728430797621, 0.2, -3362.891874385394], [1778.4574477104138, 0.2, -3360.409476183131], [1779.8741257392037, 0.2, -3359.6658207772175]]}, {"name": "Paradise building 2 approach and return", "points": [[1767.0519726457717, 0.2, -3350.0150749739646], [1771.7993025851504, 0.2, -3347.5538976774237], [1773.2197588868592, 0.2, -3346.8174848211156]]}, {"name": "Paradise building 3 approach and return", "points": [[1740.1509789476497, 0.2, -3298.0459914839284], [1744.0559737145115, 0.2, -3295.9375568456944], [1745.4638619221394, 0.2, -3295.177391867008]]}, {"name": "Paradise building 4 approach and return", "points": [[1704.8917174862697, 0.2, -3232.7119972984624], [1709.7512804110338, 0.2, -3230.411276466164], [1711.1973964757365, 0.2, -3229.726624490772]]}, {"name": "Paradise building 5 approach and return", "points": [[1697.9417558549715, 0.2, -3219.2125786098864], [1699.3561050849428, 0.2, -3218.479416049687], [1700.7765959322574, 0.2, -3217.7430698317326]]}, {"name": "Paradise building 6 approach and return", "points": [[1688.7837669415444, 0.2, -3200.730908815092], [1692.7438504058052, 0.2, -3198.581891967966], [1694.1501264743104, 0.2, -3197.8187487185364]]}, {"name": "Paradise building 7 approach and return", "points": [[1682.7118829124772, 0.2, -3188.080016361659], [1686.3487251933304, 0.2, -3186.1175279014533], [1687.7568014163628, 0.2, -3185.357711245851]]}, {"name": "Paradise building 8 approach and return", "points": [[1674.0430323418807, 0.2, -3168.1290240231565], [1675.6174978769807, 0.2, -3167.3870543893763], [1677.0648376028128, 0.2, -3166.7049930152843]]}]};
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
