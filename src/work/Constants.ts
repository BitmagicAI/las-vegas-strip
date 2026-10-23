import type { GameConstants } from 'engine/Constants.js';
import { DEFAULT_CONSTANTS } from 'engine/Constants.js';

/**
 * Voxel template constants
 * Overrides engine defaults with template-specific values
 */
export const VOXEL_CONSTANTS: Partial<GameConstants> = {
    interactionRange: 4.0, // Slightly longer range for exploration
    // Other values use engine defaults
};

/**
 * Merged constants for this template (for engine use)
 * These override engine defaults and are passed to PlayerController
 */
export const CONSTANTS: GameConstants = {
    ...DEFAULT_CONSTANTS,
    ...VOXEL_CONSTANTS,
};

/**
 * Voxel template-specific constants
 * These are NOT part of the engine constants system and can be used freely
 * by template code without modifying engine code.
 */
export interface VoxelTemplateConstants {
}

/**
 * Template-specific constants for Voxel
 * Add any constants here that are specific to the Voxel template
 * and don't need to be part of the engine constants system.
 */
export const TEMPLATE_CONSTANTS: VoxelTemplateConstants = {
};


