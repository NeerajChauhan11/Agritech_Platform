"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { TrendingUp, TrendingDown, Target, Info, ChevronRight } from "lucide-react";
import { Card, SectionHeader } from "@/components/ui/Cards";
import { DEMO_YIELD } from "@/lib/demo-data";
import type { YieldPrediction } from "@/lib/types";

const FACTOR_COLOR: Record<string, string> = {
  positive: "var(--status-healthy)",
  negative: "var(--status-danger)",
  neutral: "var(--status-info)",
};

export default function YieldPage() {
  const [selected, setSelected] = useState<YieldPrediction>(DEMO_YIELD[0]);

  const chartData = DEMO_YIELD.map((y) => ({
    name: y.crop,
    last: y.last_season_yield,
    predicted: y.estimated_yield_t_per_hectare,
    lower: y.prediction_interval.lower,
    upper: y.prediction_interval.upper,
  }));

  const change = ((selected.estimated_yield_t_per_hectare - selected.last_season_yield) / selected.last_season_yield) * 100;
  const isPositive = change >= 0;

  return (
    <div className="page-stack" style={{ maxWidth: "1200px" }}>
      <motion.div className="page-header" initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1>Yield Prediction</h1>
        <p>ML-powered seasonal yield estimates with confidence intervals — values are predictions, not guarantees</p>
      </motion.div>

      {/* Disclaimer */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
        style={{ padding: "10px 14px", borderRadius: "10px",
          background: "rgba(59,130,246,0.06)", border: "1px solid rgba(59,130,246,0.15)",
          display: "flex", gap: "8px", alignItems: "center" }}>
        <Info size={14} color="#93c5fd" />
        <span style={{ fontSize: "0.75rem", color: "#93c5fd" }}>
          These are AI estimates based on historical and environmental data. Actual yields depend on many factors including weather events, pests, and market conditions.
        </span>
      </motion.div>

      {/* Comparison chart */}
      <Card delay={0.15}>
        <SectionHeader title="Yield Comparison" subtitle="Predicted vs last season across all fields" />
        <div style={{ height: "220px" }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 4, right: 4, left: -10, bottom: 0 }} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(34,197,94,0.06)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false}
                label={{ value: "t/ha", angle: -90, position: "insideLeft", style: { fill: "var(--text-muted)", fontSize: 10 } }} />
              <Tooltip contentStyle={{ background: "var(--bg-elevated)", border: "1px solid var(--bg-border)", borderRadius: "8px", fontSize: "11px" }}
                formatter={(value, name) => [`${Number(value ?? 0).toFixed(2)} t/ha`, name === "predicted" ? "AI Predicted" : "Last Season"]} />
              <Bar dataKey="last" name="last" fill="rgba(107,114,128,0.4)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="predicted" name="predicted" fill="var(--brand-green)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ display: "flex", gap: "16px", marginTop: "8px", justifyContent: "center" }}>
          {[["rgba(107,114,128,0.4)", "Last Season"], ["var(--brand-green)", "AI Predicted"]].map(([color, label]) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: "5px" }}>
              <div style={{ width: "12px", height: "12px", borderRadius: "3px", background: color }} />
              <span style={{ fontSize: "0.68rem", color: "var(--text-muted)" }}>{label}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Field selector + detail */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "14px" }}>
        {DEMO_YIELD.map((pred, i) => {
          const ch = ((pred.estimated_yield_t_per_hectare - pred.last_season_yield) / pred.last_season_yield) * 100;
          const pos = ch >= 0;
          const isSelected = selected.field_id === pred.field_id;
          return (
            <motion.div
              key={pred.field_id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              onClick={() => setSelected(pred)}
              className="glass glass-hover"
              style={{
                borderRadius: "14px", padding: "18px", cursor: "pointer",
                border: `1px solid ${isSelected ? "rgba(34,197,94,0.3)" : "var(--bg-border)"}`,
                background: isSelected ? "rgba(34,197,94,0.04)" : undefined,
              }}
            >
              <div style={{ fontWeight: 600, fontSize: "0.875rem", color: "var(--text-primary)", marginBottom: "2px" }}>{pred.crop}</div>
              <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginBottom: "14px" }}>{pred.field_name}</div>

              <div style={{ fontSize: "2.2rem", fontWeight: 800, color: "var(--text-primary)", lineHeight: 1, marginBottom: "4px" }}>
                {pred.estimated_yield_t_per_hectare}
                <span style={{ fontSize: "0.8rem", fontWeight: 500, color: "var(--text-muted)", marginLeft: "4px" }}>t/ha</span>
              </div>

              <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", marginBottom: "12px" }}>
                Range: {pred.prediction_interval.lower}–{pred.prediction_interval.upper} t/ha
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px" }}>
                {pos ? <TrendingUp size={13} color="var(--status-healthy)" /> : <TrendingDown size={13} color="var(--status-danger)" />}
                <span style={{ fontSize: "0.72rem", fontWeight: 700, color: pos ? "var(--status-healthy)" : "var(--status-danger)" }}>
                  {pos ? "+" : ""}{ch.toFixed(1)}% vs last season
                </span>
              </div>

              {/* Confidence bar */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                  <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>Confidence</span>
                  <span style={{ fontSize: "0.65rem", color: "var(--text-muted)", fontFamily: "monospace" }}>{(pred.confidence * 100).toFixed(0)}%</span>
                </div>
                <div style={{ height: "4px", background: "var(--bg-elevated)", borderRadius: "999px", overflow: "hidden" }}>
                  <motion.div initial={{ width: 0 }} animate={{ width: `${pred.confidence * 100}%` }}
                    transition={{ duration: 0.6, delay: i * 0.1 }}
                    style={{ height: "100%", background: "var(--brand-green)", borderRadius: "999px" }} />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Detailed factor analysis */}
      <AnimatePresence mode="wait">
        <motion.div key={selected.field_id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
          <Card>
            <SectionHeader
              title={`Factor Analysis — ${selected.crop} (${selected.field_name})`}
              subtitle="Relative impact of each input factor on the predicted yield"
            />
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {selected.factors.map((factor, i) => (
                <motion.div
                  key={factor.name}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.07 }}
                  style={{ display: "flex", alignItems: "center", gap: "12px" }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "6px", width: "140px" }}>
                    {factor.impact === "positive" ? (
                      <TrendingUp size={13} color={FACTOR_COLOR.positive} />
                    ) : factor.impact === "negative" ? (
                      <TrendingDown size={13} color={FACTOR_COLOR.negative} />
                    ) : (
                      <Target size={13} color={FACTOR_COLOR.neutral} />
                    )}
                    <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{factor.name}</span>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ height: "6px", background: "var(--bg-elevated)", borderRadius: "999px", overflow: "hidden" }}>
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${factor.weight * 100}%` }}
                        transition={{ duration: 0.6, delay: i * 0.07 }}
                        style={{ height: "100%", background: FACTOR_COLOR[factor.impact], borderRadius: "999px" }}
                      />
                    </div>
                  </div>
                  <span style={{ fontSize: "0.7rem", fontWeight: 700, color: FACTOR_COLOR[factor.impact], width: "40px", textAlign: "right" }}>
                    {(factor.weight * 100).toFixed(0)}%
                  </span>
                  <span style={{ fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "capitalize", width: "55px" }}>
                    {factor.impact}
                  </span>
                </motion.div>
              ))}
            </div>

            {/* Summary */}
            <div style={{ marginTop: "20px", padding: "12px", borderRadius: "10px",
              background: "var(--bg-elevated)", border: "1px solid var(--bg-border)" }}>
              <div style={{ display: "flex", gap: "24px", flexWrap: "wrap" }}>
                {[
                  { label: "Predicted", value: `${selected.estimated_yield_t_per_hectare} t/ha`, color: "var(--brand-green-light)" },
                  { label: "Range", value: `${selected.prediction_interval.lower}–${selected.prediction_interval.upper} t/ha`, color: "var(--text-primary)" },
                  { label: "Confidence", value: `${(selected.confidence * 100).toFixed(0)}%`, color: isPositive ? "var(--status-healthy)" : "var(--status-warning)" },
                  { label: "vs Last Season", value: `${isPositive ? "+" : ""}${change.toFixed(1)}%`, color: isPositive ? "var(--status-healthy)" : "var(--status-danger)" },
                ].map(({ label, value, color }) => (
                  <div key={label}>
                    <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", marginBottom: "2px" }}>{label}</div>
                    <div style={{ fontWeight: 700, color, fontSize: "0.9rem" }}>{value}</div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
