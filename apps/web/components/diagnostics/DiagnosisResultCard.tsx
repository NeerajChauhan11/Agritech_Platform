"use client";

import { Info } from "lucide-react";
import { Card, ProgressBar } from "@/components/ui/Cards";
import { DiagnosisGuidance } from "@/components/diagnostics/DiagnosisGuidance";
import { DiagnosisStatusNotice } from "@/components/diagnostics/DiagnosisStatusNotice";
import { PredictionList } from "@/components/diagnostics/PredictionList";
import type { DiagnosisResult } from "@/lib/types";

const SEVERITY_BADGE = {
  none: "badge-green",
  low: "badge-blue",
  moderate: "badge-yellow",
  high: "badge-red",
} as const;

const toPercent = (value: number) => `${Math.round(value * 100)}%`;

interface Props {
  result: DiagnosisResult;
}

export function DiagnosisResultCard({ result }: Props) {
  const isOk = result.status === "ok";
  const isGeneral = result.diagnosis_tier === "general_category";
  const hasDiseaseCandidates = isOk || result.status === "disease_uncertain";
  const isHealthy = result.disease_label === "healthy";
  const candidates = isGeneral ? (result.category_predictions ?? []) : result.predictions;
  const zeroShot = result.crop_id_method === "zero_shot_clip" ? " · zero-shot estimate" : "";

  return (
    <Card>
      <div className="info-row">
        <div>
          <div className="section-label">Detected crop</div>
          <div className="diag-title">{result.detected_crop ?? "Not identified"}</div>
          {result.crop_confidence !== null && (
            <div className="diag-sub">Crop confidence {toPercent(result.crop_confidence)}{zeroShot}</div>
          )}
        </div>
        {isOk && isGeneral && <span className="badge badge-blue">Preliminary</span>}
        {isOk && !isGeneral && result.severity && (
          <span className={`badge ${SEVERITY_BADGE[result.severity]}`}>
            {isHealthy ? "Healthy" : `${result.severity} severity`}
          </span>
        )}
      </div>

      {isGeneral && result.tier_notice && (
        <div className="diag-section">
          <div className="notice notice-info" role="note">
            <span className="notice-icon"><Info size={18} /></span>
            <div className="notice-title">{result.tier_notice}</div>
          </div>
        </div>
      )}

      <div className="diag-section">
        <DiagnosisStatusNotice result={result} />
      </div>

      {isOk && isGeneral && result.category && (
        <div className="diag-section">
          <div className="section-label">Condition category (not a specific disease)</div>
          <div className="diag-title">{result.category.label}</div>
          <ProgressBar label="Relative score (not calibrated)" value={result.category.confidence * 100} />
        </div>
      )}

      {isOk && !isGeneral && result.disease_name && result.disease_confidence !== null && (
        <div className="diag-section">
          <div className="section-label">Diagnosis</div>
          <div className="diag-title">{result.disease_name}</div>
          <ProgressBar label="Confidence" value={result.disease_confidence * 100} />
        </div>
      )}

      {hasDiseaseCandidates ? (
        <PredictionList
          title={isOk ? "Other candidates" : "Possible conditions (not a diagnosis)"}
          items={isOk ? candidates.slice(1) : candidates}
        />
      ) : (
        <PredictionList title="Crop candidates" items={result.crop_candidates} />
      )}

      {isOk && <DiagnosisGuidance result={result} />}

      {result.model_version && <div className="diag-sub diag-section">Model version {result.model_version}</div>}
    </Card>
  );
}
