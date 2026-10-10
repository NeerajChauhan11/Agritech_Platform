"use client";

import { useState, useEffect } from "react";
import { RefreshCw, ChevronDown } from "lucide-react";

export function TopBar() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header style={{
      height: "56px",
      background: "var(--bg-surface)",
      borderBottom: "1px solid var(--bg-border)",
      display: "flex",
      alignItems: "center",
      padding: "0 24px",
      gap: "16px",
      position: "sticky",
      top: 0,
      zIndex: 50,
    }}>
      {/* Live clock */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <span className="status-dot online pulse-live" />
        <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)", fontFamily: "JetBrains Mono, monospace" }}>
          {time.toLocaleTimeString("en-IN")}
        </span>
      </div>

      <div style={{ flex: 1 }} />

      {/* Refresh indicator */}
      <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--text-muted)", fontSize: "0.75rem" }}>
        <RefreshCw size={12} />
        <span>Updating every 5s</span>
      </div>

      {/* User */}
      <div style={{
        display: "flex", alignItems: "center", gap: "8px",
        padding: "6px 10px", borderRadius: "8px",
        background: "var(--bg-card)", border: "1px solid var(--bg-border)",
        cursor: "pointer", fontSize: "0.8rem", color: "var(--text-secondary)",
      }}>
        <div style={{
          width: "24px", height: "24px", borderRadius: "50%",
          background: "linear-gradient(135deg, #22c55e, #10b981)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "0.65rem", fontWeight: 700, color: "#fff",
        }}>
          FO
        </div>
        <span>Farm Owner</span>
        <ChevronDown size={12} />
      </div>
    </header>
  );
}
