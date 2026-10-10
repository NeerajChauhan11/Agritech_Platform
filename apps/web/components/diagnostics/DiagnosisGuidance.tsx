"use client";

import type { DiagnosisResult } from "@/lib/types";

interface Props {
  result: DiagnosisResult;
}

function GuidanceSection({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div className="diag-section">
      <div className="section-label">{title}</div>
      <ul className="bullet-list">
        {items.map((text) => (
          <li key={text}>{text}</li>
        ))}
      </ul>
    </div>
  );
}

/** Symptoms, treatment and prevention; coarse-category wording for the general tier. */
export function DiagnosisGuidance({ result }: Props) {
  const isGeneral = result.diagnosis_tier === "general_category";
  const note = result.category_guidance;
  return (
    <>
      {isGeneral && note && <div className="diag-sub diag-section">{note.description}</div>}
      <GuidanceSection title={isGeneral ? "What to look for" : "Symptoms"} items={result.symptoms} />
      <GuidanceSection
        title={isGeneral ? "Immediate actions" : "Treatment"}
        items={result.recommendations?.treatment ?? []}
      />
      <GuidanceSection title="Prevention" items={result.recommendations?.prevention ?? []} />
      {isGeneral && note && <div className="diag-sub diag-section">{note.consult}</div>}
    </>
  );
}
