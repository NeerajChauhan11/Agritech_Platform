# AgriSmart — Presentation Blueprint (15 slides)

Build **exactly 15 slides**, one per "Slide N" section below. Use **On-Slide Content** for the slide body, **Speaker Notes** for the presenter notes and **Visual Direction** as design guidance only (do not print Purpose, Key Message, Visual Direction or Project Evidence on the slides). Do not add slides beyond Slide 15.

**Deck theme: AgriTech and Rural Entrepreneurship.** Frame every slide around how technology helps rural growers and agri-entrepreneurs run viable, data-driven farm businesses. Visual style: earthy green and soil-brown palette, rural farm photography, simple icons, plain language. Do **not** add market-size, revenue, pricing, user-count or adoption numbers: none have been measured. Entrepreneurship content is *proposed use*, not validated deployment.

All technical claims are verified against the repository (2026-10-10). Status labels: **Implemented** · **Implemented (demo data)** (screen and API exist, values come from the built-in demo farm) · **Planned**.

---

## Slide 1: AgriSmart — AgriTech for rural farm enterprises

**Purpose:** Title slide.
**Key Message:** Affordable, data-driven decision support that helps rural growers run stronger farm businesses.

**On-Slide Content:**
- AgriSmart
- **AgriTech and Rural Entrepreneurship**
- AI-assisted crop health, irrigation and yield insight for Apple, Tomato and Capsicum growers
- [Team / Student names] · [Institution / Programme] · [Guide] · [Date]

**Visual Direction:** Leaf photograph with a dashboard screenshot inset; green brand colour.

**Speaker Notes:** "Our theme is AgriTech and Rural Entrepreneurship. A rural farm is a small business: every late disease call or badly timed irrigation costs money. AgriSmart brings leaf-photo screening, field monitoring, irrigation guidance, yield outlook and alerts into one platform for apple, tomato and capsicum growers."

**Project Evidence:** `apps/web/app/page.tsx`.

---

## Slide 2: Rural farm enterprises need timely, trustworthy decisions — without costly expert support

**Purpose:** Problem, motivation and objectives.
**Key Message:** A rural grower's income depends on acting early on disease, water and weather, but information and expert advice are scarce and scattered.

**On-Slide Content:**
- **Problem:** small farm businesses run on thin margins; disease noticed late; over/under-watering; data in separate places; limited access to advisors
- **Why now:** phone cameras, low-cost soil sensors and pretrained vision models make decision support affordable to build
- **Objectives:** (1) identify crop and screen leaf health, (2) monitor fields and alert, (3) recommend irrigation, (4) show yield outlook with a range, (5) deliver honest, low-infrastructure decision support a rural enterprise can adopt

**Visual Direction:** Left: four problem icons. Right: five numbered objectives.

**Speaker Notes:** "Every day a grower, who is also a small business owner, asks: is my crop healthy, does it need water, what should I expect? Today those answers come from different tools, from experience alone, or from an advisor who may be far away. Our objectives map directly to screens you can open in the app."

**Project Evidence:** `spec.md` §2, `AGENTS.md`, `services/api/tests/` (18 test files).

---

## Slide 3: One platform, seven screens — what is built today

**Purpose:** Proposed solution and honest feature inventory.
**Key Message:** One platform covers a rural farm enterprise's daily decisions; photo analysis runs on real uploads and hardware wiring is the next step.

**On-Slide Content:**

| Feature | Status |
|---|---|
| Leaf-photo quality check | Implemented |
| Crop identification (Apple / Tomato / Capsicum) | Implemented |
| Condition-category screening with guidance | Implemented |
| Specific-disease models per crop | Planned (training pipeline built) |
| Sensor ingestion: cleaning, alerts, live push | Implemented (API) |
| Dashboard, Field Monitor, Irrigation, Yield, Map, Alerts | Implemented (demo data) |
| MQTT / database persistence | Planned |

**Visual Direction:** Hub-and-spoke of the seven sidebar screens on the left; status table on the right.

**Speaker Notes:** "We organised the product around questions, not technologies. The photo pipeline works on real images; the monitoring screens run on a built-in demo farm so the whole platform can be shown without hardware, and the API already accepts real sensor payloads."

**Project Evidence:** `components/layout/Sidebar.tsx`, `services/api/app/main.py`, `tasks.md`, `lib/demo-data.ts`.

---

## Slide 4: A layered architecture on a modern, mainstream stack

**Purpose:** Architecture and technology stack.
**Key Message:** Thin web client over a layered FastAPI service with an image-analysis pipeline.

**On-Slide Content:**
- Web UI → REST API `/api/v1` (uniform `{success, data, error}` envelope) → model files on disk
- Routers → Services → Schemas; WebSocket for live telemetry
- **Frontend:** Next.js 16, React 19, TypeScript, Tailwind v4, Recharts, Leaflet
- **Backend:** Python, FastAPI, Pydantic v2
- **ML runtime:** ONNX Runtime, OpenCV, pretrained CLIP (ONNX)
- **Quality:** pytest, Ruff, ESLint, Docker (API)

**Visual Direction:** Three-tier diagram with the diagnosis pipeline inside the backend box; database/MQTT/Redis as dashed "planned" boxes.

**Speaker Notes:** "Routers validate and delegate, services hold logic, schemas define contracts. ONNX Runtime lets inference run on a normal CPU, and model files load from a configurable folder so they can be upgraded without code changes."

**Project Evidence:** `services/api/app/main.py`, `core/config.py`, `apps/web/package.json`, `requirements.txt`, `docker-compose.yml`.

---

## Slide 5: From a photo or a sensor reading to an action

**Purpose:** End-to-end workflow and data pipeline.
**Key Message:** Every photo is gated before analysis; every sensor reading is cleaned, checked and pushed.

**On-Slide Content:**
- **Photo path:** upload → format check → quality gate → crop ID → condition analysis → guidance
- **Sensor path:** `POST /telemetry` → clean (bounds, NaN handling, UTC timestamps) → alert rules → history → WebSocket push
- Domain errors with clear codes (`CROP_NOT_SUPPORTED`, `INVALID_IMAGE_PAYLOAD`)

**Visual Direction:** Two parallel swim-lanes (photo, sensor) with data labels between boxes.

**Speaker Notes:** "Field data is messy. Out-of-range or malformed values are clipped or replaced before they can trigger false alerts or distort charts."

**Project Evidence:** `data_cleaning_service.py`, `telemetry_service.py`, `alert_service.py`, `diagnosis_service.py`, `tests/test_data_cleaning.py`, `tests/test_telemetry.py`.

---

## Slide 6: Dashboard and Field Monitor — see the whole farm, then one field

**Purpose:** Monitoring screens.
**Key Message:** Glanceable summary on the dashboard, detailed trends per field.

**On-Slide Content:**
- Dashboard: farm health hero, metric cards, field cards, irrigation and yield widgets, recent alerts
- Field Monitor: field selector (4 demo fields), 24-hour charts, NPK range feedback, device battery/signal/status

**Visual Direction:** Two annotated screenshots side by side.

**Speaker Notes:** "Device health is visible, so a dead sensor is not mistaken for a dry field. In this demo configuration the readings vary around the demo farm's baselines; the same layout is ready for the live feed."

**Project Evidence:** `app/page.tsx`, `app/telemetry/page.tsx`, `components/dashboard/*`, `GET /api/v1/telemetry/{field_id}`. Status: **Implemented (demo data)**.

---

## Slide 7: Disease detection — a staged pipeline that can say "retake" or "not sure"

**Purpose:** Explain the photo pipeline.
**Key Message:** Check the photo, identify the crop, screen the condition, give guidance — or stop safely.

**On-Slide Content:**
1. **Photo quality check** — resolution, exposure, blur, leaf coverage
2. **Crop identification** — Apple / Tomato / Capsicum, or "not a supported leaf"
3. **Condition analysis** — the crop's own disease model when installed, otherwise a general category screen
4. **Guidance** — what to look for, immediate actions, prevention, when to consult an agronomist

**Visual Direction:** Four boxes left to right; under each, the safe outcome if it stops there.

**Speaker Notes:** "No crop selection is needed. Each stage can stop the process safely, and the result states which stage produced it and how confident the system is."

**Project Evidence:** `diagnosis_service.py`, `image_quality.py`, `crop_identifier.py`, `disease_model_registry.py`, `general_diagnosis.py`; `POST /api/v1/diagnose`.

---

## Slide 8: The AI component — a vision-language model with built-in refusal

**Purpose:** AI/ML role, inputs, outputs and upgrade path.
**Key Message:** A pretrained model turns a leaf photo into a ranked crop and condition-category estimate; specific-disease models plug in later.

**On-Slide Content:**
- **Input:** one leaf photo (JPG / PNG / WebP)
- **Model:** pretrained CLIP compared with text descriptions of crops and categories
- **Output:** crop + confidence, ranked categories, guidance, model version
- **Categories:** Healthy · Fungal · Bacterial · Viral · Pest damage · Nutrient stress
- Runs offline on CPU; weights fetched once and checksum-verified
- **Upgrade path:** per-crop disease models (training tooling included)

**Visual Direction:** Image encoder + text encoder → similarity → thresholds → result; badge "Upgrade path: specific-disease models".

**Speaker Notes:** "We used a pretrained model so the full workflow works today and gives a safe baseline. The registry automatically prefers a crop-specific model whenever one is installed, and we built the data preparation, training and ONNX export tools for those models."

**Project Evidence:** `clip_runtime.py`, `general_category_classifier.py`, `core/general_catalog.py`, `scripts/fetch_general_model.py`, `scripts/train_disease_model.py`, `notebooks/train_models_colab.ipynb`, `docs/models.md`. No accuracy figure is claimed.

---

## Slide 9: What the grower sees — clear results and clear refusals

**Purpose:** User-facing behaviour and verified outcomes.
**Key Message:** Every outcome is explained with a next step; results are marked preliminary.

**On-Slide Content:**
- Result: detected crop + confidence, category, symptoms to look for, actions, prevention
- Banner: "Preliminary category screening — specific-disease model is in training"
- States: Photo quality too low · Crop not recognised · Crop not supported · Model not installed · No confident category
- Verified: 136 backend tests passing; frontend type-check and build pass; non-crop images (wheat, sugarcane, rice, animals, objects) declined in internal checks

**Visual Direction:** Montage: result card with banner, blurry-photo state, unsupported-crop state.

**Speaker Notes:** "Poor photos get retake advice; unfamiliar plants are declined rather than forced into a wrong crop; uncertain results show candidates and say they are not a diagnosis. We are not presenting disease-level accuracy because per-crop models are still being trained."

**Project Evidence:** `components/diagnostics/*`, `schemas/diagnosis.py`, `tests/test_diagnosis.py`, `tests/test_general_tier.py`, `docs/models.md`.

---

## Slide 10: Irrigation Advisor and Yield Prediction — transparent, with uncertainty

**Purpose:** Decision-support modules.
**Key Message:** Rule-based, explainable recommendations; yield shown as a range.

**On-Slide Content:**
- **Irrigation:** moisture vs crop target → stress low / medium / high / critical, duration, reasons, one-click confirm
- **Yield:** estimate (t/ha) vs last season, lower/upper interval, factors (moisture, temperature, fertilisation, disease pressure)
- Caveat shown: estimates, not guarantees

**Visual Direction:** Irrigation detail screenshot left; yield bar chart with factor list right.

**Speaker Notes:** "The irrigation logic is explicit: critical below twenty percent moisture, otherwise the deficit against the crop's minimum drives the level and duration. The yield outlook is a formula-based estimate shown with an interval, because harvests depend on events no model can see."

**Project Evidence:** `irrigation_service.py`, `yield_service.py`, `core/constants.py` (`CROP_PROFILES`), `app/irrigation/page.tsx`, `app/yield/page.tsx`, `tests/test_irrigation.py`, `tests/test_yield.py`. Status: **Implemented (rule/formula-based; demo data in UI)**.

---

## Slide 11: Farm Map and Alerts — where to look, and what needs attention

**Purpose:** Spatial view and prioritisation.
**Key Message:** Fields on a map coloured by health; alerts filterable and acknowledgeable.

**On-Slide Content:**
- **Map:** Leaflet, approximate field outlines, sensor-node markers, health colours
- **Alerts:** severity (info / warning / critical), category (disease, irrigation, sensor, weather, yield), unread counters, acknowledge one or all
- Automatic alerts from thresholds: critical soil moisture, extreme heat

**Visual Direction:** Map screenshot with legend; alerts list with filter chips.

**Speaker Notes:** "When an ingested reading breaches a threshold, the backend creates an alert immediately. The map connects the numbers to places."

**Project Evidence:** `app/map/page.tsx`, `FarmMapLeaflet.tsx`, `alert_service.py`, `app/alerts/page.tsx`, `tests/test_alerts.py`. Status: **Implemented (demo data)**.

---

## Slide 12: Demonstration — five steps

**Purpose:** Live demo script.
**Key Message:** Capability and safe behaviour in five uploads.

**On-Slide Content:**
1. Dashboard overview
2. Upload an **Apple** leaf → crop + category + guidance
3. Upload a **Tomato** leaf → same flow
4. Upload a **wheat / sugarcane / non-leaf** photo → safe rejection
5. Upload a **blurry** photo → retake advice

**Visual Direction:** Storyboard, one screenshot per step.

**Speaker Notes:** "Steps four and five are intentional: they show the system declining rather than guessing. Sample images are in the `demo_images` folder."

**Project Evidence:** `demo_images/`, `/diagnostics`, start commands in `CLAUDE.md`.

---

## Slide 13: Enabling rural entrepreneurship — from decision support to farm-based services

**Purpose:** Connect the technology to the rural-entrepreneurship theme.
**Key Message:** Low-infrastructure, honest decision support can help rural growers and local service providers build more resilient farm businesses.

**On-Slide Content:**
- **Who it can serve (proposed):** small and mid-size growers · farmer groups and cooperatives · local advisory / extension service points · agri-input retailers and rural agri-startups
- **Why it suits rural settings:** runs on a standard CPU server (no GPU) · photo analysis works offline once the model is fetched · browser-based · open-source stack · says "consult an expert" when unsure
- **Enterprise opportunities (proposed, not yet validated):** photo-screening service point · shared field monitoring for a group of growers · data-driven irrigation and input planning
- **Value to the farm business:** earlier action, better water and input planning, a digital record of field conditions

**Visual Direction:** Value-chain diagram: Grower → AgriSmart → Local advisory point / Cooperative / Input dealer, over a rural farm photograph. Mark the opportunity boxes with a "proposed" tag.

**Speaker Notes:** "A farm is an enterprise, and the same platform can support several rural business roles: the grower themselves, a cooperative sharing monitoring, or a local advisory point that offers photo screening as a service. These are proposed uses that we have not yet piloted. What we can state today is that the system is designed for low-resource settings: it runs on an ordinary CPU, photo analysis works offline, and it is honest about uncertainty, which matters when livelihoods depend on the advice."

**Project Evidence:** `requirements.txt` (ONNX Runtime, CPU), `scripts/fetch_general_model.py` (offline weights), `app/knowledge/general_categories.py` ("when to consult"), `docs/models.md`. Business roles are proposals; no pilot, pricing or adoption data exists.

---

## Slide 14: Reliability, security and current scope

**Purpose:** Candid boundaries.
**Key Message:** Validation, safe failure and tests are in place; authentication, persistence and trained disease models are next.

**On-Slide Content:**
- **In place:** input validation on every endpoint; unsupported crops rejected, never substituted; uncertain results are never guessed (livelihood-critical advice); model files integrity-checked; photos analysed in memory and not stored; CORS limited to configured origins
- **Scope:** three crops only; coarse category screening today; monitoring screens run on a demo farm
- **Not yet:** authentication, database, IoT broker, field-calibrated thresholds, explainability heat-maps

**Visual Direction:** Two columns: green "Works today", grey "Next to connect".

**Speaker Notes:** "We separated what exists from what is planned. The API is stateless today, which simplifies privacy; accounts and persistence are explicit next steps."

**Project Evidence:** `core/crops.py`, `scripts/fetch_general_model.py`, `core/config.py`, `docs/models.md`, `ARCHITECTURE.md`.

---

## Slide 15: Roadmap, conclusion and questions

**Purpose:** Close the narrative and open Q&A.
**Key Message:** A trustworthy, extensible foundation, ready for real models and real sensors.

**On-Slide Content:**
- **Next:** (1) train and validate per-crop disease models, (2) explainability heat-maps, (3) IoT: MQTT → worker → time-series store → live feed, (4) persistence, authentication, mobile capture, (5) field-condition data and deferred crops, (6) pilot with local growers and a farmer group to validate usefulness and cost-effectiveness
- **Summary:** AgriTech for rural farm enterprises: unified dashboard · safe leaf-photo pipeline · sensor ingestion and alerting · honest by design
- Questions? · [Contact / repository / demo link]

**Visual Direction:** Now / Next / Later roadmap strip above a closing summary line.

**Speaker Notes:** "Our next step is to prove the value in the field by piloting with local growers and a farmer group. Nothing on the roadmap needs a redesign: the model registry, ingestion endpoint and viewer components are already in place. Thank you — we welcome your questions."

**Project Evidence:** `notebooks/train_models_colab.ipynb`, `scripts/*`, `XaiHeatmapViewer.tsx`, `ARCHITECTURE.md`.
