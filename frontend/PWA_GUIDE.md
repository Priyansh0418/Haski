# PWA - Progressive Web App Implementation

## Overview

Haski now includes full Progressive Web App (PWA) support for offline functionality and app-like experience.

### Features

- ✅ **Offline Support** - App shell cached, last 10 analyses available offline
- ✅ **App Installation** - Install as native app on mobile/desktop
- ✅ **Auto Updates** - Service worker checks for updates
- ✅ **Fast Loading** - Cache-first strategy for static assets
- ✅ **Network-First API** - Always tries network for fresh data
- ✅ **Manifest Integration** - Web app manifest with icons and shortcuts
- ✅ **Apple iOS Support** - Compatible with iOS home screen

---

## Architecture

### Service Worker (`service-worker.js`)

**App Shell Cache:**

- Precaches: `/`, `/login`, `/signup`, `/index.html`
- Strategy: Cache-first (uses cached version if available)
- Purpose: Fast loading, offline access to core routes

**Analysis Cache:**

- Caches: GET `/api/v1/analyze`, `/api/v1/recommendations`, `/analysis/history`
- Keeps: Last 10 responses
- Strategy: Network-first (tries network first, fallback to cache)
- Purpose: Offline access to analysis results

**Static Assets:**

- Strategy: Cache-first for CSS, JS, images
- Fallback: Network if not cached

---

## Usage

### Automatic Registration

Service worker registers automatically in production:

```tsx
// frontend/src/main.tsx
import { registerServiceWorker } from "./lib/pwa";

registerServiceWorker(); // Auto-registers when running as PWA
```

### Manual PWA Utilities

```tsx
import {
  registerServiceWorker,
  unregisterServiceWorker,
  clearServiceWorkerCache,
  isServiceWorkerActive,
  getCacheStats,
  updateServiceWorker,
} from "./lib/pwa";

// Check if service worker is active
if (isServiceWorkerActive()) {
  console.log("PWA is ready!");
}

// Get cache statistics (for debugging)
const stats = await getCacheStats();
console.log("Cache stats:", stats);

// Clear all caches manually
await clearServiceWorkerCache();

// Update service worker
await updateServiceWorker();

// Unregister (development only)
await unregisterServiceWorker();
```

---

## Installation

### Desktop (Chrome)

1. Open https://haski.app
2. Click install icon in address bar
3. Or: Menu → Install app

### Mobile (Android)

1. Open https://haski.app
2. Tap menu (three dots)
3. Tap "Install app" or "Add to Home Screen"
4. Choose home screen location

### iOS

1. Open in Safari
2. Tap Share button
3. Tap "Add to Home Screen"
4. Creates app shortcut on home screen

---

## Offline Behavior

### When Online

- ✅ All features work normally
- ✅ Fresh data from server
- ✅ Analysis results cached for later

### When Offline

- ✅ App shell accessible (dashboard, UI visible)
- ✅ Last 10 analysis results viewable
- ✅ Navigation works
- ❌ New analyses not possible (network required)
- ❌ New recommendations not available

---

## Cache Management

### Cache Locations

| Cache               | Purpose                   | Size    |
| ------------------- | ------------------------- | ------- |
| `haski-shell-v1`    | App shell & static assets | Auto    |
| `haski-analysis-v1` | Last 10 analysis results  | ~500 KB |

### Clear Cache

```tsx
// Option 1: From Settings page
import { clearServiceWorkerCache } from "../lib/pwa";
await clearServiceWorkerCache();

// Option 2: Browser DevTools
// Applications → Storage → Cache Storage → Delete haski-* caches

// Option 3: Automatic
// Happens on service worker update (old caches deleted)
```

### Cache Size Management

- Analysis cache keeps only last 10 responses
- Oldest automatically deleted when new ones added
- Total footprint: ~500 KB - 1 MB

---

## Web App Manifest

**File:** `public/manifest.json`

Configures:

- App name and icon
- Display mode (standalone/fullscreen)
- Theme colors
- App shortcuts (Analyze, Dashboard)
- Screenshots

---

## Testing PWA

### Test Offline Mode

1. Open DevTools (F12)
2. Go to Application → Service Workers
3. Check "Offline" checkbox
4. Refresh page
5. App should still load (shell only)

### Test Service Worker

1. DevTools → Application → Service Workers
2. Should show "Service Worker registered"
3. Click "Update on reload" to test updates
4. Manually refresh or close/reopen

### Test Installation

1. Open in Chrome/Edge
2. Address bar should show install icon
3. Click to install as app
4. Opens in standalone window

### Cache Inspection

```tsx
// In browser console
// List all caches
caches.keys().then((names) => console.log(names));

// Check shell cache contents
caches.open("haski-shell-v1").then((cache) => {
  cache.keys().then((requests) => {
    console.log(
      "Shell cache:",
      requests.map((r) => r.url)
    );
  });
});

// Check analysis cache
caches.open("haski-analysis-v1").then((cache) => {
  cache.keys().then((requests) => {
    console.log(
      "Analysis cache:",
      requests.map((r) => r.url)
    );
  });
});
```

---

## Performance Impact

### Before PWA

- First load: ~2-3 seconds
- Repeat visits: ~1-2 seconds
- Network required

### After PWA

- First load: ~2-3 seconds (unchanged)
- Repeat visits: ~500ms (cached)
- Works offline (shell + cached data)

### Bundle Size

- Service Worker: ~3 KB
- PWA utilities: ~2 KB
- Manifest: ~2 KB
- **Total: ~7 KB**

---

## Deployment Checklist

- ✅ HTTPS required (PWA only works on HTTPS)
- ✅ Manifest configured
- ✅ Service worker registered
- ✅ Icons generated
- ✅ Theme colors set
- ✅ App shortcuts defined
- ✅ Offline page configured
- ✅ Cache versioning in place

---

## File Structure

```
frontend/
├── public/
│   ├── service-worker.js      ← Service worker logic
│   └── manifest.json          ← Web app manifest
├── src/
│   ├── lib/
│   │   └── pwa.ts             ← PWA utilities & registration
│   ├── main.tsx               ← Registers service worker
│   └── index.css
└── index.html                 ← Links manifest & meta tags
```

---

## Browser Support

| Browser          | Desktop | Mobile | Notes              |
| ---------------- | ------- | ------ | ------------------ |
| Chrome           | ✅      | ✅     | Full PWA support   |
| Edge             | ✅      | ✅     | Full PWA support   |
| Firefox          | ✅      | ✅     | Full PWA support   |
| Safari           | ❌      | ⚠️     | Limited (iOS only) |
| Samsung Internet | ❌      | ✅     | Full PWA support   |

---

## Common Issues

### Service Worker Not Registering

- Ensure HTTPS is enabled
- Check browser console for errors
- Verify `import.meta.env.PROD` is true
- Clear browser cache and restart

### Cache Not Clearing

```tsx
// Force clear from client
await clearServiceWorkerCache();

// Or manually from DevTools
// Application → Storage → Clear site data
```

### Offline Mode Not Working

1. Check DevTools → Service Workers
2. Verify service worker is "activated"
3. Check Network tab in DevTools
4. Ensure HTTPS is enabled

### Installation Not Showing

- Must be HTTPS
- Must have manifest.json
- Must have service worker
- Must have icons
- Site must be visited >2 times

---

## Advanced Usage

### Check Cache Statistics

```tsx
const stats = await getCacheStats();
console.log("Shell cache:", stats["haski-shell-v1"]);
console.log("Analysis cache:", stats["haski-analysis-v1"]);
```

### Manual Update Check

```tsx
await updateServiceWorker();
// Will check for new version every 24 hours or on demand
```

### Listen for Updates

```tsx
navigator.serviceWorker.addEventListener("controller", () => {
  console.log("New service worker activated");
  // Show toast: "App updated, refresh to see changes"
});
```

---

## Future Enhancements

- [ ] Background sync (upload analyses when online)
- [ ] Push notifications for recommendations
- [ ] Periodic analysis reminders
- [ ] Desktop app via Electron
- [ ] Share to native apps
- [ ] Badge notifications

---

## References

- [MDN - Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web.dev - PWA](https://web.dev/progressive-web-apps/)
- [Google - PWA Checklist](https://developers.google.com/web/progressive-web-apps/checklist)
- [Web App Manifest](https://www.w3.org/TR/appmanifest/)

---

## Support

For PWA issues:

1. Check browser console (F12)
2. Go to DevTools → Application
3. Check Service Workers tab
4. Look for error messages
5. Check manifest.json validity
6. Verify HTTPS is enabled
