// Pack scoped source colliders after optimized GLB installation; no shared city bake.
import fs from 'node:fs';import crypto from 'node:crypto';
import {encodeCollision,encodeRecords} from '../optimize/pack-data.mjs';
const base='build/strip-landmarks/',hash=crypto.createHash('sha256');
for(const key of ['santaPaulaCourtyard','stLouisSquareFrontage']){
 const c=JSON.parse(fs.readFileSync(base+key+'-exterior-collision.json'));
 fs.writeFileSync(base+key+'-exterior-collision.bin',await encodeCollision([c]));
 hash.update(fs.readFileSync(base+key+'-exterior.glb'));
 console.log(key,c.indices.length/3,'collision triangles');
}
fs.writeFileSync(base+'version.json',JSON.stringify({revision:hash.digest('hex').slice(0,16)}));

// Preserve existing venue metadata; pack it once with this group.
const venues=JSON.parse(fs.readFileSync(base+'venues.json'));
venues.find(v=>v.key==='santaPaulaCourtyard').bounds=[1909,-3841,1983,-3772];
fs.writeFileSync(base+'venues.json',JSON.stringify(venues));
fs.writeFileSync(base+'venues.bin',encodeRecords(venues));
