// Temporary neutral-light material review; does not modify the saved world.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));const results=[];
for(const [name,eye,target] of [["entry", [1899.4393067471, 1.8, 769.6847391959348], [1896.4514283877052, 1.8, 761.1951819101006]], ["bar", [1898.502152881262, 1.8, 759.9433716003789], [1908.3075275802719, 1.7, 761.8990369633741]], ["dining", [1897.577858256032, 1.8, 757.6183598916405], [1900.6306724797532, 1.7, 749.1230479305972]]]){
 probe.teleport(eye[0],1,eye[2]);
 const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
 for(let i=0;i<300;i++)await frame();await __shot('ferraros-'+name);
 const times=[];let last=performance.now();for(let i=0;i<180;i++){await frame();const now=performance.now();times.push(now-last);last=now;}times.sort((a,b)=>a-b);release();results.push({name,eye,target,p50:times[90],p95:times[171]});
}return results;
