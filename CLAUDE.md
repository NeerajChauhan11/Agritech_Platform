# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

`AGENTS.md` (repo root) holds the mandatory code-quality rules (file-size caps, no hardcoded data in pages/routers, layered backend, CSS utility classes, naming). Read it before editing. `apps/web/AGENTS.md` warns that this Next.js version (16.x, React 19) has breaking changes: consult `apps/web/node_modules/next/dist/docs/` before writing Next.js code.

Other docs: `ARCHITECTURE.md` (target design: MQTT → FastAPI worker → TimescaleDB/Redis → WebSocket; much of this is not built yet), `patterns.md` (standards), `tasks.md` (progress and known issues, e.g. the diagnosis classifier biasing toward "Early Blight"), `spec.md`.

## Layout

Monorepo with two independent apps and no root package manager:
- `apps/web/` — Next.js App Router frontend (Tailwind v4, Radix, Framer Motion, Recharts, Leaflet)
- `services/api/` — FastAPI backend (Python)

## Commands

Frontend (run from `apps/web/`):
```bash
npm run dev            # http://localhost:3000
npm run build
npm run lint           # eslint
npx tsc --noEmit       # must exit 0 after every edit
```

Backend (run from `services/api/`):
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000   # docs at /docs
ruff check .
python -m pytest
python -m pytest tests/test_farms.py::test_name   # single test
```

Repo root: `docker compose build` / `docker compose up` runs only the `api` service (port 8000, `DEMO_MODE=true`, source bind-mounted). The web app is not containerized.

## Architecture

**Demo-first.** Both sides work without hardware, DB, or models:
- Backend: `settings.DEMO_MODE` (default `True`, `app/core/config.py`) makes services return fixtures from `app/demo/fixtures.py`. Demo responses must use the same Pydantic schemas as real ones. No database is wired up yet despite `DATABASE_URL`.
- Frontend: demo data lives only in `apps/web/lib/demo-data.ts`; `lib/types.ts` holds all shared types.

**Backend layering** (`services/api/app/`): `routers/` (thin: validate, call one service, return) → `services/` (logic, e.g. `diagnosis_service.py`, `vision_classifier.py`, `data_cleaning_service.py`) → `schemas/` (Pydantic). Thresholds and labels go in `core/constants.py`. All routers are mounted in `main.py` under `API_V1_PREFIX` (`/api/v1`).

**API envelope.** Every response is `ApiResponse` `{success, data, error?}`. `main.py` registers exception handlers so `HTTPException`s and validation errors use this envelope; raise `HTTPException(detail={"code": ..., "message": ...})` for domain errors. The frontend `lib/api/client.ts` (`apiClient<T>`) unwraps `data` and throws on `success: false`; per-domain modules in `lib/api/*.ts` wrap it and are re-exported from `lib/api/index.ts`. Base URL comes from `NEXT_PUBLIC_API_URL` (default `http://localhost:8000/api/v1`). CORS origins are `ALLOWED_ORIGINS` in backend settings.

**Frontend structure.** `app/<route>/page.tsx` (dashboard, telemetry, map, diagnostics, irrigation, yield, alerts) is layout-only; widgets live in `components/{dashboard,diagnostics,map,layout,ui}/`. Styling relies on CSS variables and shared utility classes in `app/globals.css` rather than inline styles or hex colors.

**Supported crops** are Apple, Tomato and Capsicum only, defined once in `SUPPORTED_CROPS` (`core/constants.py`; frontend mirror `apps/web/lib/crops.ts`). `capsicum` is canonical, `pepper` an alias (`core/crops.py: normalize_crop`). Unsupported crop ids get `CROP_NOT_SUPPORTED` (400); never fall back to Tomato. Wheat/Sugarcane/Rice are deferred (see `docs/models.md`).

**Diagnosis pipeline** (`POST /api/v1/diagnose`, takes only the image; the deprecated `crop` field is not used for routing but is validated if sent). `services/diagnosis_service.py` runs: `image_quality.py` gate -> `crop_identifier.py` (ONNX crop classifier incl. `unknown`) -> `disease_model_registry.py` (that crop's own ONNX model, never another crop's) -> guidance from `app/knowledge/`. Result `status` is one of `ok | low_quality_image | crop_uncertain | crop_unsupported | model_unavailable | disease_uncertain`; on anything but `ok` no disease is claimed. Class lists, file names and preprocessing live in `core/model_catalog.py`; thresholds in `core/constants.py`; weights are read from `AI_MODEL_PATH` (default `services/api/models/`). **No trained weights ship with the repo**, so diagnosis returns `model_unavailable` until they are added: see `docs/models.md` and `scripts/train_disease_model.py`. Do not reintroduce colour heuristics or demo fixtures in place of a model. `GET /api/v1/diagnose/models` reports which weights are installed. `DEMO_MODE` does not affect diagnosis.

Backend tests use FastAPI `TestClient` via the `client` fixture in `tests/conftest.py`.

## Antigravity Core Context Imports
- Use the following files to understand the project architecture, features, and next steps before writing any code.
@import spec.md
@import tasks.md
@import patterns.md
