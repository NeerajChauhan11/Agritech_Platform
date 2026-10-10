"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, AlertTriangle, XCircle, Info, CheckCircle, Filter, Eye } from "lucide-react";
import { Card, SectionHeader } from "@/components/ui/Cards";
import { DEMO_ALERTS } from "@/lib/demo-data";
import type { Alert, AlertSeverity, AlertCategory } from "@/lib/types";

const SEVERITY_ICON: Record<AlertSeverity, React.ReactNode> = {
  critical: <XCircle size={16} color="var(--status-danger)" />,
  warning: <AlertTriangle size={16} color="var(--status-warning)" />,
  info: <Info size={16} color="var(--status-info)" />,
};

const SEVERITY_BORDER: Record<AlertSeverity, string> = {
  critical: "rgba(239,68,68,0.2)",
  warning: "rgba(245,158,11,0.2)",
  info: "rgba(59,130,246,0.15)",
};

const CATEGORY_LABEL: Record<AlertCategory, string> = {
  disease: "Disease",
  irrigation: "Irrigation",
  sensor: "Sensor",
  weather: "Weather",
  yield: "Yield",
};

const CATEGORY_COLORS: Record<AlertCategory, string> = {
  disease: "#f43f5e",
  irrigation: "#3b82f6",
  sensor: "#f59e0b",
  weather: "#a78bfa",
  yield: "#22c55e",
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>(DEMO_ALERTS);
  const [filter, setFilter] = useState<AlertSeverity | "all">("all");
  const [categoryFilter, setCategoryFilter] = useState<AlertCategory | "all">("all");

  const filtered = alerts.filter((a) => {
    if (filter !== "all" && a.severity !== filter) return false;
    if (categoryFilter !== "all" && a.category !== categoryFilter) return false;
    return true;
  });

  const acknowledge = (id: string) => {
    setAlerts((prev) => prev.map((a) => a.id === id ? { ...a, acknowledged: true } : a));
  };

  const acknowledgeAll = () => {
    setAlerts((prev) => prev.map((a) => ({ ...a, acknowledged: true })));
  };

  const unread = alerts.filter((a) => !a.acknowledged).length;
  const criticalCount = alerts.filter((a) => a.severity === "critical" && !a.acknowledged).length;
  const warningCount = alerts.filter((a) => a.severity === "warning" && !a.acknowledged).length;

  return (
    <div className="page-stack" style={{ maxWidth: "1000px" }}>
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
        className="info-row" style={{ alignItems: "flex-start" }}>
        <div className="page-header">
          <h1>Alerts &amp; Notifications</h1>
          <p>{unread} unacknowledged · {criticalCount} critical · {warningCount} warnings</p>
        </div>
        {unread > 0 && (
          <button onClick={acknowledgeAll} className="tab-btn active" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <CheckCircle size={13} /> Acknowledge All
          </button>
        )}
      </motion.div>

      {/* Summary cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px" }}>
        {[
          { label: "Critical", count: criticalCount, total: alerts.filter(a => a.severity === "critical").length, color: "var(--status-danger)" },
          { label: "Warnings", count: warningCount, total: alerts.filter(a => a.severity === "warning").length, color: "var(--status-warning)" },
          { label: "Info", count: alerts.filter(a => a.severity === "info" && !a.acknowledged).length, total: alerts.filter(a => a.severity === "info").length, color: "var(--status-info)" },
        ].map(({ label, count, total, color }, i) => (
          <motion.div key={label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
            className="glass" style={{ borderRadius: "12px", padding: "16px", border: `1px solid ${color}20` }}>
            <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginBottom: "6px" }}>{label}</div>
            <div style={{ fontSize: "1.8rem", fontWeight: 800, color }}>{count}</div>
            <div style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>unread of {total}</div>
          </motion.div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", alignItems: "center" }}>
        <Filter size={13} color="var(--text-muted)" />
        {(["all", "critical", "warning", "info"] as const).map((s) => (
          <button key={s} onClick={() => setFilter(s)} className={`filter-btn${filter === s ? " active" : ""}`}>
            {s}
          </button>
        ))}
        <div style={{ width: "1px", height: "16px", background: "var(--bg-border)" }} />
        {(["all", "disease", "irrigation", "sensor", "weather"] as const).map((c) => (
          <button key={c} onClick={() => setCategoryFilter(c)} className={`filter-btn${categoryFilter === c ? " active" : ""}`}>
            {c}
          </button>
        ))}
      </div>

      {/* Alert list */}
      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        <AnimatePresence>
          {filtered.map((alert, i) => (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ delay: i * 0.05 }}
              className="glass"
              style={{
                borderRadius: "12px", padding: "16px",
                border: `1px solid ${SEVERITY_BORDER[alert.severity]}`,
                opacity: alert.acknowledged ? 0.5 : 1,
                transition: "opacity 0.2s",
              }}
            >
              <div style={{ display: "flex", gap: "12px", alignItems: "flex-start" }}>
                <div style={{ marginTop: "2px" }}>{SEVERITY_ICON[alert.severity]}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px", flexWrap: "wrap" }}>
                    <span style={{ fontWeight: 700, fontSize: "0.875rem", color: "var(--text-primary)" }}>{alert.title}</span>
                    <span style={{ fontSize: "0.65rem", fontWeight: 600, padding: "2px 7px", borderRadius: "999px",
                      background: `${CATEGORY_COLORS[alert.category]}15`,
                      color: CATEGORY_COLORS[alert.category],
                      border: `1px solid ${CATEGORY_COLORS[alert.category]}25`,
                      textTransform: "uppercase", letterSpacing: "0.05em" }}>
                      {CATEGORY_LABEL[alert.category]}
                    </span>
                    {alert.acknowledged && (
                      <span style={{ fontSize: "0.65rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "3px" }}>
                        <CheckCircle size={10} /> Acknowledged
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginBottom: "4px" }}>
                    {alert.field_name}
                  </div>
                  <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>{alert.message}</div>
                  <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", marginTop: "8px" }}>
                    {new Date(alert.timestamp).toLocaleString("en-IN")}
                  </div>
                </div>
                {!alert.acknowledged && (
                  <button onClick={() => acknowledge(alert.id)} style={{
                    padding: "5px 10px", borderRadius: "7px",
                    background: "var(--bg-elevated)", border: "1px solid var(--bg-border)",
                    color: "var(--text-muted)", fontSize: "0.68rem", fontWeight: 600,
                    cursor: "pointer", whiteSpace: "nowrap", flexShrink: 0,
                    display: "flex", alignItems: "center", gap: "4px",
                  }}>
                    <Eye size={11} /> Acknowledge
                  </button>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {filtered.length === 0 && (
          <div style={{ textAlign: "center", padding: "48px", color: "var(--text-muted)" }}>
            <Bell size={32} style={{ margin: "0 auto 12px", opacity: 0.3 }} />
            <div style={{ fontSize: "0.875rem" }}>No alerts matching current filters</div>
          </div>
        )}
      </div>
    </div>
  );
}
