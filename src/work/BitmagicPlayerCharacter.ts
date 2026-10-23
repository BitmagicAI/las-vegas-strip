import * as THREE from 'three';
import type { IBlockCharacterFactory } from 'engine/IBlockCharacterFactory.js';
import { scaleCharacterToHeight, getSkeletonHeight } from 'engine/CharacterConfig.js';

/**
 * Complete Bitmagic character system
 * Everything Bitmagic related is contained in this file for easy AI modification
 *
 * Uses the IBlockCharacterFactory interface for clean separation between
 * engine layer (animation, physics) and template layer (visual appearance).
 *
 * This is the DEFAULT player character: a clean BoxGeometry "mascot" — a white
 * rounded body with a pink antenna, blinking eyes, and sparkles. Highres
 * Asset-Forger skinned GLB characters are used only on demand (when the user
 * asks); see PlayerLoader's `renderSkinned` rule and `useHighResCharacter`.
 */

// Bitmagic character configuration
export const BITMAGIC_CONFIG = {
  targetHeight: 1.3, // meters
};

// Eye blinking state
let blinkTimer = 0;
let isBlinking = false;
let blinkDuration = 0;
const BLINK_INTERVAL_MIN = 2.0; // seconds
const BLINK_INTERVAL_MAX = 5.0; // seconds
const BLINK_DURATION = 0.15; // seconds
let nextBlinkTime = Math.random() * (BLINK_INTERVAL_MAX - BLINK_INTERVAL_MIN) + BLINK_INTERVAL_MIN;

// Store references to eye pupils for blinking
let leftEyePupil: THREE.Mesh | null = null;
let rightEyePupil: THREE.Mesh | null = null;

/**
 * Bitmagic Block Character Factory
 * Implements IBlockCharacterFactory interface for clean engine/template separation
 */
export const bitmagicCharacterFactory: IBlockCharacterFactory = {
  createBlockCharacter: createBitmagicBlockCharacter,

  getCharacterDimensions: () => {
    // Bitmagic character dimensions (scaled down from standard skeleton height)
    const bitmagicHeight = BITMAGIC_CONFIG.targetHeight; // 1.3m
    const skeletonHeight = getSkeletonHeight();
    const heightRatio = bitmagicHeight / skeletonHeight;

    return {
      width: 0.6 * heightRatio,    // Scale width proportionally
      height: bitmagicHeight,       // Actual Bitmagic height
      depth: 0.3 * heightRatio      // Scale depth proportionally
    };
  }
};

/**
 * Apply all Bitmagic modifications to a player character
 * This includes visual scaling, physics updates, and re-grounding
 *
 * Note: This is called by PlayerLoader after block character creation
 */
export function applyBitmagicModifications(
  player: THREE.Object3D,
  playerController: any,
  playerLoader: any,
  blockCharacterRenderer: any
): void {
  console.log('🔮 Applying complete Bitmagic modifications...');

  // 1. Scale skeleton to Bitmagic height
  scaleToBitmagicHeight(player, playerController);

  // 2. Update physics and re-ground
  updatePhysicsForBitmagic(player, playerController, playerLoader);

  console.log('✅ All Bitmagic modifications applied successfully');
}

/**
 * Scale the character to Bitmagic's target height (1.3m)
 *
 * Uses the shared scaling utility from CharacterConfig which handles the logic
 * of scaling from the current characterHeight (set by PlayerLoader from world.json)
 * to the target height.
 */
function scaleToBitmagicHeight(player: THREE.Object3D, playerController: any): void {
  const bitmagicHeight = BITMAGIC_CONFIG.targetHeight;
  const skeletonHeight = getSkeletonHeight();

  // Get the current character height that PlayerLoader scaled to
  const currentCharacterHeight = playerController?.characterHeight || skeletonHeight;

  // Use shared utility to scale the character
  scaleCharacterToHeight(player, currentCharacterHeight, bitmagicHeight, '🔮');
}

/**
 * Update physics body and re-ground the character for Bitmagic dimensions
 */
function updatePhysicsForBitmagic(player: THREE.Object3D, playerController: any, playerLoader: any): void {
  const bitmagicHeight = BITMAGIC_CONFIG.targetHeight;
  const skeletonHeight = getSkeletonHeight();

  // Get the current character height from PlayerController to calculate radius ratio
  const currentCharacterHeight = playerController.characterHeight || skeletonHeight;
  const heightRatio = bitmagicHeight / currentCharacterHeight;

  // Update PlayerController dimensions
  playerController.setCharacterHeight(bitmagicHeight);
  const adjustedRadius = playerController.capsuleRadius * heightRatio;
  playerController.setCapsuleDimensions(bitmagicHeight, adjustedRadius);

  // Update PlayerLoader dimensions and recreate physics body
  if (playerLoader && typeof playerLoader.updateCapsuleDimensions === 'function') {
    playerLoader.updateCapsuleDimensions(bitmagicHeight, adjustedRadius);

    // Recreate the physics body with the new dimensions
    if (typeof playerLoader.recreatePhysicsBody === 'function') {
      playerLoader.recreatePhysicsBody(player);
      // Update PlayerController reference to the new physics body
      playerController.playerBody = playerLoader.getPlayerBody();
    }
  }

  // Re-ground the character
  if (typeof playerController.regroundCharacter === 'function') {
    playerController.regroundCharacter(bitmagicHeight);
  }

  console.log(`🔮 Physics updated: height=${bitmagicHeight}m, radius=${adjustedRadius.toFixed(3)}m`);
}

/**
 * Procedural Bitmagic visual mesh generation using Three.js APIs directly
 * This code can be modified by AI to create different character variations
 * Inspired by the cute white mascot with sparkles and pink antenna
 */
export function createBitmagicBlockCharacter(characterGroup: THREE.Group) {
  // Set character-specific name
  characterGroup.name = 'BlockCharacter_Bitmagic';

  // All positions and scales are arbitrary and can be adjusted for better proportions.
  // Using BoxGeometry for blocky primitives. Y-axis up, Z-axis forward.
  // All measurements in meters - actual character scale

  // Head (white with cute rounded appearance)
  const headGroup = characterGroup.getObjectByName('head') as THREE.Group;

  // Create main head mesh - larger and more rounded
  const headMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.45, 0.4, 0.35),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  headMesh.name = 'bitmagic_head_main';
  // Position head so bone is at 1/5 from bottom (move head up)
  const headHeight = 0.4;
  const boneOffsetFromBottom = 3 * headHeight / 5;
  headMesh.position.set(0, boneOffsetFromBottom, 0);
  headGroup.add(headMesh);

  // Pink antenna/wand as child of head
  const antennaMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.05, 0.25, 0.05),
    new THREE.MeshStandardMaterial({
      color: 0xFF69B4, // Hot pink
      emissive: 0xFF69B4, // Emissive pink for bloom
      emissiveIntensity: 1.2, // High intensity for bloom
      roughness: 0.2,
      metalness: 0.3
    })
  );
  antennaMesh.name = 'bitmagic_antenna';
  antennaMesh.position.set(0, 0.32, 0);
  headMesh.add(antennaMesh);

  // Left eye (large black pupil with white surrounding)
  const leftEyeWhiteMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.12, 0.15, 0.03),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF,
      roughness: 0.1
    })
  );
  leftEyeWhiteMesh.name = 'bitmagic_eye_white_left';
  leftEyeWhiteMesh.position.set(-0.1, 0.08, 0.17);
  headMesh.add(leftEyeWhiteMesh);

  const leftEyePupilMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.08, 0.11, 0.02),
    new THREE.MeshStandardMaterial({
      color: 0x000000, // Black pupil
      roughness: 0.1
    })
  );
  leftEyePupilMesh.name = 'bitmagic_eye_pupil_left';
  leftEyePupilMesh.position.set(0, 0, 0.01);
  leftEyeWhiteMesh.add(leftEyePupilMesh);

  // Store reference for blinking animation
  leftEyePupil = leftEyePupilMesh;

  // Right eye (mirrored)
  const rightEyeWhiteMesh = leftEyeWhiteMesh.clone();
  rightEyeWhiteMesh.name = 'bitmagic_eye_white_right';
  rightEyeWhiteMesh.position.x = 0.1;
  // Update the pupil name for the cloned eye
  const rightEyePupilMesh = rightEyeWhiteMesh.children[0] as THREE.Mesh;
  rightEyePupilMesh.name = 'bitmagic_eye_pupil_right';
  headMesh.add(rightEyeWhiteMesh);

  // Store reference for blinking animation
  rightEyePupil = rightEyePupilMesh;

  // Sparkle decorations on head
  const sparklePositions = [
    { x: -0.15, y: 0.25, z: 0.1 },  // Top left
    { x: 0.15, y: 0.2, z: 0.1 },   // Top right
    { x: 0, y: 0.15, z: 0.18 },    // Front center
    { x: -0.1, y: -0.05, z: 0.16 }, // Lower left
    { x: 0.1, y: -0.05, z: 0.16 }   // Lower right
  ];

  sparklePositions.forEach((pos, index) => {
    const sparkleMesh = new THREE.Mesh(
      new THREE.BoxGeometry(0.03, 0.03, 0.01),
      new THREE.MeshStandardMaterial({
        color: 0xFFFFFF, // Bright white sparkles
        emissive: 0xFFFFFF, // Full white emissive for bloom effect
        emissiveIntensity: 1.5, // High intensity to trigger bloom (threshold is 0.9)
        roughness: 0.1,
        metalness: 0.8
      })
    );
    sparkleMesh.name = `bitmagic_sparkle_${index}`;
    sparkleMesh.position.set(pos.x, pos.y, pos.z);
    // Rotate some sparkles for variety
    if (index % 2 === 0) {
      sparkleMesh.rotation.z = Math.PI / 4;
    }
    headMesh.add(sparkleMesh);
  });

  // Neck (white, smaller)
  const neckGroup = characterGroup.getObjectByName('neck') as THREE.Group;
  const neckMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.15, 0.08, 0.12),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  neckMesh.name = 'bitmagic_neck';
  neckMesh.position.set(0, 0.04, 0);
  neckGroup.add(neckMesh);

  // Torso (white, larger and rounder like the character)
  const torsoGroup = characterGroup.getObjectByName('torso') as THREE.Group;

  // Main torso body - rounded and cute.
  // Pose v2 convention: the torso group's local +Z is the character's FRONT (the
  // engine orients it to match the head). So attach front details (here, the chest
  // sparkles below) at +Z and back details at −Z — exactly like the head. Do NOT add
  // `rotation.y = Math.PI` here; that was the v1 work-around for the torso facing
  // backwards and would now flip the body to face away.
  const torsoBodyMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.4, 0.5, 0.25),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  torsoBodyMesh.name = 'bitmagic_torso_body';
  torsoBodyMesh.position.set(0, -0.10, 0);
  torsoGroup.add(torsoBodyMesh);

  // Sparkles on torso
  const torsoSparklePositions = [
    { x: -0.12, y: 0.15, z: 0.13 },  // Upper left
    { x: 0.12, y: 0.1, z: 0.13 },   // Upper right
    { x: 0, y: 0, z: 0.13 },        // Center
    { x: -0.08, y: -0.1, z: 0.13 }, // Lower left
    { x: 0.08, y: -0.15, z: 0.13 }  // Lower right
  ];

  torsoSparklePositions.forEach((pos, index) => {
    const sparkleMesh = new THREE.Mesh(
      new THREE.BoxGeometry(0.025, 0.025, 0.01),
      new THREE.MeshStandardMaterial({
        color: 0xFFFFFF, // Bright white sparkles
        emissive: 0xFFFFFF, // Full white emissive for bloom effect
        emissiveIntensity: 1.5, // High intensity to trigger bloom
        roughness: 0.1,
        metalness: 0.8
      })
    );
    sparkleMesh.name = `bitmagic_torso_sparkle_${index}`;
    sparkleMesh.position.set(pos.x, pos.y, pos.z);
    // Rotate some sparkles for variety
    if (index % 2 === 1) {
      sparkleMesh.rotation.z = Math.PI / 4;
    }
    torsoBodyMesh.add(sparkleMesh);
  });

  // Left Upper Arm (white, rounded)
  const leftUpperArmGroup = characterGroup.getObjectByName('leftUpperArm') as THREE.Group;
  const leftUpperArmMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.12, 0.22, 0.12),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  leftUpperArmMesh.name = 'bitmagic_arm_upper_left';
  leftUpperArmMesh.position.set(0, 0.0, 0);
  leftUpperArmGroup.add(leftUpperArmMesh);

  // Left Forearm (white, simple)
  const leftForearmGroup = characterGroup.getObjectByName('leftForearm') as THREE.Group;
  const leftForearmMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.11, 0.18, 0.11),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  leftForearmMesh.name = 'bitmagic_arm_forearm_left';
  leftForearmMesh.position.set(0, 0.0, 0);
  leftForearmGroup.add(leftForearmMesh);

  // Left Hand (white, cute mittens)
  const leftHandGroup = characterGroup.getObjectByName('leftHand') as THREE.Group;
  const leftHandMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.15, 0.12, 0.1),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  leftHandMesh.name = 'bitmagic_hand_left';
  leftHandMesh.position.set(0, 0.06, 0);
  leftHandGroup.add(leftHandMesh);

  // Right Upper Arm (white, rounded)
  const rightUpperArmGroup = characterGroup.getObjectByName('rightUpperArm') as THREE.Group;
  const rightUpperArmMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.12, 0.22, 0.12),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  rightUpperArmMesh.name = 'bitmagic_arm_upper_right';
  rightUpperArmMesh.position.set(0, 0.0, 0);
  rightUpperArmGroup.add(rightUpperArmMesh);

  // Right Forearm (white, simple)
  const rightForearmGroup = characterGroup.getObjectByName('rightForearm') as THREE.Group;
  const rightForearmMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.11, 0.18, 0.11),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  rightForearmMesh.name = 'bitmagic_arm_forearm_right';
  rightForearmMesh.position.set(0, 0.0, 0);
  rightForearmGroup.add(rightForearmMesh);

  // Right Hand (white, cute mittens)
  const rightHandGroup = characterGroup.getObjectByName('rightHand') as THREE.Group;
  const rightHandMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.15, 0.12, 0.1),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  rightHandMesh.name = 'bitmagic_hand_right';
  rightHandMesh.position.set(0, 0.06, 0);
  rightHandGroup.add(rightHandMesh);

  // Left Thigh (white, chunky)
  const leftThighGroup = characterGroup.getObjectByName('leftThigh') as THREE.Group;
  const leftThighMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.18, 0.3, 0.16),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  leftThighMesh.name = 'bitmagic_leg_thigh_left';
  leftThighMesh.position.set(0, 0.0, 0);
  leftThighGroup.add(leftThighMesh);

  // Left Shin (white, chunky)
  const leftShinGroup = characterGroup.getObjectByName('leftShin') as THREE.Group;
  const leftShinMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.16, 0.35, 0.14),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  leftShinMesh.name = 'bitmagic_leg_shin_left';
  leftShinMesh.position.set(0, 0.02, 0);
  leftShinGroup.add(leftShinMesh);

  // Left Foot (white, chunky)
  // ⚠️ FOOT POSITIONING: Feet MUST use NEGATIVE Y position to extend forward from ankle!
  const leftFootGroup = characterGroup.getObjectByName('leftFoot') as THREE.Group;
  const leftFootMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.2, 0.12, 0.35),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  leftFootMesh.name = 'bitmagic_foot_left';
  leftFootMesh.rotation.x = -Math.PI / 2;  // Optional: rotate foot geometry if needed
  leftFootMesh.position.set(0, -0.08, 0);  // NEGATIVE Y = forward from ankle
  leftFootGroup.add(leftFootMesh);

  // Right Thigh (white, chunky)
  const rightThighGroup = characterGroup.getObjectByName('rightThigh') as THREE.Group;
  const rightThighMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.18, 0.3, 0.16),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  rightThighMesh.name = 'bitmagic_leg_thigh_right';
  rightThighMesh.position.set(0, 0.0, 0);
  rightThighGroup.add(rightThighMesh);

  // Right Shin (white, chunky)
  const rightShinGroup = characterGroup.getObjectByName('rightShin') as THREE.Group;
  const rightShinMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.16, 0.35, 0.14),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  rightShinMesh.name = 'bitmagic_leg_shin_right';
  rightShinMesh.position.set(0, 0.02, 0);
  rightShinGroup.add(rightShinMesh);

  // Right Foot (white, chunky) - same rules as left foot
  const rightFootGroup = characterGroup.getObjectByName('rightFoot') as THREE.Group;
  const rightFootMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.2, 0.12, 0.35),
    new THREE.MeshStandardMaterial({
      color: 0xFFFFFF, // Pure white
      roughness: 0.3,
      metalness: 0.1
    })
  );
  rightFootMesh.name = 'bitmagic_foot_right';
  rightFootMesh.rotation.x = -Math.PI / 2;  // Optional: rotate foot geometry if needed
  rightFootMesh.position.set(0, -0.08, 0);  // NEGATIVE Y = forward from ankle
  rightFootGroup.add(rightFootMesh);

  // Enable shadow casting and receiving for all meshes in the character
  characterGroup.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });
}

/**
 * Update eye blinking animation
 * Call this every frame with deltaTime to animate the eyes
 */
export function updateBitmagicEyeBlink(deltaTime: number): void {
  if (!leftEyePupil || !rightEyePupil) return;

  blinkTimer += deltaTime;

  // Check if it's time to start a new blink
  if (!isBlinking && blinkTimer >= nextBlinkTime) {
    isBlinking = true;
    blinkDuration = 0;
    blinkTimer = 0;
    // Schedule next blink
    nextBlinkTime = Math.random() * (BLINK_INTERVAL_MAX - BLINK_INTERVAL_MIN) + BLINK_INTERVAL_MIN;
  }

  // Animate the blink
  if (isBlinking) {
    blinkDuration += deltaTime;

    // Blink animation: scale Y down and back up
    const blinkProgress = blinkDuration / BLINK_DURATION;

    if (blinkProgress < 0.5) {
      // Closing eyes (first half of blink)
      const closeAmount = blinkProgress * 2; // 0 to 1
      const scaleY = 1.0 - (closeAmount * 0.9); // Scale down to 10% height
      leftEyePupil.scale.y = scaleY;
      rightEyePupil.scale.y = scaleY;
    } else if (blinkProgress < 1.0) {
      // Opening eyes (second half of blink)
      const openAmount = (blinkProgress - 0.5) * 2; // 0 to 1
      const scaleY = 0.1 + (openAmount * 0.9); // Scale back up from 10% to 100%
      leftEyePupil.scale.y = scaleY;
      rightEyePupil.scale.y = scaleY;
    } else {
      // Blink complete
      leftEyePupil.scale.y = 1.0;
      rightEyePupil.scale.y = 1.0;
      isBlinking = false;
      blinkDuration = 0;
    }
  }
}
