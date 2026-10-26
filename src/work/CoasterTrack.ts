import * as THREE from 'three';
/** The track's samples as columns (route.bin, PackedRecords.ts): arc length, then x, y, z per sample. */
export interface CoasterPoints {length:number;s:Float32Array;position:Float32Array;right:Float32Array;up:Float32Array;lift:Uint8Array}
export interface CoasterRoute {points:CoasterPoints;length:number;station:Float32Array;exit:Float32Array;entrance:Float32Array;published:{height:number;drop:number;length:number;speed:number}}
export class CoasterTrack {
 private pos=new THREE.Vector3();private right=new THREE.Vector3();private up=new THREE.Vector3();private forward=new THREE.Vector3();private matrix=new THREE.Matrix4();
 constructor(readonly route:CoasterRoute){}
 sample(distance:number,position:THREE.Vector3,orientation:THREE.Quaternion):boolean{
  const r=this.route;const s=((distance%r.length)+r.length)%r.length;
  const p=r.points;let lo=0,hi=p.length-1;while(hi-lo>1){const mid=(lo+hi)>>1;if(p.s[mid]!<=s)lo=mid;else hi=mid;}
  const t=(s-p.s[lo]!)/Math.max(.00001,p.s[hi]!-p.s[lo]!);
  position.fromArray(p.position,lo*3).lerp(this.pos.fromArray(p.position,hi*3),t);
  this.right.fromArray(p.right,lo*3).lerp(this.pos.fromArray(p.right,hi*3),t).normalize();
  this.up.fromArray(p.up,lo*3).lerp(this.pos.fromArray(p.up,hi*3),t).normalize();
  this.forward.crossVectors(this.up,this.right).normalize();this.up.crossVectors(this.right,this.forward).normalize();
  // Train geometry faces local +Z; seat camera looks along that direction.
  this.right.negate();this.matrix.makeBasis(this.right,this.up,this.forward);orientation.setFromRotationMatrix(this.matrix);
  return p.lift[lo]===1;
 }
}
/** Deterministic ride clock. One circuit, gravity-based downhill speed, station braking. */
export class CoasterRun {
 distance=0;speed=0;elapsed=0;finished=false;private dispatch=4;
 private position=new THREE.Vector3();private orientation=new THREE.Quaternion();
 private liftEnd:number;
 constructor(private track:CoasterTrack){const p=track.route.points;let end=0;for(let i=0;i<p.length;i++)if(p.lift[i])end=Math.max(end,p.s[i]!);this.liftEnd=end;}
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
