/**
 * Haski PWA Service Worker
 * - Caches app shell (static assets, routes)
 * - Caches last N analysis results (JSON responses)
 * - Enables offline functionality
 * - Vite-friendly cache versioning
 */

const CACHE_VERSION = "v1";
const SHELL_CACHE = `haski-shell-${CACHE_VERSION}`;
const ANALYSIS_CACHE = `haski-analysis-${CACHE_VERSION}`;
const ANALYSIS_CACHE_SIZE = 10; // Keep last 10 analysis results

/**
 * App shell routes to precache
 */
const SHELL_ROUTES = ["/", "/login", "/signup", "/index.html"];

/**
 * API endpoints to cache (analysis results only)
 */
const ANALYSIS_API_PATHS = [
  "/api/v1/analyze",
  "/api/v1/recommendations",
  "/analysis/history",
];

/**
 * Install event - precache app shell
 */
self.addEventListener("install", (event) => {
  console.log("[Service Worker] Installing...");

  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => {
      console.log("[Service Worker] Caching app shell routes");
      return cache.addAll(SHELL_ROUTES);
    })
  );

  // Activate immediately, don't wait for existing clients to close
  self.skipWaiting();
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener("activate", (event) => {
  console.log("[Service Worker] Activating...");

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // Remove old cache versions
          if (
            (cacheName.startsWith("haski-shell-") &&
              cacheName !== SHELL_CACHE) ||
            (cacheName.startsWith("haski-analysis-") &&
              cacheName !== ANALYSIS_CACHE)
          ) {
            console.log("[Service Worker] Deleting old cache:", cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );

  // Take control of all clients immediately
  self.clients.claim();
});

/**
 * Fetch event - network-first for API, cache-first for static assets
 */
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== "GET") {
    return;
  }

  // Skip chrome extensions and other non-http(s)
  if (!url.protocol.startsWith("http")) {
    return;
  }

  // Handle API requests (analysis data)
  if (url.pathname.includes("/api/")) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Handle static assets and shell routes (cache-first)
  event.respondWith(handleShellRequest(request));
});

/**
 * Handle API requests - network-first, cache as fallback
 * For analysis results, cache them for offline access
 */
async function handleApiRequest(request) {
  const url = new URL(request.url);
  const isAnalysisApi = ANALYSIS_API_PATHS.some((path) =>
    url.pathname.includes(path)
  );

  try {
    // Try network first
    const response = await fetch(request);

    // Cache successful analysis responses
    if (isAnalysisApi && response.ok && request.method === "GET") {
      const cache = await caches.open(ANALYSIS_CACHE);

      // Clone response before caching (can only read once)
      const clonedResponse = response.clone();

      cache.put(request, clonedResponse);

      // Manage cache size - keep only last N responses
      const cacheKeys = await cache.keys();
      if (cacheKeys.length > ANALYSIS_CACHE_SIZE) {
        // Delete oldest (first in list)
        await cache.delete(cacheKeys[0]);
      }
    }

    return response;
  } catch (error) {
    console.log("[Service Worker] Fetch failed, checking cache:", request.url);

    // Fallback to cache for analysis results
    if (isAnalysisApi) {
      const cachedResponse = await caches.match(request);
      if (cachedResponse) {
        console.log("[Service Worker] Serving from analysis cache");
        return cachedResponse;
      }
    }

    // Return offline response
    return new Response(
      JSON.stringify({
        error: "Offline",
        message: "No internet connection. Some features unavailable.",
      }),
      {
        status: 503,
        statusText: "Service Unavailable",
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}

/**
 * Handle shell requests - cache-first strategy
 * For static assets and routes
 */
async function handleShellRequest(request) {
  try {
    // Try cache first
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Then try network
    const response = await fetch(request);

    // Cache successful responses
    if (response && response.status === 200) {
      const cache = await caches.open(SHELL_CACHE);
      cache.put(request, response.clone());
    }

    return response;
  } catch (error) {
    console.log("[Service Worker] Shell request failed:", request.url);

    // Return offline page for navigation requests
    if (request.destination === "document") {
      const cachedResponse = await caches.match("/index.html");
      if (cachedResponse) {
        return cachedResponse;
      }
    }

    // Return offline response
    return new Response(
      `<!DOCTYPE html>
<html>
  <head>
    <title>Offline</title>
    <style>
      body { font-family: system-ui; text-align: center; padding: 40px; }
      h1 { color: #333; }
      p { color: #666; }
    </style>
  </head>
  <body>
    <h1>🌐 You're Offline</h1>
    <p>Please check your internet connection.</p>
    <p>Some features may be unavailable.</p>
  </body>
</html>`,
      {
        status: 503,
        statusText: "Service Unavailable",
        headers: { "Content-Type": "text/html; charset=UTF-8" },
      }
    );
  }
}

/**
 * Message handling - for manual cache clearing from client
 */
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "CLEAR_CACHE") {
    console.log("[Service Worker] Clearing caches");
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName.startsWith("haski-")) {
            return caches.delete(cacheName);
          }
        })
      );
    });
  }
});

console.log("[Service Worker] Ready to serve requests");
