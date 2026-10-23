import assert from 'node:assert/strict';
import * as THREE from 'three';
import {Film} from '../src/work/film/Film.ts';
Object.defineProperty(globalThis,'navigator',{value:{getGamepads:()=>[]},configurable:true});
globalThis.window={dispatchEvent:()=>{}};
const camera=new THREE.PerspectiveCamera(60,16/9,.1,1000);
const car={x:0,y:0,z:0,fx:0,fz:1};
const film=new Film({engine:{camera},jeep:()=>car,position:()=>car,rayDistance:(_x,_y,_z,_dx,_dy,_dz,len)=>len});
film.take={seconds:10,subframes:1,scenario:{preset:{weather:'storm'}},camera:[{from:0,to:10,anchor:'drone',focus:'camera',keys:[{t:0,pos:[3,2,-9],look:[0,1,1],fov:62},{t:10,pos:[3,2,-9],look:[0,1,1],fov:62}]}]};
film.armed=true;film.frame=1;film.t=1/60;film.applyCamera();
const pose=camera.position.clone(),rotation=camera.quaternion.clone();
car.z=2;
for(let i=0;i<100;i++){camera.position.set(99,99,99);camera.rotation.set(.5,.6,.7);camera.fov=35;film.applyCamera();assert.ok(camera.position.equals(pose));assert.ok(camera.quaternion.equals(rotation));assert.equal(camera.fov,62);}
assert.equal(film.poses().length,6,'held frames must not add camera samples');
film.frame++;film.t+=1/60;film.applyCamera();
assert.ok(camera.position.distanceTo(pose)>0,'camera must advance on the next simulation tick');
assert.equal(film.poses().length,12);
console.log('PASS: 100 held redraws preserve exact camera pose and one sample; the next simulation tick resumes the spring.');
