const frame=()=>new Promise(r=>requestAnimationFrame(r));const rows=[];
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
return rows;
