// Core telemetry types
export interface SensorReading {
  timestamp: string;
  soil_moisture: number;
  temperature: number;
  humidity: number;
  ph_level: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
}

export interface Device {
  id: string;
  name: string;
  field_id: string;
  status: "online" | "offline" | "warning";
  last_seen: string;
  battery: number;
  signal: number;
}

export interface Field {
  id: string;
  name: string;
  farm_id: string;
  crop: string;
  area_hectares: number;
  health_score: number;
  status: "healthy" | "warning" | "critical";
  growth_stage: string;
  devices: Device[];
  latest_reading: SensorReading;
  coordinates: [number, number]; // [lat, lng]
}

export interface Farm {
  id: string;
  name: string;
  location: string;
  total_area_hectares: number;
  fields: Field[];
  overall_health: number;
}

// Alert types
export type AlertSeverity = "info" | "warning" | "critical";
export type AlertCategory = "disease" | "irrigation" | "sensor" | "weather" | "yield";

export interface Alert {
  id: string;
  field_id: string;
  field_name: string;
  category: AlertCategory;
  severity: AlertSeverity;
  title: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

// Supported crops (list lives in lib/crops.ts, mirrors the backend SUPPORTED_CROPS)
export type SupportedCropId = "apple" | "tomato" | "capsicum";

// Disease detection (automatic crop identification + crop-specific diagnosis)
export type DiagnosisStatus =
  | "ok"
  | "low_quality_image"
  | "crop_uncertain"
  | "crop_unsupported"
  | "model_unavailable"
  | "disease_uncertain";

export interface PredictionItem {
  label: string;
  display_name: string;
  probability: number;
}

export interface DiagnosisRecommendations {
  treatment: string[];
  prevention: string[];
}

// "general_category" = coarse zero-shot screening, never a specific disease
export type DiagnosisTier = "specific" | "general_category";
export type CropIdMethod = "trained_classifier" | "zero_shot_clip";

export interface DiagnosisCategory {
  id: string;
  label: string;
  confidence: number;
}

export interface DiagnosisCategoryGuidance {
  description: string;
  look_for: string[];
  consult: string;
}

export interface DiagnosisResult {
  status: DiagnosisStatus;
  message: string;
  user_action: string;
  detected_crop: string | null;
  crop_confidence: number | null;
  crop_candidates: PredictionItem[];
  disease_label: string | null;
  disease_name: string | null;
  disease_confidence: number | null;
  severity: "low" | "moderate" | "high" | "none" | null;
  predictions: PredictionItem[];
  symptoms: string[];
  recommendations: DiagnosisRecommendations | null;
  model_version: string | null;
  diagnosis_tier?: DiagnosisTier | null;
  tier_notice?: string | null;
  crop_id_method?: CropIdMethod | null;
  category?: DiagnosisCategory | null;
  category_predictions?: PredictionItem[];
  category_guidance?: DiagnosisCategoryGuidance | null;
  xai?: { method: string; heatmap_url: string } | null;
}

// Irrigation
export interface IrrigationRecommendation {
  field_id: string;
  field_name: string;
  crop: string;
  water_stress: "low" | "medium" | "high" | "critical";
  irrigation_required: boolean;
  estimated_duration_minutes: number;
  confidence: number;
  reasons: string[];
  sensor_snapshot: {
    soil_moisture: number;
    temperature: number;
    humidity: number;
  };
}

// Yield prediction
export interface YieldPrediction {
  crop: string;
  field_id: string;
  field_name: string;
  estimated_yield_t_per_hectare: number;
  prediction_interval: { lower: number; upper: number };
  confidence: number;
  factors: Array<{ name: string; impact: "positive" | "negative" | "neutral"; weight: number }>;
  last_season_yield: number;
}

// Chart data
export interface TelemetryPoint {
  time: string;
  moisture: number;
  temperature: number;
  humidity: number;
  ph: number;
}
