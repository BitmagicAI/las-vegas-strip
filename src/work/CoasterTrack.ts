import * as THREE from 'three';
export interface CoasterPoint {s:number;position:number[];right:number[];up:number[];lift:boolean}
export interface CoasterRoute {points:CoasterPoint[];length:number;station:number[];exit:number[];entrance:number[];published:{height:number;drop:number;length:number;speed:number};provenance:string}
export class CoasterTrack {
 private pos=new THREE.Vector3();private right=new THREE.Vector3();private up=new THREE.Vector3();private forward=new THREE.Vector3();private matrix=new THREE.Matrix4();
 constructor(readonly route:CoasterRoute){}
 sample(distance:number,position:THREE.Vector3,orientation:THREE.Quaternion):boolean{
  const r=this.route;const s=((distance%r.length)+r.length)%r.length;
  let lo=0,hi=r.points.length-1;while(hi-lo>1){const mid=(lo+hi)>>1;if(r.points[mid]!.s<=s)lo=mid;else hi=mid;}
  const a=r.points[lo]!,b=r.points[hi]!,t=(s-a.s)/Math.max(.00001,b.s-a.s);
  position.fromArray(a.position).lerp(this.pos.fromArray(b.position),t);
  this.right.fromArray(a.right).lerp(this.pos.fromArray(b.right),t).normalize();
  this.up.fromArray(a.up).lerp(this.pos.fromArray(b.up),t).normalize();
  this.forward.crossVectors(this.up,this.right).normalize();this.up.crossVectors(this.right,this.forward).normalize();
  // Train geometry faces local +Z; seat camera looks along that direction.
  this.right.negate();this.matrix.makeBasis(this.right,this.up,this.forward);orientation.setFromRotationMatrix(this.matrix);
  return a.lift;
 }
}
/** Deterministic ride clock. One circuit, gravity-based downhill speed, station braking. */
export class CoasterRun {
 distance=0;speed=0;elapsed=0;finished=false;private dispatch=4;
 private position=new THREE.Vector3();private orientation=new THREE.Quaternion();
 private liftEnd:number;
 constructor(private track:CoasterTrack){this.liftEnd=Math.max(...track.route.points.filter(p=>p.lift).map(p=>p.s),0);}
 advance(dt:number):void{
  let remaining=Math.min(.25,Math.max(0,dt));
  while(remaining>0&&!this.finished){const step=Math.min(remaining,1/120);remaining-=step;this.elapsed+=step;
   if(this.dispatch>0){this.dispatch-=step;continue;}
   const lift=this.track.sample(this.distance,this.position,this.orientation);const r=this.track.route;const left=r.length-this.distance;
   let target=lift?2.2:Math.min(r.published.speed,Math.sqrt(16+2*9.81*Math.max(0,r.published.height-this.position.y)));
   if(this.distance<this.liftEnd&&!lift)target=4;
   if(left<115)target=Math.min(target,Math.max(2.4,Math.sqrt(left*.55)));
   const accel=target>this.speed?6:10;this.speed+=Math.max(-accel*step,Math.min(accel*step,target-this.speed));
   this.distance+=this.speed*step;
   if(this.distance>=r.length){this.distance=r.length;this.speed=0;this.finished=true;}
  }
 }
}
