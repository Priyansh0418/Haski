# Phase 0 Specification

This document contains the Phase 0 functional requirements, API sketches, data schema, and privacy notes for Haski.

- Camera analyses are performed with explicit user permission.
- Images should be processed securely; do not store raw images unnecessarily.
- Provide endpoints: /api/v1/analyze/image, /api/v1/profile/me

## Quick copy-paste snippets for in-app screens

- Permission prompt (capture):

  "Haski would like to access your camera to analyze your skin and hair.
  Images are processed temporarily and are not stored unless you choose to save them.
  Do you allow camera access?"

- Minimal privacy note (short):

  "We only process images you explicitly capture or upload. Images are used to generate insights and are not shared with third parties without your consent. Saved images remain private to your account."

- API endpoints (dev):

  - POST /api/v1/analyze/image — multipart/form-data field `image` (file)
  - GET /api/v1/profile/me — user profile
