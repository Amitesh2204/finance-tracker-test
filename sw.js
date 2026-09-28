const CACHE_NAME = 'finance-test-v3';
const BASE = new URL('./', self.registration.scope).pathname;
const FILES = [BASE, BASE + 'index.html', BASE + 'frontend/style.css', BASE + 'frontend/manifest.json', BASE + 'frontend/assets/logo.svg'];
self.addEventListener('install', event => { event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(FILES)).catch(() => {})); self.skipWaiting(); });
self.addEventListener('activate', event => { event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  event.respondWith(fetch(event.request).then(response => { const copy=response.clone(); caches.open(CACHE_NAME).then(c=>c.put(event.request,copy)); return response; }).catch(() => caches.match(event.request).then(r => r || caches.match(BASE))));
});
