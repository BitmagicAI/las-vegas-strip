const frame=()=>new Promise(r=>requestAnimationFrame(r));const results=[];
for(const view of ['entrance','aisle','counter','coolers']){
 const placed=probe.landmark('favorita-market',view);if(!placed)throw Error('La Favorita Market is not registered');
 for(let i=0;i<360;i++)await frame();
 await __shot('favorita-market-'+view);
 const times=[];let last=performance.now();for(let i=0;i<180;i++){await frame();const now=performance.now();times.push(now-last);last=now;}times.sort((a,b)=>a-b);
 results.push({view,position:probe.position(),resident:probe.resident(),p50:times[90],p95:times[171]});
}
return results;
