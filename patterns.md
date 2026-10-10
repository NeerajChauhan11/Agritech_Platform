# Code Standards, Design Rules & Patterns — AgriSmart

This document details the architectural conventions, file limits, design patterns, and code quality standards enforced across this repository.

---

## 1. File Size Caps & Structure Standards

| Layer / File Type | Line Cap | Responsibility Rule |
|---|---|---|
| Frontend Page (`page.tsx`) | **200 lines** | Layout only — zero business logic or inline static data arrays. |
| Frontend Component | **150 lines** | Pure presentational component or targeted state widget. |
| Backend Router (`routers/*.py`) | **120 lines** | Thin HTTP layer: validate inputs (Pydantic), call 1 service method, return response. |
| Backend Service (`services/*.py`) | **200 lines** | Business logic, model inference, and calculations. |
| Any Function / Method | **40 lines** | Extract helpers if exceeding line cap. |

---

## 2. Mandatory Component Structure & Extraction Triggers

### 2.1 Page File Pattern (`page.tsx`)
Every `page.tsx` must strictly follow this sequence:
```tsx
// 1. "use client" (if client component)
// 2. Imports: React hooks -> Components -> API/Data -> Types
// 3. One default exported React component function
// 4. State declarations (useState, useCallback, useEffect)
// 5. Derived values (simple inline expressions only)
// 6. Return statement returning clean JSX layout using imported components
```

### 2.2 Component Extraction Rules
Extract a sub-component immediately when:
- JSX block exceeds 40 lines.
- JSX pattern is used in 2+ locations.
- UI block contains distinct local interactive state.
- Represents a domain concept (e.g., `FieldCard`, `StressIndicator`, `XaiHeatmapViewer`).

### 2.3 Directory Organization
- `apps/web/components/dashboard/` — Feature widgets specific to dashboard pages.
- `apps/web/components/ui/` — Generic reusable primitive components (`Cards.tsx`, `Buttons`).
- `apps/web/components/layout/` — App shell (`Sidebar.tsx`, `TopBar.tsx`).
- `apps/web/lib/api/` — API fetch client modules (`telemetry.ts`, `irrigation.ts`, `diagnosis.ts`).

---

## 3. Demo Data Architecture & No Hardcoded Data Rule

- **Strict Ban**: NEVER inline mock objects, seed data arrays, or static lists inside JSX components or FastAPI route files.
- **Frontend Mock Repository**: All frontend demo data MUST be placed in `apps/web/lib/demo-data.ts`.
- **Backend Mock Repository**: All backend fixture data MUST be placed in `services/api/app/demo/fixtures.py`.
- **Backend Demo Mode**: Every route handler checks `settings.DEMO_MODE`. When `DEMO_MODE=true`, routers must return typed Pydantic responses built from `app/demo/fixtures.py`.

---

## 4. Styling System & CSS Utility Rules

- **Vanilla CSS Utility Classes**: All shared styling resides in `apps/web/app/globals.css`.
- **Utility Tokens Enforced**:
  - `.page-stack` -> Page container layout with consistent gap spacing (24px).
  - `.page-header` -> Standard page title + subtitle header block.
  - `.info-row` -> `flex; align-items: center; justify-content: space-between;`.
  - `.mini-stat` -> Bordered elevated stat chip container.
  - `.filter-btn` & `.filter-btn.active` -> Interactive filter button states.
  - `.tab-btn` & `.tab-btn.active` -> Navigation mode toggle buttons.
  - `.glass` & `.glass-hover` -> Glassmorphic panel base and hover transitions.
  - `.badge` (`.badge-green`, `.badge-yellow`, `.badge-red`, `.badge-blue`) -> Status pill badges.
  - `.status-dot` -> Colored status indicator dot.
  - `.section-label` -> Uppercase muted section header label.
  - `.mono` -> Monospace data font.
- **CSS Color Variables**: ALWAYS use CSS variables (e.g., `var(--brand-green)`, `var(--text-muted)`) in custom styles or Framer Motion animations — avoid hardcoded hex strings in inline styles.

---

## 5. Naming & Code Conventions

| Target | Style | Example |
|---|---|---|
| React Component Files | PascalCase | `FarmHealthHero.tsx` |
| Custom React Hooks | camelCase (`use` prefix) | `useLiveTelemetry.ts` |
| TypeScript Interfaces/Types | PascalCase in `lib/types.ts` | `IrrigationRecommendation` |
| Python Files / Modules | snake_case | `diagnosis_service.py` |
| Python Classes | PascalCase | `DiagnosisService` |
| Python Constants | UPPER_SNAKE_CASE in `core/constants.py` | `WATER_STRESS_THRESHOLDS` |
| CSS Utility Classes | kebab-case in `globals.css` | `.page-stack` |

---

## 6. Safety & Validation Commands

Always run validation commands prior to completing work on a feature:

```bash
# Frontend Validation (Run from apps/web/)
npx tsc --noEmit

# Backend Validation (Run from services/api/)
ruff check .
python -m pytest

# Full Stack Build Check (Run from repo root)
docker compose build
```
