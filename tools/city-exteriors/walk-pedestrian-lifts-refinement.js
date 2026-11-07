// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "cosmoPedestrianLift 0", "points": [[-50.42, 0.18, 738.82], [-50.2, 0.18, 741.3], [-51.411, 0.18, 741.633], [-53.380178864669666, 0.18, 742.1893961784666]]}, {"name": "cosmoPedestrianLift 1", "points": [[-48.82, 6.035, 741.86], [-51.384, 6.035, 742.045], [-53.380178864669666, 6.035, 742.1893961784666]]}, {"name": "crystalsPedestrianLift 0", "points": [[-34.55, 0.18, 846.28], [-37.158, 0.18, 847.709], [-39.11373836874042, 0.18, 847.2804472407922]]}, {"name": "crystalsPedestrianLift 1", "points": [[-46.94, 6.035, 846.01], [-41.07, 6.035, 846.852], [-39.11373836874042, 6.035, 847.2804472407922]]}, {"name": "parkPedestrianLift 0", "points": [[-33.82, 0.18, 1295.33], [-31.25, 0.18, 1295.21], [-30.35, 0.18, 1293.599], [-30.17396405608967, 0.18, 1291.8213161544757]]}, {"name": "parkPedestrianLift 1", "points": [[-30.38, 6.035, 1301.06], [-30.197, 6.035, 1293.61], [-30.17396405608967, 6.035, 1291.8213161544757]]}, {"name": "harmonEastLift 0", "points": [[67.0592100258078, 6.035, 892.4127225558805], [66.8076272968483, 6.035, 894.396835992781], [66.982, 6.035, 896.44]]}, {"name": "harmonEastLift 1", "points": [[68.4976922675607, 0.18, 892.595120034376], [68.24610953860119, 0.18, 894.5792334712766], [66.982, 0.18, 896.44]]}]};
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
  press(false);if(k===points.length-1){await waitReady();await __shot('walk-endpoint-'+allResults.length);}results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await waitReady();await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {doorEvents,routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
