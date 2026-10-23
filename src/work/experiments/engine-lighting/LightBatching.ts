import type * as THREE from 'three';

/**
 * Which lights `EngineLighting` batches into uniform arrays, and which stay on three's
 * per-light path. Pure, so the rule is testable without the node system.
 *
 * A batched light is evaluated in a shader loop over a count uniform: adding, removing or
 * hiding one changes a uniform, never the shader. A per-light light is compiled into every
 * lit material by id, so its arrival, departure or `castShadow` flip re-keys all of them.
 *
 * WHY `light.type` AND NOT THE CLASS NAME. three's own `DynamicLightsNode` looks a light up by
 * `light.constructor.name`. Published games load three from esm.sh's minified build, where
 * `PointLight.name` is `"nl"` and `SpotLight.name` is `"Sr"` — the lookup misses every light and
 * the addon batches nothing, silently. `type` is a string field a minifier never touches. It is
 * paired with the `is*Light` flag so an object that only borrows the string is not batched.
 *
 * Kept on the per-light path:
 * - shadow casters — the batched loop has no shadow lookup;
 * - node lights (`isNode`);
 * - projected spots (`map`, `colorNode`);
 * - `IESSpotLight` and `ProjectorLight`, which keep `type === 'SpotLight'` but render through
 *   their own light nodes (`iesMap` / `aspect` mark them);
 * - every other type (rect-area lights, light probes).
 *
 * A game's own subclass of a light (`class Torch extends PointLight`) keeps the parent's `type`
 * and is batched. That is an improvement, not a hazard: three's per-light path looks a light
 * node up by EXACT constructor, so such a subclass rendered nothing there.
 */

/** A light type `EngineLighting` batches, spelled as three's `Light.type`. */
export type BatchedLightType = 'AmbientLight' | 'HemisphereLight' | 'DirectionalLight' | 'PointLight' | 'SpotLight';

/** Every batched type, in the order their data nodes join the lighting. */
export const BATCHED_LIGHT_TYPES: readonly BatchedLightType[] = [
    'AmbientLight', 'HemisphereLight', 'DirectionalLight', 'PointLight', 'SpotLight',
];

/** The fields the rule reads. All optional, because a light only carries its own type's flag. */
interface ClassifiableLight {
    type: string;
    castShadow: boolean;
    isNode?: boolean;
    isAmbientLight?: boolean;
    isHemisphereLight?: boolean;
    isDirectionalLight?: boolean;
    isPointLight?: boolean;
    isSpotLight?: boolean;
    map?: THREE.Texture | null;
    colorNode?: unknown;
}

/** The batch `light` belongs to, or null when it must stay on three's per-light path. */
export function batchedLightType(light: THREE.Light): BatchedLightType | null {
    const l = light as unknown as ClassifiableLight;
    if (l.isNode === true || l.castShadow === true) return null;
    switch (l.type) {
        case 'AmbientLight': return l.isAmbientLight === true ? 'AmbientLight' : null;
        case 'HemisphereLight': return l.isHemisphereLight === true ? 'HemisphereLight' : null;
        case 'DirectionalLight': return l.isDirectionalLight === true ? 'DirectionalLight' : null;
        case 'PointLight': return l.isPointLight === true ? 'PointLight' : null;
        case 'SpotLight': {
            if (l.isSpotLight !== true) return null;
            if ((l.map ?? null) !== null || l.colorNode !== undefined) return null;
            if ('iesMap' in light || 'aspect' in light) return null;
            return 'SpotLight';
        }
        default: return null;
    }
}
