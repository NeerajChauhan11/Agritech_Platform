"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  AreaChart, Area, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { Activity, Wifi, WifiOff, Battery, Signal, RefreshCw } from "lucide-react";
import { Card, SectionHeader, StatusBadge, ProgressBar } from "@/components/ui/Cards";
import { DEMO_FARM, DEMO_TELEMETRY } from "@/lib/demo-data";
import { addJitter } from "@/lib/utils";
import type { Field, TelemetryPoint } from "@/lib/types";

export default function TelemetryPage() {
  const [selectedFieldId, setSelectedFieldId] = useState("field-01");
  const [telemetryData, setTelemetryData] = useState<Record<string, TelemetryPoint[]>>(DEMO_TELEMETRY);

  const selectedField = DEMO_FARM.fields.find((f) => f.id === selectedFieldId) as Field;

  const tick = useCallback(() => {
    setTelemetryData((prev) => {
      const updated = { ...prev };
      DEMO_FARM.fields.forEach((field) => {
        const base = field.latest_reading;
        const newPoint: TelemetryPoint = {
          time: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
          moisture: Math.round(addJitter(base.soil_moisture, 2) * 10) / 10,
          temperature: Math.round(addJitter(base.temperature, 1) * 10) / 10,
          humidity: Math.round(addJitter(base.humidity, 3) * 10) / 10,
          ph: Math.round(addJitter(base.ph_level, 0.1) * 100) / 100,
        };
        updated[field.id] = [...(prev[field.id] || []).slice(-23), newPoint];
      });
      return updated;
    });
  }, []);

  useEffect(() => {
    const interval = setInterval(tick, 5000);
    return () => clearInterval(interval);
  }, [tick]);

  const currentData = telemetryData[selectedFieldId] || [];
  const latest = currentData[currentData.length - 1];

  return (
    <div className="page-stack" style={{ maxWidth: "1400px" }}>
      <motion.div className="page-header" initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1>Field Monitor</h1>
        <p>Real-time IoT sensor telemetry — updating every 5 seconds</p>
      </motion.div>

      {/* Field selector */}
      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        {DEMO_FARM.fields.map((field, i) => (
          <motion.button
            key={field.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
            onClick={() => setSelectedFieldId(field.id)}
            className={`tab-btn${selectedFieldId === field.id ? " active" : ""}`}
            style={{ display: "flex", alignItems: "center", gap: "8px" }}
          >
            <span className={`status-dot ${field.status === "healthy" ? "online" : field.status === "warning" ? "warning" : "offline"}`} />
            {field.name}
          </motion.button>
        ))}
      </div>

      {/* Field info strip */}
      <Card delay={0.1}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "24px", alignItems: "center" }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: "1rem", color: "var(--text-primary)" }}>{selectedField.name}</div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
              {selectedField.crop} · {selectedField.growth_stage} · {selectedField.area_hectares} ha
            </div>
          </div>
          <StatusBadge status={selectedField.status} />
          <div style={{ marginLeft: "auto", display: "flex", gap: "16px" }}>
            {selectedField.devices.map((device) => (
              <div key={device.id} style={{ display: "flex", flexDirection: "column", gap: "3px", alignItems: "center" }}>
                {device.status === "online" ? <Wifi size={14} color="var(--status-healthy)" /> : <WifiOff size={14} color="var(--status-danger)" />}
                <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>{device.name}</span>
                <div style={{ display: "flex", gap: "4px" }}>
                  <Battery size={10} color={device.battery > 30 ? "var(--text-muted)" : "var(--status-danger)"} />
                  <span style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>{device.battery}%</span>
                  <Signal size={10} color="var(--text-muted)" />
                  <span style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>{device.signal}%</span>
                </div>
              </div>
            ))}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "5px", color: "var(--text-muted)", fontSize: "0.72rem" }}>
            <RefreshCw size={11} />
            <span className="status-dot online pulse-live" />
            Live
          </div>
        </div>
      </Card>

      {/* Live readings grid */}
      {latest && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "12px" }}>
          {[
            { label: "Soil Moisture", value: latest.moisture, unit: "%", color: "#22c55e", threshold: [40, 25] },
            { label: "Temperature", value: latest.temperature, unit: "°C", color: "#f59e0b", threshold: [30, 35] },
            { label: "Humidity", value: latest.humidity, unit: "%", color: "#3b82f6", threshold: [80, 30] },
            { label: "pH Level", value: latest.ph, unit: "", color: "#a78bfa", threshold: [7.5, 6.0] },
          ].map(({ label, value, unit, color }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
              className="glass"
              style={{ borderRadius: "12px", padding: "16px", textAlign: "center", border: `1px solid ${color}20` }}
            >
              <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginBottom: "8px" }}>{label}</div>
              <div style={{ fontSize: "1.8rem", fontWeight: 800, color, lineHeight: 1 }}>
                {value.toFixed(label === "pH Level" ? 2 : 1)}
              </div>
              <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "2px" }}>{unit}</div>
              <div style={{ marginTop: "10px" }}>
                <ProgressBar value={value} max={label === "pH Level" ? 14 : 100} color={color} showValue={false} />
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Charts */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
        <Card delay={0.2}>
          <SectionHeader title="Moisture & Temperature" subtitle="24-hour trend" />
          <div style={{ height: "200px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={currentData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="m2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="t2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(34,197,94,0.05)" />
                <XAxis dataKey="time" tick={{ fontSize: 9, fill: "var(--text-muted)" }} tickLine={false} axisLine={false} interval={5} />
                <YAxis tick={{ fontSize: 9, fill: "var(--text-muted)" }} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "var(--bg-elevated)", border: "1px solid var(--bg-border)", borderRadius: "8px", fontSize: "11px" }} />
                <Area type="monotone" dataKey="moisture" stroke="#22c55e" strokeWidth={2} fill="url(#m2)" name="Moisture %" dot={false} />
                <Area type="monotone" dataKey="temperature" stroke="#f59e0b" strokeWidth={2} fill="url(#t2)" name="Temp °C" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card delay={0.25}>
          <SectionHeader title="Humidity & pH" subtitle="24-hour trend" />
          <div style={{ height: "200px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={currentData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(34,197,94,0.05)" />
                <XAxis dataKey="time" tick={{ fontSize: 9, fill: "var(--text-muted)" }} tickLine={false} axisLine={false} interval={5} />
                <YAxis tick={{ fontSize: 9, fill: "var(--text-muted)" }} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "var(--bg-elevated)", border: "1px solid var(--bg-border)", borderRadius: "8px", fontSize: "11px" }} />
                <Line type="monotone" dataKey="humidity" stroke="#3b82f6" strokeWidth={2} name="Humidity %" dot={false} />
                <Line type="monotone" dataKey="ph" stroke="#a78bfa" strokeWidth={2} name="pH" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* NPK Table */}
      <Card delay={0.3}>
        <SectionHeader title="Soil Nutrient Profile" subtitle={`${selectedField.name} — latest reading`} />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px" }}>
          {[
            { label: "Nitrogen (N)", value: selectedField.latest_reading.nitrogen, unit: "mg/kg", optimal: [40, 60], color: "#fb923c" },
            { label: "Phosphorus (P)", value: selectedField.latest_reading.phosphorus, unit: "mg/kg", optimal: [25, 45], color: "#f43f5e" },
            { label: "Potassium (K)", value: selectedField.latest_reading.potassium, unit: "mg/kg", optimal: [30, 50], color: "#a78bfa" },
          ].map(({ label, value, unit, optimal, color }) => {
            const [lo, hi] = optimal;
            const inRange = value >= lo && value <= hi;
            return (
              <div key={label} style={{
                padding: "16px", borderRadius: "10px",
                background: "var(--bg-elevated)", border: `1px solid ${color}20`,
              }}>
                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginBottom: "8px" }}>{label}</div>
                <div style={{ fontSize: "1.6rem", fontWeight: 700, color, marginBottom: "4px" }}>
                  {value.toFixed(0)}
                </div>
                <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", marginBottom: "10px" }}>{unit}</div>
                <ProgressBar value={value} max={80} color={color} showValue={false} />
                <div style={{ marginTop: "6px", fontSize: "0.65rem", color: inRange ? "var(--status-healthy)" : "var(--status-warning)" }}>
                  {inRange ? "✓ Within optimal range" : `⚠ Optimal: ${lo}–${hi} mg/kg`}
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
