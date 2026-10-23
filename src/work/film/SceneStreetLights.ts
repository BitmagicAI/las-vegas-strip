import * as THREE from 'three';

// Cinematic street-spill sites along the existing Harmon/Strip kerbs and arrival walk.
// Heights and intensities are lighting estimates; this adds no poles or level geometry.
const SITES=new Float32Array([
 410,8,863, 350,8,863, 290,8,863, 230,8,863, 170,8,863, 110,8,858,
 38,8,794, -24,8,770, 38,8,734, -24,8,710, 38,8,674, -24,8,650,
 38,8,614, -24,8,590, 38,8,554, -24,8,535,
 -60,6,514, -107,6,483, -151,6,459, -164,6,427, -195,6,430,
]);
/** Boot-allocated pool; fixed source positions with distance-faded spill. */
export class SceneStreetLights {
 private slots:Int16Array;private scores:Float32Array;
 constructor(private pool:readonly THREE.PointLight[]){this.slots=new Int16Array(pool.length).fill(-1);this.scores=new Float32Array(pool.length);}
 update(focus:THREE.Vector3,power:number):void{
  for(let i=0;i<this.slots.length;i++){const site=this.slots[i]!;this.scores[i]=site<0?0:this.score(site,focus);}
  for(let site=0;site<SITES.length/3;site++){
   let used=false;for(let i=0;i<this.slots.length;i++)if(this.slots[i]===site){used=true;break;}if(used)continue;
   const score=this.score(site,focus);let weak=0;
   for(let i=1;i<this.slots.length;i++)if(this.scores[i]!<this.scores[weak]!)weak=i;
   if(score>this.scores[weak]!){this.slots[weak]=site;this.scores[weak]=score;}
  }
  for(let i=0;i<this.pool.length;i++){
   const light=this.pool[i]!,site=this.slots[i]!;if(site<0){light.intensity=0;continue;}
   const j=site*3;light.position.set(SITES[j]!,SITES[j+1]!,SITES[j+2]!);
   const d=light.position.distanceTo(focus),fade=THREE.MathUtils.smoothstep(90-d,0,30);
   light.color.setHex(site%3===0?0xd0e0ff:0xffd7a1);light.intensity=850*power*fade;light.distance=48;light.decay=2;
  }
 }
 private score(site:number,p:THREE.Vector3):number{const j=site*3,dx=SITES[j]!-p.x,dz=SITES[j+2]!-p.z,d2=dx*dx+dz*dz;return d2>90*90?0:1/Math.max(1,d2);}
}
