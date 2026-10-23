// Controller settings match engine/engine/physics/PhysicsWorld.ts.
// Match PhysicsBodyFactory: FIX_INTERNAL_EDGES (144) for trimeshes.
import fs from 'node:fs';import R from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));await R.init();const world=new R.World({x:0,y:-9.81,z:0});
const owners=new Map();for(const [ci,c] of [...read('build/geographic-strip/city-colliders.json'),...read('src/work/geographic/level.json').colliders,read('build/resort-blocks/bellagio/bellagioBlock-exterior-runtime-collision.json')].entries())if(c.vertices?.length&&c.indices?.length){const hit=world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices),144));owners.set(hit.handle,c.name??`collision ${ci}`);}
world.step();for(const x of [155,165,170,180,190,205,215,220])for(const z of [195,207,220]){const h=world.castRay(new R.Ray({x,y:12,z},{x:0,y:-1,z:0}),15,true);console.log(x,z,h?12-h.timeOfImpact:null)}world.free();