const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "palace-circuit-0", "points": [[-219.24899565437073, 0.32, -2832.070805365252], [-218.88423329772618, 0.32, -2829.5174688687403], [-217.05400701466252, 0.32, -2828.0939595374684], [-212.18912251853314, 0.32, -2828.7216865692267], [-210.79251261541543, 0.32, -2831.9804430098347], [-213.26447364998666, 0.32, -2833.3114989515266], [-210.86248200697466, 0.32, -2833.8094728287365], [-207.91537542383784, 0.32, -2837.9845404881808], [-204.57507365507587, 0.32, -2839.187049124935], [-203.81980188734596, 0.32, -2845.3802776203197], [-208.3125397660337, 0.32, -2850.0091590710895], [-215.84493686331766, 0.32, -2853.914846454866], [-217.7621944270743, 0.32, -2851.422411621982], [-219.5615103589542, 0.32, -2845.687092089115], [-223.73313764628637, 0.32, -2844.6143879295155], [-226.20739211166884, 0.32, -2838.291293184649], [-226.05123727901633, 0.32, -2834.8558868662935], [-221.70799438375002, 0.32, -2831.561012945747], [-219.24899565437073, 0.32, -2832.070805365252]]}, {"name": "us-bank-street-frontage", "points": [[-34.004692113561475, 0.32, -3231.7913603068687], [-34.004692113561475, 0.32, -3189.5813603068686], [-38.94929211356148, 0.32, -3179.3303603068684], [-46.78829211356148, 0.32, -3175.1093603068684], [-95.02829211356148, 0.32, -3175.1093603068684]]}]};
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
  press(false);if(k===points.length-1){await waitReady();await __shot('walk-palace-bank-'+allResults.length);}results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await waitReady();await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
