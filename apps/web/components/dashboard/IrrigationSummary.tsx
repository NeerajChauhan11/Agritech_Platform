"use client";

import Link from "next/link";
import { Droplets } from "lucide-react";
import { Card, SectionHeader } from "@/components/ui/Cards";
import { DEMO_IRRIGATION_SUMMARY } from "@/lib/demo-data";

export function IrrigationSummary() {
  return (
    <Card delay={0.3}>
      <SectionHeader
        title="Irrigation Status"
        subtitle="Water stress across all fields"
        action={
          <Link href="/irrigation" style={{ fontSize: "0.72rem", color: "var(--brand-green-light)", textDecoration: "none" }}>
            Manage →
          </Link>
        }
      />
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {DEMO_IRRIGATION_SUMMARY.map(({ name, stress, minutes, color }) => (
          <div key={name} className="info-row mini-stat" style={{ padding: "8px 10px" }}>
            <Droplets size={13} color={color} />
            <span style={{ flex: 1, fontSize: "0.75rem", color: "var(--text-secondary)" }}>{name}</span>
            <span style={{ fontSize: "0.7rem", fontWeight: 700, color }}>{stress}</span>
            {minutes > 0 && (
              <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>{minutes} min</span>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}
