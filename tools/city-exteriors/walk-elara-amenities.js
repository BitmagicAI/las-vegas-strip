const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "west-access", "points": [[321.2, 0.31, 821], [321.2, 0.31, 842], [316, 0.31, 842], [316, 0.31, 843.05]]}, {"name": "south-lower", "points": [[321, 0.31, 848.2], [353, 0.31, 848.2]]}, {"name": "east-lower", "points": [[353, 0.31, 825], [353, 0.31, 844]]}, {"name": "north-lower", "points": [[321, 0.31, 821], [349, 0.31, 821]]}, {"name": "spiral", "points": [[316.0, 0.31, 843.05], [316.3448166149701, 0.41, 843.0754352015828], [316.682168991548, 0.51, 843.1511902110293], [317.00475446956114, 0.61, 843.2756251611598], [317.30559004759607, 0.71, 843.446046411089], [317.57816354389047, 0.8099999999999999, 843.6587648554158], [317.81657456540245, 0.9099999999999999, 843.9091757822154], [318.0156622335006, 1.01, 844.1918585511459], [318.17111690140155, 1.1099999999999999, 844.500693933942], [318.2795734450072, 1.21, 844.8289965772273], [318.3386841076797, 1.3099999999999998, 845.1696597202255], [318.34716932208215, 1.41, 845.5153090346694], [318.3048454089476, 1.51, 845.8584622567379], [318.2126285531801, 1.6099999999999999, 846.1916911554717], [318.07251497121865, 1.71, 846.5077823315411], [317.88753769897954, 1.8099999999999998, 846.7998933655572], [317.66170093578836, 1.91, 847.0617009357884], [317.3998933655572, 2.01, 847.2875376989795], [317.1077823315411, 2.11, 847.4725149712186], [316.7916911554717, 2.21, 847.6126285531801], [316.4584622567379, 2.3099999999999996, 847.7048454089476], [316.11530903466945, 2.4099999999999997, 847.7471693220822], [315.76965972022555, 2.51, 847.7386841076797], [315.42899657722734, 2.61, 847.6795734450071], [315.100693933942, 2.71, 847.5711169014015], [314.79185855114594, 2.81, 847.4156622335006], [314.50917578221544, 2.9099999999999997, 847.2165745654024], [314.25876485541585, 3.01, 846.9781635438904], [314.04604641108904, 3.11, 846.705590047596], [313.8756251611599, 3.21, 846.4047544695611], [313.7511902110293, 3.3099999999999996, 846.082168991548], [313.6754352015828, 3.4099999999999997, 845.7448166149701], [313.65, 3.51, 845.4], [311.8, 3.51, 845.4], [311.8, 3.51, 850.1], [314, 3.51, 850.1]]}, {"name": "upper-south", "points": [[314, 3.51, 850.1], [358, 3.51, 850.1]]}, {"name": "upper-west", "points": [[311.8, 3.51, 845.4], [311.8, 3.51, 839]]}]};
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
  press(false);if(k===points.length-1)await __shot('walk-elara-'+allResults.length);results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
