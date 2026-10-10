# AgriSmart — Presenter's internal notes (NOT for slides)

Companion to `ppt.md`. Do not upload this file to the PowerPoint add-in.


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

**Rural-entrepreneurship framing (added)**
- The theme is AgriTech and Rural Entrepreneurship. Slide 13 describes *proposed* user roles and service ideas only. There is no pilot, pricing, user, revenue or adoption data in the project; do not quote any.
- Safe to say: runs on CPU, photo analysis works offline after the model is fetched, browser-based, open-source stack.
- Do not say: "mobile app", "works on low-end phones", "affordable for X rupees", "increases income/yield by N%". None of these are verified.
- Likely question: "What is the business model?" Answer: "That is the proposed next phase; we would validate it through a pilot with a farmer group or advisory point before setting any pricing."
