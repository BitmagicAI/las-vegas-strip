import * as THREE from 'three';
import type { IBlockCharacterFactory } from 'engine/IBlockCharacterFactory.js';
import { bitmagicCharacterFactory } from './BitmagicPlayerCharacter.js';

/**
 * Clean BoxGeometry NPC characters — the DEFAULT NPC look.
 *
 * Built with the same simple BoxGeometry blocks and the same body-part dimensions
 * as the player mascot (`BitmagicPlayerCharacter.ts`), just recoloured per NPC type
 * and given two cartoon eyes. This is the clean-block counterpart to the player; it
 * is what NPCs render unless the user explicitly asks for a highres (Asset-Forger
 * GLB) character, in which case the NPC is registered with a `characterAssetId`
 * instead and renders as a skinned GLB.
 *
 * Usage — pass the factory as the NPC's `characterFactory`:
 *   import { createBlockNpcCharacter, blockNpcVariant } from './BlockNpcCharacter.js';
 *   engine.registerNpc('villager', new NpcVillagerBehavior({...}), {
 *     characterFactory: createBlockNpcCharacter({ shirt: 0x8C4A3B, pants: 0x2E3440 }),
 *   });
 *   // or, for a varied crowd: characterFactory: blockNpcVariant(i)
 */

// ─── Colours ────────────────────────────────────────────────────────
export interface BlockNpcColors {
  skin: number;   // head, neck, hands
  shirt: number;  // torso, arms
  pants: number;  // thighs, shins
  shoes: number;  // feet
  eye: number;    // eye pupils
}

export const DEFAULT_BLOCK_NPC_COLORS: BlockNpcColors = {
  skin: 0xE0B68A, shirt: 0x3A6EA5, pants: 0x394150, shoes: 0x23262B, eye: 0x202428,
};

/** A few palettes so a crowd of NPCs isn't all identical. */
export const BLOCK_NPC_PALETTES: BlockNpcColors[] = [
  DEFAULT_BLOCK_NPC_COLORS,
  { skin: 0xC68642, shirt: 0x8C4A3B, pants: 0x2E3440, shoes: 0x20242A, eye: 0x201A14 },
  { skin: 0xF0C8A0, shirt: 0x4F7A52, pants: 0x44372B, shoes: 0x2A2A2A, eye: 0x2A3A5A },
  { skin: 0x8D5524, shirt: 0x6A5ACD, pants: 0x33373F, shoes: 0x222222, eye: 0x101010 },
];

/** Standard matte material for a block body part. */
function bodyMaterial(color: number): THREE.MeshStandardMaterial {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.4, metalness: 0.05 });
}

/** Add a box mesh of the given size/colour to a named body-part group. */
function addPart(
  characterGroup: THREE.Group,
  partName: string,
  w: number, h: number, d: number,
  color: number,
  position: [number, number, number],
  name: string,
): THREE.Mesh | null {
  const group = characterGroup.getObjectByName(partName) as THREE.Group | null;
  if (!group) return null;
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), bodyMaterial(color));
  mesh.name = name;
  mesh.position.set(position[0], position[1], position[2]);
  group.add(mesh);
  return mesh;
}

/** Build the recoloured clean-block NPC meshes onto the provided body-part groups. */
function createBlockNpcMeshes(characterGroup: THREE.Group, c: BlockNpcColors): void {
  characterGroup.name = 'BlockCharacter_Npc';

  // Head (with two cartoon eyes on the front facet, +Z)
  const headMesh = addPart(characterGroup, 'head', 0.45, 0.4, 0.35, c.skin, [0, 0.24, 0], 'npc_head_main');
  if (headMesh) {
    const eyeWhite = new THREE.Mesh(
      new THREE.BoxGeometry(0.11, 0.13, 0.03),
      new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.1 }),
    );
    eyeWhite.position.set(-0.1, 0.05, 0.17);
    headMesh.add(eyeWhite);

    const pupil = new THREE.Mesh(
      new THREE.BoxGeometry(0.07, 0.09, 0.02),
      new THREE.MeshStandardMaterial({ color: c.eye, roughness: 0.1 }),
    );
    pupil.position.set(0, 0, 0.01);
    eyeWhite.add(pupil);

    const rightEye = eyeWhite.clone();
    rightEye.position.x = 0.1;
    headMesh.add(rightEye);
  }

  // Neck
  addPart(characterGroup, 'neck', 0.15, 0.08, 0.12, c.skin, [0, 0.04, 0], 'npc_neck');

  // Torso. Pose v2: the torso group's +Z already faces the front (engine-oriented to
  // match the head), so the body box needs no flip and any front detail (badge, etc.)
  // goes at +Z like on the head. (The v1 `rotation.y = Math.PI` work-around is gone.)
  addPart(characterGroup, 'torso', 0.4, 0.5, 0.25, c.shirt, [0, -0.1, 0], 'npc_torso');

  // Arms (shirt) + hands (skin)
  addPart(characterGroup, 'leftUpperArm', 0.12, 0.22, 0.12, c.shirt, [0, 0, 0], 'npc_arm_upper_left');
  addPart(characterGroup, 'leftForearm', 0.11, 0.18, 0.11, c.shirt, [0, 0, 0], 'npc_arm_forearm_left');
  addPart(characterGroup, 'leftHand', 0.15, 0.12, 0.1, c.skin, [0, 0.06, 0], 'npc_hand_left');
  addPart(characterGroup, 'rightUpperArm', 0.12, 0.22, 0.12, c.shirt, [0, 0, 0], 'npc_arm_upper_right');
  addPart(characterGroup, 'rightForearm', 0.11, 0.18, 0.11, c.shirt, [0, 0, 0], 'npc_arm_forearm_right');
  addPart(characterGroup, 'rightHand', 0.15, 0.12, 0.1, c.skin, [0, 0.06, 0], 'npc_hand_right');

  // Legs (pants)
  addPart(characterGroup, 'leftThigh', 0.18, 0.3, 0.16, c.pants, [0, 0, 0], 'npc_leg_thigh_left');
  addPart(characterGroup, 'leftShin', 0.16, 0.35, 0.14, c.pants, [0, 0.02, 0], 'npc_leg_shin_left');
  addPart(characterGroup, 'rightThigh', 0.18, 0.3, 0.16, c.pants, [0, 0, 0], 'npc_leg_thigh_right');
  addPart(characterGroup, 'rightShin', 0.16, 0.35, 0.14, c.pants, [0, 0.02, 0], 'npc_leg_shin_right');

  // Feet (shoes) — NEGATIVE Y so the foot extends forward from the ankle.
  const lf = addPart(characterGroup, 'leftFoot', 0.2, 0.12, 0.35, c.shoes, [0, -0.08, 0], 'npc_foot_left');
  if (lf) lf.rotation.x = -Math.PI / 2;
  const rf = addPart(characterGroup, 'rightFoot', 0.2, 0.12, 0.35, c.shoes, [0, -0.08, 0], 'npc_foot_right');
  if (rf) rf.rotation.x = -Math.PI / 2;

  // Shadows
  characterGroup.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });
}

/**
 * Build a clean-block NPC factory with the given colours. Pass it as the NPC's
 * `characterFactory`. Omitted colours fall back to the default palette. Matches
 * the player mascot's exact dimensions so the shared skeleton scales correctly.
 */
export function createBlockNpcCharacter(colors: Partial<BlockNpcColors> = {}): IBlockCharacterFactory {
  const c: BlockNpcColors = { ...DEFAULT_BLOCK_NPC_COLORS, ...colors };
  return {
    createBlockCharacter: (characterGroup: THREE.Group) => createBlockNpcMeshes(characterGroup, c),
    getCharacterDimensions: () => bitmagicCharacterFactory.getCharacterDimensions(),
  };
}

/** Pick a palette-varied clean-block NPC factory by index (wraps) — handy for crowds. */
export function blockNpcVariant(index: number): IBlockCharacterFactory {
  const len = BLOCK_NPC_PALETTES.length;
  const i = ((index % len) + len) % len;
  return createBlockNpcCharacter(BLOCK_NPC_PALETTES[i]);
}
