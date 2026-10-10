# AgriSmart — Presentation Blueprint (`ppt.md`)

Master script for the project presentation / pitch deck. Every claim below was checked against the repository on 2026-10-10 (source files, routers, services, tests, docs). Where a capability is partial, planned or unverified it is labelled as such. Anything marked **[INTERNAL]** is for the presenter only and must not appear on slides.

**Suggested deck length:** 28 slides (about 25 minutes with demo). For a 10-minute slot use the **core set**: 1, 3, 6, 8, 10, 13, 14, 15, 20, 24, 25, 26.

**Status vocabulary used throughout**

| Label | Meaning |
|---|---|
| **Implemented** | Works end to end and is covered by code (and, where noted, tests) |
| **Implemented (demo data)** | UI and API exist; values come from the built-in demo farm, not live hardware |
| **Partial** | Some layers exist, others are not connected yet |
| **Planned** | Designed in `ARCHITECTURE.md` or the roadmap, not built |

---

## Slide 1: Title

**Purpose:** Introduce the project and set a professional tone.
**Key Message:** AgriSmart is an AI-assisted farm decision platform for Apple, Tomato and Capsicum growers.

**On-Slide Content:**
- AgriSmart
- AI-assisted crop health, irrigation and yield insight for Apple, Tomato and Capsicum
- [Team / Student names] · [Institution / Programme] · [Guide / Evaluator] · [Date]

**Visual Direction:** Full-bleed leaf photograph with a subtle dashboard screenshot inset (the dashboard page). Logo/wordmark top-left. Green brand colour from the app (`--brand-green`).

**Speaker Notes:** "Good morning. We are presenting AgriSmart, a web platform that brings crop-disease screening, irrigation guidance, yield outlook and field monitoring into one place for growers of apple, tomato and capsicum."

**Project Evidence:** `apps/web/app/page.tsx` (dashboard), `README`-level scope in `CLAUDE.md`.

---

## Slide 2: Project overview — one platform, seven screens

**Purpose:** Give the audience the whole picture before details.
**Key Message:** AgriSmart combines a web dashboard with a FastAPI backend and an image-analysis pipeline.

**On-Slide Content:**
- Web application (Next.js) + REST API (FastAPI) + image-analysis pipeline
- Seven screens: Dashboard · Field Monitor · Disease Detection · Irrigation Advisor · Yield Prediction · Farm Map · Alerts
- Focused scope: Apple, Tomato, Capsicum
- Runs fully without hardware or a database (demo-first design)

**Visual Direction:** Hub-and-spoke diagram: "AgriSmart" at the centre, seven spokes matching the sidebar items (Dashboard, Field Monitor, Disease Detection, Irrigation Advisor, Yield Prediction, Farm Map, Alerts) with the same icons used in the app sidebar.

**Speaker Notes:** "The application has seven screens, reachable from one sidebar. Behind them is a REST API with a consistent response envelope and an image pipeline for leaf photos. We deliberately scoped to three crops so each feature can be done properly."

**Project Evidence:** `apps/web/components/layout/Sidebar.tsx` (NAV_ITEMS), `services/api/app/main.py` (7 routers mounted under `/api/v1`).

---

## Slide 3: Problem statement

**Purpose:** Establish the real-world problem.
**Key Message:** Growers must act on crop disease, water stress and weather risk quickly, but the information is scattered and hard to interpret.

**On-Slide Content:**
- Crop disease is often noticed late and misjudged by eye
- Over- and under-watering waste water and reduce yield
- Sensor readings, weather and field notes live in separate places
- Small and mid-size farms rarely have an agronomist on call

**Visual Direction:** Four-icon row (leaf spot, water droplet, scattered data sources, farmer with question mark). Keep to one line of text per icon.

**Speaker Notes:** "A grower has to answer three questions every day: is my crop healthy, does it need water, and what should I expect at harvest. Today those answers come from different tools or from experience alone, which makes timely decisions difficult."

**Project Evidence:** Problem framing from `spec.md` §2 (feature intent). No statistics are quoted — do not add any unless sourced.

---

## Slide 4: Motivation and need

**Purpose:** Explain why a software solution is justified now.
**Key Message:** Cheap sensors, smartphones and pretrained vision models make decision support practical for small farms.

**On-Slide Content:**
- Photo-based screening needs only a phone camera
- IoT soil nodes can report moisture, temperature, humidity, pH and NPK
- A unified interface turns raw readings into simple actions
- Honest uncertainty: the system says "retake" or "not sure" instead of guessing

**Visual Direction:** Left-to-right chain: Phone photo / Soil sensor → AgriSmart → "Action for today".

**Speaker Notes:** "The enabling pieces already exist: cameras everywhere and low-cost sensor nodes. What is missing is a coherent layer that converts data into an action and is honest when it cannot be sure."

**Project Evidence:** Sensor fields in `services/api/app/schemas/telemetry.py` (`SensorReading`: moisture, temperature, humidity, pH, N, P, K); status handling in `diagnosis_service.py`.

---

## Slide 5: Project objectives

**Purpose:** State what the project set out to do.
**Key Message:** Five measurable objectives, each mapped to a module.

**On-Slide Content:**
1. Identify the crop and screen leaf-photo health automatically
2. Monitor field conditions and surface threshold alerts
3. Recommend irrigation based on soil moisture against crop needs
4. Present yield outlook with an uncertainty range
5. Keep the platform honest, modular and testable

**Visual Direction:** Numbered list on the left; on the right, small module chips (Diagnostics, Field Monitor, Irrigation, Yield, Alerts/Quality).

**Speaker Notes:** "Each objective corresponds to something you can open in the app. The fifth objective is about engineering quality: layered code, a single source of truth for crops, and automated tests."

**Project Evidence:** `AGENTS.md` (layering and quality rules), `services/api/tests/` (18 test files).

---

## Slide 6: Proposed solution

**Purpose:** Show the solution at a conceptual level.
**Key Message:** One interface, one API, one image pipeline — organised around the grower's daily questions.

**On-Slide Content:**
- "Is my crop healthy?" → Disease Detection
- "Does it need water?" → Irrigation Advisor
- "How is the field right now?" → Field Monitor + Farm Map
- "What should I expect?" → Yield Prediction
- "What needs attention?" → Alerts

**Visual Direction:** Five question cards mapped by arrows to five screens (use real screenshots as thumbnails).

**Speaker Notes:** "We organised the product around questions rather than technologies. A grower opens the dashboard, sees status, and drills into whichever area needs attention."

**Project Evidence:** `apps/web/app/*/page.tsx` for the seven routes.

---

## Slide 7: Features at a glance — what is built today

**Purpose:** Give an honest, complete inventory.
**Key Message:** Every module has a working UI and API; the leaf-photo pipeline runs on real input; sensor/IoT hardware wiring is the next integration step.

**On-Slide Content (table):**

| Feature | Status |
|---|---|
| Leaf-photo quality check | Implemented |
| Automatic crop identification (Apple/Tomato/Capsicum) | Implemented |
| General condition-category screening with guidance | Implemented |
| Specific-disease models per crop (training pipeline built) | Planned (models in training) |
| Sensor ingestion: cleaning, bounds checks, alerts, live push | Implemented (API) |
| Field monitor, irrigation, yield, alerts, map screens | Implemented (demo data) |
| Irrigation / yield calculation logic | Implemented (rule-based) |
| MQTT / Redis / database persistence | Planned |

**Visual Direction:** Clean two-column table with status pills (green / blue / grey). No more than 8 rows.

**Speaker Notes:** "We want to be precise about maturity. The diagnosis pipeline operates on real uploaded images. The monitoring screens run on a built-in demo farm so the whole platform can be shown without hardware; the API accepts real sensor payloads today."

**Project Evidence:** `tasks.md`, `ARCHITECTURE.md` (target design), `services/api/app/routers/*.py`, `apps/web/lib/demo-data.ts`.

---

## Slide 8: System architecture

**Purpose:** Show how the parts connect.
**Key Message:** A thin web client over a layered FastAPI service, with an image-analysis pipeline behind the diagnosis endpoint.

**On-Slide Content:**
- Web UI (Next.js 16, React 19)
- REST API `/api/v1` (FastAPI) — uniform `{success, data, error}` envelope
- Routers → Services → Schemas (strict layering)
- Image pipeline: quality gate → crop ID → condition analysis → guidance
- WebSocket `/api/v1/telemetry/ws` for live sensor frames

**Visual Direction:** Three-tier diagram (Browser / FastAPI / Model files on disk). Draw the diagnosis pipeline as a horizontal sub-flow inside the FastAPI box. Show database/MQTT/Redis as dashed grey boxes labelled "planned".

**Speaker Notes:** "Routers only validate and delegate; services hold logic; schemas define contracts. The model files are read from a configurable folder, so models can be upgraded without code changes."

**Project Evidence:** `services/api/app/main.py`, `core/config.py` (`AI_MODEL_PATH`), `schemas/common.py` (`ApiResponse`), `ARCHITECTURE.md` (target).

---

## Slide 9: Technology stack

**Purpose:** Present the tools used, grounded in what is installed.
**Key Message:** Modern, mainstream, well-supported stack.

**On-Slide Content:**
- **Frontend:** Next.js 16.3 (App Router), React 19, TypeScript, Tailwind CSS v4, Recharts, Leaflet, Framer Motion, Radix UI
- **Backend:** Python, FastAPI, Pydantic v2, Uvicorn
- **Image / ML runtime:** ONNX Runtime, OpenCV, Pillow, NumPy
- **Pretrained vision-language model:** OpenAI CLIP ViT-B/16 (ONNX, MIT licence)
- **Quality:** pytest, Ruff, ESLint, `tsc --noEmit`, Docker (API service)

**Visual Direction:** Three horizontal bands (Frontend / Backend / ML) with logos; keep logos monochrome.

**Speaker Notes:** "ONNX Runtime means inference runs on a normal CPU with no GPU or PyTorch dependency at serving time. The CLIP model is used unmodified."

**Project Evidence:** `apps/web/package.json`, `services/api/requirements.txt`, `scripts/fetch_general_model.py` (pinned revision + checksums), `docker-compose.yml`.

---

## Slide 10: End-to-end workflow

**Purpose:** Explain the grower's journey from input to action.
**Key Message:** From a photo or a sensor reading to a clear next step in a few seconds.

**On-Slide Content:**
1. Open dashboard → see field health, irrigation and yield summary
2. Upload a leaf photo → quality check → crop identified → condition screened → guidance
3. Review sensor trends in Field Monitor
4. Follow irrigation recommendation → confirm
5. Acknowledge alerts

**Visual Direction:** Horizontal swim-lane with five numbered steps and a screenshot thumbnail under each.

**Speaker Notes:** "This is the daily loop. Notice that at every step the system either gives an action or tells the user what to do to get a better answer."

**Project Evidence:** Pages under `apps/web/app/`; `POST /api/v1/diagnose`; `POST /api/v1/irrigation/confirm`; `PATCH /api/v1/alerts/{id}/acknowledge`.

---

## Slide 11: Module — Dashboard

**Purpose:** Present the command-centre view.
**Key Message:** One screen summarises farm health, live readings, irrigation and yield.

**On-Slide Content:**
- Farm health hero with per-field breakdown
- Live-style metric cards (moisture, temperature, humidity, pH)
- Field cards → drill into a field
- Irrigation and yield summary widgets; recent alerts

**Visual Direction:** Annotated screenshot of the dashboard with four numbered callouts.

**Speaker Notes:** "The dashboard is intentionally glanceable. The metric cards refresh every few seconds; in this demo configuration the values vary around the demo farm's baselines, and the same layout is ready for the live WebSocket feed."

**Project Evidence:** `apps/web/app/page.tsx`, `components/dashboard/{FarmHealthHero,FieldCard,IrrigationSummary,YieldSummary}.tsx`. Status: **Implemented (demo data)**.

---

## Slide 12: Module — Field Monitor (telemetry)

**Purpose:** Show field-level sensing and trends.
**Key Message:** Per-field charts for moisture, temperature, humidity, pH and NPK with plain-language range checks.

**On-Slide Content:**
- Field selector (4 demo fields: 2 tomato, 1 apple, 1 capsicum)
- 24-hour trend charts (area + line)
- NPK nutrient bars with "within optimal range" feedback
- Device list: battery, signal, online/offline

**Visual Direction:** Screenshot of Field Monitor with the chart area highlighted and NPK panel zoomed.

**Speaker Notes:** "Operators can switch fields and read trends at a glance. Nutrient values are compared with crop-appropriate ranges, and device health is visible so a dead sensor is not mistaken for a dry field."

**Project Evidence:** `apps/web/app/telemetry/page.tsx`, `GET /api/v1/telemetry/{field_id}`, `lib/demo-data.ts`. Status: **Implemented (demo data)**.

---

## Slide 13: Module — Disease Detection pipeline

**Purpose:** Explain what happens when a leaf photo is uploaded.
**Key Message:** A staged pipeline that checks the photo, identifies the crop, screens the condition and returns guidance — or asks for a better photo.

**On-Slide Content:**
1. **Photo quality check** — resolution, exposure, blur, leaf coverage
2. **Crop identification** — Apple / Tomato / Capsicum, or "not a supported leaf"
3. **Condition analysis** — uses a crop's own disease model when installed; otherwise a general category screen
4. **Guidance** — what to look for, immediate actions, prevention, when to consult an agronomist

**Visual Direction:** Left-to-right flow of four boxes; below each box, the outcome if that stage cannot proceed ("Retake photo", "Crop not recognised", "No confident category").

**Speaker Notes:** "No crop selection is needed — the system identifies it. Each stage can stop the process safely. The result always says which stage produced it and how confident the system is."

**Project Evidence:** `services/api/app/services/diagnosis_service.py`, `image_quality.py`, `crop_identifier.py`, `disease_model_registry.py`, `general_diagnosis.py`; `POST /api/v1/diagnose`.

---

## Slide 14: The AI component and its role

**Purpose:** Describe the AI/ML component, its inputs, outputs and integration.
**Key Message:** A vision-language model turns a leaf photo into a ranked crop and condition-category estimate, with built-in refusal when unsure.

**On-Slide Content:**
- **Input:** one leaf photo (JPG / PNG / WebP)
- **Model:** pretrained CLIP vision-language model compared against text descriptions of crops and condition categories
- **Output:** detected crop + confidence, ranked condition categories, guidance, model version
- **Categories:** Healthy · Fungal · Bacterial · Viral · Pest damage · Nutrient stress
- **Runs offline** on CPU through ONNX Runtime (weights fetched once, checksum-verified)
- **Upgrade path:** per-crop specific-disease models (training pipeline included) drop in without code changes

**Visual Direction:** Diagram: image → image encoder; text prompts → text encoder; similarity → ranked categories → thresholds → result. Small badge: "Upgrade path: specific-disease models".

**Speaker Notes:** "We use a pretrained model rather than a custom classifier for the first release, which lets the platform screen into broad categories today. The same pipeline automatically prefers a crop-specific model whenever one is installed. We also built the data preparation, training and ONNX export tooling for those models."

**Project Evidence:** `services/api/app/services/clip_runtime.py`, `general_category_classifier.py`, `core/general_catalog.py`; `scripts/fetch_general_model.py`, `scripts/prepare_datasets.py`, `scripts/train_disease_model.py`, `notebooks/train_models_colab.ipynb`; `docs/models.md`. Do **not** quote accuracy — none is validated for production.

---

## Slide 15: Disease detection — what the user sees

**Purpose:** Show user-facing behaviour, including safe failure.
**Key Message:** Every outcome is explained in plain language with a next step.

**On-Slide Content:**
- **Result:** detected crop + confidence, condition category, symptoms to look for, immediate actions, prevention
- Banner on every screening result: "Preliminary category screening — specific-disease model is in training"
- Clear states: Photo quality too low · Crop not recognised · Crop not supported · Model not installed · No confident category
- Supported crops listed on the "not supported" state

**Visual Direction:** Montage of three screenshots: successful result card with the banner, blurry-photo state, unsupported-crop state.

**Speaker Notes:** "The interface is designed so a grower is never left with a bare 'error'. Poor photos get retake advice; unfamiliar plants are declined rather than forced into a wrong crop; uncertain results show candidates and say they are not a diagnosis."

**Project Evidence:** `apps/web/components/diagnostics/{DiagnosisResultCard,DiagnosisStatusNotice,DiagnosisGuidance,PredictionList}.tsx`; statuses in `schemas/diagnosis.py`; tests `tests/test_diagnosis.py`, `tests/test_general_tier.py`.

---

## Slide 16: Module — Irrigation Advisor

**Purpose:** Explain water-management guidance.
**Key Message:** Soil moisture is compared with each crop's target range to produce a stress level, duration and reasons.

**On-Slide Content:**
- Per-field water stress: low / medium / high / critical
- Recommended duration (minutes) and confidence
- Reasons in plain language (e.g. moisture below crop minimum, high temperature)
- One-click confirm to schedule

**Visual Direction:** Screenshot: field list on the left with stress badges; detail panel on the right with sensor snapshot and the confirm button.

**Speaker Notes:** "The logic is transparent and rule-based: critical below twenty percent moisture; otherwise the deficit against the crop's minimum drives the stress level and duration. Because the rules are explicit, growers can see why a recommendation was made."

**Project Evidence:** `services/api/app/services/irrigation_service.py` (`evaluate_irrigation`), `core/constants.py` (`CROP_PROFILES`, thresholds), `apps/web/app/irrigation/page.tsx`, `POST /api/v1/irrigation/confirm`, `tests/test_irrigation.py`. Status: **Implemented (rule-based; demo data in UI)**.

---

## Slide 17: Module — Yield Prediction

**Purpose:** Present harvest outlook.
**Key Message:** Estimated yield per field with a range and the factors that move it.

**On-Slide Content:**
- Estimated yield (t/ha) vs last season, per field
- Prediction interval (lower / upper)
- Contributing factors: soil moisture, temperature, fertilisation, disease pressure
- Clear caveat: estimates, not guarantees

**Visual Direction:** Bar chart "last season vs predicted" plus a factor list with positive/negative/neutral arrows (as in the app).

**Speaker Notes:** "The outlook combines crop baselines with current moisture and temperature. We show an interval, not a single number, because harvests depend on events no model can see."

**Project Evidence:** `services/api/app/services/yield_service.py` (`calculate_yield`), `apps/web/app/yield/page.tsx`, `GET /api/v1/yield/predictions`, `tests/test_yield.py`. Status: **Implemented (formula-based; demo data in UI)**. **[INTERNAL]** The page subtitle says "ML-powered"; the engine is a formula, so say "model-based estimate" or reword the subtitle before presenting.

---

## Slide 18: Module — Farm Map

**Purpose:** Show spatial awareness.
**Key Message:** Fields and sensor nodes on an interactive map, coloured by health.

**On-Slide Content:**
- Interactive Leaflet map with approximate field outlines and sensor-node markers
- Colour-coded health status; select a field for details
- Sensor node placement and status

**Visual Direction:** Full-width map screenshot with legend (healthy / warning / critical).

**Speaker Notes:** "The map connects numbers to places. Selecting a field shows its crop, area and node status."

**Project Evidence:** `apps/web/app/map/page.tsx`, `components/map/FarmMapLeaflet.tsx`, `GET /api/v1/farms/{id}/fields`. Status: **Implemented (demo data)**. Field outlines are approximate polygons drawn around each field's centre point, not surveyed GeoJSON boundaries; loading real boundaries from the API is the next wiring step (`tasks.md`).

---

## Slide 19: Module — Alerts

**Purpose:** Show prioritised attention management.
**Key Message:** Alerts are filterable by severity and category, and can be acknowledged.

**On-Slide Content:**
- Severities: info · warning · critical
- Categories: disease · irrigation · sensor · weather · yield
- Unread / critical counters; acknowledge one or all
- Automatic alerts from sensor thresholds (critical soil moisture, extreme heat)

**Visual Direction:** Screenshot of the alerts list with the filter chips highlighted.

**Speaker Notes:** "Alerts close the loop: when an ingested sensor reading breaches a threshold, the backend creates an alert immediately. In the interface growers can filter and acknowledge."

**Project Evidence:** `services/api/app/services/alert_service.py` (`evaluate_reading`), `apps/web/app/alerts/page.tsx`, `PATCH /api/v1/alerts/{id}/acknowledge`, `tests/test_alerts.py`. Status: **Implemented** (backend rules); UI acknowledgement uses demo state.

---

## Slide 20: Data flow and processing pipeline

**Purpose:** Show how data moves and is cleaned.
**Key Message:** Every incoming sensor reading is sanitised, evaluated and broadcast; every photo is gated before analysis.

**On-Slide Content:**
- **Sensor path:** `POST /telemetry` → clean (bounds, NaN/∞ handling, ISO-8601 UTC timestamps) → evaluate alert rules → append to history → push over WebSocket
- **Photo path:** upload → format validation → quality gate → crop ID → condition analysis → guidance
- Uniform response envelope; domain error codes (`CROP_NOT_SUPPORTED`, `INVALID_IMAGE_PAYLOAD`)

**Visual Direction:** Two parallel pipelines (top: sensor, bottom: photo) with data-shape labels between boxes.

**Speaker Notes:** "Dirty data is the norm in the field. Out-of-range or malformed values are clipped to physical bounds or replaced with defaults before they can trigger false alerts or distort charts."

**Project Evidence:** `services/api/app/services/data_cleaning_service.py`, `telemetry_service.py` (`ingest`, `broadcast`), `core/constants.py` (`SENSOR_BOUNDS`), `tests/test_data_cleaning.py`, `tests/test_telemetry.py`.

---

## Slide 21: Demonstration workflow

**Purpose:** Walk through a live demo.
**Key Message:** Five steps show capability and safe behaviour.

**On-Slide Content:**
1. Dashboard overview
2. Upload an **Apple** leaf → crop + category + guidance
3. Upload a **Tomato** leaf → same flow
4. Upload a **wheat / sugarcane / non-leaf** photo → safe rejection
5. Upload a **blurry** photo → retake advice

**Visual Direction:** Numbered storyboard with one screenshot per step.

**Speaker Notes:** "Steps four and five are intentional: they demonstrate that the system declines rather than guesses. Sample images are in `demo_images/`." **[INTERNAL]** Use the files `1_apple_cedar_rust.jpg`, `2_tomato_late_blight.jpg`, `3_capsicum_field_photo.jpg`, `4_reject_*.jpg`, `5_blurry_apple.jpg`. Avoid the "sample preset" buttons on the diagnostics page — they display stored sample outputs rather than live analysis.

**Project Evidence:** `demo_images/`, `/diagnostics` page; start commands in `CLAUDE.md`.

---

## Slide 22: Current capabilities and results

**Purpose:** Summarise verified outcomes without overclaiming.
**Key Message:** The pipeline behaves safely and consistently on real photographs; broad-category screening works best for fungal-type symptoms.

**On-Slide Content:**
- Backend automated tests: 136 passing (last run on build date)
- Frontend type-check and production build pass
- Non-crop images (wheat, sugarcane, rice, animals, objects) declined in internal checks
- Blurry/dark/low-resolution photos stopped before analysis
- Runs on CPU in well under a second per image after start-up
- Specific-disease accuracy: **not claimed** — models in training

**Visual Direction:** Four metric tiles (tests passing, build passing, safe rejection, CPU-only) plus one "roadmap" tile.

**Speaker Notes:** "We report what we verified. In an internal check on public sample photographs the system declined every non-crop image we tried, and gave a category only when it was clearly ahead. We are not presenting disease-level accuracy because per-crop models are still being trained."

**Project Evidence:** `pytest` result (136 passed), `npm run build`, `docs/models.md` → "Measured behaviour" table. **[INTERNAL]** Measured limits: of 189 public images, 18 received a category (15 correct — all fungal, 2 wrong, 1 unlabelled); healthy leaves were never labelled "Healthy"; look-alike unsupported leaves (grape/potato/corn) are sometimes read as a supported crop. Keep this ready for Q&A; do not state percentages on slides.

---

## Slide 23: Benefits and practical applications

**Purpose:** Connect features to value.
**Key Message:** Earlier attention, less guesswork, and a single place to look.

**On-Slide Content:**
- Faster triage of suspicious leaves
- Water use tied to measured soil moisture
- Fewer missed events through threshold alerts
- Clear uncertainty handling builds user trust
- Suitable for farms, agri-extension demos, education and pilots

**Visual Direction:** Benefit icons mapped to the user roles (grower, extension officer, student).

**Speaker Notes:** "Our goal is decision support, not replacing the agronomist. When confidence is low, the system routes the user to expert help."

**Project Evidence:** Category guidance "when to consult" in `app/knowledge/general_categories.py`; disease guidance in `app/knowledge/`.

---

## Slide 24: Reliability, data handling and security

**Purpose:** Show engineering discipline and be candid about boundaries.
**Key Message:** Input validation, safe failure and test coverage are in place; authentication and persistence are future work.

**On-Slide Content:**
- Input validation on every endpoint (Pydantic); image-payload checks
- Unsupported crops rejected with a clear error — never silently substituted
- Model files integrity-checked (pinned revision + SHA-256)
- Uploaded photos are analysed in memory and not stored by the API
- CORS restricted to configured origins
- Not yet implemented: authentication, multi-user tenancy, database persistence

**Visual Direction:** Checklist with green ticks for implemented items and a grey "roadmap" group.

**Speaker Notes:** "We separated what exists from what is planned. The API is stateless today, which simplifies privacy; accounts and persistence are explicit next steps."

**Project Evidence:** `core/crops.py`, `routers/diagnosis.py`, `scripts/fetch_general_model.py`, `core/config.py` (`ALLOWED_ORIGINS`), `tests/test_crops.py`.

---

## Slide 25: Current scope and limitations

**Purpose:** Be transparent so the evaluators trust the rest.
**Key Message:** The platform is a working foundation; some integrations and models are still to come.

**On-Slide Content:**
- Three crops only (Apple, Tomato, Capsicum); other crops deferred pending accessible datasets
- Photo analysis today is a coarse category screen; specific-disease models are in training
- Monitoring, irrigation, yield, alerts and map screens run on a built-in demo farm
- No IoT broker, cache or database integration yet
- Thresholds are starting values, not field-calibrated

**Visual Direction:** Two-column "Works today / Next to connect" layout.

**Speaker Notes:** "Our priority was a correct, safe pipeline and a clean architecture so that real data and trained models can be connected without redesign."

**Project Evidence:** `docs/models.md` (scope, limitations), `tasks.md`, `ARCHITECTURE.md`.

---

## Slide 26: Future enhancements

**Purpose:** Present a credible roadmap.
**Key Message:** Four clear next steps, each already prepared by existing tooling or design.

**On-Slide Content:**
1. Train and validate per-crop disease models (Colab notebook + scripts ready)
2. Add explainability heat-maps (UI viewer exists; needs model attention data)
3. Connect IoT: MQTT → ingestion worker → time-series store → live WebSocket
4. Persistence, authentication, and mobile-friendly capture
5. Field-condition image data to close the lab-vs-field gap; re-enable deferred crops

**Visual Direction:** Horizontal roadmap with "Now / Next / Later" lanes.

**Speaker Notes:** "Nothing here requires redesign: the model registry, the ingestion endpoint and the viewer components are already in place."

**Project Evidence:** `notebooks/train_models_colab.ipynb`, `scripts/{prepare_datasets,train_disease_model,make_colab_bundle}.py`, `components/diagnostics/XaiHeatmapViewer.tsx`, `ARCHITECTURE.md`.

---

## Slide 27: Conclusion

**Purpose:** Close the narrative.
**Key Message:** AgriSmart delivers a trustworthy, extensible foundation for AI-assisted crop management.

**On-Slide Content:**
- Problem → one platform for health, water and yield decisions
- Built: unified dashboard, safe leaf-photo pipeline, sensor ingestion and alerting
- Honest by design: refuses to guess, labels preliminary results
- Ready for real models and real sensors

**Visual Direction:** Single summary graphic: the five question cards from Slide 6, each with a green tick or "next" tag.

**Speaker Notes:** "To summarise: we built the platform, the safe image pipeline and the integration points, and we documented precisely what remains."

**Project Evidence:** Aggregate of the slides above.

---

## Slide 28: Q&A

**Purpose:** Invite questions.
**Key Message:** Thank you.

**On-Slide Content:**
- Questions?
- [Contact / repository / demo link]

**Visual Direction:** Clean closing slide with the title graphic.

**Speaker Notes:** See the appendix for prepared answers.

**Project Evidence:** —

---

# Appendix A — Presenter's internal verification notes (not for slides)

**Facts confirmed in the repository**
- 7 routers under `/api/v1`: health, farms, telemetry (incl. WebSocket), diagnose, irrigation, yield, alerts.
- Response envelope `{success, data, error}`; frontend `lib/api/client.ts` unwraps it.
- Supported crops defined once (`SUPPORTED_CROPS`); `pepper` is an alias of `capsicum`.
- Diagnosis result statuses: `ok | low_quality_image | crop_uncertain | crop_unsupported | model_unavailable | disease_uncertain`; tier field `specific | general_category`.
- Backend tests: 136 passed; `ruff check .` clean; frontend `tsc --noEmit` clean; `npm run build` passes.

**Items that must not be over-stated**
1. **Frontend data source.** Only the Diagnostics page calls the backend. Dashboard, Field Monitor, Irrigation, Yield, Alerts and Map read `lib/demo-data.ts`. "Live" values on Dashboard / Field Monitor are simulated in the browser.
2. **Irrigation and yield endpoints** return demo fixtures; the calculation logic (`evaluate_irrigation`, `calculate_yield`) exists and is unit-tested but the list endpoints do not call it.
3. **Persistence / IoT.** No database, Redis or MQTT is connected, although `DATABASE_URL`, `REDIS_URL`, `MQTT_BROKER_URL` appear in docs. `ARCHITECTURE.md` is a target design.
4. **Explainability.** The heat-map viewer exists in the UI, but the backend returns no attention map, so no heat-map is shown.
5. **Authentication.** None.
6. **Stale documents.** `spec.md` mentions Grad-CAM, PostgreSQL/SQLAlchemy and Next.js 14; `tasks.md` still lists the old "Early Blight" bias issue (resolved by the current pipeline); `docs/models.md` top section says "no weights installed" and predates the general tier (its last section is current). Do not quote these as current.
7. **Dead link.** The sidebar has a `/settings` link with no page behind it — avoid clicking it in the demo.
8. **Yield page subtitle** says "ML-powered"; the engine is formula-based.
9. **Sample presets** on the diagnostics page show stored sample outputs; use real uploads in the demo.

**Suggested answers to likely questions**
- *How accurate is the disease detection?* "We are not claiming disease-level accuracy yet. Today it is a preliminary category screen that declines when unsure; per-crop models are the training roadmap and the pipeline already prefers them when installed."
- *Why zero-shot / why not train first?* "Datasets and GPU time were the constraint; the zero-shot tier lets the full workflow work now and gives a safe baseline."
- *Is the sensor data real?* "The ingestion API and cleaning pipeline are real and tested; the demo farm supplies sample readings so the platform can be shown without hardware."
- *What if the leaf is from another crop?* "It is declined as 'not recognised' rather than forced into a supported crop; look-alike leaves can occasionally be misidentified, which is why results are marked preliminary."

**Screenshots to capture before building the deck**
Dashboard · Field Monitor (charts + NPK) · Diagnostics result (Apple) · Diagnostics blurry state · Diagnostics unsupported state · Irrigation detail · Yield chart · Map · Alerts with filters.
