// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta={"routes": [{"name": "siegel-paradise-stair-test-0", "points": [[1786.8243408203125, 0.2511375188827515, -3512.332763671875], [1783.336669921875, 1.8001684188842773, -3514.072998046875], [1782.552734375, 1.7899998664855956, -3512.635498046875], [1786.081298828125, 3.3506402015686034, -3510.806396484375], [1786.864013671875, 3.3502530097961425, -3512.2216796875], [1783.35546875, 4.900010490417481, -3514.063232421875], [1782.5545654296875, 4.889999771118164, -3512.6376953125], [1786.0718994140625, 6.449756050109864, -3510.810302734375], [1784.779296875, 6.448593997955323, -3508.03076171875]]}, {"name": "siegel-paradise-stair-test-1", "points": [[1798.890625, 0.2400000333786011, -3497.577880859375], [1795.0576171875, 1.7900003433227538, -3496.840576171875], [1795.3043212890625, 1.8000000953674316, -3495.235595703125], [1799.258544921875, 3.3497060775756835, -3495.919677734375], [1798.9837646484375, 3.3500179290771483, -3497.518798828125], [1795.05078125, 4.899995231628418, -3496.839111328125], [1795.304443359375, 4.8999980926513675, -3495.234130859375], [1799.2637939453125, 6.450312519073487, -3495.9208984375], [1799.8839111328125, 6.450975322723389, -3492.86328125]]}, {"name": "siegel-paradise-stair-test-2", "points": [[1798.0914306640625, 0.25066604614257815, -3469.807861328125], [1794.5875244140625, 1.8000403881072997, -3471.525390625], [1793.809326171875, 1.789998435974121, -3470.072021484375], [1797.363037109375, 3.3504008293151855, -3468.2744140625], [1798.132080078125, 3.350544834136963, -3469.702880859375], [1794.576171875, 4.889999294281006, -3471.53076171875], [1793.819091796875, 4.9, -3470.091552734375], [1797.350830078125, 6.439999961853028, -3468.280517578125], [1796.0482177734375, 6.450000190734864, -3465.439453125]]}, {"name": "siegel-paradise-stair-test-3", "points": [[1787.8917236328125, 0.2504263162612915, -3451.697509765625], [1784.38232421875, 1.8000000953674316, -3453.5751953125], [1783.5743408203125, 1.8000000953674316, -3452.15234375], [1787.0784912109375, 3.3499902725219726, -3450.205322265625], [1787.892822265625, 3.340000057220459, -3451.644287109375], [1784.3890380859375, 4.9001201629638675, -3453.571533203125], [1783.580322265625, 4.900198364257813, -3452.161865234375], [1787.0760498046875, 6.449992084503174, -3450.20654296875], [1785.6417236328125, 6.450328731536866, -3447.43408203125]]}, {"name": "siegel-paradise-stair-test-4", "points": [[1779.5849609375, 0.2400000333786011, -3431.880615234375], [1776.1224365234375, 1.8001128673553466, -3433.6865234375], [1775.31103515625, 1.7899998664855956, -3432.276611328125], [1778.79541015625, 3.339969539642334, -3430.377685546875], [1779.617919921875, 3.3399995803833007, -3431.79150390625], [1776.11279296875, 4.900113487243653, -3433.691162109375], [1775.3101806640625, 4.899999046325684, -3432.27587890625], [1778.80615234375, 6.43999662399292, -3430.371826171875], [1777.4464111328125, 6.450381183624268, -3427.619140625]]}]};
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
