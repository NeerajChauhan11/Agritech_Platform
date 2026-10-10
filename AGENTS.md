# AgriSmart — Agent Rules & Code Quality Standards

This file is automatically read by AI coding agents (Antigravity, Cursor, Claude Code, Windsurf, etc.).
These rules are **mandatory** for every contribution to this repository — frontend, backend, scripts, and tests alike.
Do not skip any rule. Do not ask the user to confirm before applying them.

---

## 0. First Steps for Every Task

Before writing any code in an existing file:
1. Read the file you are about to edit.
2. Identify the layer it belongs to (UI, logic, data, API, config).
3. Apply the layer-specific rules from this document.
4. Run the relevant validation command after your edit (see §7).

---

## 1. Universal Rules (All Layers)

### 1.1 Single Responsibility
- Every file has **one job**. If a file does two jobs, split it.
- Page/route files contain **layout only** — no business logic, no hardcoded data.
- Logic goes into hooks / services / utilities, not into UI components.

### 1.2 No Hardcoded Data in Component/Route Files
- All demo, seed, or mock data lives exclusively in:
  - **Frontend:** `apps/web/lib/demo-data.ts`
  - **Backend:** `services/api/app/demo/fixtures.py`
- If you need a constant array or object inside a JSX file or a FastAPI route, move it to the appropriate data file and import it.

### 1.3 No Repeated Inline Styles or Magic Strings
- **Frontend:** Before writing a new `style={{ ... }}` block, check `apps/web/app/globals.css` for an existing utility class. Use the class. If no class exists for a pattern used in >=2 places, add it to `globals.css` first.
- **Backend:** Constants (thresholds, labels, color maps, model paths) go in `services/api/app/core/constants.py`. Never inline them in route handlers.

### 1.4 File Size Caps
| File type | Hard limit |
|---|---|
| Frontend page (`page.tsx`) | 200 lines |
| Frontend component | 150 lines |
| Backend route file (`routers/*.py`) | 120 lines |
| Backend service file | 200 lines |
| Any single function / method | 40 lines |

If you are about to exceed these limits, stop and extract a sub-component or helper first.

### 1.5 Naming Conventions
| Layer | Convention | Example |
|---|---|---|
| React components | PascalCase | `FarmHealthHero.tsx` |
| React hooks | camelCase + `use` prefix | `useLiveTelemetry.ts` |
| TypeScript types/interfaces | PascalCase, in `lib/types.ts` | `IrrigationRecommendation` |
| Python modules | snake_case | `irrigation_service.py` |
| Python classes | PascalCase | `IrrigationAdvisor` |
| Python constants | UPPER_SNAKE_CASE | `WATER_STRESS_THRESHOLDS` |
| CSS utility classes | kebab-case | `.filter-btn`, `.page-stack` |
| Demo data exports | UPPER_SNAKE_CASE | `DEMO_IRRIGATION_SUMMARY` |

---

## 2. Frontend Rules (Next.js / TypeScript)

### 2.1 Page Structure (Mandatory Pattern)
Every `page.tsx` must follow this exact structure — nothing more:

```tsx
// 1. "use client" (if needed)
// 2. Imports — React hooks, then components, then data, then types
// 3. One exported default function
// 4. State declarations (useState, useCallback, useEffect)
// 5. Derived values (simple expressions only — no loops, no fetch calls)
// 6. Return: pure JSX layout using imported components
```

### 2.2 Component Extraction Triggers
Extract a sub-component when **any** of these are true:
- The JSX block is > 40 lines
- The same JSX pattern appears in 2+ places
- The block has its own meaningful state
- The block represents a named UI concept (e.g., `FieldCard`, `StressIndicator`)

Store extracted components in:
- `components/dashboard/` — dashboard-specific widgets
- `components/ui/` — fully generic, reusable primitives
- `components/layout/` — Sidebar, TopBar, shell

### 2.3 CSS Rules
- **Use CSS variables** (`var(--brand-green)`, `var(--text-muted)`, etc.) — never hardcode hex colors in JSX.
- **Use utility classes** from `globals.css` before writing inline styles.
- New patterns used >=2 times -> add to `globals.css` with a comment.
- Framer Motion `initial/animate` values are allowed inline (they are animation state, not layout styles).

### 2.4 TypeScript
- All shared types in `lib/types.ts` — no `any`, no type assertions unless unavoidable.
- Always run `npx tsc --noEmit` after edits. Zero errors required before finishing.
- Recharts formatter props: use `value ?? 0` guard — `ValueType` can be `undefined`.

### 2.5 Demo Data Architecture
```
lib/demo-data.ts
  DEMO_FARM              — full Farm object with fields + devices
  DEMO_TELEMETRY         — per-field 24h history
  DEMO_ALERTS            — Alert[]
  DEMO_DIAGNOSIS         — DiagnosisResult (AI disease detection)
  DEMO_IRRIGATION        — IrrigationRecommendation[] (full detail)
  DEMO_IRRIGATION_SUMMARY — dashboard widget rows (name/stress/minutes/color)
  DEMO_YIELD             — YieldPrediction[] (full detail)
  DEMO_YIELD_SUMMARY     — dashboard widget rows (crop/field/est/last/conf)
```
Add new demo exports to this file. Never export demo data from inside `app/`.

---

## 3. Backend Rules (FastAPI / Python)

### 3.1 Router Structure (Mandatory Pattern)
Every `routers/*.py` must follow this structure:

```python
# 1. Imports
# 2. Router definition
# 3. Route handlers — thin, delegate to service layer
# 4. No business logic in route handlers
```

Route handlers must:
- Validate input (Pydantic models)
- Call one service function
- Return the result

### 3.2 Layered Architecture
```
services/api/app/
  routers/          # HTTP endpoints only — no logic
  services/         # Business logic (irrigation_service.py, diagnosis_service.py)
  models/           # SQLAlchemy ORM models
  schemas/          # Pydantic request/response schemas
  core/
    constants.py    # All thresholds, labels, config values
    config.py       # Pydantic Settings (env vars)
    deps.py         # FastAPI dependency injection
  demo/
    fixtures.py     # Python equivalent of lib/demo-data.ts
```

### 3.3 Demo Mode
- Every route must check `settings.DEMO_MODE` and return fixture data when `True`.
- Demo fixtures live in `app/demo/fixtures.py` — never inline in routers.
- Demo responses must match the exact same Pydantic schema as real responses.

### 3.4 Constants File (`core/constants.py`)
Any value appearing in more than one file must be a named constant:
```python
# Correct
from app.core.constants import SOIL_MOISTURE_CRITICAL_THRESHOLD

# Wrong — magic number in service
if reading.soil_moisture < 20:
```

---

## 4. Component / Module Structure Reference

### Frontend Components
```
components/
  dashboard/
    FarmHealthHero.tsx    # Health score + field breakdown
    FieldCard.tsx         # Individual field tile (clickable)
    IrrigationSummary.tsx # Dashboard irrigation widget
    YieldSummary.tsx      # Dashboard yield widget
  layout/
    Sidebar.tsx
    TopBar.tsx
  ui/
    Cards.tsx             # MetricCard, SectionHeader, StatusBadge, Card, ProgressBar
```

### Shared CSS Utility Classes (`globals.css`)
| Class | Purpose |
|---|---|
| `.page-stack` | Page-level column layout (gap: 24px) |
| `.page-header` | h1 + p title block on every page |
| `.info-row` | flex; align-items:center; justify-content:space-between |
| `.mini-stat` | Elevated chip box with border |
| `.filter-btn` | Pill filter button (inactive state) |
| `.filter-btn.active` | Pill filter button (selected state) |
| `.tab-btn` | Tab/mode toggle button (inactive) |
| `.tab-btn.active` | Tab/mode toggle button (active) |
| `.glass` | Glassmorphism card base |
| `.glass-hover` | Hover transitions for glass cards |
| `.badge`, `.badge-*` | Status badges (green/yellow/red/blue) |
| `.status-dot` | Colored dot indicator |
| `.section-label` | Uppercase small label |
| `.mono` | Monospace font |

---

## 5. Git & Commit Standards

- Commit message format: `type(scope): description`
  - Types: `feat`, `fix`, `refactor`, `style`, `docs`, `test`, `chore`
  - Examples: `feat(dashboard): add live telemetry chart`
  - Examples: `refactor(irrigation): extract StressIndicator component`
- Never commit with TypeScript errors or Python lint failures.
- Never commit hardcoded secrets, API keys, or credentials.

---

## 6. Cleanup Triggers (When to Run a Cleanup Pass)

Run a cleanup pass before merging any feature branch if ANY of these are true:
- Any `page.tsx` exceeds 200 lines
- Any JSX inline style object is duplicated in 2+ places
- Any hardcoded data array exists inside a component or route file
- Any Python route handler contains business logic or constants
- `tsc --noEmit` fails
- `ruff check .` or `flake8` fails

---

## 7. Validation Commands (Run After Every Edit)

### Frontend
```bash
# From apps/web/
npx tsc --noEmit          # Must exit 0
```

### Backend (when implemented)
```bash
# From services/api/
ruff check .              # Must exit 0
python -m pytest          # Must pass
```

### Full project
```bash
# From repo root
docker compose build      # Must succeed without warnings
```

---

## 8. Environment Variables

All secrets and config values are in `.env` files. Never hardcode them.

| Variable | Layer | Description |
|---|---|---|
| `DEMO_MODE` | Both | `true` uses fixture data, skips real hardware/AI calls |
| `DATABASE_URL` | Backend | PostgreSQL connection string |
| `REDIS_URL` | Backend | Redis connection string |
| `MQTT_BROKER_URL` | Backend | EMQX / HiveMQ broker |
| `AI_MODEL_PATH` | Backend | Path to ONNX/PyTorch model weights |
| `NEXT_PUBLIC_API_URL` | Frontend | Base URL for FastAPI backend |

---

*This file is a living document. When new patterns are established during development, add them here before closing the PR.*
