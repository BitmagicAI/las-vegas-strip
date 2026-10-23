import * as THREE from 'three';
import {glbUrl} from './OptimizedGlb.js';
import {DrivingSpeedAssist, assistedAcceleration, type DriveRoad} from './DrivingSpeedAssist.js';
import {mapPoint} from './geographic/Coordinates.js';
import { CollisionGroup } from 'engine/CollisionLayers.js';
import { vehicleExitCandidates } from './VehicleExit.js';
import type RAPIER from '@dimforge/rapier3d-compat';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import type { EngineLike } from 'types/game.js';
import { createGltfLoader } from 'engine/loaders/GltfLoaderSupport.js';
import { Vehicle, VehicleAutoRightSystem, DEFAULT_VEHICLE_AUTO_RIGHT_OPTIONS } from 'engine/Vehicle.js';
import { VehicleCamera } from 'engine/VehicleCamera.js';
import type { VehicleRenderer } from 'engine/VehicleRenderer.js';
import type { VehicleSpawner } from 'engine/VehicleSpawner.js';
import type { VehicleManager } from 'engine/VehicleManager.js';
import type { PlayerController } from 'engine/PlayerController.js';
import { PhysicsBodyFactory } from 'engine/physics/PhysicsBodyFactory.js';
import type { GameHUD } from './GameHUD.js';

const BAY = new THREE.Vector3(...mapPoint([-40,.51,2],'sanctuary'));
// Aim above the low chase point: keep the jeep in the lower part of the view
// and reserve the upper frame for the Strip skyline.
const DRIVING_CAMERA = { distance: 6.7, height: 1.65, lookAtHeight: 2.15 };

/** Combine only static parts with matching materials/attributes. The four wheels
 * remain independent, driven by the engine's actual suspension and axle poses. */
function batchPart(source: THREE.Object3D): THREE.Group {
    source.updateWorldMatrix(true, true);
    const inverse = source.matrixWorld.clone().invert();
    const batches = new Map<string, { material: THREE.Material; geometries: THREE.BufferGeometry[] }>();
    source.traverse(object => {
        if (!(object instanceof THREE.Mesh) || Array.isArray(object.material)) return;
        const geometry = object.geometry.index ? object.geometry.toNonIndexed() : object.geometry.clone();
        // Optimized GLBs store some attributes quantized (8-bit normals, 16-bit UVs) and padded
        // (interleaved): unpack those into plain attributes of the same type, and only merge
        // parts whose attribute types agree, so compact formats stay compact.
        for (const [name, attribute] of Object.entries(geometry.attributes)) {
            if (!(attribute as THREE.InterleavedBufferAttribute).isInterleavedBufferAttribute) continue;
            const a = attribute as THREE.InterleavedBufferAttribute, Ctor = a.array.constructor as new (n: number) => THREE.TypedArray, out = new Ctor(a.count * a.itemSize);
            for (let i = 0; i < a.count; i++) for (let c = 0; c < a.itemSize; c++) out[i * a.itemSize + c] = a.data.array[i * a.data.stride + a.offset + c]!;
            geometry.setAttribute(name, new THREE.BufferAttribute(out, a.itemSize, a.normalized));
        }
        geometry.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inverse, object.matrixWorld));
        const key = object.material.uuid + Object.entries(geometry.attributes).sort(([a], [b]) => a < b ? -1 : 1).map(([n, a]) => { const b = a as THREE.BufferAttribute; return `${n}:${b.array.constructor.name}:${b.itemSize}:${b.normalized}`; }).join(',');
        if (!batches.has(key)) batches.set(key, { material: object.material, geometries: [] });
        batches.get(key)!.geometries.push(geometry);
    });
    const group = new THREE.Group(); group.name = source.name;
    for (const { material, geometries } of batches.values()) {
        const merged = mergeGeometries(geometries);
        if (!merged) throw new Error(`Could not batch jeep component ${source.name}`);
        const mesh = new THREE.Mesh(merged, material);
        mesh.castShadow = !material.transparent; mesh.receiveShadow = true;
        group.add(mesh); geometries.forEach(g => g.dispose());
    }
    return group;
}

export class SanctuaryJeep {
    private vehicle: Vehicle | null = null;
    private heldBodyEnabled:boolean|null=null;
    setStreamingHeld(held:boolean):void {
        const body=this.vehicle?.getChassisBody();if(!body?.isValid())return;
        if(held&&this.heldBodyEnabled===null){this.heldBodyEnabled=body.isEnabled();body.setEnabled(false);}
        else if(!held&&this.heldBodyEnabled!==null){body.setEnabled(this.heldBodyEnabled);this.heldBodyEnabled=null;}
    }
    private readonly wheelMeshes: THREE.Mesh[] = [];
    private readonly autoRight = new VehicleAutoRightSystem(DEFAULT_VEHICLE_AUTO_RIGHT_OPTIONS);
    private speedAssist = new DrivingSpeedAssist([]);
    private assistTimer = 0;
    private speedTarget = 10;
    private pendingTarget = 10;
    private pendingTime = 0;
    private grounded = false;
    private wasDriving = false;
    private walkingFov: number | null = null;
    private lastHud = '';
    /** Body and wheels: what NearbyLights lights (see Game). */
    lightRoots: THREE.Object3D[] = [];
    private ownedGeometry = new Set<THREE.BufferGeometry>();
    private ownedMaterial = new Set<THREE.Material>();

    constructor(private engine: EngineLike, private manager: VehicleManager,
        private spawner: VehicleSpawner, private controller: PlayerController, private hud: GameHUD,
        private capsule: { height: number; radius: number }, private restoreWalkingCamera: () => void) {}

    async load(): Promise<void> {
        const network = await fetch('/build/geographic-strip/road-network.json').then(r => { if(!r.ok) throw new Error('Road speed map unavailable'); return r.json(); });
        const arrival = await fetch('/build/resort-blocks/bellagio/south-arrival-report.json').then(r => { if(!r.ok) throw new Error('Arrival speed map unavailable'); return r.json(); });
        const replacements = new Map<number, DriveRoad>(arrival.roads.map((r: DriveRoad) => [r.id, {...r, highway: 'service'}]));
        this.speedAssist = new DrivingSpeedAssist(network.roads.map((r: DriveRoad) => replacements.get(r.id) ?? r));
        const loader = createGltfLoader();
        const gltf = await loader.loadAsync(await glbUrl('/build/vehicles/afterlight-jeep.glb?v=4'));
        const part = (name: string) => {
            const source = gltf.scene.getObjectByName(name);
            if (!source) throw new Error(`Jeep GLB is missing ${name}`);
            return batchPart(source);
        };
        const body = part('Body'), wheel = part('Wheel');
        const renderer: VehicleRenderer = {
            createChassisMesh: (_config, position) => { body.position.copy(position); return body; },
            createWheelMeshes: (_config, position, wheels) => (wheels ?? []).map(() => {
                // Keep a real mesh at the root: WebGPU still compiles empty wrapper meshes.
                const first = wheel.children[0];
                if (!(first instanceof THREE.Mesh)) throw new Error('Jeep wheel has no mesh');
                const mesh = first.clone();
                for (const child of wheel.children.slice(1)) mesh.add(child.clone(true));
                mesh.position.copy(position); this.wheelMeshes.push(mesh);
                return mesh;
            })
        };
        const axle = { radius: .384, width: .30, suspensionRestLength: .20,
            suspensionStiffness: 30, suspensionDamping: .4, friction: 120, isDriven: true };
        const result = this.spawner.spawnVehicle(BAY, { width: 1.64, length: 3.95, mass: 2100,
            engineForce: 11000, frontWheels: axle, rearWheels: axle,
            handling: { topSpeed: 24, reverseTopSpeed: 6, accelerationScale: 1,
                maxSteerAngle: 33, steerSpeed: 110, steerSpeedFalloff: .13,
                minSteerAtSpeed: .25, downforce: .35 } }, renderer, Math.PI / 2);
        if (!result) throw new Error('No sanctuary ground found for electric jeep');
        this.vehicle = result.vehicle;
        this.vehicle.setAlwaysActive(true);
        this.vehicle.addBodyPhysicsBatch([
            { position: new THREE.Vector3(0, .628, -.32), size: { width: 1.458, height: 1.333, length: 2.15 } },
            { position: new THREE.Vector3(0, .335, 1.2), size: { width: 1.409, height: .559, length: 1.45 } },
            { position: new THREE.Vector3(0, .04, 2.12), size: { width: 1.717, height: .215, length: .25 } }
        ]);
        // Wheel friction supplies tire grip; bodywork should slide along guards.
        const chassis = this.vehicle.getChassisBody();
        if(chassis)for(let i=0;i<chassis.numColliders();i++){
            const collider=chassis.collider(i);
            if(!collider.isSensor())collider.setFriction(.03);
        }
        this.autoRight.register(this.vehicle);
        this.controller.setVehicleCameraMode('chase');
        this.controller.configureVehicleCamera(DRIVING_CAMERA);
        this.hud.createIconText('electric-jeep', { anchor: 'bottom-right', icon: '', text: '' });
        this.lightRoots = [body, ...this.wheelMeshes];
        for (const root of [body, ...this.wheelMeshes]) root.traverse(object => {
            if (object instanceof THREE.Mesh) {
                this.ownedGeometry.add(object.geometry);
                for (const material of Array.isArray(object.material) ? object.material : [object.material]) this.ownedMaterial.add(material);
            }
        });
        gltf.scene.traverse(object => { if (object instanceof THREE.Mesh) object.geometry.dispose(); });
        console.log('[SanctuaryJeep] AL-01 ready at its bay; four-wheel electric drive / E enter-exit');
    }

    private configureDrivingView(): void {
        const chase = this.controller.getCameraController();
        if (!(chase instanceof VehicleCamera)) return;
        // Interactive E entry creates the camera through a separate engine path;
        // reapply the saved settings now that that actual chase camera exists.
        this.controller.configureVehicleCamera(DRIVING_CAMERA);
        // Release the engine's latched FOV before supplying the wider driving
        // baseline. Its speed/portrait framing then continues to work normally.
        chase.setEnabled(false);
        const camera = chase.getCamera();
        this.walkingFov = camera.fov;
        camera.fov += 12;
        camera.updateProjectionMatrix();
        chase.setEnabled(true);
    }

    private restoreWalkingFov(): void {
        if (this.walkingFov === null) return;
        const camera = this.engine.camera;
        if (camera instanceof THREE.PerspectiveCamera) { camera.fov = this.walkingFov; camera.updateProjectionMatrix(); }
        this.walkingFov = null;
    }

    private placeDriverBesideJeep(): void {
        const vehicle = this.vehicle!, physics = this.engine.physicsWorld!;
        const solid = CollisionGroup.TERRAIN | CollisionGroup.ENVIRONMENT | CollisionGroup.VEHICLE | CollisionGroup.DYNAMIC_PROP;
        const floorMask = CollisionGroup.TERRAIN | CollisionGroup.ENVIRONMENT;
        for (const point of vehicleExitCandidates(vehicle.getPosition(), vehicle.getForwardDirection(), this.capsule.radius)) {
            const floor = physics.raycast(new THREE.Vector3(point.x, point.y + 1, point.z), new THREE.Vector3(0, -1, 0), 4, floorMask);
            if (!floor.hasHit || floor.hitNormal.y < .7) continue;
            const feetY = floor.hitPoint.y + .025;
            // The query excludes the player's own capsule and includes the jeep,
            // cabinet, walls and props. Keep the whole standing capsule clear.
            const center = { x: point.x, y: feetY + this.capsule.height / 2, z: point.z };
            if (physics.capsuleOverlaps(center, this.capsule.radius + .04,
                Math.max(0, this.capsule.height / 2 - this.capsule.radius - .04), solid)) continue;
            this.controller.teleportTo(point.x, feetY, point.z);
            console.log('[SanctuaryJeep] Clear exit', JSON.stringify({ x: point.x, y: feetY, z: point.z }));
            return;
        }
        // An entirely boxed-in vehicle has no safe standing position. Stay seated.
        this.controller.enterVehicle(vehicle);
        console.warn('[SanctuaryJeep] Exit obstructed on all sides; staying in vehicle');
    }

    /** Local review probe and filming only (?probe, or localStorage 'afterlight:film' on localhost): put the jeep at (x,y,z)
     * facing `heading` (yaw, 0 = +Z) and seat the player in it. */
    seatForReview(x: number, y: number, z: number, heading: number): boolean {
        let filming = false;
        try { filming = ['localhost', '127.0.0.1'].includes(location.hostname) && localStorage.getItem('afterlight:film') === '1'; } catch { /* no storage */ }
        if (!this.vehicle || !(filming || new URLSearchParams(location.search).has('probe'))) return false;
        this.vehicle.teleportTo(new THREE.Vector3(x, y, z), heading);
        return this.controller.isPlayerInVehicle() || this.controller.enterVehicle(this.vehicle);
    }

    /** Explicit local review action; normal spawning and gameplay are unchanged. */
    placeForGarageReview(): void {
        if (!new URLSearchParams(location.search).has('resortReview') || this.controller.isPlayerInVehicle()) return;
        const body=this.vehicle?.getChassisBody(); if(!body)return;
        body.setTranslation({x:-258,y:4.6,z:571},true);
        body.setRotation({x:0,y:1,z:0,w:0},true);
        body.setLinvel({x:0,y:0,z:0},true);body.setAngvel({x:0,y:0,z:0},true);
        this.controller.teleportTo(-260,3.55,571);
    }

    update(dt: number, player: THREE.Vector3): void {
        if (!this.vehicle) return;
        this.autoRight.update(dt);
        const position = this.vehicle.getPosition();
        const speed = this.vehicle.getSpeed();
        let driving = this.controller.getActiveVehicle()===this.vehicle;
        if (driving !== this.wasDriving) {
            if (!driving) { this.restoreWalkingFov(); if(!this.controller.isPlayerInVehicle()){this.restoreWalkingCamera();this.placeDriverBesideJeep();} }
            if (driving) this.configureDrivingView();
            this.hud.setActionRowVisible('camera-view', !driving);
            if (driving) this.hud.hideElement('cast-status'); else this.hud.showElement('cast-status');
            this.wasDriving = driving;
        }
        this.assistTimer -= dt;
        if (this.assistTimer <= 0) {
            this.assistTimer = .1;
            const desired = this.speedAssist.targetAt(position.x, position.y, position.z);
            if(desired !== this.pendingTarget){this.pendingTarget=desired;this.pendingTime=0;}
            else this.pendingTime += .1;
            // Short release hysteresis avoids full throttle bursts at junction seams.
            if(desired < this.speedTarget || this.pendingTime >= .5) this.speedTarget=desired;
            const floor=this.engine.physicsWorld!.raycast(position, new THREE.Vector3(0,-1,0), .95,
                CollisionGroup.TERRAIN | CollisionGroup.ENVIRONMENT);
            this.grounded=floor.hasHit && floor.hitNormal.y>.7;
        }
        const chassis=this.vehicle.getChassisBody();
        if(!chassis)return;
        const velocity=chassis.linvel();
        const horizontal=Math.hypot(velocity.x,velocity.z);
        this.vehicle.setHandling({topSpeed:this.speedTarget, reverseTopSpeed:Math.min(4,this.speedTarget),
            accelerationScale:assistedAcceleration(horizontal,this.speedTarget,false)});
        // Gentle 2 m/s² assistance when entering a slower area; preserve vertical motion.
        // Do not affect jumps/falls, parked cars, or normal braking below the target.
        if(driving && this.grounded && horizontal>this.speedTarget && this.speedTarget<24){
            const factor=Math.max(this.speedTarget,horizontal-2*Math.min(dt,.05))/horizontal;
            chassis.setLinvel({x:velocity.x*factor,y:velocity.y,z:velocity.z*factor},true);
        }
        const distance = player.distanceTo(position);
        const near = distance < 6;
        const text = driving ? `AL-01  /  ${Math.round(speed * 3.6)} km/h  /  Assist ${Math.round(this.speedTarget*3.6)} km/h  •  WASD drive · Space brake · E exit`
            : near ? `${distance < 3 ? 'E / DRIVE' : 'APPROACH'} AL-01` : '';
        if (text !== this.lastHud) { this.lastHud = text; this.hud.updateIconText('electric-jeep', { text }); }
    }

    setRenderVisibility(test: (p: THREE.Vector3) => boolean): void {
        const camera=this.engine.camera!.position;
        if (this.vehicle) {
            const position=this.vehicle.getPosition();
            const visible = this.controller.isPlayerInVehicle() || camera.distanceToSquared(position)<250*250 && test(position);
            this.vehicle.getChassisGroup().visible = visible;
            this.wheelMeshes.forEach(mesh => mesh.visible = visible);
        }
    }

    dispose(): void {
        if (this.vehicle) { this.autoRight.unregister(this.vehicle); this.manager.removeVehicle(this.vehicle); this.vehicle = null; }
        this.restoreWalkingFov();
        this.ownedGeometry.forEach(g => g.dispose()); this.ownedMaterial.forEach(m => m.dispose());
    }
}
