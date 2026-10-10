"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon: ReactNode;
  trend?: { value: number; label: string };
  status?: "healthy" | "warning" | "critical" | "info";
  delay?: number;
  subtitle?: string;
}

const STATUS_COLORS = {
  healthy: "var(--status-healthy)",
  warning: "var(--status-warning)",
  critical: "var(--status-danger)",
  info: "var(--status-info)",
};

export function MetricCard({
  title, value, unit, icon, trend, status = "info", delay = 0, subtitle,
}: MetricCardProps) {
  const color = STATUS_COLORS[status];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className="glass glass-hover"
      style={{ borderRadius: "14px", padding: "20px", display: "flex", flexDirection: "column", gap: "12px" }}
    >
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", fontWeight: 500 }}>{title}</span>
        <div style={{
          width: "34px", height: "34px", borderRadius: "9px",
          background: `${color}18`,
          display: "flex", alignItems: "center", justifyContent: "center",
          color,
        }}>
          {icon}
        </div>
      </div>

      {/* Value */}
      <div style={{ display: "flex", alignItems: "baseline", gap: "4px" }}>
        <span className="metric-value" style={{ color }}>{value}</span>
        {unit && <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 500 }}>{unit}</span>}
      </div>

      {/* Subtitle / trend */}
      {subtitle && (
        <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{subtitle}</span>
      )}
      {trend && (
        <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <span style={{
            fontSize: "0.72rem", fontWeight: 600,
            color: trend.value >= 0 ? "var(--status-healthy)" : "var(--status-danger)",
          }}>
            {trend.value >= 0 ? "▲" : "▼"} {Math.abs(trend.value)}%
          </span>
          <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{trend.label}</span>
        </div>
      )}
    </motion.div>
  );
}

// ── Section Header ────────────────────────────────────────────────
interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}

export function SectionHeader({ title, subtitle, action }: SectionHeaderProps) {
  return (
    <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "16px" }}>
      <div>
        <h2 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--text-primary)" }}>{title}</h2>
        {subtitle && <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "2px" }}>{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

// ── Status Badge ────────────────────────────────────────────────
interface StatusBadgeProps {
  status: "healthy" | "warning" | "critical" | "info" | "online" | "offline" | "low" | "medium" | "high";
  label?: string;
}

const BADGE_MAP: Record<string, string> = {
  healthy: "badge-green",
  online: "badge-green",
  info: "badge-blue",
  warning: "badge-yellow",
  low: "badge-blue",
  medium: "badge-yellow",
  high: "badge-red",
  critical: "badge-red",
  offline: "badge-red",
};

export function StatusBadge({ status, label }: StatusBadgeProps) {
  return (
    <span className={cn("badge", BADGE_MAP[status] || "badge-blue")}>
      <span className={cn("status-dot", status === "online" || status === "healthy" ? "online" : status === "warning" || status === "medium" ? "warning" : "offline")} />
      {label || status.toUpperCase()}
    </span>
  );
}

// ── Card ─────────────────────────────────────────────────────────
interface CardProps {
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
  hover?: boolean;
  delay?: number;
}

export function Card({ children, style, hover = false, delay = 0 }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay }}
      className={cn("glass", hover && "glass-hover")}
      style={{ borderRadius: "14px", padding: "20px", ...style }}
    >
      {children}
    </motion.div>
  );
}

// ── Progress Bar ─────────────────────────────────────────────────
interface ProgressBarProps {
  value: number;
  max?: number;
  color?: string;
  label?: string;
  showValue?: boolean;
}

export function ProgressBar({ value, max = 100, color = "var(--brand-green)", label, showValue = true }: ProgressBarProps) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div style={{ width: "100%" }}>
      {(label || showValue) && (
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
          {label && <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{label}</span>}
          {showValue && <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontFamily: "monospace" }}>{value.toFixed(1)}%</span>}
        </div>
      )}
      <div className="progress-bar">
        <motion.div
          className="progress-fill"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}
