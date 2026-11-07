// Supplemental repeat drives with low side endpoint cameras; not the matched benchmark.
// Real jeep, keyboard throttle/steering. Only initial route placement is teleported.
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const routes=[{name:'western first ramp',start:[-335,.84,-953.5],end:[-303,3.64,-953.5]},{name:'guest first ramp',start:[-129,.84,-952.5],end:[-94,3.44,-952.5]},{name:'southern first ramp',start:[54,.84,-809.5],end:[86,3.24,-809.5]}];
const results=[],down=new Set();
const press=(code,on)=>{if(on===down.has(code))return;on?down.add(code):down.delete(code);document.dispatchEvent(new KeyboardEvent(on?'keydown':'keyup',{code,key:code.replace('Key','').toLowerCase(),bubbles:true,cancelable:true}));};
const release=()=>{for(const key of [...down])press(key,false);};
for(let index=0;index<routes.length;index++){
 const route=routes[index];if(index===0)continue;probe.teleport(route.start[0],1.3,route.start[2]);
 for(let i=0;i<360;i++)await frame();
 const deadline=performance.now()+120000;while(probe.streaming().busy){if(performance.now()>deadline)throw Error('Area not ready');await frame();}
 if(!probe.seatJeep(...route.start,Math.PI/2))throw Error('Jeep unavailable');
 for(let i=0;i<180;i++)await frame();
 await __shot('jeep-start-'+index);
 const samples=[],times=[];let reached=false,error=null,stuck=0,lastX=probe.jeep().x,start=performance.now(),last=start;
 try{
  while(performance.now()-start<45000){
   const j=probe.jeep();if(!j){error='Driver left jeep';break;}
   const now=performance.now();times.push(now-last);last=now;
   if(j.x>=route.end[0]){reached=Math.abs(j.z-route.end[2])<3&&j.y>route.end[1]-.1&&j.y<route.end[1]+2;break;}
   if(Math.abs(j.z-route.end[2])>7||j.y<-.5){error='Route deviation or lost support';break;}
   if(j.x<lastX+.02){if(!stuck)stuck=now;else if(now-stuck>7000){error='No forward progress for7s';break;}}else{lastX=j.x;stuck=0;}
   const want=Math.atan2(route.end[0]-j.x,route.end[2]-j.z),yaw=Math.atan2(j.fx,j.fz);let err=want-yaw;while(err>Math.PI)err-=Math.PI*2;while(err< -Math.PI)err+=Math.PI*2;
   press('KeyA',err>.05);press('KeyD',err<-.05);press('KeyW',j.speed<2.5);press('KeyS',false);
   if(samples.length===0||now-start-samples[samples.length-1].t>250)samples.push({t:Math.round(now-start),...j});
   await frame();
  }
 }finally{release();}
 const endpoint=probe.jeep();
 for(let i=0;i<90;i++){const j=probe.jeep();press('KeyS',!!j&&j.speed>.15);await frame();}release();
 await __shot('jeep-end-'+index);
 const j=probe.jeep();const releaseCamera=engine.registerBeforeRender(()=>{engine.camera.position.set(j.x-3,j.y+.9,j.z+5);engine.camera.lookAt(j.x,j.y+.45,j.z);engine.camera.updateMatrixWorld();});
 for(let i=0;i<30;i++)await frame();await __shot('jeep-side-'+index);releaseCamera();times.sort((a,b)=>a-b);
 results.push({name:route.name,start:route.start,end:route.end,reached,error,endpoint,seconds:(performance.now()-start)/1000,p50:times[Math.floor(times.length*.5)],p95:times[Math.floor(times.length*.95)],maxGap:Math.max(...times),samples});
}
return {routes:results,passed:results.every(r=>r.reached),method:'Real jeep with keyboard input,2.5m/s target. Teleport only at route starts; no full garage-to-street loop claim.'};
