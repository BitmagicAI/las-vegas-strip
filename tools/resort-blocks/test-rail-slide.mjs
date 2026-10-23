import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';
await R.init();
const root='build/resort-blocks/bellagio/';const c=JSON.parse(fs.readFileSync(root+'bellagioBlock-exterior-runtime-collision.json'));
const w=new R.World({x:0,y:0,z:0});w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices),144));
// Jeep-sized chassis, 14-degree glancing approach along the actual access guard.
const start={x:-356,y:10.95,z:575.8};
const b=w.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(start.x,start.y,start.z).setRotation({x:0,y:Math.sin(Math.PI/4),z:0,w:Math.cos(Math.PI/4)}).setCcdEnabled(true));
w.createCollider(R.ColliderDesc.cuboid(.82,.3,1.975).setMass(2100).setFriction(.03).setFrictionCombineRule(R.CoefficientCombineRule.Min).setRestitution(0),b);
b.setLinvel({x:6,y:0,z:1.5},true);
for(let i=0;i<90;i++)w.step();
const p=b.translation(),v=b.linvel();
const result={advanceM:p.x-start.x,alongRailSpeed:v.x,lateralPosition:p.z};
assert.ok(result.advanceM>6,'Glancing contact should retain forward progress');assert.ok(v.x>3,'Glancing contact must not dead-stop');assert.ok(p.z<577,'Guard must retain vehicle');
fs.writeFileSync(root+'rail-slide-audit.json',JSON.stringify(result,null,2));console.log(result);
