/// <reference lib="webworker" />

declare const self: ServiceWorkerGlobalScope;

self.addEventListener("install", (_event: ExtendableEvent) => {
  console.log("[Service Worker] Installing...");
  self.skipWaiting();
});

self.addEventListener("activate", (_event: ExtendableEvent) => {
  console.log("[Service Worker] Activating...");
  self.clients.claim();
});

self.addEventListener("fetch", (_event: FetchEvent) => {
  console.log("[Service Worker] Fetching:", _event.request.url);
});

export {};
