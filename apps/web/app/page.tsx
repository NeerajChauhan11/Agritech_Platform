"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { Droplets, Thermometer, Wind, Leaf, Activity, Zap, AlertTriangle, XCircle, CheckCircle } from "lucide-react";
import { MetricCard, SectionHeader, Card } from "@/components/ui/Cards";
import { FarmHealthHero } from "@/components/dashboard/FarmHealthHero";
import { FieldCard } from "@/components/dashboard/FieldCard";
import { IrrigationSummary } from "@/components/dashboard/IrrigationSummary";
import { YieldSummary } from "@/components/dashboard/YieldSummary";
import { DEMO_FARM, DEMO_ALERTS, DEMO_TELEMETRY } from "@/lib/demo-data";
import { addJitter } from "@/lib/utils";
import type { TelemetryPoint } from "@/lib/types";
import Link from "next/link";

export default function DashboardPage() {
  const [telemetry, setTelemetry] = useState<TelemetryPoint[]>(DEMO_TELEMETRY["field-01"]);
  const [liveReading, setLiveReading] = useState(DEMO_FARM.fields[0].latest_reading);

  const updateLive = useCallback(() => {
    const newPoint: TelemetryPoint = {
      time: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
      moisture:    Math.round(addJitter(42.5, 3)    * 10)  / 10,
      temperature: Math.round(addJitter(28.4, 1.5)  * 10)  / 10,
      humidity:    Math.round(addJitter(65,   4)    * 10)  / 10,
      ph:          Math.round(addJitter(6.8,  0.15) * 100) / 100,
    };
    setTelemetry((prev) => [...prev.slice(-23), newPoint]);
    setLiveReading((prev) => ({
      ...prev,
      soil_moisture: newPoint.moisture,
      temperature:   newPoint.temperature,
      humidity:      newPoint.humidity,
      ph_level:      newPoint.ph,
    }));
  }, []);

  useEffect(() => {
    const interval = setInterval(updateLive, 5000);
    return () => clearInterval(interval);
  }, [updateLive]);

  const activeAlerts = DEMO_ALERTS.filter((a) => !a.acknowledged);

  const SENSOR_CARDS = [
    { title: "Soil Moisture", value: liveReading.soil_moisture.toFixed(1), unit: "%",      icon: <Droplets size={16} />,    status: liveReading.soil_moisture >= 40 ? "healthy" : liveReading.soil_moisture >= 25 ? "warning" : "critical", trend: { value: 2.1,  label: "vs last hour" }, delay: 0    },
    { title: "Temperature",   value: liveReading.temperature.toFixed(1),   unit: "°C",     icon: <Thermometer size={16} />, status: liveReading.temperature <= 30 ? "healthy" : liveReading.temperature <= 35 ? "warning" : "critical",   trend: { value: -0.8, label: "vs last hour" }, delay: 0.05 },
    { title: "Humidity",      value: liveReading.humidity.toFixed(0),       unit: "%",      icon: <Wind size={16} />,        status: "healthy",                                                                                              delay: 0.1  },
    { title: "Soil pH",       value: liveReading.ph_level.toFixed(2),       unit: "",       icon: <Activity size={16} />,    status: liveReading.ph_level >= 6.0 && liveReading.ph_level <= 7.5 ? "healthy" : "warning",                    delay: 0.15 },
    { title: "Nitrogen",      value: liveReading.nitrogen.toFixed(0),        unit: "mg/kg", icon: <Leaf size={16} />,        status: "healthy",                                                                                              delay: 0.2  },
    { title: "Potassium",     value: liveReading.potassium.toFixed(0),       unit: "mg/kg", icon: <Zap size={16} />,         status: "info",                                                                                                 delay: 0.25 },
  ] as const;

  const SEVERITY_ICON = {
    critical: <XCircle size={14} color="var(--status-danger)" style={{ flexShrink: 0, marginTop: "1px" }} />,
    warning:  <AlertTriangle size={14} color="var(--status-warning)" style={{ flexShrink: 0, marginTop: "1px" }} />,
    info:     <CheckCircle size={14} color="var(--status-info)" style={{ flexShrink: 0, marginTop: "1px" }} />,
  };

  const ALERT_BORDER = {
    critical: "rgba(239,68,68,0.2)",
    warning:  "rgba(245,158,11,0.2)",
    info:     "rgba(59,130,246,0.15)",
  };

  return (
    <div className="page-stack" style={{ maxWidth: "1400px" }}>

      {/* Title */}
      <motion.div className="page-header" initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1>Farm Dashboard</h1>
        <p>{DEMO_FARM.name} · {DEMO_FARM.location} · {DEMO_FARM.fields.length} fields · {DEMO_FARM.total_area_hectares} ha</p>
      </motion.div>

      {/* Farm health hero */}
      <FarmHealthHero farm={DEMO_FARM} activeAlerts={activeAlerts} />

      {/* Live sensor KPIs */}
      <div>
        <SectionHeader title="Live Sensor Reading" subtitle="Tomato Field A — updating every 5 seconds" />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "14px" }}>
          {SENSOR_CARDS.map((card) => (
            <MetricCard key={card.title} {...card} />
          ))}
        </div>
      </div>

      {/* Chart + alerts */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: "16px", alignItems: "start" }}>
        <Card delay={0.2}>
          <SectionHeader
            title="Soil Moisture Trend"
            subtitle="Tomato Field A — last 24 hours"
            action={
              <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "4px" }}>
                <span className="status-dot online pulse-live" /> Live
              </span>
            }
          />
          <div style={{ height: "220px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={telemetry} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="moistureGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(34,197,94,0.06)" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false} interval={4} />
                <YAxis tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "var(--bg-elevated)", border: "1px solid var(--bg-border)", borderRadius: "8px", fontSize: "12px" }} labelStyle={{ color: "var(--text-muted)" }} />
                <Area type="monotone" dataKey="moisture" stroke="#22c55e" strokeWidth={2} fill="url(#moistureGrad)" name="Moisture %" dot={false} />
                <Area type="monotone" dataKey="temperature" stroke="#f59e0b" strokeWidth={2} fill="url(#tempGrad)" name="Temp °C" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: "flex", gap: "16px", marginTop: "8px" }}>
            {[["#22c55e", "Moisture %"], ["#f59e0b", "Temperature °C"]].map(([color, label]) => (
              <div key={label} style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <div style={{ width: "10px", height: "3px", background: color, borderRadius: "2px" }} />
                <span style={{ fontSize: "0.68rem", color: "var(--text-muted)" }}>{label}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card delay={0.25}>
          <SectionHeader
            title="Active Alerts"
            subtitle={`${activeAlerts.length} requiring attention`}
            action={<Link href="/alerts" style={{ fontSize: "0.72rem", color: "var(--brand-green-light)", textDecoration: "none" }}>View all →</Link>}
          />
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {activeAlerts.slice(0, 4).map((alert) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: 8 }}
                animate={{ opacity: 1, x: 0 }}
                style={{ padding: "10px 12px", borderRadius: "10px", background: "var(--bg-elevated)", border: `1px solid ${ALERT_BORDER[alert.severity]}`, display: "flex", gap: "8px" }}
              >
                {SEVERITY_ICON[alert.severity]}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-primary)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{alert.title}</div>
                  <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", marginTop: "2px" }}>{alert.field_name}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      </div>

      {/* All fields */}
      <div>
        <SectionHeader
          title="All Fields"
          subtitle="Real-time status across all monitored fields"
          action={<Link href="/telemetry" style={{ fontSize: "0.72rem", color: "var(--brand-green-light)", textDecoration: "none" }}>Detailed view →</Link>}
        />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "14px" }}>
          {DEMO_FARM.fields.map((field, i) => (
            <FieldCard key={field.id} field={field} index={i} />
          ))}
        </div>
      </div>

      {/* Bottom row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
        <IrrigationSummary />
        <YieldSummary />
      </div>

    </div>
  );
}
