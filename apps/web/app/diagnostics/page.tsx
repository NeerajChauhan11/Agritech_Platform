"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, Microscope, CheckCircle, ScanSearch, Loader2, AlertCircle } from "lucide-react";
import { Card, SectionHeader } from "@/components/ui/Cards";
import { DiagnosisResultCard } from "@/components/diagnostics/DiagnosisResultCard";
import { XaiHeatmapViewer } from "@/components/diagnostics/XaiHeatmapViewer";
import { diagnoseCrop } from "@/lib/api/diagnosis";
import { SUPPORTED_CROP_NAMES } from "@/lib/crops";
import { DEMO_DIAGNOSIS_PRESETS } from "@/lib/demo-data";
import type { DiagnosisResult } from "@/lib/types";

export default function DiagnosticsPage() {
  const [isDragging, setIsDragging] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    const previewUrl = URL.createObjectURL(file);
    setImageUrl(previewUrl);
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const diagResult = await diagnoseCrop(file);
      setResult(diagResult);
    } catch (err) {
      console.error("Diagnosis error:", err);
      setError(err instanceof Error ? err.message : "Inference service connection error");
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) handleFileUpload(file);
  };

  return (
    <div className="page-stack" style={{ maxWidth: "1200px" }}>
      <motion.div className="page-header" initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1>AI Disease Detection</h1>
        <p>Upload a leaf photo of {SUPPORTED_CROP_NAMES} — the crop is identified automatically, then analysed by the disease model made for that crop</p>
      </motion.div>

      <div style={{ display: "grid", gridTemplateColumns: imageUrl ? "1fr 1fr" : "1fr", gap: "20px", alignItems: "start" }}>
        {/* Upload Panel */}
        <Card delay={0.1}>
          <SectionHeader title="Leaf Image Upload" subtitle={`JPG, PNG, WebP — no need to choose the crop (${SUPPORTED_CROP_NAMES})`} />

          {/* Drop zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
            style={{
              border: `2px dashed ${isDragging ? "var(--brand-green)" : "var(--bg-border)"}`,
              borderRadius: "12px", padding: "28px", textAlign: "center", cursor: "pointer",
              background: isDragging ? "rgba(34,197,94,0.06)" : "var(--bg-elevated)",
              transition: "all 0.15s", marginBottom: "16px",
            }}
          >
            <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }}
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFileUpload(f); }} />
            <Upload size={30} color={isDragging ? "var(--brand-green)" : "var(--text-muted)"} style={{ margin: "0 auto 10px" }} />
            <div style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "4px" }}>
              Drag & drop leaf photo or browse
            </div>
            <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Supported: JPG, PNG, WebP (max 10 MB)</div>
          </div>

          {/* Demo presets */}
          <div style={{ marginBottom: "12px" }}>
            <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginBottom: "6px", fontWeight: 600 }}>OR TEST SAMPLE PRESETS:</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {DEMO_DIAGNOSIS_PRESETS.map((p) => (
                <button
                  key={p.label}
                  onClick={() => { setImageUrl(p.url); setResult(p.data); setError(null); }}
                  style={{
                    padding: "6px 10px", borderRadius: "8px", background: "rgba(34,197,94,0.08)",
                    border: "1px solid rgba(34,197,94,0.2)", color: "var(--brand-green-light)",
                    fontSize: "0.72rem", fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: "6px",
                  }}
                >
                  <Microscope size={13} />
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div style={{ padding: "10px 12px", borderRadius: "8px", background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)", marginBottom: "12px", display: "flex", gap: "8px", alignItems: "center" }}>
              <AlertCircle size={15} color="var(--status-danger)" />
              <div style={{ fontSize: "0.74rem", color: "var(--status-danger)" }}>
                API Note: {error}. Ensure backend is running at http://localhost:8000.
              </div>
            </div>
          )}

          {/* Uploaded Preview */}
          {imageUrl && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ marginTop: "14px" }}>
              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginBottom: "6px" }}>Selected Image</div>
              <img src={imageUrl} alt="Leaf preview" style={{ width: "100%", borderRadius: "10px", maxHeight: "200px", objectFit: "cover" }} />
            </motion.div>
          )}

          {/* Loading */}
          <AnimatePresence>
            {loading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                style={{ marginTop: "14px", padding: "16px", background: "var(--bg-elevated)", borderRadius: "10px", border: "1px solid var(--bg-border)", textAlign: "center" }}>
                <Loader2 size={24} color="var(--brand-green)" style={{ margin: "0 auto 8px", animation: "spin 1s linear infinite" }} />
                <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)" }}>Running Computer Vision Diagnosis...</div>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "4px" }}>Quality check → Crop identification → Disease analysis</div>
                <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
              </motion.div>
            )}
          </AnimatePresence>
        </Card>

        {/* Result Panel */}
        <AnimatePresence>
          {result && !loading && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <DiagnosisResultCard result={result} />
              {result.xai && <XaiHeatmapViewer heatmapUrl={result.xai.heatmap_url} imageUrl={imageUrl} />}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Info Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "14px" }}>
        {[
          { icon: <Microscope size={18} />, title: "Automatic Crop Detection", desc: "The crop is identified first. Its own disease model is used when installed; otherwise a preliminary category screen runs." },
          { icon: <ScanSearch size={18} />, title: "Quality-Checked Input", desc: "Blurry, dark or off-subject photos are rejected with advice to retake, instead of guessing." },
          { icon: <CheckCircle size={18} />, title: "Honest Results", desc: "Low-confidence results show candidates only, never a made-up diagnosis, plus symptoms and treatment when confident." },
        ].map(({ icon, title, desc }) => (
          <Card key={title} delay={0.3} hover>
            <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
              <div style={{ color: "var(--brand-green)", marginTop: "2px" }}>{icon}</div>
              <div>
                <div style={{ fontWeight: 600, fontSize: "0.82rem", color: "var(--text-primary)", marginBottom: "4px" }}>{title}</div>
                <div style={{ fontSize: "0.73rem", color: "var(--text-muted)", lineHeight: 1.5 }}>{desc}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
