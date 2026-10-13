/* Офлайн-кэш веб-версии «Планировщика».
   Сама страница — «сначала сеть»: новая версия подхватывается сразу, без сети открывается сохранённая.
   Шрифты Google — из кэша (они не меняются). Данные приложения тут не хранятся — они в памяти браузера (localStorage). */
const CACHE = 'planer-web-v1';
const CORE = ['./', './index.html', './manifest.webmanifest', './apple-touch-icon.png', './icon-192.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

function put(req, res){ const cp = res.clone(); caches.open(CACHE).then(c => c.put(req, cp)); return res; }

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {
    const fromCache = () => caches.match(req, { ignoreSearch: true })
      .then(m => m || (req.mode === 'navigate' ? caches.match('./index.html') : undefined));
    e.respondWith(new Promise(resolve => {
      let done = false;
      const timer = setTimeout(() => fromCache().then(m => { if (m && !done) { done = true; resolve(m); } }), 5000);
      fetch(req).then(res => {
        clearTimeout(timer);
        if (res.ok) put(req, res);
        if (!done) { done = true; resolve(res); }
      }).catch(() => {
        clearTimeout(timer);
        fromCache().then(m => { if (!done) { done = true; resolve(m || Response.error()); } });
      });
    }));
  } else if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.match(req).then(m => m || fetch(req).then(res => put(req, res))));
  }
});
