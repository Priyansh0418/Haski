# Haski — Skin & Hair AI

Haski is a privacy-first web application that uses computer vision and machine learning to analyze skin and hair, track user health over time, and provide personalized care recommendations.

This repository contains the frontend (React + Vite + Tailwind), backend API (FastAPI), ML training/inference code (PyTorch/TensorFlow), and deployment infrastructure (Docker Compose / infra).

## Quick summary

- Purpose: Camera-based skin & hair analysis, health tracking, personalized recommendations, and alerts for possible infections.
- Privacy: On-device / backend inference with explicit permission for camera usage — no unauthorized sharing of images.

## Tech stack

- Backend: FastAPI (Python)
- Frontend: React + Vite + TypeScript
- Styling: Tailwind CSS
- ML: PyTorch or TensorFlow (notebooks and training scripts under `ml/`)
- Infra: Docker Compose for local development; optional k8s manifests in `infra/k8s`

## Quickstart (dev via Docker Compose)

1. Copy the example env and edit secrets:

   cp .env.example .env

2. Start services with Docker Compose:

   docker-compose -f infra/docker-compose.yml up --build

3. Open the frontend at http://localhost:3000 and backend at http://localhost:8000

Notes:

- If you prefer to run services locally without Docker, see the individual `frontend/` and `backend/` README snippets under their folders.

## Local development (virtualenv)

If you prefer to run the backend locally without Docker, use a Python virtual environment. Create it once and then activate it in your shell.

Windows (PowerShell):

```powershell
python -m venv .venv
. .\scripts\activate-venv.ps1   # dot-source the helper so activation persists in this session
```

Bash / WSL / Git Bash:

```bash
python -m venv .venv
source ./.venv/bin/activate       # or: source ./scripts/activate-venv.sh
```

After activation, install backend deps and run the app:

```bash
pip install -r backend/requirements.txt
pip install "pydantic[email]"
cd backend
python -m app.main                # or: ..\\.venv\\Scripts\\python -m uvicorn app.main:app --reload
```

## Folder structure (high-level)

HASKI/
├─ .github/
│ └─ workflows/
│ └─ ci.yml
├─ frontend/
│ ├─ package.json
│ ├─ vite.config.ts
│ ├─ index.html
│ └─ src/ (React + Vite app)
├─ backend/
│ ├─ pyproject.toml / requirements.txt
│ ├─ app/
│ │ ├─ main.py
│ │ ├─ api/v1/ (auth, profile, photos, analyze endpoints)
│ │ └─ services/ml_infer.py (inference stubs)
│ └─ Dockerfile
├─ ml/
│ ├─ notebooks/
│ ├─ training/ (train.py, model.py)
│ └─ exports/ (saved models)
├─ infra/
│ └─ docker-compose.yml
├─ docs/
│ ├─ part0_spec.md
│ ├─ privacy_short.md
│ └─ disclaimer.md
├─ .env.example
└─ .gitignore

## Contribution notes

- Follow the branch naming convention: `feature/<short-desc>`, `fix/<short-desc>`.
- Add unit tests for backend endpoints (pytest) and basic frontend tests (Vitest/React Testing Library).
- Respect privacy: do not commit real user images or sensitive data. Use fixtures or synthetic images for tests.
- Add model artifacts under `ml/exports/` and reference them in `backend/services/ml_infer.py`.

## Docs and spec

See `docs/part0_spec.md` for Phase 0 functional and privacy requirements, API sketches, and data schema.

---

Phase 0: README added. Next: scaffold initial folder files (package manifests, Dockerfiles, .gitignore). If you want, I can scaffold the `frontend/` and `backend/` starter files now.

## MVP suggestion (start here)

Add a focused MVP to validate core value quickly. Keep it small, privacy-first, and testable end-to-end.

- User sign-up & profile

  - Allow users to register and maintain a profile with: age, gender, location (optional), allergies, and lifestyle notes (sleep, smoking, hair treatments).

- Camera / photo upload + basic classification

  - Live camera capture and image upload flow.
  - Lightweight ML classifiers for simple skin types (e.g., dry, oily, combination, normal) and hair types (e.g., straight, wavy, curly, coily).
  - Start with mocked or small-rule models, then replace with a PyTorch transfer-learning model when ready.

- Simple recommendations

  - Generate daily care routines (cleanse, moisturize, sunscreen, hair care) and dietary tips based on detected type and profile data.
  - Keep recommendations short, actionable, and link to longer content in the app.

- Progress dashboard

  - Store historic analyses and show a simple dashboard with trends: last score, 7/30-day trend line, and a small timeline of saved images.

- Permissions, privacy & deletion
  - Perform analyses only after explicit permission for camera or upload.
  - Show the short privacy blurb and medical disclaimer before analysis (see `docs/privacy_short.md` and `docs/disclaimer.md`).
  - Allow users to delete saved photos and export/delete their account data.

This MVP will let you validate user demand, iterate on model accuracy, and build the UI flows required for more advanced recommendations.

## Changelog

- 2025-10-24: Updated README � clarified quickstart and added a changelog entry.
