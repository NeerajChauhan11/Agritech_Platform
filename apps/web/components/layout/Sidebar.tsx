"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Activity,
  Microscope,
  Droplets,
  TrendingUp,
  Map,
  Bell,
  Settings,
  Leaf,
  Wifi,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { DEMO_ALERTS } from "@/lib/demo-data";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/telemetry", label: "Field Monitor", icon: Activity },
  { href: "/diagnostics", label: "Disease Detection", icon: Microscope },
  { href: "/irrigation", label: "Irrigation Advisor", icon: Droplets },
  { href: "/yield", label: "Yield Prediction", icon: TrendingUp },
  { href: "/map", label: "Farm Map", icon: Map },
  { href: "/alerts", label: "Alerts", icon: Bell },
];

export function Sidebar() {
  const pathname = usePathname();
  const unacknowledged = DEMO_ALERTS.filter((a) => !a.acknowledged).length;

  return (
    <aside style={{
      width: "240px",
      minWidth: "240px",
      background: "var(--bg-surface)",
      borderRight: "1px solid var(--bg-border)",
      display: "flex",
      flexDirection: "column",
      padding: "16px 12px",
      gap: "4px",
      position: "sticky",
      top: 0,
      height: "100vh",
      overflowY: "auto",
    }}>
      {/* Logo */}
      <div style={{ padding: "8px 8px 20px", display: "flex", alignItems: "center", gap: "10px" }}>
        <div style={{
          width: "36px", height: "36px", borderRadius: "10px",
          background: "linear-gradient(135deg, #22c55e, #10b981)",
          display: "flex", alignItems: "center", justifyContent: "center",
          flexShrink: 0,
        }}>
          <Leaf size={18} color="#fff" />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: "0.95rem", color: "var(--text-primary)", lineHeight: 1.2 }}>
            AgriSmart
          </div>
          <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", fontWeight: 500 }}>
            Precision Agriculture
          </div>
        </div>
      </div>

      {/* Demo Badge */}
      <div style={{
        background: "rgba(34,197,94,0.08)",
        border: "1px solid rgba(34,197,94,0.15)",
        borderRadius: "8px",
        padding: "6px 10px",
        display: "flex",
        alignItems: "center",
        gap: "6px",
        marginBottom: "8px",
      }}>
        <span className="status-dot online pulse-live" />
        <span style={{ fontSize: "0.7rem", color: "var(--brand-green-light)", fontWeight: 600 }}>
          DEMO MODE ACTIVE
        </span>
        <Wifi size={11} color="var(--brand-green-light)" style={{ marginLeft: "auto" }} />
      </div>

      {/* Section: Main */}
      <div className="section-label" style={{ padding: "4px 8px", marginBottom: "4px" }}>Navigation</div>

      {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
        const isActive = href === "/" ? pathname === "/" : pathname.startsWith(href);
        const isAlerts = href === "/alerts";
        return (
          <Link key={href} href={href} className={cn("nav-item", isActive && "active")}>
            <Icon size={16} />
            <span style={{ flex: 1 }}>{label}</span>
            {isAlerts && unacknowledged > 0 && (
              <span style={{
                background: "#ef4444", color: "#fff",
                borderRadius: "999px", minWidth: "18px", height: "18px",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "0.65rem", fontWeight: 700, padding: "0 4px",
              }}>
                {unacknowledged}
              </span>
            )}
          </Link>
        );
      })}

      {/* Bottom section */}
      <div style={{ marginTop: "auto", borderTop: "1px solid var(--bg-border)", paddingTop: "12px" }}>
        <Link href="/settings" className={cn("nav-item", pathname === "/settings" && "active")}>
          <Settings size={16} />
          <span>Settings</span>
        </Link>

        {/* Farm info */}
        <div style={{
          marginTop: "12px",
          padding: "10px",
          background: "var(--bg-card)",
          borderRadius: "10px",
          border: "1px solid var(--bg-border)",
        }}>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", fontWeight: 600, marginBottom: "4px" }}>
            GREEN VALLEY FARM
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>Chandigarh, Punjab</div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>24.5 ha · 4 Fields</div>
        </div>
      </div>
    </aside>
  );
}
