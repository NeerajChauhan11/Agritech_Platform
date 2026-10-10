"use client";

import { motion } from "framer-motion";
import { getHealthColor, getHealthLabel } from "@/lib/utils";
import { ProgressBar, StatusBadge } from "@/components/ui/Cards";
import type { Farm, Alert } from "@/lib/types";

interface FarmHealthHeroProps {
  farm: Farm;
  activeAlerts: Alert[];
}

export function FarmHealthHero({ farm, activeAlerts }: FarmHealthHeroProps) {
  const healthColor = getHealthColor(farm.overall_health);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="glass"
      style={{
        borderRadius: "18px",
        padding: "24px",
        background: "linear-gradient(135deg, rgba(20,31,24,0.9) 0%, rgba(10,15,13,0.9) 100%)",
        border: `1px solid ${healthColor}22`,
        boxShadow: `0 0 40px ${healthColor}0a`,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "32px", flexWrap: "wrap" }}>
        {/* Health score circle */}
        <div style={{ textAlign: "center" }}>
          <div style={{
            width: "100px", height: "100px", borderRadius: "50%",
            border: `3px solid ${healthColor}`,
            display: "flex", flexDirection: "column",
            alignItems: "center", justifyContent: "center",
            background: `${healthColor}12`,
            boxShadow: `0 0 30px ${healthColor}20`,
          }}>
            <span style={{ fontSize: "2rem", fontWeight: 800, color: healthColor, lineHeight: 1 }}>
              {farm.overall_health}
            </span>
            <span style={{ fontSize: "0.6rem", color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase" }}>
              Health
            </span>
          </div>
        </div>

        {/* Field health breakdown */}
        <div style={{ flex: 1, minWidth: "280px" }}>
          <div className="section-label" style={{ marginBottom: "8px" }}>Field Health Overview</div>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {farm.fields.map((field) => (
              <div key={field.id} style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ width: "120px", fontSize: "0.75rem", color: "var(--text-secondary)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {field.name}
                </span>
                <div style={{ flex: 1 }}>
                  <ProgressBar value={field.health_score} color={getHealthColor(field.health_score)} showValue={false} />
                </div>
                <span style={{ fontSize: "0.72rem", color: getHealthColor(field.health_score), fontWeight: 600, width: "28px", textAlign: "right" }}>
                  {field.health_score}
                </span>
                <StatusBadge status={field.status} label={getHealthLabel(field.health_score)} />
              </div>
            ))}
          </div>
        </div>

        {/* Quick stats */}
        <div style={{ display: "flex", flexDirection: "column", gap: "8px", minWidth: "140px" }}>
          {[
            { label: "Online Sensors", value: "5/6", color: "var(--status-healthy)" },
            { label: "Active Alerts", value: activeAlerts.length.toString(), color: activeAlerts.length > 2 ? "var(--status-danger)" : "var(--status-warning)" },
            { label: "Crops Monitored", value: "4", color: "var(--status-info)" },
          ].map(({ label, value, color }) => (
            <div key={label} className="info-row">
              <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{label}</span>
              <span style={{ fontSize: "0.9rem", fontWeight: 700, color }}>{value}</span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
