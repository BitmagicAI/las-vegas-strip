const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "way/399554413", "points": [[-226.705, 0.64, 2786.268], [-226.584, 0.64, 2784.023]]}, {"name": "way/399554415", "points": [[-241.281, 0.64, 2791.953], [-242.352, 0.64, 2790.151]]}, {"name": "way/399554417", "points": [[-230.935, 0.64, 2787.362], [-231.623, 0.64, 2785.277]]}, {"name": "way/399554421", "points": [[-244.792, 0.64, 2791.47], [-247.067, 0.64, 2792.215]]}, {"name": "way/399554436", "points": [[-255.336, 0.64, 2797.718], [-255.783, 0.64, 2795.667]]}, {"name": "way/399554437", "points": [[-234.737, 0.64, 2787.901], [-235.298, 0.64, 2785.887]]}, {"name": "way/399554438", "points": [[-261.657, 0.64, 2796.747], [-259.411, 0.64, 2796.596]]}, {"name": "way/399554439", "points": [[-252.892, 0.64, 2794.861], [-250.767, 0.64, 2793.863]]}, {"name": "way/399554441", "points": [[-238.263, 0.64, 2789.921], [-239.308, 0.64, 2788.113]]}]};
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
  press(false);if(k===points.length-1){await waitReady();await __shot('walk-mandalay-cabana-'+allResults.length);}results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await waitReady();await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
