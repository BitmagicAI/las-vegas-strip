// Installed 2026-10-07 from tools/optimize/GltfDecoders.ts.txt; imported FIRST by src/work/Game.ts.
//
// WHY. The optimized GLBs in build/optimized/ (see OptimizedGlb.ts) are EXT_meshopt_compression files (the encoder
// marks the extension REQUIRED). A GLTFLoader with no meshopt decoder throws
// "THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files".
// This game builds its loaders with a bare `new GLTFLoader()` at ten call sites (GeographicCity,
// StripLandmarks x2, HighriseCity, BigAppleCoaster x2, SphereVenue x2, HotelTemplates, ResortFoliage),
// and the vendored engine's createGltfLoader() (MeshLevel, SanctuaryJeep, VegasCharacter, engine.loader
// for spawned assets and doors) attaches KTX2 only: `grep -c setMeshoptDecoder
// engine/engine/loaders/GltfLoaderSupport.ts` prints 0. Game code cannot reach the engine's loaders,
// so the decoder is attached where every loader passes: GLTFLoader.prototype.parse. GLTFLoader reads
// `this.meshoptDecoder` when it PARSES (it hands it to the GLTFParser), not when it is constructed,
// so loaders built before this module ran (the engine's shared one) are covered too.
//
// TWO MODULE INSTANCES. index.html's import map sends 'three/addons/' and 'three/examples/jsm/' to
// two different esm.sh URLs, and the engine imports GLTFLoader through both specifiers. Two URLs can
// be two module instances with two prototypes, so both are patched (once each; a shared prototype
// is patched once).
//
// WHAT IT NEVER DOES. It never replaces a decoder a loader already has (setMeshoptDecoder wins),
// and it adds no KTX2 handling: no optimized candidate uses KTX2 (there is no ktx binary on this
// machine and this engine lacks the KTX2 boot-race wait, `expectGltfLoaderSupport`).
//
// DELETE IT once `bitmagic upgrade` brings an engine whose GltfLoaderSupport.ts attaches the meshopt
// decoder (SKILL.md step 5: `grep -c setMeshoptDecoder engine/engine/loaders/GltfLoaderSupport.ts` > 0)
// AND every bare `new GLTFLoader()` in src/work/ has become createGltfLoader().
//
// PUBLISHING. In the CDN lane 'three/addons/libs/meshopt_decoder.module.js' is one more esm.sh
// request (~8 KB gzip, the WebAssembly is embedded); single-file builds inline it. Squall Riders and
// Trick or Roll vendored a copy into src/ so their publish bundles it instead of fetching it.
// The dev asset panel runs no game code, so it cannot open meshopt files: verify in the game.
import { GLTFLoader as AddonsGLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { GLTFLoader as ExamplesGLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
// Decode in worker threads (2026-10-25): decoding ran on the main thread inside each parse, up to ~1.5 s for one
// landmark, which stalls the game once the city loads behind play. Blob workers; nothing else changes.
try { MeshoptDecoder.useWorkers(Math.max(1, Math.min(4, (navigator.hardwareConcurrency || 4) - 1))); } catch { /* the main-thread decoder stays */ }

type Parse = AddonsGLTFLoader['parse'];

/** Called with every parsed glTF scene before its loader's callback sees it (RealisticWater swaps water materials here,
 * so every asset gets them whatever loader brought it in). Added 2026-10-08. */
export const gltfSceneHooks: ((scene: import('three').Object3D) => void)[] = [];
/** Called after the scene hooks for every glTF loaded by URL (`load`/`loadAsync`), with that URL (PbrDetail decides by
 * the asset's path). Added 2026-10-08. */
export const gltfUrlHooks: ((scene: import('three').Object3D, url: string) => void)[] = [];
type Load = AddonsGLTFLoader['load'];
interface PatchedPrototype { parse: Parse; load: Load; decoderNotice?: string }

function attachMeshoptOnParse(proto: PatchedPrototype): void {
    if (proto.decoderNotice) return;   // already patched (the two specifiers share one module)
    // Kept as a string: minifiers strip the decoder's licence comment, and MIT asks for the notice.
    proto.decoderNotice = 'meshoptimizer decoder, MIT License, Copyright (c) Arseny Kapoulkine';
    const parse = proto.parse;
    proto.parse = function (this: AddonsGLTFLoader, ...args: Parameters<Parse>): void {
        const self = this as unknown as { meshoptDecoder: unknown };
        self.meshoptDecoder ??= MeshoptDecoder;   // read by parse(), so a late attach still counts
        const onLoad = args[2];
        if (gltfSceneHooks.length && typeof onLoad === 'function') {
            args[2] = ((gltf: { scene?: import('three').Object3D }) => {
                if (gltf.scene) for (const hook of gltfSceneHooks) { try { hook(gltf.scene); } catch (e) { console.warn('[GltfDecoders] scene hook failed', e); } }
                onLoad(gltf as never);
            }) as typeof onLoad;
        }
        return parse.apply(this, args);
    } as Parse;
    const load = proto.load;
    proto.load = function (this: AddonsGLTFLoader, ...args: Parameters<Load>): void {
        const onLoad = args[1], url = String(args[0]);
        if (gltfUrlHooks.length && typeof onLoad === 'function') {
            args[1] = ((gltf: { scene?: import('three').Object3D }) => {
                if (gltf.scene) for (const hook of gltfUrlHooks) { try { hook(gltf.scene, url); } catch (e) { console.warn('[GltfDecoders] url hook failed', e); } }
                onLoad(gltf as never);
            }) as typeof onLoad;
        }
        return load.apply(this, args);
    } as Load;
}

attachMeshoptOnParse(AddonsGLTFLoader.prototype as unknown as PatchedPrototype);
attachMeshoptOnParse(ExamplesGLTFLoader.prototype as unknown as PatchedPrototype);
