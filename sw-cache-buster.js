// Retired service worker: it now only removes itself.
//
// Older engines registered this worker at scope `/` on localhost to keep work/
// modules fresh. It was not needed and is no longer registered, but a browser that ever ran it keeps
// it installed and re-checks this script on navigation. This version unregisters on activation and
// reloads the pages it controlled, so they come back with no worker in the way. It ships for one
// release, then the file leaves the engine bundle.

self.addEventListener('install', () => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil((async () => {
        await self.registration.unregister();
        const clients = await self.clients.matchAll({ type: 'window' });
        for (const client of clients) {
            if ('navigate' in client) client.navigate(client.url);
        }
    })());
});
