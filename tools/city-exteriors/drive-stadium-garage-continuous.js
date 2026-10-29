// Actual vehicle inputs through the entry, all three ramps and both interlevel turns.
// Single initial placement; no intermediate teleports.
const frame=()=>new Promise(r=>requestAnimationFrame(r));
const meta=await (await fetch('/build/strip-landmarks/stadium-garage-metadata.json')).json();
const press=(code,on)=>document.dispatchEvent(new KeyboardEvent(on?'keydown':'keyup',{code,key:code.slice(3).toLowerCase(),bubbles:true,cancelable:true}));
const release=()=>{for(const k of ['KeyW','KeyA','KeyD','KeyS'])press(k,false);};
const yaw=-Math.atan2(30.624,25.216);
const c=Math.cos(yaw),sn=Math.sin(yaw),P=(x,y,z)=>[-824.745+c*x+sn*z,y,1779.52-sn*x+c*z];
const points=[P(83,.12,-28.7),P(77,.12,-28.7),P(73,.12,-30.4)];
for(let level=0;level<3;level++){
 const lo=.12+level*3.24,hi=lo+3.24;
 points.push(P(70,lo,-31.5),P(56.5,(lo+hi)/2,-36.5),P(43,hi,-41.5),P(39.5,hi,-42.8));
 if(level<2)for(const [x,z] of [[35,-40],[34,-35],[38,-30],[48,-24],[58,-18.5],[68,-18.5],[72,-23],[73,-28.5]])points.push(P(x,hi,z));
}
const routes=[{name:'Continuous ground entrance to roof',points}];
const results=[];
for(const route of routes){for(const reverse of [false]){
 const pts=reverse?[...route.points].reverse():route.points;
 const a=pts[0],b=pts[1],end=pts.at(-1),heading=Math.atan2(b[0]-a[0],b[2]-a[2]);
 release();probe.teleport(a[0],a[1]+.1,a[2]);for(let i=0;i<180;i++)await frame();
 if(!probe.seatJeep(a[0],a[1]+.6,a[2],heading))throw Error('Cannot seat review jeep');
 for(let i=0;i<120;i++)await frame();
 const start=performance.now(),samples=[];let reached=false,next=1;
 try{while(performance.now()-start<180000){
  const st=probe.jeep();if(!st)throw Error('Left jeep');
  if(Math.hypot(st.x-end[0],st.z-end[2])<1.7&&Math.abs(st.y-end[1]-.56)<.5){reached=true;break;}
  while(next<pts.length-1&&Math.hypot(st.x-pts[next][0],st.z-pts[next][2])<4)next++;
  const target=pts[next],want=Math.atan2(target[0]-st.x,target[2]-st.z),yaw=Math.atan2(st.fx,st.fz);
  const err=Math.atan2(Math.sin(want-yaw),Math.cos(want-yaw));
  press('KeyA',err>.05);press('KeyD',err<-.05);press('KeyW',st.speed<3.5);
  if(!samples.length||performance.now()-samples.at(-1).t>250)samples.push({t:performance.now(),...st});
  await frame();
 }}finally{release();}
 await __shot('drive-'+results.length+(reached?'-pass':'-blocked'));
 results.push({name:route.name,reverse,reached,elapsedMs:performance.now()-start,end:probe.jeep(),samples});
}}
return {scope:'Continuous ground entrance to roof through both interlevel turns',passed:results.every(r=>r.reached),results};
