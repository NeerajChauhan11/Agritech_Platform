"use client";

import { ProgressBar } from "@/components/ui/Cards";
import type { PredictionItem } from "@/lib/types";

interface Props {
  title: string;
  items: PredictionItem[];
}

/** Ranked candidates (crops or diseases) as labelled probability bars. */
export function PredictionList({ title, items }: Props) {
  if (items.length === 0) return null;
  return (
    <div className="diag-section">
      <div className="section-label">{title}</div>
      {items.map((item, i) => (
        <ProgressBar
          key={item.label}
          label={item.display_name}
          value={item.probability * 100}
          color={i === 0 ? "var(--brand-green)" : "var(--text-muted)"}
        />
      ))}
    </div>
  );
}
