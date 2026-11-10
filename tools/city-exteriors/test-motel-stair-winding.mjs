// A two-sided Rapier walk can pass a ramp that the runtime ground index rejects.
// Require upward normals on the two Nirvana stair-ramp triangles as well.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const c=JSON.parse(fs.readFileSync('build/strip-landmarks/nirvanaAncillary-exterior-collision.json'));
let count=0;
for(let i=0;i<c.indices.length;i+=3){
 const points=c.indices.slice(i,i+3).map(j=>c.vertices.slice(j*3,j*3+3));
 if(!points.every(([x,y,z])=>x>=104.99&&x<=106.31&&z>=2711.34&&z<=2717.21))continue;
 const ys=points.map(p=>p[1]);if(Math.max(...ys)-Math.min(...ys)<2.8)continue;
 const [a,b,d]=points,ab=b.map((v,k)=>v-a[k]),ac=d.map((v,k)=>v-a[k]);
 const cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]];
 assert.ok(cross[1]/Math.hypot(...cross)>.65,'Nirvana ramp must satisfy runtime standable-normal threshold');count++;
}
assert.equal(count,2,'Expected both triangles of the unchanged 1.3 m wide stair ramp');
console.log('Nirvana: two upward standable ramp triangles passed');
