import * as THREE from 'three';
import {CollisionGroup} from 'engine/physics/CollisionLayers.js';
import type {PhysicsWorld} from 'engine/physics/PhysicsWorld.js';

/** The stock camera accepts only fixed bodies; doors are kinematic. Run a
 * final obstruction check AFTER its shoulder offset, accepting both kinds. */
export class CameraObstruction {
    private origin=new THREE.Vector3();
    private direction=new THREE.Vector3();
    private end=new THREE.Vector3();
    private right=new THREE.Vector3();
    private up=new THREE.Vector3();
    private result={hasHit:false,hitPoint:new THREE.Vector3(),hitNormal:new THREE.Vector3(),hitDistance:0,hitCollider:null,hitRigidBody:null};
    update(camera:THREE.Camera,feet:THREE.Vector3,world:PhysicsWorld):void {
        this.origin.copy(feet);this.origin.y+=1.65;
        this.right.setFromMatrixColumn(camera.matrixWorld,0).multiplyScalar(.12);
        this.up.setFromMatrixColumn(camera.matrixWorld,1).multiplyScalar(.12);
        let fraction=1;
        for(const [x,y] of [[0,0],[-1,-1],[-1,1],[1,-1],[1,1]]){
            this.end.copy(camera.position).addScaledVector(this.right,x!).addScaledVector(this.up,y!);
            this.direction.subVectors(this.end,this.origin);
            const length=this.direction.length();if(length<.05)continue;
            this.direction.divideScalar(length);
            const hit=world.raycast(this.origin,this.direction,length,CollisionGroup.TERRAIN|CollisionGroup.ENVIRONMENT,this.result);
            if(hit.hasHit)fraction=Math.min(fraction,Math.max(0,hit.hitDistance-.28)/length);
        }
        if(fraction<1)camera.position.lerpVectors(this.origin,camera.position,fraction);
        camera.updateMatrixWorld();
    }
}
