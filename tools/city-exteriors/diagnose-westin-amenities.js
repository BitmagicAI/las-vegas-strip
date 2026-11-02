// Use unchanged names and cameras for both before and after installation.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const frame=()=>new Promise(r=>requestAnimationFrame(r));
probe.teleport(567,1.1,134);
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(567,28,134);engine.camera.lookAt(600,8,103);engine.camera.updateMatrixWorld();});
for(let i=0;i<1200;i++)await frame();
const nodes=[];scene.traverse(o=>{if(o.isMesh&&(/westinAmenities|westin/.test(o.name)&&/realistic water/.test(o.material?.name||'')))nodes.push(o);});
if(nodes.length!==1)throw new Error('Expected exactly one Westin water mesh, found '+nodes.length);
const records=[],names=nodes.map(o=>({name:o.name,source:o.userData.source,materials:(Array.isArray(o.material)?o.material:[o.material]).map(m=>m.name)}));
for(const mode of ['on','off','on','off','on']){
 for(const n of nodes)n.visible=mode==='off'?false:mode==='water-off'?!/pool/i.test(n.name):true;
 for(let i=0;i<180;i++)await frame();const t=[];let last=performance.now();for(let i=0;i<360;i++){await frame();const now=performance.now();t.push(now-last);last=now;}t.sort((a,b)=>a-b);records.push({mode,p50:t[180],p95:t[342],render:JSON.parse(JSON.stringify(renderer.info.render)),nodes:nodes.length});
}
release();return {records,names};
