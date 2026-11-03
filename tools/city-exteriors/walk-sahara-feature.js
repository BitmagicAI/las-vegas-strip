const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes":[{"name":"sahara-west-feature-arc","points":[[1361.007650711028,0.7312498092651367,-2890.246711095626],[1357.2467110956259,0.38284921646118164,-2894.007650711028],[1354.8320392229823,0.30200815200805664,-2898.746711095626],[1354,0.13500022888183594,-2904],[1354.8320392229823,0.13500022888183594,-2909.253288904374],[1357.2467110956259,0.13500022888183594,-2913.992349288972],[1361.007650711028,0.13500022888183594,-2917.753288904374]]}]};
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
  press(false);if(k===points.length-1){await waitReady();await __shot('walk-sahara-feature-'+allResults.length);}results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await waitReady();await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
