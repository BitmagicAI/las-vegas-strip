// Test only: isolate the new building's rendering cost without changing installed assets.
const frame=()=>new Promise(r=>requestAnimationFrame(r));
let eye=[0,62,1205],target=[75,14,1100],hide=false;
const meshes=[];const original=new Map();const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();for(const m of meshes)m.visible=hide?false:original.get(m);});
probe.teleport(25,2,1150);for(let i=0;i<200;i++)await frame();
scene.traverse(o=>{if(!o.isMesh)return;let p=o;while(p){if(/blvd/i.test(p.name)){meshes.push(o);original.set(o,o.visible);break;}p=p.parent;}});
const rows=[];
for(const hidden of [false,true,false,true,false]){hide=hidden;for(let i=0;i<120;i++)await frame();const ms=[];let prev=performance.now();for(let i=0;i<180;i++){await frame();let n=performance.now();ms.push(n-prev);prev=n;}ms.sort((a,b)=>a-b);rows.push({hidden,p50:ms[90],p95:ms[171],calls:renderer.info.render.calls,triangles:renderer.info.render.triangles});}
hide=false;for(const m of meshes)m.visible=original.get(m);release();return {matched:meshes.length,names:meshes.slice(0,4).map(m=>m.name),rows};
