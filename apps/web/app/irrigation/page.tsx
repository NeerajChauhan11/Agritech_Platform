"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Droplets, CheckCircle, AlertTriangle, XCircle, ChevronRight, Play, Clock } from "lucide-react";
import { Card, SectionHeader, StatusBadge, ProgressBar } from "@/components/ui/Cards";
import { DEMO_IRRIGATION } from "@/lib/demo-data";
import type { IrrigationRecommendation } from "@/lib/types";

const STRESS_COLOR: Record<string, string> = {
  low: "var(--status-healthy)",
  medium: "var(--status-warning)",
  high: "#f59e0b",
  critical: "var(--status-danger)",
};

const STRESS_BADGE: Record<string, string> = {
  low: "badge-green",
  medium: "badge-yellow",
  high: "badge-yellow",
  critical: "badge-red",
};

export default function IrrigationPage() {
  const [selected, setSelected] = useState<IrrigationRecommendation>(DEMO_IRRIGATION[0]);
  const [confirmed, setConfirmed] = useState<Set<string>>(new Set());

  const handleConfirm = (fieldId: string) => {
    setConfirmed((prev) => new Set([...prev, fieldId]));
  };

  return (
    <div className="page-stack" style={{ maxWidth: "1200px" }}>
      <motion.div className="page-header" initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1>AI Irrigation Advisor</h1>
        <p>Explainable water stress analysis and irrigation recommendations</p>
      </motion.div>

      <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: "20px", alignItems: "start" }}>

        {/* Field list */}
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <div className="section-label" style={{ padding: "0 4px" }}>Fields</div>
          {DEMO_IRRIGATION.map((rec, i) => (
            <motion.div
              key={rec.field_id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.07 }}
              onClick={() => setSelected(rec)}
              className="glass glass-hover"
              style={{
                padding: "14px", borderRadius: "12px", cursor: "pointer",
                border: `1px solid ${selected.field_id === rec.field_id ? STRESS_COLOR[rec.water_stress] + "40" : "var(--bg-border)"}`,
                background: selected.field_id === rec.field_id ? `${STRESS_COLOR[rec.water_stress]}0a` : undefined,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "6px" }}>
                <div style={{ fontWeight: 600, fontSize: "0.8rem", color: "var(--text-primary)" }}>{rec.field_name}</div>
                <span className={`badge ${STRESS_BADGE[rec.water_stress]}`}>{rec.water_stress.toUpperCase()}</span>
              </div>
              <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginBottom: "8px" }}>{rec.crop}</div>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <Droplets size={11} color={STRESS_COLOR[rec.water_stress]} />
                <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                  {rec.irrigation_required ? `${rec.estimated_duration_minutes} min needed` : "No irrigation needed"}
                </span>
                {confirmed.has(rec.field_id) && <CheckCircle size={11} color="var(--status-healthy)" style={{ marginLeft: "auto" }} />}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Detail panel */}
        <AnimatePresence mode="wait">
          <motion.div
            key={selected.field_id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            style={{ display: "flex", flexDirection: "column", gap: "16px" }}
          >

            {/* Stress Overview */}
            <Card>
              <div style={{ display: "flex", alignItems: "center", gap: "20px", flexWrap: "wrap" }}>
                {/* Stress Indicator */}
                <div style={{
                  width: "90px", height: "90px", borderRadius: "50%",
                  border: `3px solid ${STRESS_COLOR[selected.water_stress]}`,
                  display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                  background: `${STRESS_COLOR[selected.water_stress]}10`,
                  boxShadow: `0 0 24px ${STRESS_COLOR[selected.water_stress]}20`,
                }}>
                  <Droplets size={20} color={STRESS_COLOR[selected.water_stress]} />
                  <span style={{ fontSize: "0.55rem", fontWeight: 700, color: STRESS_COLOR[selected.water_stress], marginTop: "4px", textTransform: "uppercase" }}>
                    {selected.water_stress}
                  </span>
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: "1.1rem", color: "var(--text-primary)", marginBottom: "4px" }}>
                    {selected.field_name}
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "12px" }}>
                    {selected.crop} · Water Stress: <span style={{ color: STRESS_COLOR[selected.water_stress], fontWeight: 700 }}>
                      {selected.water_stress.toUpperCase()}
                    </span>
                  </div>

                  {/* Sensor snapshot */}
                  <div style={{ display: "flex", gap: "10px" }}>
                    {[
                      { label: "Soil Moisture", value: `${selected.sensor_snapshot.soil_moisture}%` },
                      { label: "Temperature",  value: `${selected.sensor_snapshot.temperature}°C`  },
                      { label: "Humidity",     value: `${selected.sensor_snapshot.humidity}%`       },
                    ].map(({ label, value }) => (
                      <div key={label} className="mini-stat">
                        <div style={{ fontSize: "0.62rem", color: "var(--text-muted)" }}>{label}</div>
                        <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--text-primary)" }}>{value}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Confidence */}
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "0.6rem", color: "var(--text-muted)", marginBottom: "4px" }}>AI CONFIDENCE</div>
                  <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--brand-green-light)" }}>
                    {(selected.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            </Card>

            {/* Recommendation */}
            {selected.irrigation_required ? (
              <Card>
                <div style={{
                  padding: "16px", borderRadius: "12px",
                  background: `${STRESS_COLOR[selected.water_stress]}08`,
                  border: `1px solid ${STRESS_COLOR[selected.water_stress]}25`,
                  marginBottom: "16px",
                  display: "flex", alignItems: "center", gap: "16px",
                }}>
                  {selected.water_stress === "critical" ? <XCircle size={24} color="var(--status-danger)" /> :
                   <AlertTriangle size={24} color="var(--status-warning)" />}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
                      Irrigation Required
                    </div>
                    <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                      Estimated duration: <strong style={{ color: STRESS_COLOR[selected.water_stress] }}>
                        {selected.estimated_duration_minutes} minutes
                      </strong>
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "5px", color: "var(--text-muted)", fontSize: "0.72rem" }}>
                    <Clock size={12} />
                    {selected.estimated_duration_minutes} min
                  </div>
                </div>

                {/* Reasons */}
                <div style={{ marginBottom: "16px" }}>
                  <div className="section-label" style={{ marginBottom: "10px" }}>Why does the AI recommend this?</div>
                  {selected.reasons.map((reason, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.08 }}
                      style={{ display: "flex", gap: "8px", alignItems: "flex-start", marginBottom: "8px" }}
                    >
                      <ChevronRight size={14} color="var(--brand-green)" style={{ marginTop: "2px", flexShrink: 0 }} />
                      <span style={{ fontSize: "0.78rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>{reason}</span>
                    </motion.div>
                  ))}
                </div>

                {/* Confirmation buttons */}
                {!confirmed.has(selected.field_id) ? (
                  <div style={{ display: "flex", gap: "10px" }}>
                    <button
                      onClick={() => handleConfirm(selected.field_id)}
                      style={{
                        flex: 1, padding: "12px", borderRadius: "10px",
                        background: "linear-gradient(135deg, #22c55e, #10b981)",
                        border: "none", color: "#fff", fontWeight: 700,
                        fontSize: "0.85rem", cursor: "pointer",
                        display: "flex", alignItems: "center", justifyContent: "center", gap: "8px",
                      }}
                    >
                      <Play size={15} /> Confirm & Start Irrigation
                    </button>
                    <button style={{
                      padding: "12px 20px", borderRadius: "10px",
                      background: "var(--bg-elevated)", border: "1px solid var(--bg-border)",
                      color: "var(--text-secondary)", fontWeight: 600, fontSize: "0.82rem", cursor: "pointer",
                    }}>
                      Skip
                    </button>
                  </div>
                ) : (
                  <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                    style={{ padding: "14px", borderRadius: "10px",
                      background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.2)",
                      display: "flex", alignItems: "center", gap: "10px" }}>
                    <CheckCircle size={18} color="var(--status-healthy)" />
                    <div>
                      <div style={{ fontWeight: 700, color: "var(--status-healthy)", fontSize: "0.85rem" }}>
                        Irrigation Confirmed
                      </div>
                      <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                        {selected.estimated_duration_minutes}-minute cycle initiated for {selected.field_name}
                      </div>
                    </div>
                  </motion.div>
                )}
              </Card>
            ) : (
              <Card>
                <div style={{ display: "flex", alignItems: "center", gap: "14px", padding: "10px" }}>
                  <CheckCircle size={28} color="var(--status-healthy)" />
                  <div>
                    <div style={{ fontWeight: 700, color: "var(--status-healthy)", fontSize: "1rem" }}>No Irrigation Needed</div>
                    <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "4px" }}>
                      Current soil moisture levels are adequate for {selected.crop}.
                    </div>
                  </div>
                </div>
                <div style={{ marginTop: "14px" }}>
                  {selected.reasons.map((reason, i) => (
                    <div key={i} style={{ display: "flex", gap: "8px", alignItems: "flex-start", marginBottom: "8px" }}>
                      <CheckCircle size={13} color="var(--status-healthy)" style={{ marginTop: "2px", flexShrink: 0 }} />
                      <span style={{ fontSize: "0.78rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>{reason}</span>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
