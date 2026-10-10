"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import { motion } from "framer-motion";
import { MapPin, Wifi, WifiOff, Droplets } from "lucide-react";
import { Card, SectionHeader, StatusBadge } from "@/components/ui/Cards";
import { DEMO_FARM } from "@/lib/demo-data";
import { getHealthColor } from "@/lib/utils";

// Leaflet must be client-only
const FarmMapLeaflet = dynamic(() => import("@/components/map/FarmMapLeaflet"), {
  ssr: false,
  loading: () => (
    <div style={{ height: "480px", borderRadius: "14px", background: "var(--bg-elevated)",
      display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", fontSize: "0.85rem" }}>
      Loading map…
    </div>
  ),
});

export default function MapPage() {
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);
  const selectedField = DEMO_FARM.fields.find((f) => f.id === selectedFieldId);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px", maxWidth: "1400px" }}>
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-primary)" }}>Farm Map</h1>
        <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginTop: "4px" }}>
          {DEMO_FARM.name} · {DEMO_FARM.location} · Interactive GIS field view
        </p>
      </motion.div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: "20px", alignItems: "start" }}>
        {/* Map */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
          <FarmMapLeaflet
            fields={DEMO_FARM.fields}
            selectedFieldId={selectedFieldId}
            onFieldSelect={setSelectedFieldId}
          />
        </motion.div>

        {/* Sidebar */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <Card delay={0.15}>
            <SectionHeader title="Fields" subtitle="Click a field to select" />
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {DEMO_FARM.fields.map((field, i) => (
                <motion.div
                  key={field.id}
                  initial={{ opacity: 0, x: 8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06 }}
                  onClick={() => setSelectedFieldId(field.id === selectedFieldId ? null : field.id)}
                  style={{
                    padding: "10px 12px", borderRadius: "10px", cursor: "pointer",
                    background: selectedFieldId === field.id ? "rgba(34,197,94,0.08)" : "var(--bg-elevated)",
                    border: `1px solid ${selectedFieldId === field.id ? "rgba(34,197,94,0.25)" : "var(--bg-border)"}`,
                    transition: "all 0.15s",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "4px" }}>
                    <span style={{ fontWeight: 600, fontSize: "0.78rem", color: "var(--text-primary)" }}>{field.name}</span>
                    <StatusBadge status={field.status} />
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginBottom: "5px" }}>
                    {field.crop} · {field.area_hectares} ha
                  </div>
                  <div style={{ display: "flex", gap: "8px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
                      <Droplets size={10} color="var(--text-muted)" />
                      <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>
                        {field.latest_reading.soil_moisture.toFixed(0)}%
                      </span>
                    </div>
                    {field.devices.map((d) => (
                      <div key={d.id} style={{ display: "flex", alignItems: "center", gap: "3px" }}>
                        {d.status === "online"
                          ? <Wifi size={10} color="var(--status-healthy)" />
                          : <WifiOff size={10} color="var(--status-danger)" />
                        }
                        <span style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>{d.name}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </Card>

          {/* Selected field detail */}
          {selectedField && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
              <Card>
                <div style={{ marginBottom: "10px" }}>
                  <div style={{ fontWeight: 700, fontSize: "0.9rem", color: "var(--text-primary)" }}>
                    {selectedField.name}
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                    {selectedField.crop} · {selectedField.growth_stage}
                  </div>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px" }}>
                  {[
                    { label: "Moisture", value: `${selectedField.latest_reading.soil_moisture.toFixed(1)}%` },
                    { label: "Temp", value: `${selectedField.latest_reading.temperature.toFixed(1)}°C` },
                    { label: "Humidity", value: `${selectedField.latest_reading.humidity.toFixed(0)}%` },
                    { label: "pH", value: selectedField.latest_reading.ph_level.toFixed(1) },
                    { label: "Health", value: `${selectedField.health_score}/100` },
                    { label: "Area", value: `${selectedField.area_hectares} ha` },
                  ].map(({ label, value }) => (
                    <div key={label} style={{ padding: "7px 9px", borderRadius: "7px",
                      background: "var(--bg-elevated)", border: "1px solid var(--bg-border)" }}>
                      <div style={{ fontSize: "0.58rem", color: "var(--text-muted)" }}>{label}</div>
                      <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--text-primary)" }}>{value}</div>
                    </div>
                  ))}
                </div>
              </Card>
            </motion.div>
          )}

          {/* Legend */}
          <Card delay={0.2}>
            <div className="section-label" style={{ marginBottom: "10px" }}>Map Legend</div>
            {[
              { color: "var(--status-healthy)", label: "Healthy field (>80)" },
              { color: "var(--status-warning)", label: "Fair field (60–80)" },
              { color: "var(--status-danger)", label: "Critical field (<60)" },
              { color: "#22c55e", label: "Active sensor node" },
              { color: "var(--status-danger)", label: "Offline sensor" },
            ].map(({ color, label }) => (
              <div key={label} style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                <div style={{ width: "10px", height: "10px", borderRadius: "50%", background: color, flexShrink: 0 }} />
                <span style={{ fontSize: "0.72rem", color: "var(--text-secondary)" }}>{label}</span>
              </div>
            ))}
          </Card>
        </div>
      </div>
    </div>
  );
}
