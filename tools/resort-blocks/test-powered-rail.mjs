import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';await R.init();
const path=process.argv[2]??'build/resort-blocks/bellagio/bellagioBlock-exterior-runtime-collision.json';const c=JSON.parse(fs.readFileSync(path));
const results=[];
for(const angle of [12,25]){
 const w=new R.World({x:0,y:-9.81,z:0});w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices),144));
 const yaw=Math.PI/2-angle*Math.PI/180;
 const body=w.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(-357,10.94,575.25).setRotation({x:0,y:Math.sin(yaw/2),z:0,w:Math.cos(yaw/2)}).setCcdEnabled(true));
 const surface=d=>d.setFriction(.03).setFrictionCombineRule(R.CoefficientCombineRule.Min).setRestitution(0);
 w.createCollider(surface(R.ColliderDesc.cuboid(.82,.075,1.975).setMass(1950)),body);
 for(const [x,y,z,hx,hy,hz] of [[0,.628,-.32,.729,.6665,1.075],[0,.335,1.2,.7045,.2795,.725],[0,.04,2.12,.8585,.1075,.125]])w.createCollider(surface(R.ColliderDesc.cuboid(hx,hy,hz).setTranslation(x,y,z).setMass(50)),body);
 const v=w.createVehicleController(body);v.indexUpAxis=1;v.setIndexForwardAxis=2;
 for(const x of [-.82,.82])for(const z of [-1.5,1.5]){
  const i=v.numWheels();v.addWheel({x,y:0,z},{x:0,y:-1,z:0},{x:-1,y:0,z:0},.20,.384);
  v.setWheelSuspensionStiffness(i,90);v.setWheelSuspensionCompression(i,3.2);v.setWheelSuspensionRelaxation(i,4);v.setWheelMaxSuspensionTravel(i,.1);v.setWheelMaxSuspensionForce(i,10500);v.setWheelFrictionSlip(i,4.8);
 }
 const grade=x=>{const knots=[[-357,10.335],[-349,10.335],[-313,6.935],[-305,6.935],[-297,6.935],[-266,3.535],[-258,3.535],[-250,3.535],[-222,.135],[-210,.135]];for(let i=1;i<knots.length;i++){const [a,ya]=knots[i-1],[b,yb]=knots[i];if(x<=b){const t=Math.max(0,Math.min(1,(x-a)/(b-a)));return ya+(yb-ya)*t*t*(3-2*t);}}return .135;};
 let minY=Infinity,maxZ=-Infinity,minClearance=Infinity,lateX=0;
 for(let f=0;f<600;f++){
  for(let i=0;i<4;i++)v.setWheelEngineForce(i,f<60?0:2750);
  v.updateVehicle(1/60,undefined,undefined,col=>col.parent()?.handle!==body.handle);w.step();
  const p=body.translation();if(f===480)lateX=p.x;minY=Math.min(minY,p.y);maxZ=Math.max(maxZ,p.z);minClearance=Math.min(minClearance,p.y-grade(p.x));
 }
 results.push({angle,position:body.translation(),velocity:body.linvel(),minY,maxZ,minClearance,lateAdvance:body.translation().x-lateX});w.free();
}
console.log(JSON.stringify(results,null,2));
if(!process.argv[2]){
 for(const r of results){assert.ok(r.lateAdvance>1,'Sustained shallow contact must retain forward drive');assert.ok(r.position.x>-354,'Must advance along rail');assert.ok(r.maxZ<577,'Powered car crossed barrier');assert.ok(r.minClearance>.15,'Powered car sank through ramp');}
 fs.writeFileSync('build/resort-blocks/bellagio/powered-rail-audit.json',JSON.stringify(results,null,2));
}
