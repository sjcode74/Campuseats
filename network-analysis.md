# Network Analysis

## Website Tested
BBC News

## Network Analysis Results

- **Request count:** 143 requests
- **Total page resources:** 5.8 MB
- **Total transferred:** 1.4 MB
- **Slowest resource:** `_clientMiddlewareManifest.js`
- **Slowest resource time:** 1.5 minutes
- **Resource type:** Script
- **Resource size:** 0 B
- **3xx responses:** None observed
- **4xx responses:** None observed

## Observation

I opened the website in Chrome DevTools and navigated to the Network tab. I enabled **Disable cache** and reloaded the page. The Network panel showed 143 requests during the page load. The total resources loaded were 5.8 MB, while 1.4 MB was transferred over the network.

The slowest resource was `_clientMiddlewareManifest.js`, which took approximately 1.5 minutes to complete. It was a JavaScript resource and showed a size of 0 B.

No 3xx or 4xx HTTP responses were observed during the page load.