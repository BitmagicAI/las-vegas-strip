// Pack scoped source colliders after optimized GLB installation; no shared city bake.
import fs from 'node:fs';import crypto from 'node:crypto';
import {encodeCollision} from '../optimize/pack-data.mjs';
const base='build/strip-landmarks/',hash=crypto.createHash('sha256');
for(const key of ['goldCoastExterior','wyndhamDesertBlue']){
 const c=JSON.parse(fs.readFileSync(base+key+'-exterior-collision.json'));
 fs.writeFileSync(base+key+'-exterior-collision.bin',await encodeCollision([c]));
 hash.update(fs.readFileSync(base+key+'-exterior.glb'));
 console.log(key,c.indices.length/3,'collision triangles');
}
fs.writeFileSync(base+'version.json',JSON.stringify({revision:hash.digest('hex').slice(0,16)}));
