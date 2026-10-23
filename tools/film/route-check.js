// probe-eval script (with --storage 'afterlight:film=1'): clear a film drive route of posts and curbs. ROUTE = [[x,z,speed],...].
// Walks the route (the player is moved along so the city's colliders stream in), casts rays along the route at bumper height
// across the jeep's width, finds for each point the smallest sideways shift (up to 3 m) that clears it, smooths the shifts
// over +-15 m and returns the corrected route plus the blocked spots.
const ROUTE=__ROUTE__;
const wait=ms=>new Promise(r=>setTimeout(r,ms));const pw=engine.physicsWorld;const V=engine.camera.position.constructor;
const idle=async()=>{for(let i=0;i<120&&probe.streaming().busy;i++)await wait(250);await wait(800);};
const n=ROUTE.length,shift=new Float64Array(n),blocked=[];
const dirAt=i=>{const a=ROUTE[Math.max(0,i-1)],b=ROUTE[Math.min(n-1,i+1)];const dx=b[0]-a[0],dz=b[1]-a[1],l=Math.hypot(dx,dz)||1;return [dx/l,dz/l];};
const ground=(x,z)=>{const r=pw.raycast(new V(x,30,z),new V(0,-1,0),60,(1<<0)|(1<<1)|(1<<2)|(1<<3));return r.hasHit?r.hitPoint.y:0;};
const clear=(x,z,dx,dz,nx,nz,s)=>{for(const o of [-1.9,-1.25,-.6,0,.6,1.25,1.9]){const px=x+nx*(s+o),pz=z+nz*(s+o),gy=ground(px,pz);
  for(const h of [.45,.9]){const r=pw.raycast(new V(px-dx*1.5,gy+h,pz-dz*1.5),new V(dx,0,dz),4.5);if(r.hasHit&&Math.abs(r.hitNormal.y)<.6)return false;}}return true;};
let lastTeleport=-1e9;
for(let i=0;i<n;i++){
  const [x,z]=ROUTE[i];
  if(Math.hypot(x-(ROUTE[Math.max(0,lastTeleport)]?.[0]??1e9),z-(ROUTE[Math.max(0,lastTeleport)]?.[1]??1e9))>120||lastTeleport<0){probe.teleport(x,ground(x,z)+1,z);await idle();lastTeleport=i;}
  const [dx,dz]=dirAt(i),nx=-dz,nz=dx;
  if(clear(x,z,dx,dz,nx,nz,0))continue;
  let found=null;for(const s of [.5,-.5,1,-1,1.5,-1.5,2,-2,2.5,-2.5,3,-3,3.5,-3.5]){if(clear(x,z,dx,dz,nx,nz,s)){found=s;break;}}
  shift[i]=found??0;blocked.push([i,+x.toFixed(1),+z.toFixed(1),found]);
}
// spread each shift over +-15 m (5 samples of 3 m) with a smooth bump, keep the largest magnitude
const sm=new Float64Array(n);
for(let i=0;i<n;i++)if(shift[i]){for(let k=-5;k<=5;k++){const j=i+k;if(j<0||j>=n)continue;const w=.5+.5*Math.cos(Math.PI*k/6);const v=shift[i]*w;if(Math.abs(v)>Math.abs(sm[j]))sm[j]=v;}}
const out=ROUTE.map((p,i)=>{const [dx,dz]=dirAt(i);return [+(p[0]-dz*sm[i]).toFixed(2),+(p[1]+dx*sm[i]).toFixed(2),p[2]];});
return {blocked,route:out};
