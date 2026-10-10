// Single source of truth for the crops the app supports. Keep ids in sync with
// SUPPORTED_CROPS in services/api/app/core/constants.py.
// Wheat, sugarcane and rice/paddy are deferred (datasets not accessible); see docs/models.md.
import type { SupportedCropId } from "./types";

export const SUPPORTED_CROPS: ReadonlyArray<{ id: SupportedCropId; name: string }> = [
  { id: "apple", name: "Apple" },
  { id: "tomato", name: "Tomato" },
  { id: "capsicum", name: "Capsicum" },
];

/** "Apple, Tomato, Capsicum" for hints and messages. */
export const SUPPORTED_CROP_NAMES = SUPPORTED_CROPS.map((crop) => crop.name).join(", ");
