const frame=()=>new Promise(r=>requestAnimationFrame(r));
const press=on=>document.dispatchEvent(new KeyboardEvent(on?'keydown':'keyup',{code:'KeyW',key:'w',bubbles:true,cancelable:true}));
const results=[];
for(const [name,a,b] of [['north',[2001,.21,1174.2],[2010,.21,1174.2]]]){
 probe.teleport(a[0],a[1]+.1,a[2]);for(let i=0;i<240;i++)await frame();
 try{for(const goal of [b,a]){
  let reached=false;const start=performance.now();
  while(performance.now()-start<14000){const p=probe.position(),dx=goal[0]-p.x,dz=goal[2]-p.z;if(Math.hypot(dx,dz)<.5){reached=true;break;}probe.look(Math.atan2(-dx,-dz),0);press(true);await frame();}
  press(false);results.push({name,reached,position:probe.position()});if(!reached)break;
 }}finally{press(false);}
 await __shot('walk-'+name);
}return {results,passed:results.length===2&&results.every(r=>r.reached)};
