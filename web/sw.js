/* Service worker minimo: garante instalabilidade e da um fallback
   offline. Estrategia network-first (o jogo sempre pega a versao nova
   quando ha internet; cache so quando a rede falha). */
var CACHE = "chovelafora-v1";

self.addEventListener("install", function (e) {
  self.skipWaiting();
});

self.addEventListener("activate", function (e) {
  e.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  /* So mesma origem: o runtime do pygbag vem de CDN e cuida de si */
  if (new URL(e.request.url).origin !== self.location.origin) return;

  e.respondWith(
    fetch(e.request)
      .then(function (resp) {
        var copia = resp.clone();
        caches.open(CACHE)
          .then(function (c) { c.put(e.request, copia); })
          .catch(function () {});
        return resp;
      })
      .catch(function () { return caches.match(e.request); })
  );
});
