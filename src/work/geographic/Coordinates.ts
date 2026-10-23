import anchors from './anchors.json';
export type District=keyof typeof anchors.transforms;
export function mapPoint(p:readonly number[],key:District):[number,number,number]{const t=anchors.transforms[key],[a,b,c,d]=t.linear;return [a!*p[0]!+b!*p[2]!+t.translation[0]!,p[1]!,c!*p[0]!+d!*p[2]!+t.translation[1]!];}
export function mapYaw(yaw:number,key:District):number {const [a,b,c,d]=anchors.transforms[key].linear,x=Math.sin(yaw),z=Math.cos(yaw);return Math.atan2(a!*x+b!*z,c!*x+d!*z);}
export function reviewDistrict(name:string):District {if(name.startsWith('jeep') || name==='shadows' || name==='bellagio-exterior')return 'sanctuary';if(name.includes('forum'))return 'caesars';if(name.startsWith('citycenter') || name==='veer-street-entry')return 'crystals';if(name.includes('miracle'))return 'planet-hollywood';return (Object.keys(anchors.transforms) as District[]).find(k=>name.startsWith(k))??'sanctuary';}
