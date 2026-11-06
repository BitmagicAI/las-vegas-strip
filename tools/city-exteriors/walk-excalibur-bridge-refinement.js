// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "mapped-bridge-27628757", "points": [[-90.8966143535239, 6.035, 1722.17729959042], [-91.03012060476017, 6.035, 1730.1761855179027], [-91.16362685599643, 6.035, 1738.1750714453854], [-91.29713310723268, 6.035, 1746.173957372868], [-91.43063935846895, 6.035, 1754.1728433003507], [-91.56414560970521, 6.035, 1762.1717292278336], [-91.68511498903561, 6.035, 1769.4194817264781]]}, {"name": "mapped-bridge-29713830", "points": [[-96.39040165490549, 6.035, 1774.9125779092917], [-91.7036228253275, 6.035, 1769.6842244037296], [-86.77660684613386, 6.035, 1764.7422168174423], [-81.12742356608558, 6.035, 1759.0777019866362], [-75.4782402860373, 6.035, 1753.41318715583], [-69.82905700598903, 6.035, 1747.7486723250238], [-64.17987372594075, 6.035, 1742.0841574942176], [-58.530690445892475, 6.035, 1736.4196426634114], [-56.276743705568634, 6.035, 1734.1595788443628]]}, {"name": "mapped-bridge-115541317", "points": [[-21.97129453763517, 0.135, 1744.466521930814], [-21.98574969218532, 2.796328618593077, 1750.541504733136], [-22.00153404238899, 6.035, 1757.1751007767125], [-22.003735032999508, 6.035, 1758.100098158136]]}, {"name": "mapped-bridge-115541322", "points": [[-71.67932969938344, 0.135, 1715.4104273480607], [-77.75432814417357, 2.6975512983296195, 1715.4060804183985], [-84.60798819237726, 6.035, 1715.4011763219728], [-85.53298795557576, 6.035, 1715.4005144437938]]}, {"name": "mapped-bridge-1382402324", "points": [[-90.68926773822156, 6.035, 1769.6665721596103], [-82.68927845571972, 6.035, 1769.6534771278891], [-74.68928917321789, 6.035, 1769.640382096168], [-66.68929989071606, 6.035, 1769.6272870644468], [-60.728459158722714, 6.035, 1769.079778222415], [-58.84376932548216, 6.035, 1768.807001728765]]}]};
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
  press(false);if(k===points.length-1){await waitReady();await __shot('walk-frontage-'+allResults.length);}results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await waitReady();await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {doorEvents,routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
