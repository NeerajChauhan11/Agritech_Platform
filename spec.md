# System Specification — AgriSmart Platform

## 1. System Architecture
AgriSmart is a full-stack precision agriculture and AI-driven farm management platform structured as a monorepo:

- **Frontend (`apps/web`)**: Built with **Next.js 14+ (App Router)**, **React 18**, and **TypeScript**. Uses modern vanilla CSS tokens and utility classes (`globals.css`), **Recharts** for field analytics, and **Leaflet** for GIS field mapping.
- **Backend Services (`services/api`)**: Built with **FastAPI (Python 3.11+)**, **Pydantic v2** for schemas, and **SQLAlchemy** ORM. Handles sensor ingestion, AI disease diagnostics, irrigation scheduling, and telemetry.
- **Data & Ingestion Pipeline**: Supported by **PostgreSQL** (relational data), **Redis** (caching & real-time telemetry streaming), and **MQTT Broker** (EMQX/HiveMQ for field IoT hardware data ingestion).
- **AI / ML Engine**: Multi-class PyTorch / ONNX model execution pipeline for plant disease diagnosis with Grad-CAM Explainable AI (XAI) heatmap visualization.

```
┌─────────────────────────────────────────────────────────────┐
│                      Next.js Web UI                         │
│   (Dashboard, Diagnostics, GIS Maps, Telemetry Charts)      │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST / WebSockets
┌──────────────────────────────▼──────────────────────────────┐
│                     FastAPI Gateway                         │
├───────────────┬─────────────────────────────┬───────────────┤
│ Telemetry Router │    Diagnosis & XAI Service  │  Irrigation   │
└───────┬───────┴──────────────┬──────────────┴───────┬───────┘
        │                      │                      │
┌───────▼───────┐      ┌───────▼───────┐      ┌───────▼───────┐
│ MQTT / Redis  │      │ ONNX Engine   │      │ PostgreSQL DB │
└───────────────┘      └───────────────┘      └───────────────┘
```

---

## 2. Core Feature Specifications

### 2.1 AI Plant Disease Diagnostics & Explainability (XAI)
- **Upload Engine**: Accepts leaf image uploads via drag-and-drop or file input.
- **Multi-Class Classification**: Identifies crop health states across multiple categories (e.g., Healthy, Early Blight, Late Blight, Leaf Mold, Yellow Leaf Curl).
- **Grad-CAM Visualization**: Computes visual attention maps overlaying the original image to show exact regions influencing model predictions. Supports Original, Heatmap, and Overlay viewing modes.

### 2.2 Dynamic Field GIS & Telemetry
- **Interactive Mapping**: GeoJSON-based field boundaries with soil sensor node placement overlays.
- **Real-Time Sensor Ingestion**: Monitors soil moisture (%), ambient temperature (°C), relative humidity (%), and soil NPK nutrient ratios.
- **Historical Analysis**: Time-series charts for 24h/7d soil health trends.

### 2.3 Smart Irrigation Advisor
- **Stress Index Computation**: Calculates crop water stress indices based on moisture levels and evapotranspiration data.
- **Actionable Watering Recommendations**: Delivers automated daily irrigation duration (in minutes) per zone.

### 2.4 Yield Prediction Model
- **Harvest Forecasts**: Provides estimated crop yield (tons/hectare) alongside confidence intervals based on seasonal weather patterns and field history.

---

## 3. Database Schemas & Data Models

### 3.1 `Farm`
- `id` (UUID / int, Primary Key)
- `name` (string)
- `location` (string / LatLng)
- `total_area_hectares` (float)
- `created_at` (timestamp)

### 3.2 `Field`
- `id` (UUID / int, Primary Key)
- `farm_id` (ForeignKey -> Farm.id)
- `name` (string)
- `crop_type` (string)
- `area_hectares` (float)
- `boundary_geojson` (JSON string / Geometry)

### 3.3 `Device` (IoT Sensor Node)
- `id` (UUID / string, Primary Key)
- `field_id` (ForeignKey -> Field.id)
- `serial_number` (string, Unique)
- `device_type` (enum: `SOIL_NODE`, `WEATHER_STATION`, `VALVE_CONTROLLER`)
- `status` (enum: `ONLINE`, `OFFLINE`, `LOW_BATTERY`)
- `last_seen` (timestamp)

### 3.4 `TelemetryReading`
- `id` (int, Primary Key)
- `device_id` (ForeignKey -> Device.id)
- `timestamp` (timestamp)
- `soil_moisture` (float)
- `temperature` (float)
- `humidity` (float)
- `npk_nitrogen` (float)
- `npk_phosphorus` (float)
- `npk_potassium` (float)

### 3.5 `DiagnosisRecord`
- `id` (UUID / int, Primary Key)
- `field_id` (ForeignKey -> Field.id, Optional)
- `image_url` (string)
- `disease_detected` (string)
- `confidence` (float)
- `confidence_scores` (JSON key-value of class probabilities)
- `grad_cam_heatmap_url` (string)
- `created_at` (timestamp)

---

## 4. Environment Configuration (`.env`)
- `DEMO_MODE`: `true` | `false` (when true, uses local mock fixtures without database or model overhead)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `MQTT_BROKER_URL`: MQTT broker endpoint
- `AI_MODEL_PATH`: Path to ONNX / PyTorch model weights
- `NEXT_PUBLIC_API_URL`: FastAPI gateway base URL
