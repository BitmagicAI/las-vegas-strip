const frame=()=>new Promise(r=>requestAnimationFrame(r));let eye=[79,8,909.4],target=[67,4,896.4];
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const rows=[];
for(const v of [
 {name:'lift-east',eye:[79,8,909.4],target:[67,4,896.4],p:[76,1,904.4]},
 {name:'lift-landing',eye:[65,8,886],target:[67,7.5,896.4],p:[66,7,890]},
 {name:'bridge-aerial',eye:[109,37,910],target:[65,5,865],p:[68,7,878]},
 {name:'bridge-north-entry',eye:[71,8,850],target:[75,7.7,831],p:[74,7,840]},
 {name:'atrium-corridor',eye:[75.5,7.7,828],target:[76,7.5,809],p:[75,7,827]},
 {name:'west-landing',eye:[24,10,790],target:[41,7.8,781],p:[35,7,779]}
]){eye=v.eye;target=v.target;probe.teleport(...v.p);for(let i=0;i<180;i++)await frame();await __shot(v.name);const ms=[];let prev=performance.now();for(let i=0;i<180;i++){await frame();const now=performance.now();ms.push(now-prev);prev=now;}ms.sort((a,b)=>a-b);rows.push({...v,p50:ms[90],p95:ms[171]});}
// Exercise the real registered lift interaction and Door instances, rather than
// duplicating the teleport or animation code in this review script.
probe.teleport(66.982,1.1,896.44);for(let i=0;i<180;i++)await frame();
const {getInteractionManager}=await import('/dist/engine/engine/InteractionManager.js');
const manager=getInteractionManager(),components=()=>Array.from(manager.registry.values()).filter(c=>{const p=c.getObject3D().position;return Math.hypot(p.x-66.982,p.z-896.44)<4;});
const up=components().find(c=>c.getInteractable().getInteractStartDisplayName?.()==='Lift to pedestrian bridge');
if(!up)throw new Error('Actual lift interaction not registered');
up.getInteractable().onInteractStart();for(let i=0;i<100;i++)await frame();const upper=probe.position();
const down=components().find(c=>c.getInteractable().getInteractStartDisplayName?.()==='Lift to street');if(!down)throw new Error('Return lift interaction not registered');
down.getInteractable().onInteractStart();for(let i=0;i<100;i++)await frame();const lower=probe.position();
const doors=components().map(c=>c.getInteractable()).filter(d=>typeof d.isOpen==='function');
for(const d of doors)d.open();for(let i=0;i<80;i++)await frame();const open=doors.every(d=>d.isOpen());for(const d of doors)d.close();for(let i=0;i<80;i++)await frame();const closed=doors.every(d=>!d.isOpen());
rows.push({interaction:{upper,lower,doors:doors.length,open,closed}});if(Math.abs(upper.y-lower.y-5.855)>.4||doors.length!==4||!open||!closed)throw new Error('Lift interaction check failed '+JSON.stringify(rows.at(-1)));
release();return rows;
