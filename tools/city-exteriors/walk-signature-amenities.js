const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "pool1-west", "points": [[525.52, 0.32, 1132.97], [525.52, 0.32, 1151.27]]}, {"name": "pool1-east", "points": [[536.52, 0.32, 1132.97], [536.52, 0.32, 1151.27]]}, {"name": "pool1-gate", "points": [[551.02, 0.32, 1141.47], [536.52, 0.32, 1141.47]]}, {"name": "pool1-south", "points": [[525.52, 0.32, 1151.27], [536.52, 0.32, 1151.27]]}, {"name": "pool2-west", "points": [[525.64, 0.32, 983.25], [525.64, 0.32, 1011.55]]}, {"name": "pool2-east", "points": [[539.64, 0.32, 983.25], [539.64, 0.32, 1011.55]]}, {"name": "pool2-gate", "points": [[552.64, 0.32, 996.75], [539.64, 0.32, 996.75]]}, {"name": "pool2-south", "points": [[525.64, 0.32, 1011.55], [539.64, 0.32, 1011.55]]}, {"name": "pool3-west", "points": [[525.89, 0.32, 922.44], [525.89, 0.32, 947.24]]}, {"name": "pool3-east", "points": [[539.39, 0.32, 922.44], [539.39, 0.32, 947.24]]}, {"name": "pool3-gate", "points": [[552.64, 0.32, 934.19], [539.39, 0.32, 934.19]]}, {"name": "pool3-south", "points": [[525.89, 0.32, 947.24], [539.39, 0.32, 947.24]]}]};
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
  press(false);if(k===points.length-1)await __shot('walk-signature-'+allResults.length);results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
