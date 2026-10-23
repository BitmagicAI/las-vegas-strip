/**
 * Environment Object Factories for Voxel Genre
 *
 * AI AGENTS: This file contains customizable factories for environment objects!
 *
 * You can modify:
 * - Tree colors, dimensions, and shapes
 * - Rock colors, sizes, and shapes
 * - Add entirely new environment object types
 *
 * The EnvironmentObjectSystem in engine/ provides generic infrastructure,
 * while this file contains all the game-specific implementations.
 *
 * For Voxel genre, objects are created using VoxelObject for a consistent
 * blocky aesthetic that matches the terrain.
 *
 * AI editor note: no community template currently overrides this file — it
 * flows into every template's merged source from here. If a template ever
 * starts customizing it, the customization map in templates/README.md will
 * reflect that, and you'll need to update each overriding overlay when
 * changing factory signatures here.
 */

import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { SeededRandom } from 'engine/SeededRandom.js';
import { TerrainTypeRegistry } from 'engine/TerrainTypes.js';
import type { TerrainHeightProvider } from 'engine/TerrainTypeProvider.js';
import { VoxelObject } from 'engine/VoxelObject.js';
import { BlockType, type BlockTypeId, getVoxelTextureAtlas } from 'engine/VoxelTextureAtlas.js';
import { getRapier } from 'engine/physics/RapierPhysics.js';
import { CollisionGroup, CollisionMask, makeCollisionGroups } from 'engine/CollisionLayers.js';
import type { PhysicsWorld } from 'engine/physics/PhysicsWorld.js';
import { enableStructuralCollapse } from 'engine/VoxelStructuralCollapse.js';
import type RAPIER from '@dimforge/rapier3d-compat';

function getBlockIdByName(name: string): BlockTypeId {
    const atlas = getVoxelTextureAtlas();
    const id = atlas.getBlockTypeByName(name);
    if (id === undefined) {
        console.warn(`[EnvironmentObjects] Block type '${name}' not found, using NONE`);
        return BlockType.NONE;
    }
    return id as BlockTypeId;
}
import type {
    EnvironmentObjectSystem,
    EnvironmentObjectData,
    EnvironmentInstance
} from 'engine/EnvironmentObjectSystem.js';

// ============================================================================
// CONFIGURATION INTERFACES
// ============================================================================

/**
 * Configuration for tree generation.
 * AI AGENTS: Modify these defaults to change all trees!
 */
export interface TreeConfig {
    /** Size of each block in the tree (default: 1.0) */
    blockSize?: number;
    /** Minimum trunk height in blocks (default: 4) */
    minTrunkHeight?: number;
    /** Maximum trunk height in blocks (default: 6) */
    maxTrunkHeight?: number;
    /** Number of layers of leaves (default: 3) */
    leavesLayers?: number;
}

/**
 * Configuration for rock generation.
 * AI AGENTS: Modify these defaults to change all rocks!
 */
export interface RockConfig {
    /** Minimum width (default: 1) */
    minWidth?: number;
    /** Maximum width (default: 3) */
    maxWidth?: number;
    /** Minimum height (default: 0.5) */
    minHeight?: number;
    /** Maximum height (default: 1.5) */
    maxHeight?: number;
    /** Minimum depth (default: 1) */
    minDepth?: number;
    /** Maximum depth (default: 3) */
    maxDepth?: number;
}

// ============================================================================
// TREE FACTORY
// ============================================================================

/**
 * Create a simple block-based tree.
 *
 * AI AGENTS: Modify this function to change tree appearance!
 *
 * @param rng - Seeded random number generator
 * @param material - Material to use for the tree mesh
 * @param config - Optional configuration for tree dimensions
 *
 * Example - Taller trees:
 * ```typescript
 * createTree(rng, material, {
 *     minTrunkHeight: 8,  // Minimum 8 blocks tall
 *     maxTrunkHeight: 12, // Maximum 12 blocks tall
 *     leavesLayers: 4     // 4 layers of leaves
 * });
 * ```
 */
export function createTree(
    rng: SeededRandom,
    material: THREE.MeshStandardMaterial,
    config?: TreeConfig
): EnvironmentObjectData {
    const blockSize = config?.blockSize ?? 1.0;
    const minTrunkHeight = config?.minTrunkHeight ?? 4;
    const maxTrunkHeight = config?.maxTrunkHeight ?? 6;
    const leavesLayers = config?.leavesLayers ?? 3;

    interface TreeCube {
        position: THREE.Vector3;
        materialType: 'trunk' | 'leaves' | 'rock';
        size: number;
    }

    const cubes: TreeCube[] = [];
    const geometries: THREE.BufferGeometry[] = [];

    // Create trunk blocks (randomized height between min and max)
    const trunkHeightRange = maxTrunkHeight - minTrunkHeight + 1;
    const trunkHeight = minTrunkHeight + Math.floor(rng.next() * trunkHeightRange);

    for (let i = 0; i < trunkHeight; i++) {
        const y = i * blockSize + blockSize / 2;
        const cubePos = new THREE.Vector3(0, y, 0);

        const trunkGeometry = new THREE.BoxGeometry(blockSize, blockSize, blockSize);
        const matrix = new THREE.Matrix4();
        matrix.makeTranslation(0, y, 0);
        trunkGeometry.applyMatrix4(matrix);

        // Set UV coordinates to map to trunk pixel (row 0 in 1x4 texture)
        // V coordinate: pixel 0 (top) is at V=0.875 (center of pixel)
        const uvAttribute = trunkGeometry.attributes.uv;
        if (uvAttribute) {
            for (let j = 0; j < uvAttribute.count; j++) {
                uvAttribute.setXY(j, 0, 0.875);
            }
            uvAttribute.needsUpdate = true;
        }

        geometries.push(trunkGeometry);
        cubes.push({
            position: cubePos.clone(),
            materialType: 'trunk',
            size: blockSize
        });
    }

    // Create leaves blocks in a cross pattern around and above the trunk
    const leavesStartY = trunkHeight - 1;

    for (let y = 0; y < leavesLayers; y++) {
        const currentY = leavesStartY + y;
        let positions: [number, number, number][] = [];

        // Determine layer type based on position within leaves
        const isBottomLayer = y === 0;
        const isTopLayer = y === leavesLayers - 1;

        if (isTopLayer && leavesLayers > 1) {
            // Top layer: smaller cross
            positions = [
                [0, 0, -1], [0, 0, 1], [-1, 0, 0], [1, 0, 0]
            ];
        } else if (isBottomLayer) {
            // Bottom layer: cross pattern
            positions = [
                [0, 0, -1], [0, 0, 1], [-1, 0, 0], [1, 0, 0],
                [-1, 0, -1], [-1, 0, 1], [1, 0, -1], [1, 0, 1]
            ];
        } else {
            // Middle layers: larger cross
            positions = [
                [0, 0, -2], [0, 0, -1], [0, 0, 1], [0, 0, 2],
                [-2, 0, 0], [-1, 0, 0], [1, 0, 0], [2, 0, 0],
                [-1, 0, -1], [-1, 0, 1], [1, 0, -1], [1, 0, 1],
                [-2, 0, -1], [-2, 0, 1], [2, 0, -1], [2, 0, 1],
                [-1, 0, -2], [-1, 0, 2], [1, 0, -2], [1, 0, 2]
            ];
        }

        for (const [dx, , dz] of positions) {
            const leafY = currentY * blockSize + blockSize / 2;
            const cubePos = new THREE.Vector3(dx * blockSize, leafY, dz * blockSize);

            const leafGeometry = new THREE.BoxGeometry(blockSize, blockSize, blockSize);
            const leafMatrix = new THREE.Matrix4();
            leafMatrix.makeTranslation(dx * blockSize, leafY, dz * blockSize);
            leafGeometry.applyMatrix4(leafMatrix);

            // Set UV coordinates to map to leaves pixel (row 1 in 1x4 texture)
            // V coordinate: pixel 1 is at V=0.625 (center of pixel)
            const uvAttribute = leafGeometry.attributes.uv;
            if (uvAttribute) {
                for (let j = 0; j < uvAttribute.count; j++) {
                    uvAttribute.setXY(j, 0, 0.625);
                }
                uvAttribute.needsUpdate = true;
            }

            geometries.push(leafGeometry);
            cubes.push({
                position: cubePos.clone(),
                materialType: 'leaves',
                size: blockSize
            });
        }
    }

    // Merge all geometries into a single mesh
    const mergedGeometry = mergeGeometries(geometries);
    const mesh = new THREE.Mesh(mergedGeometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.name = 'Tree';

    return {
        cubes,
        mergedGeometry,
        mesh
    };
}

// ============================================================================
// ROCK FACTORY
// ============================================================================

/**
 * Create a simple box-based rock.
 *
 * AI AGENTS: Modify this function to change rock appearance!
 *
 * @param rng - Seeded random number generator
 * @param material - Material to use for the rock mesh
 * @param config - Optional configuration for rock dimensions
 */
export function createRock(
    rng: SeededRandom,
    material: THREE.MeshStandardMaterial,
    config?: RockConfig
): EnvironmentObjectData {
    const minWidth = config?.minWidth ?? 1;
    const maxWidth = config?.maxWidth ?? 3;
    const minHeight = config?.minHeight ?? 0.5;
    const maxHeight = config?.maxHeight ?? 1.5;
    const minDepth = config?.minDepth ?? 1;
    const maxDepth = config?.maxDepth ?? 3;

    const width = minWidth + rng.next() * (maxWidth - minWidth);
    const height = minHeight + rng.next() * (maxHeight - minHeight);
    const depth = minDepth + rng.next() * (maxDepth - minDepth);

    interface RockCube {
        position: THREE.Vector3;
        materialType: 'trunk' | 'leaves' | 'rock';
        size: number;
    }

    // Track as a single cube (rock is one piece)
    const cubes: RockCube[] = [{
        position: new THREE.Vector3(0, height / 2, 0),
        materialType: 'rock',
        size: Math.max(width, height, depth)
    }];

    // Create a base geometry (will be scaled per-instance)
    const baseGeometry = new THREE.BoxGeometry(1, 1, 1);

    // Set UV coordinates to map to rock pixel (row 2 in 1x4 texture)
    // V coordinate: pixel 2 is at V=0.375 (center of pixel)
    const uvAttribute = baseGeometry.attributes.uv;
    if (uvAttribute) {
        for (let j = 0; j < uvAttribute.count; j++) {
            uvAttribute.setXY(j, 0, 0.375);
        }
        uvAttribute.needsUpdate = true;
    }

    // Create a temporary mesh for reference
    const mesh = new THREE.Mesh(baseGeometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.name = 'Rock';

    // Store scale info in geometry userData for physics creation
    baseGeometry.userData = {
        rockScale: { width, height, depth }
    };

    return {
        cubes,
        mergedGeometry: baseGeometry,
        mesh,
        scale: { width, height, depth }
    };
}

// ============================================================================
// PHYSICS HELPERS
// ============================================================================

/**
 * Create physics body for a tree instance.
 *
 * @param x - X position
 * @param y - Y position
 * @param z - Z position
 * @param worldBodies - Array to push the physics body into (for cleanup tracking)
 * @param scale - Optional scale for the tree
 * @param physicsWorld - Optional physics world for creating body directly
 */
export function createTreePhysics(
    x: number,
    y: number,
    z: number,
    worldBodies: RAPIER.RigidBody[],
    scale?: { width: number; height: number; depth: number },
    physicsWorld?: PhysicsWorld
): void {
    if (!physicsWorld) {
        console.warn('createTreePhysics: No physics world provided, skipping physics creation');
        return;
    }
    
    const RAPIER = getRapier();
    const blockSize = 1.0;
    const avgTreeHeight = 4.5;
    const scaleW = scale?.width ?? 1;
    const scaleH = scale?.height ?? 1;
    const scaleD = scale?.depth ?? 1;

    const trunkHalfHeight = (avgTreeHeight * blockSize * scaleH) / 2;
    const trunkHalfWidth = (blockSize * scaleW) / 2;
    const trunkHalfDepth = (blockSize * scaleD) / 2;

    // Create fixed rigid body
    const bodyDesc = RAPIER.RigidBodyDesc.fixed()
        .setTranslation(x, y + trunkHalfHeight, z);
    const body = physicsWorld.createRigidBody(bodyDesc);

    // Create box collider
    const colliderDesc = RAPIER.ColliderDesc.cuboid(trunkHalfWidth, trunkHalfHeight, trunkHalfDepth)
        .setFriction(0.7)
        .setRestitution(0.1)
        .setCollisionGroups(makeCollisionGroups(CollisionGroup.ENVIRONMENT, CollisionMask.ALL));
    
    physicsWorld.createCollider(colliderDesc, body);
    worldBodies.push(body);
}

/**
 * Create physics body for a rock instance.
 *
 * @param x - X position
 * @param y - Y position
 * @param z - Z position
 * @param rotation - Y rotation in radians
 * @param scale - Rock scale dimensions
 * @param worldBodies - Array to push the physics body into (for cleanup tracking)
 * @param physicsWorld - Optional physics world for creating body directly
 */
export function createRockPhysics(
    x: number,
    y: number,
    z: number,
    rotation: number,
    scale: { width: number; height: number; depth: number },
    worldBodies: RAPIER.RigidBody[],
    physicsWorld?: PhysicsWorld
): void {
    if (!physicsWorld) {
        console.warn('createRockPhysics: No physics world provided, skipping physics creation');
        return;
    }
    
    const RAPIER = getRapier();
    
    // Create quaternion from Y rotation
    const quat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), rotation);
    
    // Create fixed rigid body with rotation
    const bodyDesc = RAPIER.RigidBodyDesc.fixed()
        .setTranslation(x, y, z)
        .setRotation({ x: quat.x, y: quat.y, z: quat.z, w: quat.w });
    const body = physicsWorld.createRigidBody(bodyDesc);

    // Create box collider
    const colliderDesc = RAPIER.ColliderDesc.cuboid(
        scale.width / 2,
        scale.height / 2,
        scale.depth / 2
    )
        .setFriction(0.8)
        .setRestitution(0.2)
        .setCollisionGroups(makeCollisionGroups(CollisionGroup.ENVIRONMENT, CollisionMask.ALL));
    
    physicsWorld.createCollider(colliderDesc, body);
    worldBodies.push(body);
}

// ============================================================================
// INSTANCED MESH HELPERS
// ============================================================================

/**
 * Create InstancedMesh for trees with physics.
 */
export function createTreeInstancedMesh(
    instances: EnvironmentInstance[],
    instancedMesh: THREE.InstancedMesh | null,
    instanceData: EnvironmentObjectData[],
    world: THREE.Object3D,
    worldBodies: any[],
    material: THREE.MeshStandardMaterial,
    physicsWorld: PhysicsWorld | null
): { instancedMesh: THREE.InstancedMesh; instanceData: EnvironmentObjectData[] } {
    if (instances.length === 0) {
        throw new Error('Cannot create InstancedMesh with no instances');
    }

    const firstInstance = instances[0];
    if (!firstInstance) {
        throw new Error('First instance is missing');
    }
    const baseGeometry = firstInstance.data.mergedGeometry.clone();

    const mesh = instancedMesh || new THREE.InstancedMesh(
        baseGeometry,
        material,
        instances.length
    );
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.name = 'Trees';

    const matrix = new THREE.Matrix4();
    const resultInstances: EnvironmentObjectData[] = [];

    for (let i = 0; i < instances.length; i++) {
        const instance = instances[i];
        if (!instance) continue;

        const scale = instance.scale || { width: 1, height: 1, depth: 1 };

        // Create matrix with position, rotation, and scale
        const position = new THREE.Vector3(instance.x, instance.y, instance.z);
        const quaternion = new THREE.Quaternion().setFromEuler(new THREE.Euler(0, instance.rotation || 0, 0));
        const scaleVec = new THREE.Vector3(scale.width, scale.height, scale.depth);
        matrix.compose(position, quaternion, scaleVec);
        mesh.setMatrixAt(i, matrix);

        // Store instance data
        const data: EnvironmentObjectData = {
            cubes: instance.data.cubes.map(cube => {
                const pos = cube.position.clone();
                pos.multiply(new THREE.Vector3(scale.width, scale.height, scale.depth));
                if (instance.rotation !== undefined && instance.rotation !== 0) {
                    const rotMatrix = new THREE.Matrix4().makeRotationY(instance.rotation);
                    pos.applyMatrix4(rotMatrix);
                }
                pos.add(new THREE.Vector3(instance.x, instance.y, instance.z));
                return {
                    ...cube,
                    position: pos,
                    size: cube.size * Math.max(scale.width, scale.height, scale.depth)
                };
            }),
            mergedGeometry: instance.data.mergedGeometry,
            mesh: instance.data.mesh,
            instanceId: i,
            scale
        };
        resultInstances.push(data);

        // Create physics body
        createTreePhysics(instance.x, instance.y, instance.z, worldBodies, scale, physicsWorld ?? undefined);
    }

    mesh.instanceMatrix.needsUpdate = true;
    world.add(mesh);

    return { instancedMesh: mesh, instanceData: resultInstances };
}

/**
 * Create InstancedMesh for rocks with physics.
 */
export function createRockInstancedMesh(
    instances: EnvironmentInstance[],
    instancedMesh: THREE.InstancedMesh | null,
    instanceData: EnvironmentObjectData[],
    world: THREE.Object3D,
    worldBodies: any[],
    material: THREE.MeshStandardMaterial,
    physicsWorld: PhysicsWorld | null
): { instancedMesh: THREE.InstancedMesh; instanceData: EnvironmentObjectData[] } {
    if (instances.length === 0) {
        throw new Error('Cannot create InstancedMesh with no instances');
    }

    const firstInstance = instances[0];
    if (!firstInstance) {
        throw new Error('First instance is missing');
    }
    const baseGeometry = firstInstance.data.mergedGeometry.clone();

    const mesh = instancedMesh || new THREE.InstancedMesh(
        baseGeometry,
        material,
        instances.length
    );
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.name = 'Rocks';

    const matrix = new THREE.Matrix4();
    const resultInstances: EnvironmentObjectData[] = [];

    for (let i = 0; i < instances.length; i++) {
        const instance = instances[i];
        if (!instance) continue;

        // Get scale from rock geometry userData or instance
        const rockUserData = instance.data.mergedGeometry.userData as { rockScale?: { width: number; height: number; depth: number } };
        const scale = instance.scale || rockUserData?.rockScale || { width: 1, height: 1, depth: 1 };

        // Create matrix with position, rotation, and scale
        const position = new THREE.Vector3(instance.x, instance.y, instance.z);
        const quaternion = new THREE.Quaternion().setFromEuler(new THREE.Euler(0, instance.rotation || 0, 0));
        const scaleVec = new THREE.Vector3(scale.width, scale.height, scale.depth);
        matrix.compose(position, quaternion, scaleVec);
        mesh.setMatrixAt(i, matrix);

        // Store instance data
        const data: EnvironmentObjectData = {
            cubes: instance.data.cubes.map(cube => {
                const pos = cube.position.clone();
                pos.multiply(new THREE.Vector3(scale.width, scale.height, scale.depth));
                if (instance.rotation !== undefined && instance.rotation !== 0) {
                    const rotMatrix = new THREE.Matrix4().makeRotationY(instance.rotation);
                    pos.applyMatrix4(rotMatrix);
                }
                pos.add(new THREE.Vector3(instance.x, instance.y, instance.z));
                return {
                    ...cube,
                    position: pos,
                    size: cube.size * Math.max(scale.width, scale.height, scale.depth)
                };
            }),
            mergedGeometry: instance.data.mergedGeometry,
            mesh: instance.data.mesh,
            instanceId: i,
            scale
        };
        resultInstances.push(data);

        // Create physics body
        createRockPhysics(
            instance.x, instance.y, instance.z,
            instance.rotation || 0,
            scale,
            worldBodies,
            physicsWorld ?? undefined
        );
    }

    mesh.instanceMatrix.needsUpdate = true;
    world.add(mesh);

    return { instancedMesh: mesh, instanceData: resultInstances };
}

// ============================================================================
// VOXEL-BASED OBJECT FACTORIES
// ============================================================================

/**
 * Configuration for voxel tree generation.
 */
export interface VoxelTreeConfig {
    /** Size of each voxel block (default: 0.5m) */
    voxelSize?: number;
    /** Minimum trunk height in blocks (default: 6) */
    minTrunkHeight?: number;
    /** Maximum trunk height in blocks (default: 10) */
    maxTrunkHeight?: number;
    /** Number of layers of leaves (default: 4) */
    leavesLayers?: number;
}

/**
 * Configuration for voxel rock generation.
 */
export interface VoxelRockConfig {
    /** Size of each voxel block (default: 0.5m) */
    voxelSize?: number;
    /** Minimum width in blocks (default: 2) */
    minWidth?: number;
    /** Maximum width in blocks (default: 4) */
    maxWidth?: number;
    /** Minimum height in blocks (default: 1) */
    minHeight?: number;
    /** Maximum height in blocks (default: 3) */
    maxHeight?: number;
}

/**
 * Create a voxel-based tree using VoxelObject with texture atlas.
 * See BlockType in VoxelTextureAtlas.ts for available types. For custom colors, use BlockType.COLOR with RGB hex.
 */
export function createVoxelTree(
    rng: SeededRandom,
    config?: VoxelTreeConfig
): VoxelObject {
    const voxelSize = config?.voxelSize ?? 0.5;
    const minTrunkHeight = config?.minTrunkHeight ?? 6;
    const maxTrunkHeight = config?.maxTrunkHeight ?? 10;
    const leavesLayers = config?.leavesLayers ?? 4;
    
    const voxelTree = new VoxelObject({
        voxelSize,
        useAtlas: true,
        shadows: true
    });
    voxelTree.name = 'VoxelTree';
    
    // Random trunk height
    const trunkHeight = minTrunkHeight + Math.floor(rng.next() * (maxTrunkHeight - minTrunkHeight + 1));
    
    // Create trunk (single column of TRUNK blocks)
    const trunkBlockId = getBlockIdByName('trunk');
    for (let y = 0; y < trunkHeight; y++) {
        voxelTree.setVoxel(0, y, 0, trunkBlockId);
    }
    
    // Create leaves in layers above and around the trunk top
    const leavesStartY = trunkHeight - 2;
    
    for (let layer = 0; layer < leavesLayers; layer++) {
        const y = leavesStartY + layer;
        const isTopLayer = layer === leavesLayers - 1;
        const isBottomLayer = layer === 0;
        
        // Determine radius based on layer position
        let radius: number;
        if (isTopLayer) {
            radius = 1; // Small top
        } else if (isBottomLayer) {
            radius = 2; // Medium bottom
        } else {
            radius = 3; // Large middle layers
        }
        
        // Fill a roughly circular area with leaves
        for (let dx = -radius; dx <= radius; dx++) {
            for (let dz = -radius; dz <= radius; dz++) {
                // Skip the trunk position for lower layers
                if (dx === 0 && dz === 0 && layer < 2) continue;
                
                // Circular shape (roughly)
                const dist = Math.sqrt(dx * dx + dz * dz);
                if (dist <= radius + 0.5) {
                    // Add some randomness to edges
                    if (dist > radius - 0.5 && rng.next() > 0.6) continue;
                    
                    voxelTree.setVoxel(dx, y, dz, getBlockIdByName('leaves'));
                }
            }
        }
    }
    
    voxelTree.finalize();
    return voxelTree;
}

/**
 * Create a voxel-based rock using VoxelObject with texture atlas.
 * Rocks use STONE texture with irregular shapes.
 */
export function createVoxelRock(
    rng: SeededRandom,
    config?: VoxelRockConfig
): VoxelObject {
    const voxelSize = config?.voxelSize ?? 0.5;
    const minWidth = config?.minWidth ?? 2;
    const maxWidth = config?.maxWidth ?? 4;
    const minHeight = config?.minHeight ?? 1;
    const maxHeight = config?.maxHeight ?? 3;
    
    const voxelRock = new VoxelObject({
        voxelSize,
        useAtlas: true,
        shadows: true
    });
    voxelRock.name = 'VoxelRock';
    
    // Random dimensions
    const width = minWidth + Math.floor(rng.next() * (maxWidth - minWidth + 1));
    const depth = minWidth + Math.floor(rng.next() * (maxWidth - minWidth + 1));
    const height = minHeight + Math.floor(rng.next() * (maxHeight - minHeight + 1));
    
    // Create irregular rock shape
    const halfW = Math.floor(width / 2);
    const halfD = Math.floor(depth / 2);
    
    for (let y = 0; y < height; y++) {
        // Taper slightly at top
        const yRatio = y / height;
        const layerScale = 1 - (yRatio * 0.3);
        const effectiveHalfW = Math.ceil(halfW * layerScale);
        const effectiveHalfD = Math.ceil(halfD * layerScale);
        
        for (let dx = -effectiveHalfW; dx <= effectiveHalfW; dx++) {
            for (let dz = -effectiveHalfD; dz <= effectiveHalfD; dz++) {
                // Add some randomness for natural look
                if (Math.abs(dx) === effectiveHalfW || Math.abs(dz) === effectiveHalfD) {
                    if (rng.next() > 0.7) continue; // Skip some edge blocks
                }
                
                voxelRock.setVoxel(dx, y, dz, getBlockIdByName('stone'));
            }
        }
    }
    
    voxelRock.finalize();
    return voxelRock;
}

// ============================================================================
// REGISTRATION HELPERS
// ============================================================================

/**
 * Snap a position to the center of a terrain voxel.
 * @param pos Position to snap
 * @param terrainVoxelSize Size of terrain voxels
 */
function snapToTerrainVoxelCenter(pos: number, terrainVoxelSize: number): number {
    return Math.floor(pos / terrainVoxelSize) * terrainVoxelSize + terrainVoxelSize / 2;
}

/**
 * Pending VoxelObjects that need physics bodies created.
 * These are collected during scenery generation and processed afterward.
 */
const pendingVoxelObjectPhysics: Array<{ obj: VoxelObject; parent: THREE.Object3D }> = [];

/**
 * Add a VoxelObject to the pending physics list.
 */
export function addPendingVoxelObjectPhysics(voxelObject: VoxelObject, parent?: THREE.Object3D): void {
    pendingVoxelObjectPhysics.push({ obj: voxelObject, parent: parent ?? voxelObject.parent ?? new THREE.Object3D() });
}

/**
 * Create physics bodies for all pending VoxelObjects.
 * Call this after scenery generation when physics world is ready.
 * @param physicsWorld The Rapier physics world
 */
// TODO: Update to use PhysicsWorld - currently using any for compatibility
export function createPendingVoxelObjectPhysics(physicsWorld: any): void {
    console.log(`[EnvironmentObjects] Creating physics for ${pendingVoxelObjectPhysics.length} voxel objects`);
    for (const { obj, parent } of pendingVoxelObjectPhysics) {
        obj.createPhysicsBody(physicsWorld);
        enableStructuralCollapse(obj, physicsWorld, parent);
    }
    // Clear the pending list
    pendingVoxelObjectPhysics.length = 0;
}

/**
 * Clear the pending voxel object physics list without creating physics.
 */
export function clearPendingVoxelObjectPhysics(): void {
    pendingVoxelObjectPhysics.length = 0;
}

/**
 * Register voxel tree type with the environment object system.
 * Uses VoxelObject for blocky aesthetic.
 *
 * @param system - The EnvironmentObjectSystem instance
 * @param options - Configuration options (getTerrainHeight is REQUIRED for voxel terrain)
 */
export function registerVoxelTreeType(
    system: EnvironmentObjectSystem,
    options: {
        proceduralCount?: number;
        treeConfig?: VoxelTreeConfig;
        getTerrainHeight: (x: number, z: number) => number; // REQUIRED - must query actual voxel terrain
        terrainVoxelSize?: number;
    }
): void {
    const treeConfig = options.treeConfig;
    const getTerrainHeight = options.getTerrainHeight;
    const terrainVoxelSize = options.terrainVoxelSize ?? 1.0;
    
    system.registerEnvironmentObjectType({
        typeName: 'voxelTree',
        factory: () => {
            const voxelTree = createVoxelTree(system.getRng(), treeConfig);
            // Return a compatible data structure
            return {
                cubes: [],
                mergedGeometry: new THREE.BufferGeometry(), // Placeholder
                mesh: voxelTree,
                voxelObject: voxelTree
            };
        },
        canPlace: (x: number, z: number, terrainHeightProvider: TerrainHeightProvider, terrainRegistry: TerrainTypeRegistry) => {
            const terrainType = terrainHeightProvider.getTerrainTypeAt(x, z);
            const terrainProps = terrainRegistry.getType(terrainType);
            return terrainProps ? (terrainProps.canPlaceTrees ?? false) : false;
        },
        proceduralCount: options?.proceduralCount ?? 20,
        createInstancedMesh: (instances, instancedMesh, instanceData, world, worldBodies, material) => {
            // For VoxelObject, we add each tree individually (no instancing)
            const resultInstances: EnvironmentObjectData[] = [];
            
            for (const instance of instances) {
                if (!instance.data.voxelObject) continue;
                
                const voxelTree = instance.data.voxelObject as VoxelObject;
                
                // Snap position to terrain voxel center
                const snappedX = snapToTerrainVoxelCenter(instance.x, terrainVoxelSize);
                const snappedZ = snapToTerrainVoxelCenter(instance.z, terrainVoxelSize);
                
                // Get height at snapped position (getTerrainHeight is required)
                const y = getTerrainHeight(snappedX, snappedZ);
                
                voxelTree.position.set(snappedX, y, snappedZ);
                if (instance.rotation) {
                    voxelTree.rotation.y = instance.rotation;
                }
                world.add(voxelTree);

                // Add to pending physics list - physics will be created after scenery generation
                addPendingVoxelObjectPhysics(voxelTree, world);
                
                resultInstances.push({
                    ...instance.data,
                    instanceId: resultInstances.length
                });
            }
            
            // Return null for instancedMesh since we're not using instancing
            return { instancedMesh: instancedMesh!, instanceData: resultInstances };
        },
        createPhysics: (instance, worldBodies) => {
            // Physics is created after scenery generation via createPendingVoxelObjectPhysics
        },
        getPlacementY: (instance, _heightmapSystem, groundOffset) => {
            // Snap to terrain voxel center first
            const snappedX = snapToTerrainVoxelCenter(instance.x, terrainVoxelSize);
            const snappedZ = snapToTerrainVoxelCenter(instance.z, terrainVoxelSize);
            
            // Use voxel terrain height (getTerrainHeight is required)
            return getTerrainHeight(snappedX, snappedZ) + groundOffset;
        },
        getClearRadius: () => 1.5,
        getClearSize: () => ({ width: 3, depth: 3 })
    });
}

/**
 * Register voxel rock type with the environment object system.
 * Uses VoxelObject for blocky aesthetic.
 *
 * @param system - The EnvironmentObjectSystem instance
 * @param options - Configuration options (getTerrainHeight is REQUIRED for voxel terrain)
 */
export function registerVoxelRockType(
    system: EnvironmentObjectSystem,
    options: {
        proceduralCount?: number;
        rockConfig?: VoxelRockConfig;
        getTerrainHeight: (x: number, z: number) => number; // REQUIRED - must query actual voxel terrain
        terrainVoxelSize?: number;
    }
): void {
    const rockConfig = options.rockConfig;
    const getTerrainHeight = options.getTerrainHeight;
    const terrainVoxelSize = options.terrainVoxelSize ?? 1.0;
    
    system.registerEnvironmentObjectType({
        typeName: 'voxelRock',
        factory: () => {
            const voxelRock = createVoxelRock(system.getRng(), rockConfig);
            return {
                cubes: [],
                mergedGeometry: new THREE.BufferGeometry(),
                mesh: voxelRock,
                voxelObject: voxelRock
            };
        },
        canPlace: (x: number, z: number, terrainHeightProvider: TerrainHeightProvider, terrainRegistry: TerrainTypeRegistry) => {
            const terrainType = terrainHeightProvider.getTerrainTypeAt(x, z);
            const terrainProps = terrainRegistry.getType(terrainType);
            return terrainProps ? (terrainProps.canPlaceRocks ?? false) : false;
        },
        proceduralCount: options?.proceduralCount ?? 10,
        createInstancedMesh: (instances, instancedMesh, instanceData, world, worldBodies, material) => {
            const resultInstances: EnvironmentObjectData[] = [];
            
            for (const instance of instances) {
                if (!instance.data.voxelObject) continue;
                
                const voxelRock = instance.data.voxelObject as VoxelObject;
                
                // Snap position to terrain voxel center
                const snappedX = snapToTerrainVoxelCenter(instance.x, terrainVoxelSize);
                const snappedZ = snapToTerrainVoxelCenter(instance.z, terrainVoxelSize);
                
                // Get height at snapped position (getTerrainHeight is required)
                const y = getTerrainHeight(snappedX, snappedZ);
                
                voxelRock.position.set(snappedX, y, snappedZ);
                if (instance.rotation) {
                    voxelRock.rotation.y = instance.rotation;
                }
                world.add(voxelRock);

                // Add to pending physics list - physics will be created after scenery generation
                addPendingVoxelObjectPhysics(voxelRock, world);
                
                resultInstances.push({
                    ...instance.data,
                    instanceId: resultInstances.length
                });
            }
            
            return { instancedMesh: instancedMesh!, instanceData: resultInstances };
        },
        createPhysics: (instance, worldBodies) => {
            // Physics is created after scenery generation via createPendingVoxelObjectPhysics
        },
        getPlacementY: (instance, _heightmapSystem, groundOffset) => {
            // Snap to terrain voxel center first
            const snappedX = snapToTerrainVoxelCenter(instance.x, terrainVoxelSize);
            const snappedZ = snapToTerrainVoxelCenter(instance.z, terrainVoxelSize);
            
            // Use voxel terrain height (getTerrainHeight is required)
            return getTerrainHeight(snappedX, snappedZ) + groundOffset;
        },
        getClearRadius: () => 1.0,
        getClearSize: () => ({ width: 2, depth: 2 })
    });
}

/**
 * Register tree type with the environment object system.
 *
 * AI AGENTS: Modify this function to customize tree behavior!
 *
 * @param system - The EnvironmentObjectSystem instance
 * @param options - Configuration options
 */
export function registerTreeType(
    system: EnvironmentObjectSystem,
    options?: {
        proceduralCount?: number;
        treeConfig?: TreeConfig;
    }
): void {
    const treeConfig = options?.treeConfig;

    system.registerEnvironmentObjectType({
        typeName: 'tree',
        factory: () => {
            const material = system.getEnvironmentMaterial();
            if (!material) throw new Error('Environment material not initialized');
            return createTree(system.getRng(), material, treeConfig);
        },
        canPlace: (x: number, z: number, terrainHeightProvider: TerrainHeightProvider, terrainRegistry: TerrainTypeRegistry) => {
            const terrainType = terrainHeightProvider.getTerrainTypeAt(x, z);
            const terrainProps = terrainRegistry.getType(terrainType);
            return terrainProps ? (terrainProps.canPlaceTrees ?? false) : false;
        },
        proceduralCount: options?.proceduralCount ?? 20,
        createInstancedMesh: (instances, instancedMesh, instanceData, world, worldBodies, material, physicsWorld) => {
            return createTreeInstancedMesh(instances, instancedMesh, instanceData, world, worldBodies, material, physicsWorld);
        },
        createPhysics: (instance, worldBodies, physicsWorld) => {
            createTreePhysics(instance.x, instance.y, instance.z, worldBodies, instance.scale, physicsWorld ?? undefined);
        },
        getPlacementY: (instance, terrainHeightProvider, groundOffset) => {
            return terrainHeightProvider.getHeightAt(instance.x, instance.z) + groundOffset;
        },
        getClearRadius: () => 0.5,
        getClearSize: () => ({ width: 0.8, depth: 0.8 })
    });
}

/**
 * Register rock type with the environment object system.
 *
 * AI AGENTS: Modify this function to customize rock behavior!
 *
 * @param system - The EnvironmentObjectSystem instance
 * @param options - Configuration options
 */
export function registerRockType(
    system: EnvironmentObjectSystem,
    options?: {
        proceduralCount?: number;
        rockConfig?: RockConfig;
    }
): void {
    const rockConfig = options?.rockConfig;

    system.registerEnvironmentObjectType({
        typeName: 'rock',
        factory: () => {
            const material = system.getEnvironmentMaterial();
            if (!material) throw new Error('Environment material not initialized');
            return createRock(system.getRng(), material, rockConfig);
        },
        canPlace: (x: number, z: number, terrainHeightProvider: TerrainHeightProvider, terrainRegistry: TerrainTypeRegistry) => {
            const terrainType = terrainHeightProvider.getTerrainTypeAt(x, z);
            const terrainProps = terrainRegistry.getType(terrainType);
            return terrainProps ? (terrainProps.canPlaceRocks ?? false) : false;
        },
        proceduralCount: options?.proceduralCount ?? 10,
        createInstancedMesh: (instances, instancedMesh, instanceData, world, worldBodies, material, physicsWorld) => {
            return createRockInstancedMesh(instances, instancedMesh, instanceData, world, worldBodies, material, physicsWorld);
        },
        createPhysics: (instance, worldBodies, physicsWorld) => {
            const rockUserData = instance.data.mergedGeometry.userData as { rockScale?: { width: number; height: number; depth: number } };
            const scale = instance.scale || rockUserData?.rockScale || { width: 1, height: 1, depth: 1 };
            createRockPhysics(instance.x, instance.y, instance.z, instance.rotation || 0, scale, worldBodies, physicsWorld ?? undefined);
        },
        getPlacementY: (instance, terrainHeightProvider, groundOffset) => {
            const rockUserData = instance.data.mergedGeometry.userData as { rockScale?: { width: number; height: number; depth: number } };
            const scale = instance.scale || rockUserData?.rockScale || { width: 1, height: 1, depth: 1 };
            const rockHeight = scale.height;
            return terrainHeightProvider.getHeightAt(instance.x, instance.z) + rockHeight / 2 + groundOffset;
        },
        getClearRadius: (instance) => {
            const rockUserData = instance.data.mergedGeometry.userData as { rockScale?: { width: number; height: number; depth: number } };
            const scale = instance.scale || rockUserData?.rockScale || { width: 1, height: 1, depth: 1 };
            return Math.max(scale.width, scale.depth) / 2;
        },
        getClearSize: (instance) => {
            const rockUserData = instance.data.mergedGeometry.userData as { rockScale?: { width: number; height: number; depth: number } };
            const scale = instance.scale || rockUserData?.rockScale || { width: 1, height: 1, depth: 1 };
            return { width: scale.width, depth: scale.depth };
        }
    });
}


