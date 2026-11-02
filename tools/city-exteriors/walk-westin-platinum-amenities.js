const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "westin-pool-circuit", "points": [[596.1094892961271, 7.57, 103.13730848180656], [589.2830677514655, 7.57, 109.80858408227131], [598.5128631721052, 7.57, 119.038379502911], [604.8902455950547, 7.57, 112.34990525445184], [596.1094892961271, 7.57, 103.13730848180656]]}, {"name": "platinum-outdoor", "points": [[877, 12.47, 267.4], [874, 12.47, 267.4], [874, 12.47, 255.5], [888.2, 12.47, 255.5], [888.2, 12.47, 267.1]]}, {"name": "platinum-indoor-link", "points": [[877, 12.47, 267.4], [877, 12.47, 269.5], [874, 12.47, 269.5], [874, 12.47, 278.4], [885.7, 12.47, 278.4], [885.7, 12.47, 271]]}]};
const waitReady=async()=>{const end=performance.now()+120000;while(probe.streaming().busy){if(performance.now()>end)throw new Error('Area not ready');await frame();}};
const allResults=[];
for(const route of meta.routes){
const points=route.points,walk=points.concat(points.slice(0,-1).reverse());
probe.teleport(points[0][0],points[0][1]+.1,points[0][2]);
for(let i=0;i<240;i++)await frame();await waitReady();
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
  press(false);if(k===points.length-1){await waitReady();await __shot('walk-westin-platinum-'+allResults.length);}results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await waitReady();await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
