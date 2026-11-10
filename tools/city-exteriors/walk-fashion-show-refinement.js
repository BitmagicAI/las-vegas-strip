// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "Existing upper plaza via both exterior stairs and return", "points": [[402.9866904319994, 0.24, -1225.887305977996], [397.9771952025266, 3.5549999999999997, -1229.3679607362117], [392.9676999730538, 6.87, -1232.8486154944273], [391.9001026290678, 6.87, -1233.5903943773258], [386.1941112221569, 6.87, -1225.3781071158949], [377.63512411179045, 6.87, -1213.0596762237487], [369.076137001424, 6.87, -1200.7412453316026], [363.3701455945131, 6.87, -1192.5289580701717], [364.43774293849907, 6.87, -1191.7871791872733], [369.4472381679719, 3.5549999999999997, -1188.3065244290576], [374.4567333974447, 0.24, -1184.825869670842]]}, {"name": "Preserved ground portal and galleria, enter and return", "points": [[380.5094246532912, 0.24, -1211.06257923133], [375.5820522964328, 0.24, -1214.4861740754764], [370.6546799395743, 0.24, -1217.909768919623], [353.4088766905696, 0.24, -1229.892350874136]]}, {"name": "Northern raked facade local approach 1 and return (not full perimeter)", "points": [[426.3833872606922, 0.24, -1280.508322571664], [424.4422809324037, 0.24, -1279.743998786299], [422.50117460411536, 0.24, -1278.9796750009343], [420.5600682758269, 0.24, -1278.2153512155692], [418.6189619475384, 0.24, -1277.4510274302045], [416.67785561925, 0.24, -1276.6867036448393], [414.73674929096154, 0.24, -1275.9223798594744], [412.79564296267307, 0.24, -1275.1580560741095], [410.8545366343846, 0.24, -1274.3937322887446], [408.91343030609613, 0.24, -1273.6294085033796], [406.9723239778077, 0.24, -1272.8650847180147], [405.0312176495193, 0.24, -1272.10076093265], [403.0901113212308, 0.24, -1271.3364371472846], [401.14900499294237, 0.24, -1270.57211336192], [399.20789866465395, 0.24, -1269.8077895765553]]}, {"name": "Northern raked facade local approach 2 and return (not full perimeter)", "points": [[401.80003756717184, 0.24, -1320.8613474553308], [403.45022449691373, 0.24, -1319.8279860528878], [405.10041142665557, 0.24, -1318.7946246504453], [406.7505983563975, 0.24, -1317.7612632480023], [408.4007852861394, 0.24, -1316.7279018455597], [410.0509722158813, 0.24, -1315.6945404431165], [411.7011591456232, 0.24, -1314.6611790406737], [413.35134607536514, 0.24, -1313.627817638231], [415.001533005107, 0.24, -1312.594456235788], [416.65171993484887, 0.24, -1311.5610948333454], [418.30190686459076, 0.24, -1310.5277334309023], [419.95209379433265, 0.24, -1309.4943720284596], [421.60228072407455, 0.24, -1308.4610106260168], [423.25246765381644, 0.24, -1307.4276492235738], [424.90265458355833, 0.24, -1306.394287821131]]}]};
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
  press(false);if(k===5&&allResults.length===0){await __shot('walk-upper-plaza');}if(k===points.length-1){await waitReady();await __shot('walk-frontage-'+allResults.length);}results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await waitReady();await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {doorEvents,routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
