const CACHE = 'gta6-leonida-v1';
const CORE = [
  './', './index.html', './app.js', './style.css', './manifest.webmanifest',
  './assets/hero.png', './assets/loading_screen.png', './assets/logo.png', './assets/keyart.jpg', './assets/manifest.json',
  '../environment.json'
];
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE.map(u => new Request(u, {cache:'reload'}))).catch(()=>{})).then(()=>self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));
    return;
  }
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request).then(resp => {
      const copy = resp.clone();
      if (resp.ok && (url.origin === location.origin)) caches.open(CACHE).then(c=>c.put(e.request, copy)).catch(()=>{});
      return resp;
    }).catch(()=>cached || caches.match('./index.html')))
  );
});
