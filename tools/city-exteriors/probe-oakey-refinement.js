// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const views=[
 ["luvit-front",[1929,2.5,-3932],[1930,2,-3943]],
 ["luvit-service",[1943,2.2,-3945],[1933,2,-3946]],
 ["oakey-front",[1873,3,-3952],[1899,2,-3953]],
 ["oakey-store",[1902,2.1,-3950],[1914,1.8,-3952]],
 ["shops-front",[1851,3,-3943],[1838,2,-3946]],
 ["shops-north",[1864,3,-3983],[1848,2,-3985]]
];
const frame=()=>new Promise(r=>requestAnimationFrame(r)),results=[];
for(const [name,eye,target] of views){probe.teleport(eye[0],Math.max(.2,eye[1]-1.7),eye[2]);const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});for(let i=0;i<900;i++)await frame();const readyDeadline=performance.now()+120000;while(probe.streaming().busy){if(performance.now()>readyDeadline)throw new Error('Area still loading; capture rejected');await frame();}for(let i=0;i<60;i++)await frame();await __shot(name);const times=[];let last=performance.now();for(let i=0;i<180;i++){await frame();const now=performance.now();times.push(now-last);last=now;}times.sort((a,b)=>a-b);release();results.push({name,eye,target,p50:times[90],p95:times[171]});}return results;
