// Temporary neutral-light material review; does not modify the saved world.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));const results=[];
for(const [name,eye,target] of [['patio',[-835,3.2,1661],[-830,3.2,1635]],['west',[-865,3.2,1633],[-840,3.2,1633]],['east',[-796,3.2,1633],[-816,3.2,1633]],['dining',[-831,1.8,1635.8],[-841,1.4,1638.65]],['counter',[-839,1.8,1635.8],[-835,1.6,1629]]]){
 probe.teleport(eye[0],1,eye[2]);
 const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
 for(let i=0;i<300;i++)await frame();await __shot('inout-dean-martin-'+name);
 const times=[];let last=performance.now();for(let i=0;i<180;i++){await frame();const now=performance.now();times.push(now-last);last=now;}times.sort((a,b)=>a-b);release();results.push({name,eye,target,p50:times[90],p95:times[171]});
}return results;
