"use client";

import { useState } from "react";
import { Card, SectionHeader } from "@/components/ui/Cards";

interface Props {
  heatmapUrl: string;
  imageUrl: string | null;
}

export function XaiHeatmapViewer({ heatmapUrl, imageUrl }: Props) {
  const [xaiMode, setXaiMode] = useState<"original" | "heatmap" | "overlay">("original");
  const heatmapSrc = heatmapUrl;

  return (
    <Card>
      <SectionHeader title="XAI Heatmap Viewer" subtitle="Grad-CAM visualization of model attention" />
      <div style={{ display: "flex", gap: "8px", marginBottom: "14px" }}>
        {(["original", "heatmap", "overlay"] as const).map((mode) => (
          <button key={mode} onClick={() => setXaiMode(mode)} className={`tab-btn${xaiMode === mode ? " active" : ""}`}>
            {mode.charAt(0).toUpperCase() + mode.slice(1)}
          </button>
        ))}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px" }}>
        {(["original", "heatmap", "overlay"] as const).map((mode) => (
          <div
            key={mode}
            style={{
              borderRadius: "10px",
              overflow: "hidden",
              border: `2px solid ${xaiMode === mode ? "var(--brand-green)" : "transparent"}`,
              transition: "border-color 0.15s",
              cursor: "pointer",
            }}
            onClick={() => setXaiMode(mode)}
          >
            <div style={{ height: "100px", background: "var(--bg-elevated)", display: "flex", alignItems: "center", justifyContent: "center", position: "relative" }}>
              {mode === "original" && imageUrl && (
                <img src={imageUrl} alt="Original" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              )}
              {mode === "heatmap" && (
                <img
                  src={heatmapSrc}
                  alt="Heatmap"
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  onError={(e) => {
                    // Fallback to synthetic CSS gradient if static file not served
                    (e.target as HTMLElement).style.display = "none";
                  }}
                />
              )}
              {mode === "overlay" && (
                <div style={{ position: "relative", width: "100%", height: "100%" }}>
                  {imageUrl && <img src={imageUrl} alt="Underlay" style={{ width: "100%", height: "100%", objectFit: "cover" }} />}
                  <img
                    src={heatmapSrc}
                    alt="Overlay"
                    style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", mixBlendMode: "screen", opacity: 0.8 }}
                  />
                </div>
              )}
            </div>
            <div style={{ padding: "4px", textAlign: "center", fontSize: "0.65rem", color: "var(--text-muted)", background: "var(--bg-card)", textTransform: "capitalize" }}>
              {mode}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
