const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={routes:[{name:'Forum Shops public frontage',points:[[6.532, 0.24, -390], [3.112, 0.24, -385], [0.292, 0.24, -380], [-1.928, 0.24, -375], [-3.548, 0.24, -370], [-4.568, 0.24, -365], [-4.988, 0.24, -360], [-4.9, 0.24, -355], [-4.9, 0.24, -350], [-4.9, 0.24, -345], [-4.996, 0.24, -340], [-4.856, 0.24, -335], [-4.516, 0.24, -330], [-3.976, 0.24, -325], [-3.236, 0.24, -320], [-2.296, 0.24, -315], [-1.156, 0.24, -310]]},{name:'Cooling-tower service lane (not public access)',points:[[-166.65,16.8,-418.8],[-166.65,16.8,-406.8]]}]};
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
  press(false);if(k===points.length-1)await __shot('walk-arrival-'+allResults.length);results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
