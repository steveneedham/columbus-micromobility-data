const CACHE_PREFIX = "columbus-mobility-observer-";
const CACHE_NAME = `${CACHE_PREFIX}v2`;

const CORE_ASSETS = [
  "./index.html",
  "./research-library.html",
  "./manifest.webmanifest",
  "./assets/field-ledger-mark.svg",
  "./assets/columbus-ride-hub-marker.svg",
  "./assets/pwa-icon-192.png",
  "./assets/pwa-icon-512.png",
  "./data-311.json",
  "./data-gbfs.json",
  "./data-gbfs-observations.json",
  "./data-policy.json",
  "./data-mds-geographies.json",
  "./data-ride-hubs.json",
  "./data-osu-boundary.json",
  "./demand-forecast-card.svg",
  "./claude-demand-forecast-card.svg",
  "./demand-forecast-chart.svg",
  "./claude-demand-forecast-chart.svg"
];

const OPTIONAL_ASSETS = [
  "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,500&display=swap"
];

self.addEventListener("install", event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await cache.addAll(CORE_ASSETS);
    await Promise.all(OPTIONAL_ASSETS.map(async asset => {
      try {
        const response = await fetch(asset, { mode: "cors" });
        if (response.ok) await cache.put(asset, response);
      } catch {
        // Optional third-party assets can be filled by runtime caching later.
      }
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names
      .filter(name => name.startsWith(CACHE_PREFIX) && name !== CACHE_NAME)
      .map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});

async function networkFirst(request, fallbackUrl) {
  const cache = await caches.open(CACHE_NAME);
  const requestUrl = new URL(request.url);
  const normalizedKey = requestUrl.origin === self.location.origin
    ? `${requestUrl.origin}${requestUrl.pathname}`
    : request;
  try {
    // Bypass the HTTP cache so a stale GitHub Pages copy can't be revalidated into the SW cache.
    const response = await fetch(request, { cache: "no-store" });
    if (response && response.ok) await cache.put(normalizedKey, response.clone());
    return response;
  } catch {
    return (await cache.match(normalizedKey))
      || (fallbackUrl && await cache.match(fallbackUrl))
      || Response.error();
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request, { ignoreSearch: true });
  if (cached) return cached;
  const response = await fetch(request);
  if (response && (response.ok || response.type === "opaque")) {
    await cache.put(request, response.clone());
  }
  return response;
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request, { ignoreSearch: true });
  const update = fetch(request).then(response => {
    if (response && (response.ok || response.type === "opaque")) {
      cache.put(request, response.clone());
    }
    return response;
  }).catch(() => null);
  return cached || await update || Response.error();
}

self.addEventListener("fetch", event => {
  const { request } = event;
  if (request.method !== "GET") return;
  const url = new URL(request.url);

  if (request.mode === "navigate") {
    const fallback = url.pathname.endsWith("/research-library.html")
      ? "./research-library.html"
      : "./index.html";
    event.respondWith(networkFirst(request, fallback));
    return;
  }

  if (url.origin === self.location.origin) {
    if (url.pathname.endsWith(".json") || url.pathname.endsWith(".html")) {
      event.respondWith(networkFirst(request));
    } else {
      event.respondWith(cacheFirst(request));
    }
    return;
  }

  if (url.hostname === "unpkg.com"
      || url.hostname === "fonts.googleapis.com"
      || url.hostname === "fonts.gstatic.com"
      || url.hostname.includes("tile.openstreetmap.org")) {
    event.respondWith(staleWhileRevalidate(request));
  }
});
