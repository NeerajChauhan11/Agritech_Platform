# prompt.md — Automatic Crop Identification + Disease Diagnosis, Scope Limited to Apple / Tomato / Capsicum

## 0. Read first (mandatory)
Read `AGENTS.md`, `patterns.md`, `tasks.md`, `spec.md`, `ARCHITECTURE.md`, then `apps/web/AGENTS.md`. Consult `apps/web/node_modules/next/dist/docs/` before writing any Next.js code. Follow the file-size caps, layering, naming and CSS-utility rules in `AGENTS.md`.

## 1. Objective
Make diagnosis fully automatic:

**Upload leaf image → quality gate → identify crop → select that crop's disease model → analyze → show diagnosis + recommendations.**

The user never has to pick a crop to run a diagnosis.

### 1.1 Active crop scope (current development phase)
Only these three crops are supported:

| Display name | Notes |
|---|---|
| Apple | |
| Tomato | |
| Capsicum | Inspect the repo for the existing identifier (`capsicum`, `pepper`, `bell_pepper`). Keep ONE canonical identifier end-to-end (backend enum, API, frontend types, dataset config, model metadata). If `pepper` is already used, keep it as an alias mapped to the canonical id; do not leave two competing ids. |

**Why the scope was reduced:** Google Colab cannot currently download or access the wheat dataset, and no accessible datasets are configured for the other crops. The reduction is deliberate. Wheat, Sugarcane and Rice/Paddy must not be advertised or accepted as active features. Potato and Corn (and any other crop that is not Apple/Tomato/Capsicum) are also out of active scope unless the repo shows a configured, available dataset and model for them, in which case report it and do not enable it without confirmation.

**Scope ≠ accuracy.** Restricting the supported list does not prove the disease models are accurate. Keep "supported crop" separate from "validated disease capability". Never fabricate disease classes, dataset paths, model availability or metrics.

## 2. Phase 1 — Inspect (no edits yet)
Report findings briefly before changing anything. Base everything on actual files, not assumptions about frameworks, paths or model formats.

1. **Pipeline trace:** diagnostics page → `apps/web/lib/api/*.ts` → diagnosis router → `diagnosis_service.py` → `vision_classifier.py`. Identify where the "always Tomato / Early Blight" bias originates (see `tasks.md`).
2. **Models and weights:** search the whole repo and `services/api/models/` for `.onnx .pt .pth .h5 .keras .tflite` and `*.meta.json`. For each: crop, class list, input size, preprocessing. State what is missing.
3. **Heuristics:** identify any colour-based or placeholder logic standing in for a trained model.
4. **Dataset/training config:** inspect `scripts/`, `notebooks/train_models_colab.ipynb`, `scripts/make_colab_bundle.py`, and any dataset registry or config. Note which datasets are referenced, hardcoded paths, and external download dependencies.
5. **Crop reference audit:** run a repo-wide, case-insensitive search (excluding `node_modules`, `.next`, `__pycache__`, `.venv`, build output, large binaries) for: `wheat`, `sugarcane`, `sugar cane`, `rice`, `paddy`, `potato`, `corn`, `maize`, plus `pepper`/`capsicum`. Classify every hit as:
   - **A. Active functionality** (enums, registries, dropdowns, routing, dataset config, demo fixtures served by the UI/API) → must change.
   - **B. Obsolete/dead code** → remove only if clearly unused and its usage was verified.
   - **C. Historical documentation / experiment records** (`tasks.md` history, notes, changelogs) → keep for traceability; add a one-line "out of current scope" note where helpful.
   - **D. Test fixtures** → update if they assert unsupported crops are supported; keep if they test rejection.
   - **E. Unrelated usage** (e.g. the word "rice" in unrelated text, a shared constant used elsewhere) → inspect usage before touching; leave alone if unrelated.
6. Present the classified list and a short change plan, then proceed.

## 3. Phase 2 — Backend (`services/api/app/`)
Keep layering: `routers/` (thin) → `services/` → `schemas/`. Thresholds and labels in `core/constants.py`. Demo responses use the same Pydantic schemas as real ones. Keep the `ApiResponse` envelope; domain errors via `HTTPException(detail={"code","message"})`.

### 3.1 Mandatory
1. **Single source of truth** for supported crops in `core/constants.py` (or the existing registry if one exists): `SUPPORTED_CROPS = ("apple", "tomato", "capsicum")` with display names and aliases. Every other module imports from it. No duplicated hardcoded lists.
2. **Remove wheat and sugarcane** from active crop enums, schemas, registries, dataset mappings, model config and routing. Ensure rice/paddy is not accepted either.
3. **Validation:** any endpoint that accepts a crop identifier must reject unsupported values (wheat, sugarcane, rice/paddy, anything unknown) with a clear domain error, e.g. `{"code": "CROP_NOT_SUPPORTED", "message": "...supported crops: apple, tomato, capsicum"}`. No silent fallback to Tomato or any other crop. Normalize case and aliases before validating.
4. **Crop identification** (`services/crop_identifier.py`, new unless an equivalent exists):
   - A trained classifier over the 3 crops plus an explicit `unknown / not_a_supported_leaf` class. A CLIP zero-shot fallback is acceptable only if no trained crop-ID weights exist and it is clearly labelled as such in the response and docs.
   - Return top-k with probabilities. Accept the crop only if top-1 ≥ `CROP_CONFIDENCE_MIN` and margin over top-2 ≥ `CROP_MARGIN_MIN` (both in constants).
   - A leaf of an unsupported crop (e.g. wheat, sugarcane, rice) must land in `unknown`/`crop_unsupported`, not be forced into one of the three crops. If the crop-ID model has no `unknown` class and cannot reject, say so as a limitation rather than hiding it.
5. **Model registry** (`services/disease_model_registry.py`, new unless equivalent exists):
   - Map crop → {weights path, class list, input size, preprocessing, version}, loaded from `*.meta.json` / config, not hardcoded paths.
   - Lazy-load and cache. Report per-crop availability: `available` / `weights_missing`.
   - Never fall back to another crop's model.
   - Expose via `GET /api/v1/diagnose/models` (extend if it exists), listing only the three crops.
6. **Quality gate** before inference: blur, exposure, minimum resolution, leaf coverage. Reject unusable images.
7. **Orchestrator** in `diagnosis_service.py`: quality gate → crop ID → registry lookup → disease inference → result. `status` is one of `ok`, `low_quality_image`, `crop_uncertain`, `crop_unsupported`, `model_unavailable`, `disease_uncertain`.
   - Non-`ok` statuses return a human-readable message and the action to take (retake, closer shot, single leaf, etc.). No invented disease.
   - Always include `detected_crop`, `crop_confidence`, disease confidence, top-k `predictions[]`, `model_version`.
   - Disease confidence below `DISEASE_CONFIDENCE_MIN` → `disease_uncertain`: show candidates, make no definitive claim.
8. **Recommendations/knowledge** in a data module (e.g. `app/knowledge/disease_info.py`), not in routers or pages: symptoms, treatment, prevention per (crop, disease) for every class of every registered model. Do not invent classes; derive them from the model metadata/dataset.
9. **Schemas:** extend the diagnosis response with `status`, `detected_crop`, `crop_confidence`, `predictions[]`, `symptoms`, `recommendations`, `model_version`. If the request currently takes a manual crop parameter, ignore it for routing, mark it deprecated, and keep validating it if supplied (unsupported value → `CROP_NOT_SUPPORTED`). Preserve existing API contracts otherwise.

### 3.2 Conditional (only if the repo has them)
- Other services/routers that use crops (irrigation, yield, alerts, telemetry, farms): restrict crop enums/options there to the three crops only after checking how they are used. Do not break unrelated logic; if a farm fixture holds an unsupported crop, update the fixture and note it.
- `app/demo/fixtures.py`: remove active unsupported-crop fixtures that the UI or API would surface; keep demo schema parity.

## 4. Phase 3 — ML data/training config (no fabrication)
1. Update dataset configuration, loaders and preprocessing in `scripts/` and `notebooks/train_models_colab.ipynb` (and `make_colab_bundle.py` if it references crops) to operate **only on apple, tomato, capsicum**. Remove wheat/sugarcane/rice dataset downloads from the active training path so Colab no longer tries to fetch the inaccessible wheat dataset.
2. Dataset sources must be configurable (env var / config file / notebook parameter), not hardcoded local or Drive paths. Do not assume a dataset exists because its name appears; check availability explicitly and fail with a clear message if missing.
3. Training, validation and inference must use the same crop list and class ordering, written to each model's `*.meta.json` (crop, classes, input size, normalization, version, training dataset name, validation metrics if produced).
4. Provide or keep a reproducible fine-tuning script with augmentation, a held-out validation split, and a metrics report (accuracy, per-class F1, confusion matrix) saved next to the weights.
5. If the crop-ID model needs training, define its dataset as the union of the three crops' images plus a negative/`unknown` set. If no negative set is accessible, report this limitation.
6. Do **not** delete existing datasets, trained models, DB records or experiment artifacts. Only remove them from active config. If an artifact for an out-of-scope crop exists, leave it on disk and mention it in the report.
7. Document in `docs/models.md` (or `tasks.md`): per crop, the dataset used, class list, architecture, expected file path/format, preprocessing, and what is missing. Note that PlantVillage-style lab images generalize poorly to field photos and recommend field-condition data. Note that Wheat, Sugarcane and Rice/Paddy are deferred because datasets are not currently accessible, and what would be needed to re-enable them.
8. Do not use colour heuristics, random output or placeholder logic as a model. If weights for a crop are missing, the registry reports `weights_missing` and the API returns `model_unavailable` for that crop.

## 5. Phase 4 — Frontend (`apps/web/`)
Preserve the existing design system, component structure, styling and responsive behaviour. Make only the changes the new scope requires. Types in `lib/types.ts`, API wrappers in `lib/api/`, demo data only in `lib/demo-data.ts`, styling via CSS variables and utility classes in `app/globals.css` (no inline styles or hex colours).

### 5.1 Mandatory
1. **Diagnostics flow:** remove the manual crop selector for diagnosis. Show the detected crop with its confidence, top predictions, symptoms and recommendations.
2. **Status states:** a distinct, clear UI state for each non-`ok` status (`low_quality_image`, `crop_uncertain`, `crop_unsupported`, `model_unavailable`, `disease_uncertain`) with the guidance message from the API. `crop_unsupported` should tell the user which crops are supported (Apple, Tomato, Capsicum).
3. **Supported-crop surfaces:** everywhere a crop list is shown or chosen (dropdowns, selection cards, forms, upload hints, dashboard widgets and crop statistics, crop-info sections, supported-crop listings, filters, labels, icons, navigation, empty states, validation messages, notifications), show only Apple, Tomato, Capsicum.
4. **Remove Wheat, Sugarcane and Rice/Paddy** from all active selections and displays, including Rice/Paddy even if it existed only in the UI and never in the backend.
5. Source the crop list from one shared constant in the frontend (e.g. in `lib/types.ts` or a small config module) that matches the backend identifiers; do not duplicate literals across components.
6. Update `lib/demo-data.ts` so demo content shows only the three crops.

### 5.2 Conditional
- Remove now-unused icons/assets/components only if verified unreferenced.
- Other pages (irrigation, yield, alerts, map, telemetry) that list crops: restrict to the three crops; leave their other behaviour unchanged.

## 6. Phase 5 — Tests
Add or update pytest tests (use the `client` fixture in `tests/conftest.py`):
- Crop validation: `apple`, `tomato`, `capsicum` accepted (plus alias handling); `wheat`, `sugarcane`, `rice`, `paddy`, unknown → `CROP_NOT_SUPPORTED` error in the `ApiResponse` envelope.
- Blurry image → `low_quality_image`; non-leaf image → `crop_uncertain`; unsupported-crop image → `crop_unsupported`/`crop_uncertain`; crop with missing weights → `model_unavailable`; low-confidence disease → `disease_uncertain`.
- Happy path with a mocked classifier: the correct per-crop model is selected; a model is never used for a different crop.
- Regression: different crop inputs do not all return Tomato or Early Blight.
- `GET /api/v1/diagnose/models` lists exactly the three crops.
- Update any existing tests that assumed wheat/sugarcane were supported.

## 7. Phase 6 — Verification (all mandatory)
Run and report results of:
```bash
# services/api
ruff check .
python -m pytest

# apps/web
npx tsc --noEmit      # must exit 0
npm run lint
npm run build
```
Then:
1. Repeat the repo-wide search from Phase 1 and list every remaining hit for `wheat`, `sugarcane`, `rice`, `paddy`, classified as active / historical documentation / test fixture / unrelated. **Active functionality must have zero hits** (except rejection logic and tests of rejection).
2. Start the API and check `GET /api/v1/diagnose/models`: only apple, tomato, capsicum, each `available` or `weights_missing` truthfully.
3. If feasible, exercise the diagnose endpoint with sample images and confirm status handling. If no weights exist, confirm `model_unavailable` is returned rather than a guessed disease.
4. Confirm unrelated features (dashboard, telemetry, map, irrigation, yield, alerts) still render and their tests pass.

## 8. Acceptance criteria
**Crops**
- [ ] Apple, Tomato, Capsicum are the only active supported crops, with one canonical id each, consistent across backend, frontend, dataset config and model metadata.
- [ ] Wheat and Sugarcane are not active anywhere; Rice/Paddy is not offered in any frontend crop interface.
- [ ] Dataset config and crop registries contain only the three crops, apart from clearly justified historical or explanatory references.

**Frontend**
- [ ] All crop selectors, cards, forms, filters, widgets and listings show only the three crops; no obsolete option is reachable through the normal UI.
- [ ] Diagnosis requires no manual crop selection; every status has a clear UI state.
- [ ] Design, responsiveness and unrelated features unchanged.

**Backend / ML**
- [ ] Unsupported crop identifiers are rejected with a clear error; no silent fallback.
- [ ] Model routing uses the correct per-crop configured resources; missing datasets/models are reported explicitly, never masked.
- [ ] No fabricated classes, paths, availability or metrics; no heuristic standing in for a model.
- [ ] Uncertain, low-quality or unsupported inputs produce an uncertainty status, not a disease claim.

**Validation**
- [ ] `ruff`, `pytest`, `tsc --noEmit`, `lint`, `build` pass, or each failure is documented with its cause.
- [ ] Final repo-wide search completed and classified.

## 9. Safety rules
- Inspect before editing; reuse existing architecture, naming, dependencies and patterns. Do not assume frameworks, dataset storage or model formats; verify them in the files.
- Do not rewrite working modules just to apply the scope change. No new dependencies or unrelated features unless a step above requires one, and then justify it.
- Never delete datasets, trained weights, DB records or experiment artifacts without a demonstrated need and explicit justification. Keep historical docs for traceability.
- If a crop reference is shared with unrelated code, inspect its usage first.
- If a required dataset or model is missing, report it. Do not substitute anything.
- Keep changes modular, maintainable and backward-compatible where reasonable.

## 10. Final report (required)
End with:
1. Files modified, added and removed, with one line each.
2. Checks executed and their results.
3. The classified list of remaining wheat/sugarcane/rice references.
4. What works end to end now; which of the three crops are blocked on missing weights and exactly what is needed (dataset, class list, architecture, file path/format).
5. Remaining limitations (e.g. crop-ID cannot reject unsupported leaves, lab-vs-field domain gap).

---

# Addendum (2026-10-10) — Inspection-Day Fast Path: General Disease Categories

## A1. Context and goal
Inspection is today and per-crop disease models are not trained yet. Provide a **working end-to-end demo** by adding a second, lighter diagnosis tier that reports a **general disease category** per crop instead of a specific disease. Keep it simple and fast; do not touch unrelated modules.

## A2. Honesty rules (non-negotiable; they override any "demo" shortcut)
- The tier must run a **real pretrained model on the uploaded image**. No hardcoded outputs, no fixtures, no random output, no colour heuristics, no filename/keyword tricks. (This amends the CLAUDE.md "no demo fixtures in place of a model" rule only in the sense that a real pretrained model may serve general categories; fixtures remain forbidden.)
- Every result from this tier must be labelled in the API (`diagnosis_tier: "general_category"`) and in the UI as **"Preliminary category screening — specific-disease model is in training"**. Never present a general category as a confirmed specific disease.
- Keep all existing gates: quality gate, crop identification and confidence thresholds, `crop_unsupported` / `crop_uncertain` / `low_quality_image`. When the category is uncertain, return `disease_uncertain` rather than guessing.
- If a specific-disease ONNX model for the identified crop is installed and `available`, use it (tier `specific`). Otherwise fall back to the general-category tier. Fall back to `model_unavailable` only if the general tier itself cannot load.

## A3. General categories (single shared list, in `core/constants.py` or `core/model_catalog.py`)
Define one list, used by backend, knowledge module and frontend types:

| id | Label | Typical examples (for guidance text only) |
|---|---|---|
| `healthy` | Healthy | no visible symptoms |
| `fungal` | Fungal leaf disease | spots, blight, scab, rust, mildew, mould |
| `bacterial` | Bacterial disease | water-soaked angular spots, bacterial spot, fire blight |
| `viral` | Viral disease | mosaic, curling, yellowing, stunting |
| `pest` | Pest damage | chewing, mines, mite stippling, webbing |
| `nutrient_stress` | Nutrient deficiency / stress | chlorosis, scorch, edge burn |

Per crop (apple, tomato, capsicum) define which categories are offered and 1–2 crop-relevant example diseases per category, taken from well-established, widely documented diseases of that crop. Do not invent disease names; if unsure, use a generic description.

## A4. Implementation (simple and fast)
1. **Inspect first:** check `requirements.txt`, the existing ONNX runtime usage, and how `crop_identifier.py` loads its model. Reuse whatever runtime is already a dependency (prefer ONNX Runtime over adding torch). Report the choice in one line.
2. **Model for the general tier:** use a pretrained zero-shot image-text model (CLIP-family) via the repo's existing runtime, scoring the image against text prompts per category (e.g. "a photo of a {crop} leaf with {symptom description}"). Keep prompts in the constants/knowledge module, not inline in services. If an existing trained crop-ID model is already available, keep using it for crop identification; otherwise the same CLIP model may do crop ID against the three crops plus an `unknown` prompt set, labelled as zero-shot.
3. **Offline-safe:** download the pretrained weights ahead of time into `services/api/models/` (or `AI_MODEL_PATH`) with a small script `scripts/fetch_general_model.py` that records the source, version and checksum in a `*.meta.json`. The demo must not need internet at inspection time. If the download is impossible in this environment, stop and report exactly what file is needed and where to put it. Do not substitute anything.
4. **New service** `services/general_category_classifier.py` (thin, one responsibility) returning top-k categories with probabilities. Add thresholds `CATEGORY_CONFIDENCE_MIN` and `CATEGORY_MARGIN_MIN` in constants. Below threshold → `disease_uncertain` with the top candidates shown and no definitive claim. Be conservative: report that zero-shot confidence is not calibrated and document the thresholds chosen and why.
5. **Orchestrator:** extend `diagnosis_service.py` with the tier selection from A2. Do not break the existing six statuses.
6. **Schemas:** add `diagnosis_tier` (`specific` | `general_category`), `category` (id + label), and `category_predictions[]` to the diagnosis response. Backward-compatible; keep the `ApiResponse` envelope.
7. **Knowledge** in `app/knowledge/`: per (crop, category) → short description, what to look for, immediate actions, prevention, and "when to consult an agronomist". Plain language; no dosage numbers or product names unless already in the repo's knowledge data.
8. **`GET /api/v1/diagnose/models`**: additionally report the general tier (`available` / `weights_missing`) and which crops have specific models.
9. **Frontend** (existing components, existing CSS utility classes, no hex colours):
   - Show detected crop + confidence, the general category, top category predictions, and the "Preliminary category screening" notice for `general_category` results.
   - Reuse the existing UI states for the non-`ok` statuses.
   - Update types in `lib/types.ts` and `lib/api/`. No demo data is needed for diagnosis results because they must come from the API.
10. **Docs:** add a short "Inspection demo mode" section to `docs/models.md`: what the general tier is, its limits (coarse categories, zero-shot, not validated on field data), and the path to specific models (the Colab training flow).

## A5. Tests (keep small and fast)
- General tier selected when no specific model exists; specific tier selected when one is installed (mock both).
- Low category confidence → `disease_uncertain`; blurry → `low_quality_image`; unsupported crop → `crop_unsupported`/`crop_uncertain`.
- Response always carries `diagnosis_tier`; a general result never contains a specific disease name as the headline claim.
- Run `ruff check .`, `python -m pytest`, `npx tsc --noEmit`, `npm run lint`, `npm run build`.

## A6. Inspection-day deliverable
Finish with:
1. The exact commands to start backend and frontend, and the one-line command that fetches the general model.
2. A 5-step demo script for the presenter: upload an Apple, a Tomato and a Capsicum leaf; upload a non-leaf or wheat/sugarcane image to show safe rejection; upload a blurry photo.
3. The talking points, stated truthfully: this tier is a coarse screen; per-crop specific-disease models are the training roadmap; unsupported crops and uncertain images are rejected on purpose.
4. Any case where the general tier performed poorly on the sample images you tried, with the images/results described. Do not hide weak results.

## A7. Constraints
- Smallest viable change; reuse the existing architecture and file-size/layering rules from `AGENTS.md`.
- No new dependencies unless the existing runtime cannot run the chosen model. Justify any addition.
- Do not delete datasets, weights or experiment artifacts.

---

# Addendum (2026-10-10) — Publish the Project to GitHub (Claude Code in the terminal)

## G1. Goal
Publish this repository (`apps/web`, `services/api`, `scripts`, `docs`, `notebooks`, `demo_images`, root docs) to GitHub safely, with a clean history and **no secrets, no oversized files and no build artifacts**. Do this only after the inspection/presentation work is finished. Do not change application code while doing it.

## G2. Rules (non-negotiable)
- **Confirm before anything outward-facing.** Before the first `git push`, show the user the exact remote URL, the branch name and the list of files about to be published, and wait for an explicit "yes". Never push on assumption.
- **Never** commit or push: `.env` files (`services/api/.env`), keys/tokens/credentials, `node_modules/`, `.next/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, virtual environments, or the model weights.
- **Model weights stay out of Git.** `services/api/models/clip_general/*.onnx` are 254 MB and 345 MB; GitHub rejects files over 100 MB. They are re-created by `python scripts/fetch_general_model.py`, so only the script is published. Do not use Git LFS unless the user asks.
- **No force-push**, no history rewriting on a pushed branch, no `--no-verify`, no changing the user's global git config. If something fails, report the exact error instead of working around it.
- Do not delete any local files, datasets or weights to make the push work.
- Do not print secret values in the terminal; report only the file names and variable names.

## G3. Steps
1. **Inspect first.**
   - `git rev-parse --is-inside-work-tree` (the folder is not a repository yet), `git --version`, `git config user.name`, `git config user.email`. If name or email is missing, ask the user; do not invent them.
   - Check whether `gh` (GitHub CLI) is installed; if not, use plain `git` with an HTTPS remote. Do not install tools without asking.
2. **Create a root `.gitignore`** (none exists at the repo root; `apps/web/.gitignore` already covers the frontend). It must contain at least:
   ```
   # secrets
   .env
   .env.*
   !.env.example
   # python
   __pycache__/
   *.pyc
   .venv/
   venv/
   .pytest_cache/
   .ruff_cache/
   # node / next
   node_modules/
   .next/
   # model weights and datasets (re-created by scripts)
   services/api/models/**/*.onnx
   services/api/models/**/*.pt
   services/api/models/**/*.pth
   data/
   # os / editor
   .DS_Store
   Thumbs.db
   .idea/
   .vscode/
   ```
   Keep `services/api/models/clip_general/meta.json` out as well unless the user wants it; it only describes weights that are not in the repo. Add `services/api/models/.gitkeep` if the empty folder should exist.
3. **Secrets check before staging.**
   - Open `services/api/.env` and `.env.example`; confirm `.env` is ignored and `.env.example` contains placeholders only (no real keys or passwords).
   - Search tracked-to-be files for obvious secrets (`api_key`, `secret`, `token`, `password`, `BEGIN PRIVATE KEY`) and report any hit.
4. **Initialise and stage.**
   - `git init -b main`
   - `git add .` then run `git status` and `git ls-files | wc -l`; list the 20 largest staged files with their sizes. **Stop and fix the ignore rules** if any staged file is larger than 50 MB or if `.env`, `node_modules`, `.next` or `*.onnx` appear.
5. **Commit** using the repository format `type(scope): description` from `AGENTS.md`, for example:
   `chore(repo): initial import of AgriSmart platform` — and end the commit message with the attribution line required by the session instructions, if one is given.
6. **Add the remote.** The target repository is `https://github.com/NeerajChauhan11/Agritech_Platform.git` (provided by the user, branch `main`). Before adding it, run the read-only check `git ls-remote https://github.com/NeerajChauhan11/Agritech_Platform.git`: empty output means the repository is empty and safe to push to; if it already has branches or commits, stop and ask the user (do not merge, overwrite or force-push). Then `git remote add origin https://github.com/NeerajChauhan11/Agritech_Platform.git` and verify with `git remote -v`.
7. **Push** (after the explicit confirmation required in G2): `git push -u origin main`. If authentication is needed, tell the user to run the login command themselves with the `!` prefix (for example `! gh auth login`, or enter a personal access token when Git prompts). Do not ask the user to paste tokens into the chat.
8. **Verify.** Run `git status` (clean), `git log --oneline -n 3`, and `git ls-remote --heads origin`. Ask the user to open the repository page and confirm the file tree.

## G4. After publishing — README for evaluators
If the repository has no root `README.md`, offer to add one containing: project name and theme (AgriTech and Rural Entrepreneurship), a one-paragraph description, the folder layout, **the start commands** (backend `python -m uvicorn app.main:app --port 8000` from `services/api`; frontend `npm install && npm run dev` from `apps/web`), the model-fetch command (`python scripts/fetch_general_model.py`), and the honest status table (what is implemented, what runs on demo data, what is planned). Commit it as `docs(readme): add project overview and setup`.

## G5. Report back
Finish with:
1. The remote URL and branch that were pushed, and the commit hash.
2. The number of files published and the largest file included.
3. The files deliberately excluded (secrets, weights, build output) and how to recreate the weights.
4. Anything that failed or was skipped, with the exact error text.

