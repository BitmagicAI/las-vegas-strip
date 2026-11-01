const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "martin-pool-circuit", "points": [[-870.7530727120233, 0.31, 832.5735131385446], [-881.4804969206792, 0.31, 833.9948190178862], [-890.5547758564854, 0.31, 836.1438859527378], [-905.0790748718771, 0.31, 836.0180072959527], [-906.5775379494678, 0.31, 840.7267008814068], [-889.0852563278962, 0.31, 842.5673612531266], [-881.4192748243765, 0.31, 841.4552034542904], [-868.9, 0.31, 838.0849370884565], [-868.9, 0.31, 835.3522674682437], [-870.7530727120233, 0.31, 832.5735131385446]]}, {"name": "panorama-north-pool-circuit", "points": [[-886.195003525683, 0.31, 927.4192917501415], [-897.7248657234177, 0.31, 947.2619240180026], [-882.3183592831592, 0.31, 950.9704809016455], [-879.8895570579531, 0.31, 944.0081834930675], [-884.044571379844, 0.31, 941.5155693009127], [-878.8769162587752, 0.31, 929.5810143950472], [-886.195003525683, 0.31, 927.4192917501415]]}, {"name": "panorama-south-pool-circuit", "points": [[-899.837226593147, 0.31, 1011.4966673212709], [-889.5254363744751, 0.31, 1031.8521923770268], [-881.7490503314467, 0.31, 1029.7012478458607], [-887.2716015106472, 0.31, 1017.7968781112941], [-882.1399219336857, 0.31, 1015.1148054898131], [-883.9265546770058, 0.31, 1007.8036452154109], [-899.837226593147, 0.31, 1011.4966673212709]]}, {"name": "panorama-1-retained-lobby", "points": [[-849.6756853354196, 0.24, 983.612071761624], [-851.092934200554, 0.24, 993.5111326087082]]}, {"name": "panorama-2-retained-lobby", "points": [[-857.97, 0.24, 890.3338295897236], [-857.97, 0.24, 900.3338295897236]]}, {"name": "martin-1-retained-lobby", "points": [[-872.9286985874982, 0.24, 840.61], [-862.9286985874982, 0.24, 840.61]]}]};
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
  press(false);if(k===points.length-1)await __shot('walk-pm-'+allResults.length);results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
