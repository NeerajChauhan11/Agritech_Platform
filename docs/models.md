# AI Models — Crop Identification & Disease Diagnosis

Diagnosis is fully automatic: **photo → image-quality gate → crop identification → that crop's own disease model → diagnosis, symptoms and recommendations.** The farmer never selects a crop.

## Active crop scope: Apple, Tomato, Capsicum

Only these three crops are supported in this development phase. They are defined once in `SUPPORTED_CROPS` (`app/core/constants.py`; the frontend mirror is `apps/web/lib/crops.ts`). `capsicum` is the canonical id; `pepper`, `bell_pepper`, `sweet_pepper` are accepted aliases (`CROP_ALIASES`). Any other crop identifier is rejected with `CROP_NOT_SUPPORTED` (HTTP 400), never silently replaced by Tomato.

**Deferred crops: Wheat, Sugarcane, Rice/Paddy** (Potato and Corn are also out of scope). Their datasets are not currently accessible from Google Colab (the wheat dataset cannot be downloaded) and none is configured, so they are not advertised, accepted or trained. Their old catalog entries, knowledge text and download code were removed from the active paths.

*Scope is not accuracy.* Supporting a crop only means the pipeline will try it; a crop's disease capability is validated only once its model is trained and its held-out metrics (`*.metrics.json`) are reviewed.

### Re-enabling a deferred crop later

1. Obtain an accessible dataset and confirm its class list.
2. Add the crop to `SUPPORTED_CROPS`, `CROP_DISPLAY_NAMES` and `CROP_PROFILES` (`constants.py`), add its `ModelSpec` to `DISEASE_MODEL_SPECS` (`model_catalog.py`), and mirror it in `apps/web/lib/crops.ts` and `SupportedCropId` (`lib/types.ts`).
3. Write a knowledge entry for every class in `app/knowledge/`, add its dataset to `scripts/prepare_datasets.py`, and add it to `CROPS` in the Colab notebook.
4. Retrain the crop identifier (its class list changes) and the new crop's model.

**Current state: no trained weights are installed.** The repository ships the whole pipeline, but every model below is `weights_missing`, so `POST /api/v1/diagnose` returns `status: "model_unavailable"` until weights are added. The API never invents a result and never falls back to another crop's model.

Check what is installed at any time: `GET /api/v1/diagnose/models`.

## How the pipeline decides

| Stage | Module | Outcome when it fails |
|---|---|---|
| Image-quality gate (resolution, exposure, blur, leaf coverage) | `services/image_quality.py` | `low_quality_image` + what to retake |
| Crop identification | `services/crop_identifier.py` | `crop_uncertain` (low confidence, small margin, or `unknown`), `crop_unsupported` (confident crop with no registry entry), `model_unavailable` (weights missing) |
| Per-crop model lookup | `services/disease_model_registry.py` | `model_unavailable` |
| Disease inference + guidance | `services/diagnosis_service.py`, `app/knowledge/` | `disease_uncertain` (top-1 below threshold: candidates shown, no diagnosis) |

Thresholds live in `app/core/constants.py`: `CROP_CONFIDENCE_MIN` (0.70), `CROP_MARGIN_MIN` (0.20), `DISEASE_CONFIDENCE_MIN` (0.60) and the `QUALITY_*` values. These are starting points, **not calibrated on real data**: tune them on a held-out set of real photos once models exist.

## Expected files

All files live in the directory set by `AI_MODEL_PATH` (default `services/api/models/`).

| Model | File | Classes (output order) | Status |
|---|---|---|---|
| Crop identifier | `crop_id.onnx` | apple, capsicum, tomato, **unknown** (alphabetical, then `unknown`) | weights_missing |
| Apple | `disease_apple.onnx` | apple_scab, black_rot, cedar_apple_rust, healthy | weights_missing |
| Tomato | `disease_tomato.onnx` | bacterial_spot, early_blight, late_blight, leaf_mold, septoria_leaf_spot, spider_mites, target_spot, yellow_leaf_curl_virus, mosaic_virus, healthy | weights_missing |
| Capsicum | `disease_capsicum.onnx` | bacterial_spot, healthy | weights_missing |

The Capsicum class list is short because PlantVillage's *Pepper, bell* folders only contain bacterial spot and healthy leaves. A model with two classes cannot recognise any other capsicum disease; it will report one of the two (or `disease_uncertain`) rather than "other". Extend the class list only when you have labelled data for more diseases.

Weights from an earlier eight-crop experiment, if any exist outside this repository, are not compatible: the crop identifier's class list changed, and `disease_pepper.onnx` must be retrained and renamed `disease_capsicum.onnx`. Nothing was deleted from disk by the scope change (the repository contains no weights).

The single source of truth for class lists is `app/core/model_catalog.py`. The training script reads it, so a trained model always matches what the API expects. Each `.onnx` may have a `.meta.json` next to it (written by the training script): the API reads its `version` and refuses to load a model whose `classes` differ from the catalog.

## Format, architecture and preprocessing

- **Format:** ONNX, run with ONNX Runtime on CPU. Input `input` `float32 [N,3,224,224]`, output `logits` `[N,num_classes]` (softmax is applied by the API).
- **Architecture:** MobileNetV3-Large fine-tuned from ImageNet weights (any backbone works if it exports to this interface).
- **Preprocessing (must match training):** BGR→RGB, resize directly to 224×224 (no crop), scale to 0–1, normalise with ImageNet mean `(0.485, 0.456, 0.406)` and std `(0.229, 0.224, 0.225)`, channels-first.

## Datasets to use for each missing model

Check each dataset's licence before use, and reconcile its class folders with the catalog (the training script stops and lists any mismatch; map names with `--alias FOLDER=CLASS`).

| Model | Recommended data | Notes |
|---|---|---|
| Apple, Tomato, Capsicum | [PlantVillage](https://github.com/spMohanty/PlantVillage-Dataset) (folders like `Tomato___Early_blight`, `Pepper,_bell___healthy`; the prep script maps them by crop) | Lab-style images, see the warning below. Add field images from [PlantDoc](https://ar5iv.labs.arxiv.org/html/1911.10317) (about 2,600 web images, 27 classes, 13 species) where classes overlap. |
| Crop identifier | Built by `prepare_datasets.py`: one folder per supported crop plus `unknown/` | `unknown` is filled with other PlantVillage/PlantDoc species (potato, corn, grape, ... so unsupported leaves are rejected) and generic non-plant photos (DTD textures, Flowers102). **Wheat, sugarcane and rice leaves are not in the negative set** because those datasets are inaccessible, so the identifier may be unreliable on them. Add your own photos of non-crop things and of those crops to `data/crop_id/unknown/`. |

Dataset sources are configurable, not hardcoded: set `AGRISMART_PLANTVILLAGE_SRC` / `AGRISMART_PLANTDOC_SRC` to a git URL or a local clone. If a source cannot be reached or its layout is unexpected, `prepare_datasets.py` stops with an explicit message.

I could not download or open these datasets while building this, so class names and counts come from their descriptions: verify them after download.

> **PlantVillage generalises poorly to field photos.** Its images are mostly single leaves on a uniform background under controlled light. Models trained only on it score very high on its own test split and drop sharply on phone photos taken in a field. Treat the validation accuracy the script reports as an upper bound, collect field-condition photos (the PlantDoc, wheat, sugarcane and RiceLeafBD sets above are closer), and photograph your own fields for the final fine-tune and for threshold calibration.

## Training

### Easiest path: Google Colab (no local GPU or dataset needed)

1. `python scripts/make_colab_bundle.py` creates `agrismart_colab_bundle.zip` (re-run it whenever `model_catalog.py` changes).
2. Open `notebooks/train_models_colab.ipynb` in [Google Colab](https://colab.research.google.com), set a **T4 GPU** runtime and run the cells in order.
3. The notebook runs `scripts/prepare_datasets.py` (downloads PlantVillage and PlantDoc plus generic non-plant photos for `unknown`), trains the three supported crops and the crop identifier, and saves the results to your Drive.
4. Copy the `*.onnx` and `*.meta.json` files into `services/api/models/` and restart the API.

`prepare_datasets.py` prints a per-class image count: read it, and fix any `INCOMPLETE` crop before trusting its model. The PlantDoc class mapping is our reading of its labels (see `PLANTDOC_MAP`); Neither dataset was downloaded or inspected while making this change, so folder names come from their public descriptions: verify them on the first run.

**Crop-identifier risk:** the identifier is trained on images from several different datasets, and can learn the *photo style* (clean lab background vs phone field photo) instead of the plant. PlantDoc field photos are prioritised in the per-crop sample to reduce this, but the real fix is adding your own phone photos of each crop (and of non-crop things such as hands, soil and people for `unknown`) to `data/crop_id/` before training.

### Manual route

```bash
python -m venv .venv-train && .venv-train/Scripts/activate        # separate environment
pip install -r scripts/requirements-train.txt

# one model per crop
python scripts/train_disease_model.py --mode disease --crop apple    --data-dir data/disease/apple
python scripts/train_disease_model.py --mode disease --crop tomato   --data-dir data/disease/tomato
python scripts/train_disease_model.py --mode disease --crop capsicum --data-dir data/disease/capsicum   # --crop pepper also works

# crop identifier (folders: apple/ capsicum/ tomato/ unknown/)
python scripts/train_disease_model.py --mode crop-id --data-dir data/crop_id
```

`--help` lists epochs, batch size, learning rate, validation fraction, seed and `--alias`. The script:

1. maps dataset folders to the catalog classes (and stops on any mismatch),
2. makes a stratified, seeded train / held-out validation split,
3. trains with augmentation (random resized crop, flips, rotation, colour jitter) and class-weighted loss: first the new head, then the whole network,
4. evaluates the final epoch on the held-out split (no checkpoint picking on it),
5. exports ONNX and checks it reproduces the PyTorch outputs when `onnxruntime` is installed,
6. writes next to the weights: `<name>.meta.json` (version, crop key, classes, preprocessing, dataset path and name, seed, validation accuracy) and `<name>.metrics.json` (accuracy, macro F1, per-class precision/recall/F1/support, confusion matrix).

Copy the `.onnx` and `.meta.json` into `AI_MODEL_PATH`, restart the API, and confirm with `GET /api/v1/diagnose/models`.

> The training script has not been run end to end in this repository's environment (PyTorch is not installed there). Its split, metrics and dataset-matching logic is unit-tested (`tests/test_training_script.py`); the training and ONNX export steps need a first run on a machine with PyTorch.

## Adding or changing a crop or class

1. Edit the class tuple in `app/core/model_catalog.py` (order = model output order). To add a whole crop, see "Re-enabling a deferred crop" above.
2. Add a knowledge entry for every class in `app/knowledge/` (a test fails if one is missing).
3. Train, copy the weights, restart.

## Known limitations

- No Grad-CAM / attention map is returned: the previous heatmap was a colour mask rather than model attention, so it was removed. Real Grad-CAM needs the PyTorch graph and can be added later as `xai` in the response.
- The quality-gate thresholds and the crop/disease confidence thresholds are untuned defaults.
- One photo is classified as a whole; there is no per-leaf localisation or multi-disease detection.
- The crop identifier can only reject unsupported leaves it was trained against (other PlantVillage/PlantDoc species and generic photos). Wheat, sugarcane and rice leaves may be forced into Apple, Tomato or Capsicum, or end as `crop_uncertain`.
- `CROP_PROFILES` agronomic baselines for apple and capsicum (irrigation/yield advisors) are approximate defaults, not measured data.

## Inspection demo mode: general disease categories (zero-shot)

Per-crop disease models are not trained yet, so diagnosis has a second, coarse tier. It is used only when the identified crop has no installed specific model (an installed `disease_<crop>.onnx` always wins).

- **What it is:** a pretrained, *unmodified* OpenAI CLIP ViT-B/16 (MIT licence, ONNX export `Xenova/clip-vit-base-patch16`, pinned revision) run through the existing ONNX Runtime. The leaf image is compared with text prompts and ranked into six categories: Healthy, Fungal, Bacterial, Viral, Pest damage, Nutrient stress. Prompts live in `app/core/general_catalog.py`; advice in `app/knowledge/general_categories.py`.
- **Crop identification** falls back to the same CLIP model (prompts for Apple / Tomato / Capsicum plus many `unknown` concepts) when `crop_id.onnx` is not installed. The response says so (`crop_id_method: "zero_shot_clip"`). A trained `crop_id.onnx` takes priority when present.
- **Labelling:** every result of this tier has `diagnosis_tier: "general_category"` and the notice "Preliminary category screening — specific-disease model is in training". It never names a specific disease (`disease_name` is null). Low confidence returns `disease_uncertain`.
- **Setup (online once, offline afterwards):** `python scripts/fetch_general_model.py` downloads four files (about 600 MB) into `services/api/models/clip_general/`, verifies pinned SHA-256 checksums and writes `meta.json` (source, revision, version, checksums). If it cannot download, place `vision_model.onnx`, `text_model.onnx`, `vocab.json`, `merges.txt` from the Hugging Face repo `Xenova/clip-vit-base-patch16` (folder `onnx/` for the two models) in that folder.
- **Thresholds:** `CROP_CONFIDENCE_MIN` 0.70 / `CROP_MARGIN_MIN` 0.20 (unchanged), `CATEGORY_CONFIDENCE_MIN` 0.60 / `CATEGORY_MARGIN_MIN` 0.15. Zero-shot scores are relative softmax values, **not calibrated probabilities**. The category threshold was picked on the same small sample used to compare prompts, so treat it as indicative.

### Measured behaviour (189 public images: PlantVillage lab photos plus Wikimedia field photos; one 3-way split for prompt choice, one held-out)

| Check | Result |
|---|---|
| Crop-ID model size (supported-crop recall, held-out split) | ViT-B/32 13-27% (unusable); ViT-B/16 51-83% depending on how prompts are aggregated, so B/16 with averaged prompt embeddings is used. ViT-L/14 could not be loaded here (needs external-data files). |
| Wheat, sugarcane, rice, cat, keyboard photos (15 images) | 15/15 rejected (`crop_uncertain` or `low_quality_image`); none passed as a crop |
| Look-alike unsupported leaves (grape, potato, corn lab photos) | Often accepted at the crop gate as Apple/Tomato/Capsicum (about 40%), but at the final thresholds none of them produced an `ok` category: all ended as `disease_uncertain` |
| Supported-crop leaves (lab + field photos) | About half pass the crop gate; the rest are `crop_uncertain` (retake the photo) |
| Accepted (`ok`) category results | 18 of 189 images: 15 correct (all **fungal**), 2 wrong (a bacterial-spot and a spider-mite leaf both called fungal), 1 field pepper photo called nutrient stress (truth unknown) |
| Healthy leaves | **Never** returned as "Healthy": they end as `crop_uncertain` or `disease_uncertain` |
| Bacterial, viral, pest leaves | Never correctly categorised; `disease_uncertain` or mislabelled as fungal |
| Speed | about 0.15 s per image on CPU after a one-off ~3 s model load |

### Limits and the path to real models

Coarse categories, zero-shot, not trained or validated on field data, biased towards "fungal" for any spotted leaf, and no nutrient-stress test images were available. It is a screening aid, not a diagnosis. The route to specific diseases is unchanged: train the per-crop models with the Colab flow above and drop `disease_<crop>.onnx` (+ `.meta.json`) into the models folder; the tier selection then switches to `diagnosis_tier: "specific"` for that crop automatically.
