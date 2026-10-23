import fs from 'fs';
import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';
// The engine's physics-mode rule, straight from the vendored engine source (see the Rapier
// flavor block below for why the bundle must use the engine's own rule and nothing else).
import { effectivePhysicsMode, rapierFlavorForPhysicsMode } from './engine/engine/physics/PhysicsModeRule.ts';

// Aliases mirror vite.config.js's, deliberately NOT wrapped in path.resolve(): every target here
// already starts with '/', which Vite resolves as project-root-relative in both serve and build
// mode. A path.resolve(__dirname, target) wrapper looks more "correct" but is actively wrong —
// Node's path.resolve() drops the trailing slash from an already-absolute second argument, and
// Vite's directory-style alias substitution needs that slash to join the replacement with the
// rest of the specifier. Strip it and 'engine/GameTemplate.js' resolves to the nonexistent
// 'dist/engine/engineGameTemplate.js' instead of 'dist/engine/engine/GameTemplate.js' — silently,
// since Rollup then just treats the unmatched id as an unresolved bare specifier and fails the
// build. Verified against a real `vite build` before trusting the plain-string form.

// Single-Rapier-flavor builds: this bundle ships exactly one physics engine (each -compat package
// embeds its full WASM — the unused one is dead megabytes). The flavor is the game's EFFECTIVE
// physics mode: src/work/game.json run through the engine's own rule, the same function the engine
// applies at boot, so the bundle can never disagree with the world the game runs. bitmagic
// build/publish/ios resolve it ahead of time into BUNDLE_RAPIER_FLAVOR, which wins when set. There
// is no dual-flavor build: a game.json this config cannot read fails the build. The stub is safe:
// the engine has no module-scope value usage of either Rapier import, and only ever init()s the
// flavor it boots.
const RAPIER_PACKAGES = { '2d': '@dimforge/rapier2d-compat', '3d': '@dimforge/rapier3d-compat' };
function resolveRapierFlavor() {
  const fromEnv = process.env.BUNDLE_RAPIER_FLAVOR || '';
  if (fromEnv) {
    if (fromEnv !== '2d' && fromEnv !== '3d') {
      throw new Error("BUNDLE_RAPIER_FLAVOR must be '2d' or '3d' when set (got '" + fromEnv + "')");
    }
    return fromEnv;
  }
  let game;
  try {
    game = JSON.parse(fs.readFileSync('src/work/game.json', 'utf8'));
  } catch (err) {
    throw new Error('Cannot decide which physics engine to bundle: src/work/game.json is unreadable (' + err.message + ').');
  }
  const mode = game.physicsMode === '2d' || game.physicsMode === '3d' || game.physicsMode === 'none' ? game.physicsMode : undefined;
  return rapierFlavorForPhysicsMode(effectivePhysicsMode(typeof game.gameGenre === 'string' ? game.gameGenre : '', mode, game.physics2d === true));
}
const rapierFlavor = resolveRapierFlavor();
const droppedRapier = RAPIER_PACKAGES[rapierFlavor === '2d' ? '3d' : '2d'];
// 'pre' is load-bearing: without it Vite's own resolver wins and the "dropped" package is
// INLINED from node_modules — WASM and all, ~2 MB heavier — with no error and no greppable
// package-name string. Same trap the creator-handler stub above documents.
const stubRapierPlugin = () => ({
  name: 'stub-rapier-flavor',
  enforce: 'pre',
  resolveId(id) {
    return id === droppedRapier ? '\0rapier-flavor-stub' : null;
  },
  load(id) {
    return id === '\0rapier-flavor-stub' ? 'export default null;' : null;
  }
});

// Published games never run in creator mode, so the creator<->game command surface (and its
// editor-only dependencies) is dead weight. 'pre' runs before Vite's alias plugin resolves the
// 'engine/' prefix, which is what lets this stub win.
const stubCreatorHandlerPlugin = () => ({
  name: 'stub-creator-handler',
  enforce: 'pre',
  resolveId(id) {
    if (id === 'engine/template/CreatorMessageHandler.js' ||
        id.endsWith('/engine/template/CreatorMessageHandler.js')) {
      return '\0creator-handler-stub';
    }
    return null;
  },
  load(id) {
    if (id === '\0creator-handler-stub') {
      return 'export function registerCreatorMessageListener() {}\n' +
             'export function notifyPhysicsReady() {}\n' +
             'export function flushPendingToolMessages() {}\n';
    }
    return null;
  }
});

// Editing-only asset fields must not ship inside published game data: the
// source recording behind a video-to-motion clip is the creator's webcam
// footage. The list mirrors EDITING_ONLY_ASSET_FIELDS in @bitmagic/asset-core
// (a project build cannot import that package). Runs before Vite's own JSON
// handling so the stripped world is what gets inlined into the bundle.
function stripEditingOnlyWorldFieldsPlugin() {
  return {
    name: 'bitmagic-strip-editing-only-world-fields',
    enforce: 'pre',
    transform(code, id) {
      if (!id.endsWith('/src/work/world.json')) return null;
      try {
        const world = JSON.parse(code);
        if (!Array.isArray(world.assets)) return null;
        for (const asset of world.assets) {
          if (typeof asset !== 'object' || asset === null) continue;
          delete asset.sourceVideoUrl;
          delete asset.trimmedStartSeconds;
          delete asset.trimmedEndSeconds;
        }
        return JSON.stringify(world);
      } catch {
        return null;
      }
    },
  };
}

export default defineConfig({
  // The engine serves world.json/game.json two different ways, and this flag is how it chooses.
  // `utils/worldDataLoader.ts` reads `typeof __BUNDLED__ !== 'undefined' && __BUNDLED__`: true
  // means "the data is inlined in this bundle, import it", false means "fetch it as separate
  // files". A single-file published bundle has no separate files to fetch, so omitting this
  // define does not degrade gracefully — the game boots, then dies at runtime with 404s on
  // src/work/world.json and "world.json not found (neither bundle nor fetch available)".
  //
  // The typeof guard is why nothing catches it at build time: the identifier is genuinely
  // undeclared when /dist is served raw in live-edit mode, so the engine cannot just read it.
  // That makes a missing define invisible until a published game is opened in a browser.
  //
  // Deliberately NOT set in the dev config — live-edit serving must take the fetch path.
  define: { __BUNDLED__: true },
  resolve: {
    alias: {
      'engine/': '/dist/engine/engine/',
      'types/': '/dist/engine/types/',
      'bundle/': '/dist/engine/bundle/',
      'debug/': '/dist/engine/debug/',
      'editor/': '/dist/engine/editor/',
      'core/': '/dist/engine/core/',
      'genres/': '/dist/engine/genres/',
      'work/': '/dist/src/work/'
    }
  },
  build: {
    // Effectively unlimited: everything the bundle references locally is inlined so the
    // published artifact is a single file. Game assets are absolute CDN URLs and are untouched.
    assetsInlineLimit: 100000000,
    cssCodeSplit: false,
    rollupOptions: {
      // No 'external' and no CDN rewriting: three.js, Rapier and the rest are bundled in, which is
      // the entire difference between this config and vite.publish.config.js.
      //
      // The import map in index.html stays even though nothing needs it here. Two of its entries
      // are what api-server reads back out of the uploaded bundle to confirm this is a real engine
      // build; strip the map and every publish of this bundle is refused.
      output: {
        inlineDynamicImports: true,
        // A licence obligation, not decoration — see engine/LICENSE.md. This bundle contains
        // compiled engine code and the third-party libraries it uses, whose licences
        // require their notices to travel with any copy. Removing this banner puts your published
        // game out of compliance.
        banner: "/*!\n * Made with Bitmagic — https://bitmagic.ai\n *\n * This bundle includes the Bitmagic engine.\n * Required Notice: Copyright Bitmagic Oy (https://bitmagic.ai)\n * Licensed under the PolyForm Shield License 1.0.0\n * <https://polyformproject.org/licenses/shield/1.0.0>, with an additional permission\n * granting the right to build, modify, sell and distribute games. Full terms:\n * https://bitmagic.ai/terms-of-service\n *\n * Third-party software included in this bundle:\n *   three.js — MIT — Copyright (c) 2010-2026 three.js authors\n *   @dimforge/rapier2d-compat, @dimforge/rapier3d-compat — Apache License 2.0\n *   @msgpack/msgpack — ISC — Copyright 2019 The MessagePack Community\n *   fflate — MIT — Copyright (c) 2023 Arjun Barrett\n *   i18next, i18next-browser-languagedetector — MIT — Copyright (c) 2025 i18next\n *   JSZip — MIT (elected) — Copyright (c) 2009-2016 Stuart Knightley and contributors\n * Full licence texts: THIRD-PARTY-NOTICES.md in the Bitmagic engine distribution.\n */",
      },
    },
  },
  plugins: [stubCreatorHandlerPlugin(), stripEditingOnlyWorldFieldsPlugin(), stubRapierPlugin(), viteSingleFile()],
});
