// EXPERIMENT (2026-10-07): copied unchanged from the Aitopia5 working tree, game/src/engine/lighting/ (uncommitted
// there on 2026-10-07; imports made relative)
// to measure the new engine lighting in this game. Not used by the game; loaded only by the local ?lighting=engine<cap>
// switch in Game.ts. Remove with that switch once the vendored engine ships EngineLighting (bitmagic upgrade).
import type * as THREE from 'three';
import { Lighting, LightsNode, NodeUtils } from 'three/webgpu';
import type { LightingNode, NodeBuilder, NodeFrame, WebGPURenderer } from 'three/webgpu';
import { NodeUpdateType } from 'three/tsl';
import { BATCHED_LIGHT_TYPES, batchedLightType, type BatchedLightType } from './LightBatching.js';
import { BatchedLightsNode } from './BatchedLightsNode.js';

/**
 * EngineLighting — the node renderer's lighting system (`renderer.lighting`), installed by
 * `GameEngine.createRenderer` for `WebGPURenderer` on both of its backends.
 *
 * ── The stall it removes ───────────────────────────────────────────────────
 * Every render object's cache key includes the SCENE's lights node (`NodeManager.getCacheKey`
 * hashes `renderList.lightsNode` — never a material's own `lightsNode` override), and three's
 * default `LightsNode` keys on every light's id and `castShadow`. So one light added, removed
 * or hidden re-keys every lit material at once, and the rebuild runs inside `render()`:
 * 0.3–2.9 s freezes in shipped games.
 *
 * ── How ────────────────────────────────────────────────────────────────────
 * Modelled on three's `DynamicLighting` addon (its dev-branch shape: builtin lights through the
 * base class, batched lights appended). Lights `batchedLightType` accepts go into one
 * `BatchedLightsNode` — a fixed-size uniform array the shader loops over with count uniforms —
 * so their number is a uniform, not part of the shader. A hidden batched light is not in the
 * loop at all, so it costs nothing. Shadow casters and the other per-light kinds keep three's
 * path and its key.
 *
 * What the addon as r186 ships gets wrong here, each fatal on its own:
 * - it classifies lights by `constructor.name`, which minified three renames — under the
 *   esm.sh build games load it batches nothing (see LightBatching);
 * - its `setupLightsNode` drops `builder.context.materialLightings`: environment (IBL), light
 *   maps, AO and GI vanish from every material;
 * - each light type takes 2–4 uniform-buffer bindings, 12 in all with every type present,
 *   which pushes lit materials past WebGPU's 12-per-stage limit (pipelines fail to build).
 *   `BatchedLightsNode` packs everything into one binding;
 * - it creates a type's data on that type's first light, which re-keys once. Here every type
 *   exists from construction, so no batched light can ever change the key.
 *
 * Over a type's cap the lights nearest the camera win (the addon took scene order).
 *
 * The base class's own methods are reused by swapping the builtin list into `_lights` for the
 * duration of the call (`withBuiltinLights`). r185 reads `_lights` directly and r186 reads it
 * through `getBuiltinLights()`; the swap is correct for both, which matters because projects on
 * the GDK lane run their own three version.
 *
 * The classic `WebGLRenderer` is untouched: it keys programs on per-type light COUNTS, so
 * constant counts remain its guarantee (see LightManager).
 */

export interface EngineLightingOptions {
    /** Batched point lights per scene; beyond it the nearest to the camera are lit. */
    maxPointLights: number;
    /** Batched spot lights per scene. */
    maxSpotLights: number;
    /** Batched non-shadow directional lights per scene. The shadowed sun is not one of them. */
    maxDirectionalLights: number;
    /** Batched hemisphere lights per scene. */
    maxHemisphereLights: number;
}

/**
 * Generous on purpose: a cap is a fixed uniform-array size, and only the lights actually present
 * are looped over, so headroom costs a few kilobytes of uniforms and no shading. The
 * LightManager's budget, not this, is what bounds per-pixel cost.
 */
export const DEFAULT_ENGINE_LIGHTING_OPTIONS: EngineLightingOptions = {
    maxPointLights: 64,
    maxSpotLights: 16,
    maxDirectionalLights: 8,
    maxHemisphereLights: 4,
};

/** `?lighting=three` keeps three's default lighting, for A/B comparison on a live game. */
const KEEP_THREE_LIGHTING_PARAM = 'lighting';

/** The base class's light list, which three's typings keep private. */
interface LightsNodeInternals {
    _lights: THREE.Light[];
}

function capsFrom(options: EngineLightingOptions): Record<BatchedLightType, number> {
    return {
        // Ambient lights are summed into one colour; there is no array to overflow.
        AmbientLight: Number.POSITIVE_INFINITY,
        HemisphereLight: options.maxHemisphereLights,
        DirectionalLight: options.maxDirectionalLights,
        PointLight: options.maxPointLights,
        SpotLight: options.maxSpotLights,
    };
}

let batchedTypesKey: number | null = null;

/**
 * Hash of the (constant) batched type set, folded into every key so it differs from three's.
 * Computed on first use: nothing from the node system may run at module load (Jest stubs it).
 */
function batchedTypesHash(): number {
    batchedTypesKey ??= NodeUtils.hashArray(BATCHED_LIGHT_TYPES.map((t) => NodeUtils.hashString(t)));
    return batchedTypesKey;
}

/**
 * The scene lights node `EngineLighting` creates. Fields start with `_` so
 * `Node.getCacheKey`'s child traversal skips them — the key is exactly `customCacheKey`.
 */
export class EngineLightsNode extends LightsNode {
    static get type(): string {
        return 'EngineLightsNode';
    }

    private readonly _caps: Readonly<Record<BatchedLightType, number>>;
    private readonly _batch: BatchedLightsNode;
    /** Every visible light of each batched type this frame. */
    private readonly _batched = new Map<BatchedLightType, THREE.Light[]>();
    /** At most the cap of each type: what the batch node loops over. */
    private readonly _shown = new Map<BatchedLightType, THREE.Light[]>();
    /** Lights on three's per-light path. These alone shape the key. */
    private readonly _builtin: THREE.Light[] = [];
    /** Types over their cap this frame; `updateBefore` picks the nearest for them. */
    private readonly _overCap: BatchedLightType[] = [];
    private readonly _warnedOverCap = new Set<BatchedLightType>();
    private readonly _rankDistances = new Map<THREE.Light, number>();
    /**
     * Latches on the first batched light. Before it, a light-less scene renders lit materials
     * unlit (three's no-lights path); after it they stay lit, even with every light gone, so a
     * light leaving can never re-key. Part of the key, so it flips exactly once per scene.
     */
    private _sawBatchedLight = false;

    constructor(options: EngineLightingOptions) {
        super();
        this._caps = capsFrom(options);
        this._batch = new BatchedLightsNode({
            DirectionalLight: options.maxDirectionalLights,
            PointLight: options.maxPointLights,
            SpotLight: options.maxSpotLights,
            HemisphereLight: options.maxHemisphereLights,
        });
        for (const type of BATCHED_LIGHT_TYPES) {
            this._batched.set(type, []);
            this._shown.set(type, []);
        }
        this.updateBeforeType = NodeUpdateType.RENDER;
    }

    /** Called by the render list every frame with the scene's visible lights. */
    override setLights(lights: THREE.Light[]): this {
        this._builtin.length = 0;
        for (const list of this._batched.values()) list.length = 0;
        for (const light of lights) {
            const type = batchedLightType(light);
            if (type === null) this._builtin.push(light);
            else this._batched.get(type)!.push(light);
        }
        this._overCap.length = 0;
        for (const type of BATCHED_LIGHT_TYPES) {
            const all = this._batched.get(type)!;
            const shown = this._shown.get(type)!;
            if (all.length > 0) this._sawBatchedLight = true;
            const cap = this._caps[type];
            shown.length = 0;
            // Scene order until updateBefore has a camera to rank by.
            for (let i = 0; i < all.length && i < cap; i++) shown.push(all[i]!);
            if (all.length > cap) this._overCap.push(type);
            this._batch.setLights(type, shown);
        }
        return super.setLights(lights);
    }

    /** Lights compiled into the shader one by one — three's `getBuiltinLights` (r186+). */
    getBuiltinLights(): THREE.Light[] {
        return this._builtin;
    }

    override get hasLights(): boolean {
        return this._sawBatchedLight || this._builtin.length > 0;
    }

    override customCacheKey(): number {
        const builtinKey = this.withBuiltinLights(() => super.customCacheKey());
        return NodeUtils.hashArray([builtinKey, batchedTypesHash(), this._sawBatchedLight ? 1 : 0]);
    }

    override setupLightsNode(builder: NodeBuilder): LightingNode[] {
        // The base class adds the material lightings (environment, light map, AO, GI) and
        // the builtin lights; the batched loops are appended after them.
        const lightNodes = this.withBuiltinLights(() => super.setupLightsNode(builder));
        lightNodes.push(this._batch as unknown as LightingNode);
        return lightNodes;
    }

    /** Runs once per render, before the batch node copies its lights into the uniforms. */
    override updateBefore(frame: NodeFrame): boolean | undefined {
        const camera = frame.camera;
        if (this._overCap.length === 0 || !camera) return undefined;
        const e = camera.matrixWorld.elements;
        for (const type of this._overCap) this.showNearest(type, e[12]!, e[13]!, e[14]!);
        return undefined;
    }

    private showNearest(type: BatchedLightType, cx: number, cy: number, cz: number): void {
        const all = this._batched.get(type)!;
        const shown = this._shown.get(type)!;
        const cap = this._caps[type];
        const distances = this._rankDistances;
        distances.clear();
        for (const light of all) {
            const m = light.matrixWorld.elements;
            const dx = m[12]! - cx, dy = m[13]! - cy, dz = m[14]! - cz;
            distances.set(light, dx * dx + dy * dy + dz * dz);
        }
        shown.length = 0;
        for (const light of all) shown.push(light);
        shown.sort((a, b) => distances.get(a)! - distances.get(b)!);
        shown.length = cap;
        this._batch.setLights(type, shown);
        if (!this._warnedOverCap.has(type)) {
            this._warnedOverCap.add(type);
            console.warn(`💡 EngineLighting: ${all.length} ${type}s are visible but the cap is ${cap}; `
                + 'the nearest to the camera are lit. Add lights through engine.getLightManager() '
                + 'so the engine ranks them and fades the swaps.');
        }
    }

    private withBuiltinLights<T>(fn: () => T): T {
        const self = this as unknown as LightsNodeInternals;
        const all = self._lights;
        self._lights = this._builtin;
        try {
            return fn();
        } finally {
            self._lights = all;
        }
    }
}

/** `renderer.lighting` for the node renderer. One `EngineLightsNode` per scene. */
export class EngineLighting extends Lighting {
    private readonly options: EngineLightingOptions;

    constructor(options: EngineLightingOptions) {
        super();
        this.options = options;
    }

    override createNode(lights: THREE.Light[] = []): LightsNode {
        return new EngineLightsNode(this.options).setLights(lights);
    }
}

/**
 * Install `EngineLighting` on a freshly constructed node renderer — before its first render,
 * since lights nodes made by the previous lighting system would stay in use.
 */
export function installEngineLighting(renderer: WebGPURenderer, options: EngineLightingOptions): void {
    if (keepThreeLighting()) {
        console.log('💡 ?lighting=three — keeping three.js default lighting (light changes re-key materials)');
        return;
    }
    renderer.lighting = new EngineLighting(options);
}

/** Whether `renderer` batches lights, i.e. changing how many are visible costs nothing. */
export function rendererBatchesLights(renderer: unknown): boolean {
    return (renderer as { lighting?: unknown } | null)?.lighting instanceof EngineLighting;
}

function keepThreeLighting(): boolean {
    if (typeof window === 'undefined') return false;
    return new URLSearchParams(window.location.search).get(KEEP_THREE_LIGHTING_PARAM) === 'three';
}
