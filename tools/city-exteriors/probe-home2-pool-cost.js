// Local diagnostic only: fixed installed pool-deck camera, reversible one-factor ablations.
// Does not modify scene files or represent an optimized release.
let skyColor;scene.traverse(o=>{if(o.isDirectionalLight){o.color.setHex(0xffffff);o.intensity=2;skyColor=o.color.clone().setHex(0xc2d5e0);}if(o.isAmbientLight||o.isHemisphereLight){o.color.setHex(0xffffff);o.intensity=1.3;}if(/skybox/i.test(o.name))o.visible=false;});if(skyColor)scene.background=skyColor;
const eye=[-810.3517062589375,1.95,1792.2806071675093],target=[-812.0763524517522,1,1780.7469349201456];
probe.teleport(eye[0],1,eye[2]);
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const rows=[];
const measure=async name=>{for(let i=0;i<300;i++)await frame();const times=[],draws=[],triangles=[];let last=performance.now();for(let i=0;i<360;i++){await frame();const now=performance.now();times.push(now-last);last=now;draws.push(renderer.info.render.drawCalls);triangles.push(renderer.info.render.triangles);}const q=(a,p)=>a.sort((a,b)=>a-b)[Math.floor(a.length*p)];await __shot(name);rows.push({name,p50:q(times,.5),p95:q(times,.95),draws:q(draws,.5),triangles:q(triangles,.5)});};
try {
 await measure('baseline');
 const water=[];scene.traverse(o=>{if(o.isMesh&&o.visible&&[o.material].flat().some(m=>m?.userData.realisticWater==='pool'))water.push(o);});
 for(const o of water)o.visible=false;await measure('pool-water-hidden');for(const o of water)o.visible=true;
 const interiors=[];scene.traverse(o=>{if(o.isMesh&&o.visible){for(let p=o;p;p=p.parent)if(p.userData?.perfKind==='interior'||/^Streamed /.test(p.name)){interiors.push(o);break;}}});
 for(const o of interiors)o.visible=false;await measure('interiors-hidden');for(const o of interiors)o.visible=true;
 await measure('restored');
 return {eye,target,settings:'960x540 ultra neutral daylight;300 settle +360 sample frames each',water:water.map(o=>o.name),interiorMeshCount:interiors.length,rows};
} finally {release();}
