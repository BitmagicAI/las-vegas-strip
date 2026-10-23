import { defineConfig } from 'vite';

// Aliases mirror tsconfig paths but point at the COMPILED output: tsc emits to dist/ and the
// browser loads the emitted JavaScript. Keep these in step with tsconfig.json.
export default defineConfig({
  root: '.',
  base: '/',
  cacheDir: '.vite-cache',
  assetsInclude: ['**/*.wasm'],
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
  server: {
    port: 3001,
    watch: {
      // Vite leaves build.outDir out of its file watcher, but this project SERVES its outDir:
      // every module the browser loads is a tsc emit under dist/. Unwatched, Vite's transform
      // cache keeps serving the PREVIOUS emit after a rebuild until the dev server restarts —
      // edits look like they did nothing. A negated pattern beats Vite's built-in ignore.
      ignored: ['!**/dist/**']
    }
  },
  plugins: [
    {
      // Watching dist/ makes each emit invalidate the stale transform (see server.watch above),
      // but it would also have Vite full-reload the page on the FIRST emitted file of a compile
      // — mid-emit, half the build still old. bitmagic dev reloads the browser itself once the
      // compile lands clean, so Vite's own reaction is swallowed here. The invalidation is not:
      // the module graph is told about the change before this hook runs.
      name: 'bitmagic:defer-dist-reloads',
      handleHotUpdate(context) {
        if (context.file.includes('/dist/')) return [];
      }
    }
  ]
});
