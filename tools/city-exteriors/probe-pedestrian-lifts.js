const frame=()=>new Promise(r=>requestAnimationFrame(r));let eye=[-41.4,8,755.2],target=[-53.4,4,742.2];const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});const rows=[];
for(const v of [
{name:'east-ground-door',eye:[73,2.4,891],target:[67.7,1.4,894.5],p:[73,1,891]},
{name:'west-landing-ground',eye:[24,10,790],target:[41,7.8,781],p:[35,7,779]},
{name:'cosmo-street',eye:[-41.4,8,755.2],target:[-53.4,4,742.2],p:[-44.4,1,750.2]},
{name:'cosmo-upper',eye:[-46,7.8,741.5],target:[-53.4,7.4,742.2],p:[-48,7,741.8]},
{name:'crystals-street',eye:[-27.1,8,860.3],target:[-39.1,4,847.3],p:[-30.1,1,855.3]},
{name:'crystals-upper',eye:[-49,7.8,845.7],target:[-39.1,7.4,847.3],p:[-46.8,7,846]},
{name:'park-street',eye:[-18.2,8,1304.8],target:[-30.2,4,1291.8],p:[-21.2,1,1299.8]},
{name:'park-upper',eye:[-30,7.8,1300],target:[-30.2,7.5,1291.8],p:[-30,7,1298]}
]){eye=v.eye;target=v.target;probe.teleport(...v.p);for(let i=0;i<180;i++)await frame();await __shot(v.name);const ms=[];let last=performance.now();for(let i=0;i<180;i++){await frame();const now=performance.now();ms.push(now-last);last=now;}ms.sort((a,b)=>a-b);rows.push({...v,p50:ms[90],p95:ms[171]});}
const {getInteractionManager}=await import('/dist/engine/engine/InteractionManager.js');const manager=getInteractionManager();
for(const key of ['cosmoPedestrianLift','crystalsPedestrianLift','parkPedestrianLift','harmonEastLift']){
 const d=await(await fetch('/build/city-exteriors/'+(key==='harmonEastLift'?'harmon-east-lift':key)+'-access.pending.json')).json();const[x,z]=d.lift;probe.teleport(x,1.1,z);for(let i=0;i<160;i++)await frame();
 const components=()=>Array.from(manager.registry.values()).filter(c=>{const p=c.getObject3D().position;return Math.hypot(p.x-x,p.z-z)<3;});
 const up=components().find(c=>c.getInteractable().getInteractStartDisplayName?.()==='Lift to pedestrian bridge');if(!up)throw Error(key+' lift action missing');up.getInteractable().onInteractStart();for(let i=0;i<80;i++)await frame();const upper=probe.position();
 const down=components().find(c=>c.getInteractable().getInteractStartDisplayName?.()==='Lift to street');if(!down)throw Error(key+' return action missing');down.getInteractable().onInteractStart();for(let i=0;i<80;i++)await frame();const lower=probe.position();
 const doors=components().map(c=>c.getInteractable()).filter(d=>typeof d.isOpen==='function');for(const door of doors)door.close();for(let i=0;i<80;i++)await frame();
 const world=engine.physicsWorld.world;
 const rays=()=>d.portals.flatMap(p=>[-.25,.25].map(offset=>!!world.castRay({origin:{x:p.p[0]+p.direction[0]*.7+p.direction[1]*offset,y:p.y+1.15,z:p.p[1]+p.direction[1]*.7-p.direction[0]*offset},dir:{x:-p.direction[0],y:0,z:-p.direction[1]}},1.4,true,undefined,undefined,undefined,undefined,c=>!c.isSensor())));
 const closed=doors.every(d=>!d.isOpen()),blocked=rays();for(const door of doors)door.open();for(let i=0;i<80;i++)await frame();const open=doors.every(d=>d.isOpen()),openBlocked=rays();
 rows.push({key,upper,lower,doors:doors.length,open,closed,blocked,openBlocked});console.info('Lift review',JSON.stringify(rows.at(-1)));
 if(Math.abs(upper.y-lower.y-5.855)>.4||doors.length!==4||!open||!closed||blocked.some(b=>!b)||openBlocked.some(Boolean))throw Error('Lift/door test failed '+JSON.stringify(rows.at(-1)));
 for(const door of doors)door.close();
}
release();return rows;
