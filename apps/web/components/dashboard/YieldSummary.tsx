"use client";

import Link from "next/link";
import { TrendingUp } from "lucide-react";
import { Card, SectionHeader } from "@/components/ui/Cards";
import { DEMO_YIELD_SUMMARY } from "@/lib/demo-data";

export function YieldSummary() {
  return (
    <Card delay={0.35}>
      <SectionHeader
        title="Yield Forecast"
        subtitle="Season predictions"
        action={
          <Link href="/yield" style={{ fontSize: "0.72rem", color: "var(--brand-green-light)", textDecoration: "none" }}>
            Details →
          </Link>
        }
      />
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {DEMO_YIELD_SUMMARY.map(({ crop, field, est, last, conf }) => (
          <div key={crop} className="info-row mini-stat" style={{ padding: "8px 10px" }}>
            <TrendingUp size={13} color={est >= last ? "var(--status-healthy)" : "var(--status-danger)"} />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-primary)" }}>
                {crop} <span style={{ fontWeight: 400, color: "var(--text-muted)" }}>({field})</span>
              </div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--text-primary)" }}>{est} t/ha</div>
              <div style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>{conf}% conf.</div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
