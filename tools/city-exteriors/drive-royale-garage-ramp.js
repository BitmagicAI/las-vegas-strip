// Real jeep input on the existing ground-to-first-deck ramp; no teleport during drive.
const frame=()=>new Promise(r=>requestAnimationFrame(r)),yaw=Math.atan2(1.394,51.853);
const point=(u,y,v)=>[201.764+Math.cos(yaw)*u+Math.sin(yaw)*v,y,-491.77-Math.sin(yaw)*u+Math.cos(yaw)*v];
const start=point(10,.24+2/38*3.2,-17),goal=point(10,.24+36/38*3.2,17);
probe.teleport(start[0],start[1]+.2,start[2]);for(let i=0;i<360;i++)await frame();
if(!probe.seatJeep(start[0],start[1]+.6,start[2],yaw))throw Error('Jeep seating failed');
for(let i=0;i<180;i++)await frame();
const down=new Set(),press=(code,on)=>{if(on===down.has(code))return;if(on)down.add(code);else down.delete(code);document.dispatchEvent(new KeyboardEvent(on?'keydown':'keyup',{code,key:code.replace('Key','').toLowerCase(),bubbles:true,cancelable:true}));};
const samples=[],deadline=performance.now()+90000;let passed=false;
await __shot('garage-ramp-start');
try{while(performance.now()<deadline){const s=probe.jeep();if(!s)throw Error('Left jeep');
const dx=goal[0]-s.x,dz=goal[2]-s.z,d=Math.hypot(dx,dz);
if(samples.length===0||performance.now()-samples[samples.length-1].time>500)samples.push({...s,time:performance.now(),distance:d});
if(d<1.4){passed=s.y>2.5&&s.y<5;break;}
let err=Math.atan2(dx,dz)-Math.atan2(s.fx,s.fz);while(err>Math.PI)err-=2*Math.PI;while(err<-Math.PI)err+=2*Math.PI;
press('KeyA',err>.035);press('KeyD',err<-.035);press('KeyW',s.speed<2);press('KeyS',false);await frame();
}}finally{for(const k of [...down])press(k,false);}
await __shot('garage-ramp-end');return {passed,start,goal,end:probe.jeep(),samples,scope:'One continuous ascending ramp segment; turning loops and upper ramps not certified.'};
