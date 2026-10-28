const frame=()=>new Promise(r=>requestAnimationFrame(r));const results=[];
for(const view of ['entrance','dining','booths','bar']){
 const placed=probe.landmark('kung-fu-plaza',view);if(!placed)throw Error('Kung Fu is not registered');
 for(let i=0;i<360;i++)await frame();
 await __shot('kung-fu-plaza-'+view);
 const times=[];let last=performance.now();for(let i=0;i<180;i++){await frame();const now=performance.now();times.push(now-last);last=now;}times.sort((a,b)=>a-b);
 results.push({view,position:probe.position(),resident:probe.resident(),p50:times[90],p95:times[171]});
}
return results;
