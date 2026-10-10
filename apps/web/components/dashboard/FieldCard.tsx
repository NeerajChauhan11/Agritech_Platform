"use client";

import { motion } from "framer-motion";
import { Clock } from "lucide-react";
import Link from "next/link";
import { getHealthColor } from "@/lib/utils";
import { ProgressBar, StatusBadge } from "@/components/ui/Cards";
import type { Field } from "@/lib/types";

const FIELD_METRICS = (field: Field) => [
  { label: "Moisture", value: `${field.latest_reading.soil_moisture.toFixed(1)}%`, icon: "💧" },
  { label: "Temp", value: `${field.latest_reading.temperature.toFixed(1)}°C`, icon: "🌡️" },
  { label: "Humidity", value: `${field.latest_reading.humidity.toFixed(0)}%`, icon: "💨" },
  { label: "pH", value: field.latest_reading.ph_level.toFixed(1), icon: "⚗️" },
];

interface FieldCardProps {
  field: Field;
  index: number;
}

export function FieldCard({ field, index }: FieldCardProps) {
  const healthColor = getHealthColor(field.health_score);

  return (
    <Link href={`/telemetry?field=${field.id}`} style={{ textDecoration: "none" }}>
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.07 }}
        className="glass glass-hover"
        style={{ borderRadius: "14px", padding: "18px", cursor: "pointer" }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "14px" }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: "0.875rem", color: "var(--text-primary)" }}>{field.name}</div>
            <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "2px" }}>
              {field.crop} · {field.growth_stage} · {field.area_hectares} ha
            </div>
          </div>
          <StatusBadge status={field.status} />
        </div>

        {/* Metrics grid */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "14px" }}>
          {FIELD_METRICS(field).map(({ label, value, icon }) => (
            <div key={label} className="mini-stat">
              <div style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>{icon} {label}</div>
              <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)", marginTop: "2px" }}>{value}</div>
            </div>
          ))}
        </div>

        {/* Health bar */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
            <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Field Health</span>
            <span style={{ fontSize: "0.7rem", fontWeight: 700, color: healthColor }}>{field.health_score}/100</span>
          </div>
          <ProgressBar value={field.health_score} color={healthColor} showValue={false} />
        </div>

        {/* Devices */}
        <div style={{ marginTop: "10px", display: "flex", gap: "6px", flexWrap: "wrap" }}>
          {field.devices.map((d) => (
            <div key={d.id} style={{ display: "flex", alignItems: "center", gap: "4px" }}>
              <span className={`status-dot ${d.status === "online" ? "online" : d.status === "warning" ? "warning" : "offline"}`} />
              <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>{d.name}</span>
            </div>
          ))}
          <div style={{ display: "flex", alignItems: "center", gap: "4px", marginLeft: "auto" }}>
            <Clock size={10} color="var(--text-muted)" />
            <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>{field.devices[0]?.last_seen}</span>
          </div>
        </div>
      </motion.div>
    </Link>
  );
}
