# Project Progress & Actionable Tasks — AgriSmart

## 1. Features [Fully Built]

- [x] **Monorepo & Project Scaffolding**: Configured Next.js 14 Web UI app and FastAPI backend structure.
- [x] **Global Styling System**: Core CSS token variables (`globals.css`) and utility classes (`.page-stack`, `.glass`, `.filter-btn`, `.badge-*`, `.status-dot`).
- [x] **Dashboard Layout & Component Hierarchy**:
  - `Sidebar` & `TopBar` layout shell.
  - Core UI primitives (`MetricCard`, `SectionHeader`, `StatusBadge`, `Card`, `ProgressBar` in `Cards.tsx`).
  - Dashboard widget cards (`FarmHealthHero.tsx`, `FieldCard.tsx`, `IrrigationSummary.tsx`, `YieldSummary.tsx`).
- [x] **Demo Data Architecture**: Centralized mock state exports in `apps/web/lib/demo-data.ts` and backend `services/api/app/demo/fixtures.py`.
- [x] **XAI Heatmap Viewer UI Component**: `XaiHeatmapViewer.tsx` component built with original/heatmap/overlay toggle modes.
- [x] **FastAPI Router & Service Architecture**: Modular routing structure split into `routers/` and business logic `services/` with strict schema validation.

---

## 2. Features [Partially Built / In-Progress]

- [~] **Plant Disease Detection & Diagnostics Pipeline**:
  - Upload interface and frontend state wiring are complete.
  - Backend diagnosis endpoint `services/api/app/routers/diagnosis.py` and service `services/api/app/services/diagnosis_service.py` are present.
  - **Issue to address**: Multi-class classification logic currently defaults or heavily biases output towards "Early Blight" across different uploaded image samples instead of evaluating true probabilities across all crop disease categories.
- [~] **Live Telemetry Engine**:
  - Frontend mock hooks (`useLiveTelemetry.ts`) and Recharts visualization components are implemented.
  - Backend WebSockets endpoint and real-time Redis/MQTT consumer loop need final connection.
- [~] **GIS Field Boundary Map**:
  - Leaflet map wrapper (`FarmMapLeaflet.tsx`) rendered on dashboard.
  - Dynamic API fetching for field GeoJSON coordinates needs full integration.

---

## 3. [Next Actionable Tasks] (In Priority Order)

1. **Fix Multi-Class Disease Classification Model Ingestion & Softmax Logic**:
   - Inspect `services/api/app/services/diagnosis_service.py` and ensure the post-processing softmax maps class indices correctly to label strings.
   - Resolve the bug where arbitrary input images classify as "Early Blight".
   - Calibrate confidence score outputs and return dynamic Grad-CAM heatmaps for uploaded images.

2. **Integrate Real Weights / ONNX Engine with Demo Fallback**:
   - Add model weight loader to `services/api/app/services/diagnosis_service.py`.
   - Ensure strict adherence to `settings.DEMO_MODE` flag: when `true`, return rich fixture results from `app/demo/fixtures.py`; when `false`, execute the ONNX runtime pipeline.

3. **Wire GIS Map to Backend Data**:
   - Connect `apps/web/components/map/FarmMapLeaflet.tsx` to `lib/api/fields.ts` to render real field polygons dynamically based on active farm selection.

4. **Connect Live Telemetry WebSocket Stream**:
   - Link `apps/web/lib/hooks/useLiveTelemetry.ts` to `ws://localhost:8000/api/v1/telemetry/ws` to consume real-time sensor updates into state.

5. **Run Full Verification Suite**:
   - Execute `npx tsc --noEmit` from `apps/web/` to confirm TypeScript compile health.
   - Execute `ruff check .` and `pytest` from `services/api/` to verify backend compliance.
