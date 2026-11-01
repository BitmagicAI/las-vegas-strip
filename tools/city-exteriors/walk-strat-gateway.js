const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "west-sidewalk", "points": [[1570.11, 0.24, -3433.302], [1591.23, 0.24, -3471.89]]}, {"name": "east-sidewalk", "points": [[1596.77, 0.24, -3418.71], [1617.89, 0.24, -3457.298]]}, {"name": "southbound-lane", "points": [[1579.055, 0.24, -3428.406], [1600.175, 0.24, -3466.994]]}, {"name": "northbound-lane", "points": [[1587.825, 0.24, -3423.606], [1608.945, 0.24, -3462.194]]}]};
const allResults=[];
for(const route of meta.routes){
const points=route.points,walk=points.concat(points.slice(0,-1).reverse());
probe.teleport(points[0][0],points[0][1]+.1,points[0][2]);
for(let i=0;i<240;i++)await frame();
const press=on=>document.dispatchEvent(new KeyboardEvent(on?'keydown':'keyup',{code:'KeyW',key:'w',bubbles:true,cancelable:true}));
const results=[];
try{
 for(let k=1;k<walk.length;k++){
  const goal=walk[k];let reached=false;const start=performance.now(),origin=probe.position(),timeout=10000+1000*Math.hypot(goal[0]-origin.x,goal[2]-origin.z)/1.5;
  while(performance.now()-start<timeout){
   const p=probe.position(),dx=goal[0]-p.x,dz=goal[2]-p.z;
   if(Math.hypot(dx,dz)<.35){reached=Math.abs(p.y-goal[1])<.45;break;}
   probe.look(Math.atan2(-dx,-dz),0);press(true);await frame();
  }
  press(false);if(k===points.length-1)await __shot('walk-gateway-'+allResults.length);results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
