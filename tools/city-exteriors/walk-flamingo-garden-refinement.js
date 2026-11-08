// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "garden-route-0", "points": [[146.6794685947076, 0.4, -94.581], [146.6794685947076, 0.4, -88.081]]}, {"name": "garden-route-1", "points": [[169.98484760543488, 0.4, -86.744], [169.98484760543488, 0.4, -80.244]]}, {"name": "garden-route-2", "points": [[193.20360575784673, 0.4, -95.249], [193.20360575784673, 0.4, -88.749]]}, {"name": "garden-route-3", "points": [[195.31, 0.075, 7], [195.31, 0.075, 9], [195.31, 6.075, 23], [195.31, 6.075, 25]]}, {"name": "garden-route-4", "points": [[204.9150949998257, 0.4, -1.4916746000305352], [207.38871999997173, 0.4, -6.8127227997262665], [207.62259000014822, 0.4, -9.03910280043295], [207.14585500032925, 0.4, -13.024323000337446], [207.19982499968168, 0.4, -15.974276500008251], [208.5940499999964, 0.4, -19.113472300308622], [210.5819449995792, 0.4, -22.007766300119954], [205.94052500030458, 0.4, -26.527317699940944], [202.8642350001462, 0.4, -31.837234000297556], [199.54508000034537, 0.4, -36.30112590025907], [195.7401949999813, 0.4, -38.34939549967531], [192.00727000045816, 0.4, -39.31787079991944], [191.44958000033228, 0.4, -39.674091600127426], [184.85624500061704, 0.4, -43.93760930012026]]}, {"name": "garden-route-5", "points": [[175.35752499954498, 0.4, -38.19354890022698], [177.4803450000654, 0.4, -37.20280979972267], [179.81904500055208, 0.4, -37.102622700133814], [182.02282000010115, 0.4, -37.89298759987847], [183.7588550005755, 0.4, -39.47371740015874], [184.7483050006339, 0.4, -41.59991029969463], [184.85624500061704, 0.4, -43.93760930012026], [184.0556899995704, 0.4, -46.141725499775795], [183.01227000015956, 0.4, -47.28831119972843], [182.4725700002439, 0.4, -47.87830190029537], [180.34974999972349, 0.4, -48.86904100000871], [178.01105000051507, 0.4, -48.969228100388534], [175.80727499968773, 0.4, -48.17886319985291], [174.9077750006805, 0.4, -47.355102599717995], [174.07124000049166, 0.4, -46.59813340036361], [173.08179000043324, 0.4, -44.47194050003675], [172.9738500004501, 0.4, -42.13424150040209], [173.77440500021848, 0.4, -39.930125299955584], [175.35752499954498, 0.4, -38.19354890022698]]}, {"name": "garden-route-6", "points": [[168.18851000077188, 0.4, -60.46848080030518], [173.54953000078623, 0.4, -62.55014610011168]]}, {"name": "garden-route-7", "points": [[191.44958000033228, 0.4, -39.674091600127426], [186.9700700003932, 0.4, -34.764923699708184]]}, {"name": "garden-route-8", "points": [[162.8454799996895, 0.4, -59.15491659998315], [158.4559200008016, 0.4, -63.44069810023616]]}, {"name": "garden-route-9", "points": [[174.9077750006805, 0.4, -47.355102599717995], [166.77629500024693, 0.4, -55.30327920005778], [162.8454799996895, 0.4, -59.15491659998315]]}, {"name": "garden-route-10", "points": [[190.54108500058078, 0.4, -28.286157899929727], [193.26656999983527, 0.4, -27.250891199696035], [197.22437000006892, 0.4, -25.625633799686376], [199.58106000076583, 0.4, -23.210011499932065], [200.66046000059714, 0.4, -20.51609170008942], [201.59594000002485, 0.4, -16.95388370038247], [203.61981500002813, 0.4, -14.159776800159996], [205.0050449995986, 0.4, -13.369411900415344], [207.14585500032925, 0.4, -13.024323000337446]]}]};
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
  press(false);if(k===points.length-1){await waitReady();const p=probe.position(),q=points[points.length-2];probe.look(Math.atan2(p.x-q[0],p.z-q[2]),0);for(let i=0;i<6;i++)await frame();await __shot('walk-endpoint-'+allResults.length);}results.push({segment:k,reached,goal,position:probe.position()});
  if(!reached){await __shot('walk-blocked-'+k);break;}
 }
}finally{press(false);}
await waitReady();const p=probe.position(),q=points[1];probe.look(Math.atan2(p.x-q[0],p.z-q[2]),0);for(let i=0;i<6;i++)await frame();await __shot('walk-return-'+allResults.length);allResults.push({name:route.name,results,passed:results.length===walk.length-1&&results.every(r=>r.reached)});}
return {doorEvents,routes:allResults,passed:allResults.every(r=>r.passed),resident:probe.resident()};
