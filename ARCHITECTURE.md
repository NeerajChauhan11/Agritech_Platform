# ARCHITECTURE.md: AgriSmart Precision Agriculture Platform

## 1. System Overview & Core Objectives

AgriSmart is an enterprise-grade, interactive Precision Agriculture platform designed to integrate Internet of Things (IoT) field telemetry, computer vision for plant disease detection, machine learning for yield prediction, and Explainable AI (XAI) for actionable farmer insights.

### Core Objectives

- **Real-time Telemetry:** Ingest and visualize soil, climate, and irrigation data with low latency via WebSockets and MQTT.
- **Computer Vision Diagnostics:** Provide crop disease detection with XAI heatmaps (Grad-CAM / SHAP) using edge-optimized lightweight models.
- **Predictive Analytics:** Offer crop yield estimation, water requirement forecasting, and automated fertigation recommendations.
- **Farmer-Centric Decision Support:** Convert sensor and AI outputs into simple, explainable recommendations.
- **Agent-First Architecture:** Maintain clean separation of concerns, strict TypeScript interfaces, modular services, and explicit API schemas for AI coding agents such as Antigravity, Cursor, Claude Code, and Windsurf.
- **Hackathon Reliability:** Support a demo/offline mode so the platform remains usable when cloud, MQTT, or external APIs are unavailable.

---

## 2. Architecture Principles

1. **Modular first:** Prefer a modular architecture over unnecessary microservice fragmentation.
2. **Teacher/Farmer final authority:** AI provides recommendations and explanations; it does not autonomously make irreversible agricultural decisions.
3. **Explainability by design:** Every important AI recommendation should expose the factors that influenced it.
4. **Strict contracts:** APIs, database models, and shared TypeScript interfaces must be explicit and versioned.
5. **Fail gracefully:** Sensor, MQTT, AI, or external-service failures must not crash the dashboard.
6. **Demo-first reliability:** Every major feature must have a deterministic demo/mock-data path.
7. **Security by default:** Secrets stay in environment variables; external inputs are validated.
8. **Observable systems:** Log important ingestion, inference, recommendation, and error events.
9. **Code quality by default:** Every file obeys the standards defined in [`AGENTS.md`](./AGENTS.md) — single responsibility, file size caps, no hardcoded data in route/page files, shared CSS utility classes, and layered service architecture. These rules apply to all layers (frontend, backend, scripts) and are enforced automatically by AI agents and during cleanup passes.

---

## 3. Tech Stack Matrix

| Layer | Technology | Justification |
| --- | --- | --- |
| **Frontend Framework** | **Next.js 15+** (App Router, React 19) | Server Components, Server Actions, SSR/SSG, and strong TypeScript support. |
| **Styling & UI Components** | **Tailwind CSS v4**, **Shadcn UI**, **Framer Motion** | Accessible, responsive, customizable UI with polished interactions. |
| **Data Visualization** | **Tremor**, **Recharts** | Time-series telemetry, KPI cards, trends, and analytical dashboards. |
| **GIS / Farm Mapping** | **Leaflet** or **Mapbox GL** | Interactive farm boundaries, sensor locations, and field-health visualization. |
| **Real-time Ingestion** | **MQTT Broker (EMQX / HiveMQ)**, **WebSockets** | Low-overhead IoT telemetry and browser live updates. |
| **Backend & APIs** | **FastAPI (Python 3.11+)** | High-performance API, ML inference, validation, and orchestration. |
| **Database** | **PostgreSQL 16 + TimescaleDB** | Relational data plus efficient time-series storage. |
| **Vector Storage** | **pgvector** | Future RAG/knowledge-base support without introducing another database. |
| **Cache / Pub-Sub** | **Redis** | Real-time event distribution, caching, rate limiting, and ephemeral state. |
| **AI / ML** | **PyTorch**, **Ultralytics YOLO**, **ONNX Runtime** | Computer vision inference and edge-friendly deployment. |
| **XAI** | **SHAP**, **LIME**, **Grad-CAM** | Model interpretability and farmer-facing explanations. |
| **Deployment** | **Docker**, **Vercel**, **AWS / Fly.io** | Reproducible local development and flexible deployment. |

---

## 4. Recommended Hackathon Architecture

For the initial Chandigarh University hackathon implementation, use a **modular backend with a separately deployable AI service**, rather than implementing a large collection of independent microservices.

```text
                    ┌──────────────────────────────┐
                    │       FARMER / ADMIN         │
                    │   Next.js Web Dashboard      │
                    └──────────────┬───────────────┘
                                   │
                       REST / WebSocket / Upload
                                   │
             ┌─────────────────────▼─────────────────────┐
             │              FastAPI Backend              │
             │                                           │
             │  ┌───────────┐ ┌────────────┐ ┌────────┐ │
             │  │Telemetry  │ │Decision    │ │ Auth   │ │
             │  │Service    │ │Engine      │ │Service │ │
             │  └─────┬─────┘ └─────┬──────┘ └────────┘ │
             │        │              │                   │
             │  ┌─────▼──────────────▼────────────────┐  │
             │  │       AI / ML Integration Layer     │  │
             │  │ Disease + Yield + Water + XAI       │  │
             │  └──────────────────┬───────────────────┘  │
             └─────────────────────┼─────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
        ┌─────▼─────┐        ┌─────▼─────┐       ┌────▼─────┐
        │ PostgreSQL│        │   Redis    │       │   MQTT   │
        │ +Timescale│        │ Pub/Sub    │       │  EMQX    │
        └───────────┘        └────────────┘       └────┬─────┘
                                                       │
                              ┌────────────────────────┼──────────────┐
                              │                        │              │
                         ┌────▼────┐              ┌────▼────┐    ┌────▼─────┐
                         │ Soil    │              │ Weather │    │ Irrigation│
                         │ Sensors │              │ Sensors │    │ Controller│
                         │ ESP32   │              │ ESP32   │    │ Relay     │
                         └─────────┘              └─────────┘    └──────────┘
```

### Architectural Rule

Do **not** use a database trigger as the primary real-time messaging mechanism.

Use:

```text
ESP32
  ↓ MQTT
EMQX
  ↓
FastAPI Telemetry Worker
  ├──→ TimescaleDB
  └──→ Redis Pub/Sub
             ↓
        WebSocket Layer
             ↓
        Next.js Dashboard
```

This keeps persistence and real-time event distribution decoupled.

---

## 5. Core Product Modules

### 5.1 Smart Field Monitor

Displays:

- Soil moisture
- Temperature
- Humidity
- pH
- NPK values where available
- Sensor status
- Last-seen timestamp
- Field health status

### 5.2 AI Irrigation Advisor

The system should convert sensor and environmental data into an explainable recommendation.

Example:

```text
FIELD A — TOMATO

Soil Moisture        31%
Temperature          29.4°C
Humidity             61%
pH                    6.7

AI ANALYSIS

Water Stress          HIGH
Disease Risk          LOW
Irrigation Need       HIGH

RECOMMENDATION

Irrigate Field A
Estimated duration: 12 minutes

WHY?

- Soil moisture is below the configured crop threshold.
- Temperature is elevated.
- No significant rainfall is expected/detected.
- Current crop growth stage requires higher moisture.

Confidence: 87%
```

The recommendation must be treated as decision support, not an autonomous agricultural command.

### 5.3 Crop Disease Vision

Workflow:

```text
Leaf Image
    ↓
Pre-processing
    ↓
AI Classification / Detection
    ↓
Disease Probability
    ↓
Grad-CAM / XAI
    ↓
Severity Assessment
    ↓
Farmer-Friendly Explanation
    ↓
Recommended Next Action
```

### 5.4 Yield Prediction

Inputs may include:

- Crop type
- Field area
- Historical yield
- Soil parameters
- Weather
- Irrigation history
- Fertilization history
- Growth stage

Output:

```text
Estimated Yield: 4.8 tonnes/hectare
Prediction Range: 4.4–5.2 tonnes/hectare
Confidence: 82%
```

Predictions must clearly state that they are estimates and depend on data quality.

### 5.5 Farm Intelligence Map

Display:

- Farm boundaries
- Sensor locations
- Field health
- Soil-moisture zones
- Irrigation zones
- Disease alerts
- Sensor connectivity

---

## 6. High-Level System Architecture

```mermaid
graph TD

    subgraph Field["Field Layer — IoT & Edge"]
        ESP32["ESP32 / Raspberry Pi"] -->|"MQTT / TLS"| Broker["EMQX MQTT Broker"]
        Camera["Mobile Camera / UAV"] -->|"HTTP POST"| Gateway["API Gateway"]
        Relay["Irrigation Relay"] <-->|"Control"| ESP32
    end

    subgraph Ingestion["Data Ingestion & Real-Time Pipeline"]
        Broker -->|"Subscribe"| Ingest["FastAPI Telemetry Worker"]
        Ingest -->|"Validate + Store"| TimescaleDB[("PostgreSQL + TimescaleDB")]
        Ingest -->|"Publish Event"| Redis["Redis Pub/Sub"]
        Redis -->|"WebSocket"| WebServer["Next.js App Server"]
    end

    subgraph AI["AI & Analytics"]
        Gateway -->|"Image Upload"| FastApiML["FastAPI AI Service"]
        FastApiML -->|"Inference"| Model["PyTorch / ONNX"]
        Model -->|"Feature Maps"| XAI["XAI Engine"]
        XAI -->|"Explanation"| FastApiML
        FastApiML -->|"Audit / Results"| PostgresDB[("PostgreSQL")]
        TimescaleDB -->|"Sensor Features"| Decision["Decision Engine"]
        Decision -->|"Recommendation"| FastApiML
    end

    subgraph Client["Client Application"]
        WebServer <-->|"REST / Server Actions"| UI["Next.js Dashboard"]
        Redis -->|"Live Telemetry"| UI
        UI -->|"GIS + Charts + XAI"| User["Farmer / Admin"]
    end
```

---

## 7. Repository & Directory Structure

```text
agrismart-platform/
├── .github/
│   └── workflows/
│       ├── deploy-frontend.yml
│       └── deploy-ai-service.yml
│
├── apps/
│   ├── web/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── (dashboard)/
│   │   │   │   ├── telemetry/
│   │   │   ├── diagnostics/
│   │   │   ├── irrigation/
│   │   │   ├── yield/
│   │   │   ├── map/
│   │   │   ├── fields/
│   │   │   ├── settings/
│   │   │   └── page.tsx
│   │   ├── api/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── dashboard/
│   │   │   ├── telemetry/
│   │   │   ├── diagnostics/
│   │   │   ├── irrigation/
│   │   │   ├── map/
│   │   │   └── xai/
│   │   ├── lib/
│   │   │   ├── hooks/
│   │   │   ├── api/
│   │   │   ├── config.ts
│   │   │   └── db.ts
│   │   └── public/
│   │
│   └── ai-service/
│       ├── app/
│       │   ├── api/
│       │   │   └── v1/
│       │   │       ├── diagnose.py
│       │   │       ├── yield_prediction.py
│       │   │       ├── irrigation.py
│       │   │       └── health.py
│       │   ├── core/
│       │   │   ├── config.py
│       │   │   ├── logging.py
│       │   │   └── security.py
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── services/
│       │   │   ├── inference_service.py
│       │   │   ├── xai_service.py
│       │   │   ├── yield_service.py
│       │   │   └── irrigation_service.py
│       │   └── main.py
│       ├── tests/
│       ├── Dockerfile
│       └── requirements.txt
│
├── packages/
│   ├── database/
│   │   ├── schema/
│   │   └── migrations/
│   ├── config/
│   └── types/
│       ├── telemetry.ts
│       ├── diagnostics.ts
│       ├── irrigation.ts
│       ├── yield.ts
│       └── api.ts
│
├── data/
│   ├── demo/
│   ├── models/
│   └── sample-images/
│
├── docs/
│   ├── API.md
│   ├── DATABASE.md
│   ├── MQTT.md
│   └── AI_MODELS.md
│
├── docker-compose.yml
├── .env.example
├── package.json
├── README.md
└── ARCHITECTURE.md
```

---

## 8. Frontend Specification

### 8.1 Design System

- Responsive dark/light theme.
- Tailwind CSS v4.
- Shadcn UI.
- Accessible contrast and typography.
- Large touch-friendly controls for outdoor/mobile use.
- Dashboard optimized for quick interpretation rather than dense technical output.

### 8.2 Dashboard

The primary dashboard should contain:

1. Overall farm health score.
2. Active alerts.
3. Current soil moisture.
4. Temperature and humidity.
5. Irrigation recommendation.
6. Disease alerts.
7. Recent telemetry.
8. Field map.
9. Yield prediction summary.

### 8.3 Real-Time Telemetry

Use Recharts/Tremor for:

- Soil moisture trend
- Temperature trend
- Humidity trend
- pH trend
- NPK trend
- Irrigation events

Charts must gracefully handle missing data.

### 8.4 XAI Viewer

The XAI viewer should support:

```text
[Original Leaf] [Grad-CAM] [Overlay]
```

and provide:

```text
Detected Disease: Early Blight
Confidence: 91%

Affected Region:
Lower-right leaf region

Explanation:
The model primarily identified discoloration and lesion
patterns in the highlighted region.
```

---

## 9. IoT Telemetry & Ingestion Worker

### Protocol

MQTT over TLS:

```text
Port: 8883
```

Development mode may use:

```text
Port: 1883
```

### Topic Convention

```text
farms/{farm_id}/fields/{field_id}/devices/{device_id}/telemetry
```

Example:

```text
farms/farm-alpha/fields/field-01/devices/esp32-node-04/telemetry
```

### Telemetry Payload

```json
{
  "device_id": "esp32-node-04",
  "farm_id": "farm-alpha",
  "field_id": "field-01",
  "timestamp": "2026-10-04T01:30:00+05:30",
  "metrics": {
    "soil_moisture": 42.5,
    "temperature": 28.4,
    "humidity": 65.0,
    "ph_level": 6.8,
    "nitrogen": 42.0,
    "phosphorus": 28.0,
    "potassium": 36.0
  }
}
```

### Validation

Every telemetry message must validate:

- Device ID
- Farm ID
- Field ID
- Timestamp
- Numeric ranges
- Required metrics
- Payload version

Invalid packets must be logged and rejected without terminating the ingestion worker.

---

## 10. AI/ML & Computer Vision Microservice

### Framework

FastAPI + Python 3.11+ + Uvicorn.

### Disease Detection Pipeline

```text
Image
  ↓
Resize / Normalize
  ↓
Model Inference
  ↓
Disease Classification / Detection
  ↓
Confidence Filtering
  ↓
Grad-CAM / XAI
  ↓
Severity Estimation
  ↓
Structured Response
```

### Initial Model Strategy

The system should support interchangeable models.

Possible initial models:

- MobileNet-family classifier for lightweight classification.
- YOLO-family model for object/disease localization.
- ONNX Runtime for optimized inference.

The actual production model must be selected based on benchmark results on the target crop/disease dataset rather than assumed in advance.

### Diagnosis Response

```json
{
  "success": true,
  "data": {
    "crop": "tomato",
    "diagnosis": {
      "label": "early_blight",
      "confidence": 0.91,
      "severity": "moderate"
    },
    "top_predictions": [
      {
        "label": "early_blight",
        "probability": 0.91
      },
      {
        "label": "late_blight",
        "probability": 0.05
      },
      {
        "label": "healthy",
        "probability": 0.04
      }
    ],
    "xai": {
      "method": "grad_cam",
      "heatmap_url": "/media/xai/example.png"
    }
  }
}
```

---

## 11. AI Irrigation Decision Engine

The irrigation engine should combine:

- Soil moisture
- Crop type
- Growth stage
- Temperature
- Humidity
- Recent rainfall
- Forecast rainfall where available
- Field area
- Soil type
- Irrigation method

### Decision Pipeline

```text
Sensor Data
     +
Crop Configuration
     +
Weather Data
     ↓
Feature Validation
     ↓
Water Stress Estimation
     ↓
Irrigation Requirement
     ↓
Recommendation
     ↓
Explanation
```

### Example

```json
{
  "success": true,
  "data": {
    "field_id": "field-01",
    "water_stress": "high",
    "irrigation_required": true,
    "estimated_duration_minutes": 12,
    "confidence": 0.87,
    "reasons": [
      "Soil moisture is below configured threshold",
      "Temperature is elevated",
      "Rainfall probability is low"
    ]
  }
}
```

The first hackathon version should provide a **recommendation**. Automated relay activation should remain behind an explicit user confirmation.

---

## 12. Yield Prediction

### Inputs

```text
Crop Type
Field Area
Historical Yield
Soil Metrics
Weather Metrics
Irrigation History
Fertilization History
Growth Stage
```

### Output

```json
{
  "success": true,
  "data": {
    "crop": "tomato",
    "estimated_yield_t_per_hectare": 4.8,
    "prediction_interval": {
      "lower": 4.4,
      "upper": 5.2
    },
    "confidence": 0.82
  }
}
```

The UI must distinguish predictions from measured values.

---

## 13. Database & Time-Series Layer

### PostgreSQL

Recommended core entities:

```text
users
farms
fields
devices
sensors
sensor_readings
crops
crop_cycles
irrigation_events
disease_detections
xai_explanations
yield_predictions
recommendations
alerts
audit_logs
```

### TimescaleDB

Sensor readings should be stored as time-series data.

Example conceptual schema:

```text
sensor_readings
----------------
id
device_id
field_id
timestamp
soil_moisture
temperature
humidity
ph_level
nitrogen
phosphorus
potassium
```

### Retention

Initial demonstration configuration:

- Raw telemetry: 90 days.
- Hourly aggregates: long-term retention.
- Daily aggregates: long-term retention.

Retention must be configurable through environment/configuration settings.

---

## 14. Data Flow & Communication Protocols

### 14.1 Sensor Ingestion

```text
ESP32
  ↓ MQTT Publish
EMQX
  ↓
FastAPI Telemetry Worker
  ├──→ Validation
  ├──→ TimescaleDB
  └──→ Redis Pub/Sub
```

### 14.2 Real-Time UI

```text
Redis Pub/Sub
      ↓
WebSocket Server
      ↓
Browser
      ↓
useTelemetry()
      ↓
Dashboard Charts
```

### 14.3 Disease Diagnosis

```text
Browser
   ↓
Next.js API / Server Action
   ↓
FastAPI /api/v1/diagnose
   ↓
Pre-processing
   ↓
ONNX / PyTorch Model
   ↓
XAI Engine
   ↓
Diagnosis + Explanation
   ↓
Next.js
   ↓
XAI Viewer
```

### 14.4 Irrigation Recommendation

```text
Telemetry
   +
Crop Profile
   +
Weather
   ↓
Decision Engine
   ↓
Water Stress
   ↓
Irrigation Recommendation
   ↓
Farmer Confirmation
   ↓
Optional Relay Command
```

---

## 15. API Contract

All APIs must use versioned endpoints:

```text
/api/v1/
```

### Standard Success Response

```json
{
  "success": true,
  "data": {}
}
```

### Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid telemetry payload"
  }
}
```

### Initial Endpoints

```text
GET    /api/v1/health
GET    /api/v1/farms
GET    /api/v1/fields
GET    /api/v1/fields/{field_id}
GET    /api/v1/telemetry/{field_id}
POST   /api/v1/telemetry
POST   /api/v1/diagnose
POST   /api/v1/yield/predict
POST   /api/v1/irrigation/recommend
POST   /api/v1/irrigation/confirm
GET    /api/v1/alerts
GET    /api/v1/recommendations
```

---

## 16. Error Handling

All services must:

1. Validate input at boundaries.
2. Return structured errors.
3. Log internal technical details.
4. Avoid exposing secrets or stack traces to users.
5. Handle external service timeouts.
6. Retry transient MQTT/database/network failures where appropriate.
7. Use correlation/request IDs for debugging.

---

## 17. Security

### Requirements

- Never hard-code secrets.
- Validate environment variables at startup.
- Validate all request bodies.
- Sanitize file uploads.
- Restrict image file types.
- Apply file-size limits.
- Authenticate protected endpoints.
- Apply rate limiting to expensive AI endpoints.
- Use TLS for production MQTT.
- Use HTTPS in production.
- Do not expose database credentials to the frontend.

---

## 18. Environment Configuration

```ini
# Application
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agrismart

# Redis
REDIS_URL=redis://localhost:6379

# MQTT
MQTT_BROKER_URL=mqtt://localhost:1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_TOPIC_TELEMETRY=farms/+/fields/+/devices/+/telemetry

# AI Service
AI_SERVICE_URL=http://localhost:8000
AI_SERVICE_PORT=8000
MODEL_PATH=./app/models/crop_disease.onnx
ENABLE_XAI_HEATMAPS=true

# Demo Mode
DEMO_MODE=true
DEMO_TELEMETRY_INTERVAL_SECONDS=5
```

Production secrets must never be committed to Git.

---

## 19. Demo / Offline Mode

The project must support a deterministic demonstration mode.

### Demo Mode Requirements

When:

```text
DEMO_MODE=true
```

the application should be able to:

- Generate realistic sensor telemetry.
- Simulate multiple fields.
- Simulate sensor failures.
- Display disease-detection sample images.
- Generate irrigation recommendations.
- Demonstrate yield prediction.
- Run without physical ESP32 hardware.
- Run without external weather APIs.

This is critical for hackathon reliability.

---

## 20. AI Agent Execution Rules

When AI coding agents such as Antigravity, Cursor, Claude Code, Windsurf, or similar tools operate on this repository, they must follow these rules.

### Rule 1 — Inspect Before Modifying

Before creating or modifying files:

1. Inspect the repository.
2. Read relevant architecture documentation.
3. Identify existing implementations.
4. Avoid duplicate modules.
5. Preserve working functionality.

### Rule 2 — Strict Type Safety

- TypeScript must use explicit types.
- Shared API interfaces belong in `packages/types`.
- Do not use `any`.
- Avoid unsafe type assertions unless technically unavoidable and documented.

### Rule 3 — Directory Isolation

- Python AI/ML code belongs under `apps/ai-service`.
- Next.js UI code belongs under `apps/web`.
- Shared TypeScript types belong under `packages/types`.
- Database schema/migrations belong under `packages/database`.

### Rule 4 — Configuration

Frontend configuration must use validated environment variables.

Backend configuration must use Pydantic Settings.

Never hard-code credentials, API keys, database URLs, or production endpoints.

### Rule 5 — Component Modularity

Target UI components under 150 lines.

If a component becomes complex:

```text
Large Component
      ↓
Split by responsibility
      ↓
Container + Presentational Components
```

### Rule 6 — API Contracts

All API endpoints must:

- Have explicit request schemas.
- Have explicit response schemas.
- Use versioned paths.
- Return the standard response structure.
- Handle errors consistently.

### Rule 7 — AI Safety & Explainability

AI recommendations must:

- Expose confidence where meaningful.
- Explain important contributing factors.
- Distinguish predictions from observations.
- Never silently trigger irreversible actions.
- Require confirmation for automated irrigation actions during the initial release.

### Rule 8 — Testing

Every major service should have:

- Unit tests.
- Validation tests.
- API tests where appropriate.
- Error-path tests.

AI models should have documented evaluation metrics where training/evaluation data is available.

---

## 21. Development Phases

### Phase 0 — Repository Bootstrap

- Initialize monorepo.
- Configure Next.js.
- Configure FastAPI.
- Configure PostgreSQL.
- Configure Redis.
- Configure Docker Compose.
- Configure linting and formatting.
- Configure environment validation.

### Phase 1 — Database & Core Backend

- Create PostgreSQL schema.
- Create TimescaleDB tables/hypertables.
- Create farm/field/device models.
- Implement FastAPI health endpoint.
- Implement CRUD APIs.

### Phase 2 — IoT Telemetry

- Configure MQTT.
- Build telemetry worker.
- Validate telemetry payloads.
- Persist readings.
- Publish Redis events.
- Build WebSocket stream.

### Phase 3 — Dashboard

- Build dashboard shell.
- Add KPI cards.
- Add real-time charts.
- Add field selector.
- Add alerts.
- Add responsive/mobile layout.

### Phase 4 — AI Disease Detection

- Add image upload.
- Implement inference service.
- Implement diagnosis API.
- Add confidence scores.
- Add Grad-CAM/XAI.
- Build diagnosis UI.

### Phase 5 — Irrigation Intelligence

- Build crop configuration.
- Implement water-stress calculation.
- Add weather input.
- Build irrigation recommendation engine.
- Add explanation layer.
- Add confirmation workflow.

### Phase 6 — Yield Prediction

- Build feature pipeline.
- Add prediction model.
- Add prediction API.
- Display prediction range and confidence.

### Phase 7 — GIS

- Add farm boundaries.
- Add sensor locations.
- Add field-health layers.
- Add disease/irrigation overlays.

### Phase 8 — Hackathon Demo Hardening

- Add DEMO_MODE.
- Add deterministic seed data.
- Add sample disease images.
- Add error states.
- Add loading states.
- Add offline fallback.
- Test the entire demo from a clean machine.

---

## 22. Hackathon MVP Scope

The first working release should prioritize these five demonstrations:

### 1. Smart Field Monitoring

```text
Live Sensor → API → Database → WebSocket → Dashboard
```

### 2. AI Disease Detection

```text
Leaf Image → AI → Disease + Confidence + XAI
```

### 3. Smart Irrigation

```text
Sensor Data → Water Stress → Recommendation → Explanation
```

### 4. Yield Prediction

```text
Historical + Environmental Data → ML → Yield Estimate
```

### 5. Farm Map

```text
GIS → Fields → Sensors → Health / Alerts
```

The team should not delay the MVP for advanced features such as full autonomous irrigation, multi-region deployment, complex RAG pipelines, or large-scale Kubernetes infrastructure.

---

## 23. Non-Functional Requirements

### Performance

Target:

- Dashboard initial load: < 3 seconds in normal local/demo conditions.
- Telemetry UI update: near real-time.
- Standard API response: < 500 ms where practical.
- AI inference: optimized according to selected model/hardware.

These are engineering targets, not guarantees.

### Reliability

- Sensor failures should not crash the platform.
- AI service failures should show a user-friendly error.
- Missing weather data should not break telemetry.
- MQTT disconnects should reconnect automatically.
- Demo mode must remain functional without hardware.

### Maintainability

- Modular services.
- Explicit schemas.
- Clear logging.
- Centralized configuration.
- Automated formatting/linting.
- Tests for critical paths.

---

## 24. Observability

Log at minimum:

```text
timestamp
request_id
service
endpoint
event_type
device_id
field_id
status
latency_ms
error_code
```

Important events:

- Telemetry received.
- Telemetry rejected.
- Device disconnected.
- AI inference completed.
- AI inference failed.
- Recommendation generated.
- Irrigation confirmation received.
- Database error.
- MQTT reconnect.

---

## 25. Future Extensions

The architecture should allow future integration of:

- Weather APIs.
- Satellite imagery.
- Drone imagery.
- Soil nutrient prediction.
- RAG-based agricultural knowledge assistant.
- Voice-based farmer assistant.
- Regional-language support.
- SMS/WhatsApp notifications.
- Edge inference on Raspberry Pi.
- Automated irrigation.
- Carbon/water-use tracking.
- Multi-farm analytics.
- Government/agricultural datasets.

These should remain future extensions and must not unnecessarily complicate the initial hackathon MVP.

---

## 26. Definition of Done

A feature is considered complete only when:

- The implementation matches the architecture.
- Input/output contracts are defined.
- Error handling exists.
- Loading/empty/error UI states exist where applicable.
- Tests exist for critical logic.
- Environment configuration is documented.
- No secrets are committed.
- Demo mode works.
- Existing functionality is not broken.
- The feature is manually verified end-to-end.

---

## 27. Final System Philosophy

AgriSmart follows the principle:

```text
SENSE
  ↓
UNDERSTAND
  ↓
EXPLAIN
  ↓
RECOMMEND
  ↓
CONFIRM
  ↓
ACT
  ↓
LEARN
```

The platform should not simply collect agricultural data.

It should transform:

```text
Raw Field Data
      ↓
Information
      ↓
AI Insight
      ↓
Explainable Recommendation
      ↓
Farmer Decision
      ↓
Measurable Agricultural Outcome
```

The primary objective is to build a technically credible, demonstrable, explainable, and farmer-centric Precision Agriculture platform suitable for academic demonstration, hackathon evaluation, and future real-world extension.
