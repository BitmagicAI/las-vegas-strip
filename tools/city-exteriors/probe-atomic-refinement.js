// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const views=[
 ["atomic-east-front",[1690,8,-3717],[1642,9,-3718]],
 ["atomic-south-front",[1667,4,-3668],[1632,5,-3668]],
 ["atomic-south-terrace",[1637,6,-3656],[1635,6,-3680]]
];
const frame=()=>new Promise(r=>requestAnimationFrame(r)),results=[];
for(const [name,eye,target] of views){probe.teleport(eye[0],Math.max(.2,eye[1]-1.7),eye[2]);const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});for(let i=0;i<900;i++)await frame();const readyDeadline=performance.now()+120000;while(probe.streaming().busy){if(performance.now()>readyDeadline)throw new Error('Area still loading; capture rejected');await frame();}for(let i=0;i<60;i++)await frame();await __shot(name);const times=[];let last=performance.now();for(let i=0;i<180;i++){await frame();const now=performance.now();times.push(now-last);last=now;}times.sort((a,b)=>a-b);release();results.push({name,eye,target,p50:times[90],p95:times[171]});}return results;
