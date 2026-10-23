// Service Worker for automatic cache busting of work files
// This intercepts all requests to work files and adds cache busting automatically

const CACHE_NAME = 'cache-buster-v3';

// The busting parameter must NOT be `v`. A `bitmagic dev` project is served by Vite, and Vite
// reserves `?v=` for pre-bundled dependency versions: any URL matching /[?&](v=[\w.-]+)\b/ is
// answered with `Cache-Control: max-age=31536000,immutable`. This worker used to bust with
// `?v=<timestamp>` and hand that response back for the PLAIN module URL, so the browser kept every
// game module across ordinary reloads — the cache buster was what made edits look like they did
// nothing. `cb` means nothing to Vite, which serves it `no-cache`.
const BUST_PARAM = 'cb';

// Check if this is a work file that needs cache busting
function isWorkFile(url) {
    // Path segments only — a looser "contains 'work'" match also caught engine modules such as
    // engine/networking/*.js and kept them from ever being cached.
    const path = new URL(url).pathname;
    return path.includes('/src/work/') || path.includes('/work/');
}

// Check if we're in development mode
function isDevelopment() {
    return self.location.hostname === 'localhost' ||
           self.location.hostname === '127.0.0.1' ||
           self.location.port === '8080' ||
           self.location.port === '3001';
}

self.addEventListener('install', (event) => {
    console.log('[SW] Cache Buster Service Worker installed');
    // Force the service worker to become active immediately
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('[SW] Cache Buster Service Worker activated');
    // Take control of all clients (pages) immediately
    event.waitUntil(
        self.clients.claim().then(() => {
            console.log('[SW] Service worker now controlling all pages');
        })
    );
});

self.addEventListener('fetch', (event) => {
    const url = event.request.url;

    // Only handle work files in development
    if (!isDevelopment() || !isWorkFile(url)) {
        return; // Let the browser handle normally
    }

    event.respondWith(
        (async () => {
            try {
                // Add cache busting if not already present
                let requestUrl = url;
                if (!url.includes(`?${BUST_PARAM}=`) && !url.includes(`&${BUST_PARAM}=`)) {
                    const separator = url.includes('?') ? '&' : '?';
                    requestUrl = `${url}${separator}${BUST_PARAM}=${Date.now()}`;
                }


                // Make the request with cache busting
                // Create a new Request to properly copy properties from the original
                const newRequest = new Request(requestUrl, {
                    method: event.request.method,
                    headers: event.request.headers,
                    mode: 'cors',
                    credentials: event.request.credentials,
                    cache: 'no-cache',
                    redirect: event.request.redirect,
                    referrer: event.request.referrer,
                });
                const response = await fetch(newRequest);

                // Whatever the server said about caching, the page must never keep a work file:
                // re-issue the response with caching switched off, so neither the HTTP cache nor
                // the renderer's memory cache can serve a previous build. (A URL that arrives
                // already carrying `?v=` — GenreLoader's entry import — still comes back from Vite
                // marked immutable; this is what keeps that harmless.)
                const headers = new Headers(response.headers);
                headers.set('Cache-Control', 'no-store');
                return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
            } catch (error) {
                console.error('[SW] Failed to fetch with cache busting:', error);
                // Fallback to original request
                return fetch(event.request);
            }
        })()
    );
});
