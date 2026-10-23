// AI editor note: the sidescroller template subclasses this controller via
// `SidescrollerPlayerController` (in templates/sidescroller/source/) to add
// X-axis-only input + disable Rapier gravity. Renaming exports here, changing
// the constructor signature, or making `calculateMoveDirection` (inherited
// from engine PlayerController) less accessible can break that subclass.
// pnpm run check does NOT type-check templates — drift lands silently.
// See ../../../../templates/README.md for the contract.
import * as THREE from 'three';
import { PlayerController, type CameraController } from 'engine/PlayerController.js';
import type { EngineLike, CameraControllerLike } from 'types/game.js';
import type { WorldGenerator } from './WorldGenerator.js';
import { TerrainTypeRegistry } from 'engine/TerrainTypes.js';
import type { GameConstants } from 'engine/Constants.js';
import type RAPIER from '@dimforge/rapier3d-compat';
import type { PhysicsWorld } from 'engine/physics/PhysicsWorld.js';

export class VoxelPlayerController extends PlayerController {
    private terrainRegistry: TerrainTypeRegistry;
    private damageAccumulator: number = 0;

    constructor(
        player: THREE.Object3D,
        playerBody: RAPIER.RigidBody,
        physicsWorld: PhysicsWorld,
        cameraController: CameraController,
        engine: EngineLike | null = null,
        physicsConfig: {
            gravity: number;
            terminalVelocity: number;
            jumpHeight: number;
            airControlMultiplier: number;
            groundFriction: number;
            airFriction: number;
        } = {
            gravity: -48.0,
            terminalVelocity: 53.0,
            jumpHeight: 2.5,
            airControlMultiplier: 0.5,
            groundFriction: 0.9,
            airFriction: 0.98
        },
        worldGenerator: WorldGenerator | null = null,
        movementSystem?: any,
        constants?: Partial<GameConstants>
    ) {
        super(player, playerBody, physicsWorld, cameraController, engine, physicsConfig, worldGenerator, movementSystem, constants);

        this.terrainRegistry = new TerrainTypeRegistry();

        // Combat is disabled by default
        // To enable combat, initialize an attack system (e.g., ProjectileShootSystem) and call setAttackSystem()

        // Disable ThirdPersonCamera's built-in touch controls when using MobileControls
        const cameraLike = cameraController as CameraControllerLike;
        if (this.mobileControls.isEnabled() && cameraLike.disableBuiltInTouchControls !== undefined) {
            cameraLike.disableBuiltInTouchControls = true;
        }
    }

    override update(deltaTime: number): void {
        if (!this.playerBody) return;

        // Apply terrain-based effects (genre-specific pre-processing)
        if (!this.isPlayerInVehicle() && this.isGrounded) {
            this.applyTerrainEffects(deltaTime);
        }

        // Base class handles mobile + desktop input via applyMobileInput()
        super.update(deltaTime);
    }

    private applyTerrainEffects(deltaTime: number): void {
        const worldGen = this.getWorldGenerator() as WorldGenerator | null;
        if (!worldGen) return;

        const playerPos = this.player.position;
        const terrainType = worldGen.getTerrainTypeAt(playerPos.x, playerPos.z);
        const terrainProps = this.terrainRegistry.getType(terrainType);

        if (!terrainProps) return;

        // Note: Terrain friction is now handled automatically by the base PlayerController
        // if the WorldGenerator implements getTerrainFriction()

        // Apply damage from terrain (e.g., lava)
        if (terrainProps.damagePerSecond !== undefined && terrainProps.damagePerSecond > 0) {
            this.damageAccumulator += terrainProps.damagePerSecond * deltaTime;

            if (this.damageAccumulator >= 1.0) {
                const damage = Math.floor(this.damageAccumulator);
                this.damageAccumulator -= damage;

                console.warn(`Player taking ${damage} damage from ${terrainProps.name} terrain!`);

                // TODO: Integrate with health system when available
                // if (this.healthSystem) {
                //     this.healthSystem.takeDamage(damage);
                // }
            }
        } else {
            this.damageAccumulator = 0;
        }
    }

    override onInteract(): boolean {
        const handled = super.onInteract();
        if (handled) return true;

        // No interactable nearby, do custom voxel interaction
        console.log('Voxel: Interact button pressed - exploring the world!');
        return false;
    }
}
