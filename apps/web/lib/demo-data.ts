import type { Farm, Alert, TelemetryPoint, DiagnosisResult, IrrigationRecommendation, YieldPrediction } from "./types";
import { addJitter } from "./utils";

// ── Demo Farm Data ──────────────────────────────────────────────────────────
export const DEMO_FARM: Farm = {
  id: "farm-alpha",
  name: "Green Valley Farm",
  location: "Chandigarh, Punjab, India",
  total_area_hectares: 24.5,
  overall_health: 78,
  fields: [
    {
      id: "field-01",
      name: "Tomato Field A",
      farm_id: "farm-alpha",
      crop: "Tomato",
      area_hectares: 5.2,
      health_score: 82,
      status: "healthy",
      growth_stage: "Fruiting",
      coordinates: [30.7333, 76.7794],
      devices: [
        { id: "esp32-node-01", name: "Node-01", field_id: "field-01", status: "online", last_seen: "Just now", battery: 87, signal: 94 },
        { id: "esp32-node-02", name: "Node-02", field_id: "field-01", status: "online", last_seen: "1 min ago", battery: 72, signal: 88 },
      ],
      latest_reading: {
        timestamp: new Date().toISOString(),
        soil_moisture: 42.5,
        temperature: 28.4,
        humidity: 65.0,
        ph_level: 6.8,
        nitrogen: 42.0,
        phosphorus: 28.0,
        potassium: 36.0,
      },
    },
    {
      id: "field-02",
      name: "Apple Orchard B",
      farm_id: "farm-alpha",
      crop: "Apple",
      area_hectares: 8.1,
      health_score: 61,
      status: "warning",
      growth_stage: "Fruit Set",
      coordinates: [30.7401, 76.7820],
      devices: [
        { id: "esp32-node-03", name: "Node-03", field_id: "field-02", status: "warning", last_seen: "3 min ago", battery: 31, signal: 65 },
        { id: "esp32-node-04", name: "Node-04", field_id: "field-02", status: "online", last_seen: "Just now", battery: 91, signal: 97 },
      ],
      latest_reading: {
        timestamp: new Date().toISOString(),
        soil_moisture: 29.1,
        temperature: 31.2,
        humidity: 52.0,
        ph_level: 7.2,
        nitrogen: 35.0,
        phosphorus: 22.0,
        potassium: 28.0,
      },
    },
    {
      id: "field-03",
      name: "Capsicum Field C",
      farm_id: "farm-alpha",
      crop: "Capsicum",
      area_hectares: 6.4,
      health_score: 91,
      status: "healthy",
      growth_stage: "Flowering",
      coordinates: [30.7280, 76.7760],
      devices: [
        { id: "esp32-node-05", name: "Node-05", field_id: "field-03", status: "online", last_seen: "Just now", battery: 78, signal: 92 },
      ],
      latest_reading: {
        timestamp: new Date().toISOString(),
        soil_moisture: 68.3,
        temperature: 26.8,
        humidity: 74.0,
        ph_level: 6.4,
        nitrogen: 55.0,
        phosphorus: 31.0,
        potassium: 42.0,
      },
    },
    {
      id: "field-04",
      name: "Tomato Field D",
      farm_id: "farm-alpha",
      crop: "Tomato",
      area_hectares: 4.8,
      health_score: 44,
      status: "critical",
      growth_stage: "Flowering",
      coordinates: [30.7350, 76.7850],
      devices: [
        { id: "esp32-node-06", name: "Node-06", field_id: "field-04", status: "offline", last_seen: "2 hrs ago", battery: 12, signal: 0 },
      ],
      latest_reading: {
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        soil_moisture: 18.2,
        temperature: 33.5,
        humidity: 44.0,
        ph_level: 7.8,
        nitrogen: 28.0,
        phosphorus: 18.0,
        potassium: 22.0,
      },
    },
  ],
};

// ── Telemetry History Generator ─────────────────────────────────────────────
function generateTelemetryHistory(
  baseMoisture: number,
  baseTemp: number,
  baseHumidity: number,
  basePh: number,
  points = 24
): TelemetryPoint[] {
  const now = Date.now();
  return Array.from({ length: points }, (_, i) => {
    const t = new Date(now - (points - 1 - i) * 60 * 60 * 1000);
    return {
      time: t.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
      moisture: Math.round(addJitter(baseMoisture, 5) * 10) / 10,
      temperature: Math.round(addJitter(baseTemp, 2) * 10) / 10,
      humidity: Math.round(addJitter(baseHumidity, 5) * 10) / 10,
      ph: Math.round(addJitter(basePh, 0.2) * 100) / 100,
    };
  });
}

export const DEMO_TELEMETRY: Record<string, TelemetryPoint[]> = {
  "field-01": generateTelemetryHistory(42, 28, 65, 6.8),
  "field-02": generateTelemetryHistory(29, 31, 52, 7.2),
  "field-03": generateTelemetryHistory(68, 27, 74, 6.4),
  "field-04": generateTelemetryHistory(18, 34, 44, 7.8),
};

// ── Alerts ──────────────────────────────────────────────────────────────────
export const DEMO_ALERTS: Alert[] = [
  {
    id: "alert-01",
    field_id: "field-04",
    field_name: "Tomato Field D",
    category: "sensor",
    severity: "critical",
    title: "Sensor Node Offline",
    message: "Node-06 has been offline for 2+ hours. Last soil moisture reading was critically low at 18.2%.",
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    acknowledged: false,
  },
  {
    id: "alert-02",
    field_id: "field-04",
    field_name: "Tomato Field D",
    category: "irrigation",
    severity: "critical",
    title: "Critical Water Stress",
    message: "Soil moisture at 18.2% — well below the 45% minimum for tomato. Immediate irrigation required.",
    timestamp: new Date(Date.now() - 6000000).toISOString(),
    acknowledged: false,
  },
  {
    id: "alert-03",
    field_id: "field-02",
    field_name: "Apple Orchard B",
    category: "disease",
    severity: "warning",
    title: "Disease Risk Elevated",
    message: "Heat (31.2°C) and low humidity (52%) increase plant stress and susceptibility to fungal disease. Inspect crop.",
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    acknowledged: false,
  },
  {
    id: "alert-04",
    field_id: "field-02",
    field_name: "Apple Orchard B",
    category: "sensor",
    severity: "warning",
    title: "Low Battery — Node-03",
    message: "Node-03 battery at 31%. Consider recharging to avoid data gaps.",
    timestamp: new Date(Date.now() - 1800000).toISOString(),
    acknowledged: false,
  },
  {
    id: "alert-05",
    field_id: "field-01",
    field_name: "Tomato Field A",
    category: "irrigation",
    severity: "info",
    title: "Irrigation Recommended",
    message: "Soil moisture trending downward. AI recommends 12-minute irrigation cycle within the next 4 hours.",
    timestamp: new Date(Date.now() - 900000).toISOString(),
    acknowledged: true,
  },
];

// ── Disease Detection Demo ──────────────────────────────────────────────────
// Illustrative results in the real API shape, shown by the sample presets only.
const DEMO_TOMATO_CROP = {
  detected_crop: "Tomato",
  crop_confidence: 0.97,
  crop_candidates: [
    { label: "tomato", display_name: "Tomato", probability: 0.97 },
    { label: "apple", display_name: "Apple", probability: 0.02 },
    { label: "capsicum", display_name: "Capsicum", probability: 0.01 },
  ],
  model_version: "demo",
};

export const DEMO_DIAGNOSIS: DiagnosisResult = {
  ...DEMO_TOMATO_CROP,
  status: "ok",
  message: "Early Blight (Alternaria solani) detected on Tomato.",
  user_action: "",
  disease_label: "early_blight",
  disease_name: "Early Blight (Alternaria solani)",
  disease_confidence: 0.91,
  severity: "moderate",
  predictions: [
    { label: "early_blight", display_name: "Early Blight (Alternaria solani)", probability: 0.91 },
    { label: "late_blight", display_name: "Late Blight (Phytophthora infestans)", probability: 0.05 },
    { label: "healthy", display_name: "Healthy", probability: 0.04 },
  ],
  symptoms: [
    "Dark brown spots with concentric rings (target-like) on older leaves.",
    "Yellowing of tissue around the spots; affected leaves may drop.",
  ],
  recommendations: {
    treatment: [
      "Remove and destroy heavily affected lower leaves.",
      "Apply a protectant fungicide registered for the crop, following the label.",
    ],
    prevention: [
      "Rotate away from tomato, capsicum and other Solanaceae crops for 2-3 seasons.",
      "Mulch the soil, water at the base, and avoid wetting the foliage.",
    ],
  },
};

export const DEMO_DIAGNOSIS_HEALTHY: DiagnosisResult = {
  ...DEMO_TOMATO_CROP,
  status: "ok",
  message: "No disease detected.",
  user_action: "",
  disease_label: "healthy",
  disease_name: "Healthy",
  disease_confidence: 0.96,
  severity: "none",
  predictions: [
    { label: "healthy", display_name: "Healthy", probability: 0.96 },
    { label: "septoria_leaf_spot", display_name: "Septoria Leaf Spot (Septoria lycopersici)", probability: 0.03 },
    { label: "early_blight", display_name: "Early Blight (Alternaria solani)", probability: 0.01 },
  ],
  symptoms: ["No disease symptoms detected on the leaf."],
  recommendations: {
    treatment: ["No treatment needed."],
    prevention: ["Keep scouting weekly and maintain balanced nutrition and irrigation."],
  },
};

export const DEMO_DIAGNOSIS_YELLOW_LEAF: DiagnosisResult = {
  ...DEMO_TOMATO_CROP,
  status: "ok",
  message: "Tomato Yellow Leaf Curl Virus detected on Tomato.",
  user_action: "",
  disease_label: "yellow_leaf_curl_virus",
  disease_name: "Tomato Yellow Leaf Curl Virus",
  disease_confidence: 0.89,
  severity: "high",
  predictions: [
    { label: "yellow_leaf_curl_virus", display_name: "Tomato Yellow Leaf Curl Virus", probability: 0.89 },
    { label: "mosaic_virus", display_name: "Tomato Mosaic Virus", probability: 0.07 },
    { label: "healthy", display_name: "Healthy", probability: 0.04 },
  ],
  symptoms: [
    "Upward curling and yellowing of leaf margins, stunted growth.",
    "Flower drop and poor fruit set. Spread by whiteflies.",
  ],
  recommendations: {
    treatment: [
      "There is no cure: remove and destroy infected plants early.",
      "Control whiteflies with sticky traps, soap/neem sprays or registered insecticides.",
    ],
    prevention: ["Use resistant or tolerant varieties and virus-free transplants."],
  },
};

export const DEMO_DIAGNOSIS_UNCERTAIN: DiagnosisResult = {
  ...DEMO_TOMATO_CROP,
  status: "disease_uncertain",
  message: "The model is not confident enough to name a disease.",
  user_action:
    "Retake a sharper close-up of the affected area, or consult an agronomist. The candidates below are possibilities, not a diagnosis.",
  disease_label: null,
  disease_name: null,
  disease_confidence: 0.41,
  severity: null,
  predictions: [
    { label: "early_blight", display_name: "Early Blight (Alternaria solani)", probability: 0.41 },
    { label: "target_spot", display_name: "Target Spot (Corynespora cassiicola)", probability: 0.33 },
    { label: "septoria_leaf_spot", display_name: "Septoria Leaf Spot (Septoria lycopersici)", probability: 0.18 },
  ],
  symptoms: [],
  recommendations: null,
};

export const DEMO_DIAGNOSIS_UNAVAILABLE: DiagnosisResult = {
  status: "model_unavailable",
  message: "The Capsicum disease model is not installed on the server.",
  user_action: "Ask the administrator to install the model weights (see docs/models.md).",
  detected_crop: "Capsicum",
  crop_confidence: 0.94,
  crop_candidates: [
    { label: "capsicum", display_name: "Capsicum", probability: 0.94 },
    { label: "tomato", display_name: "Tomato", probability: 0.04 },
    { label: "apple", display_name: "Apple", probability: 0.02 },
  ],
  disease_label: null,
  disease_name: null,
  disease_confidence: null,
  severity: null,
  predictions: [],
  symptoms: [],
  recommendations: null,
  model_version: null,
};

export const DEMO_DIAGNOSIS_PRESETS = [
  { label: "Early Blight (Tomato)", data: DEMO_DIAGNOSIS, url: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Early_blight_-_tomato.jpg/320px-Early_blight_-_tomato.jpg" },
  { label: "Healthy Foliage", data: DEMO_DIAGNOSIS_HEALTHY, url: "https://images.unsplash.com/photo-1592417817098-8f3d69109853?w=320&auto=format&fit=crop&q=60" },
  { label: "Yellow Leaf Curl", data: DEMO_DIAGNOSIS_YELLOW_LEAF, url: "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=320&auto=format&fit=crop&q=60" },
  { label: "Uncertain Disease", data: DEMO_DIAGNOSIS_UNCERTAIN, url: "https://images.unsplash.com/photo-1592417817098-8f3d69109853?w=320&auto=format&fit=crop&q=60" },
  { label: "Model Unavailable", data: DEMO_DIAGNOSIS_UNAVAILABLE, url: "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=320&auto=format&fit=crop&q=60" },
];

// ── Irrigation Recommendations ──────────────────────────────────────────────
export const DEMO_IRRIGATION: IrrigationRecommendation[] = [
  {
    field_id: "field-01",
    field_name: "Tomato Field A",
    crop: "Tomato",
    water_stress: "high",
    irrigation_required: true,
    estimated_duration_minutes: 12,
    confidence: 0.87,
    reasons: [
      "Soil moisture (42.5%) is below the 50% optimal threshold for fruiting stage",
      "Temperature elevated at 28.4°C — increases evapotranspiration rate",
      "Rainfall probability is below 10% for the next 48 hours",
      "Current growth stage (Fruiting) has high water demand",
    ],
    sensor_snapshot: { soil_moisture: 42.5, temperature: 28.4, humidity: 65.0 },
  },
  {
    field_id: "field-02",
    field_name: "Apple Orchard B",
    crop: "Apple",
    water_stress: "medium",
    irrigation_required: true,
    estimated_duration_minutes: 8,
    confidence: 0.74,
    reasons: [
      "Soil moisture (29.1%) approaching lower threshold for fruit set stage",
      "High temperature (31.2°C) accelerating moisture loss",
      "No significant rainfall in past 7 days",
    ],
    sensor_snapshot: { soil_moisture: 29.1, temperature: 31.2, humidity: 52.0 },
  },
  {
    field_id: "field-03",
    field_name: "Capsicum Field C",
    crop: "Capsicum",
    water_stress: "low",
    irrigation_required: false,
    estimated_duration_minutes: 0,
    confidence: 0.92,
    reasons: [
      "Soil moisture (68.3%) is within the optimal 50-70% range for capsicum",
      "Humidity is optimal at 74%",
      "Current flowering stage is adequately watered",
    ],
    sensor_snapshot: { soil_moisture: 68.3, temperature: 26.8, humidity: 74.0 },
  },
  {
    field_id: "field-04",
    field_name: "Tomato Field D",
    crop: "Tomato",
    water_stress: "critical",
    irrigation_required: true,
    estimated_duration_minutes: 25,
    confidence: 0.96,
    reasons: [
      "CRITICAL: Soil moisture at 18.2% — severely below 45% threshold",
      "Extreme temperature stress at 33.5°C",
      "Sensor offline — last known reading 2+ hours ago indicates deteriorating conditions",
      "Flowering stage has high water demand",
    ],
    sensor_snapshot: { soil_moisture: 18.2, temperature: 33.5, humidity: 44.0 },
  },
];

// ── Dashboard Summary Widgets ────────────────────────────────────────────────
export const DEMO_IRRIGATION_SUMMARY = [
  { name: "Tomato Field A",    stress: "HIGH",     minutes: 12, color: "#f59e0b" },
  { name: "Apple Orchard B",     stress: "MEDIUM",   minutes: 8,  color: "#fbbf24" },
  { name: "Capsicum Field C",      stress: "LOW",      minutes: 0,  color: "#22c55e" },
  { name: "Tomato Field D", stress: "CRITICAL", minutes: 25, color: "#ef4444" },
];

export const DEMO_YIELD_SUMMARY = [
  { crop: "Tomato", field: "Field A", est: 4.8, last: 4.2, conf: 82 },
  { crop: "Apple",  field: "Field B", est: 12.6, last: 13.1, conf: 71 },
  { crop: "Capsicum",   field: "Field C", est: 9.4, last: 8.8, conf: 88 },
];

// ── Yield Predictions ───────────────────────────────────────────────────────
export const DEMO_YIELD: YieldPrediction[] = [
  {
    crop: "Tomato",
    field_id: "field-01",
    field_name: "Tomato Field A",
    estimated_yield_t_per_hectare: 4.8,
    prediction_interval: { lower: 4.4, upper: 5.2 },
    confidence: 0.82,
    last_season_yield: 4.2,
    factors: [
      { name: "Soil Moisture", impact: "positive", weight: 0.85 },
      { name: "Temperature", impact: "negative", weight: 0.72 },
      { name: "Fertilization", impact: "positive", weight: 0.91 },
      { name: "Disease Pressure", impact: "negative", weight: 0.45 },
      { name: "Irrigation History", impact: "positive", weight: 0.78 },
    ],
  },
  {
    crop: "Apple",
    field_id: "field-02",
    field_name: "Apple Orchard B",
    estimated_yield_t_per_hectare: 12.6,
    prediction_interval: { lower: 11.4, upper: 13.8 },
    confidence: 0.71,
    last_season_yield: 13.1,
    factors: [
      { name: "Soil Moisture", impact: "negative", weight: 0.62 },
      { name: "Temperature", impact: "negative", weight: 0.68 },
      { name: "Fertilization", impact: "neutral", weight: 0.55 },
      { name: "Disease Pressure", impact: "negative", weight: 0.38 },
    ],
  },
  {
    crop: "Capsicum",
    field_id: "field-03",
    field_name: "Capsicum Field C",
    estimated_yield_t_per_hectare: 9.4,
    prediction_interval: { lower: 8.7, upper: 10.1 },
    confidence: 0.88,
    last_season_yield: 8.8,
    factors: [
      { name: "Soil Moisture", impact: "positive", weight: 0.94 },
      { name: "Temperature", impact: "positive", weight: 0.82 },
      { name: "Fertilization", impact: "positive", weight: 0.89 },
      { name: "Disease Pressure", impact: "neutral", weight: 0.22 },
    ],
  },
];

