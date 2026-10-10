"use client";

import { AlertCircle, Camera, Info, Leaf, ShieldAlert } from "lucide-react";
import type { ComponentType } from "react";
import { SUPPORTED_CROPS } from "@/lib/crops";
import type { DiagnosisResult, DiagnosisStatus } from "@/lib/types";

type Tone = "warning" | "danger" | "info";

const STATUS_VIEW: Record<
  Exclude<DiagnosisStatus, "ok">,
  { tone: Tone; title: string; Icon: ComponentType<{ size?: number }> }
> = {
  low_quality_image: { tone: "warning", title: "Photo quality too low", Icon: Camera },
  crop_uncertain: { tone: "warning", title: "Crop not recognised", Icon: Leaf },
  crop_unsupported: { tone: "danger", title: "Crop not supported", Icon: ShieldAlert },
  model_unavailable: { tone: "info", title: "Model not installed", Icon: Info },
  disease_uncertain: { tone: "warning", title: "No confident diagnosis", Icon: AlertCircle },
};

interface Props {
  result: DiagnosisResult;
}

/** Explains any non-`ok` outcome and what the user should do next. */
export function DiagnosisStatusNotice({ result }: Props) {
  if (result.status === "ok") return null;
  const { tone, title, Icon } = STATUS_VIEW[result.status];
  return (
    <div className={`notice notice-${tone}`} role="alert">
      <span className="notice-icon">
        <Icon size={18} />
      </span>
      <div>
        <div className="notice-title">{title}</div>
        <div className="notice-text">{result.message}</div>
        {result.status === "crop_unsupported" ? (
          <div className="notice-text">
            Supported crops:{" "}
            <span className="notice-chips">
              {SUPPORTED_CROPS.map(({ id, name }) => (
                <span key={id} className="badge badge-green">{name}</span>
              ))}
            </span>
          </div>
        ) : (
          result.user_action && <div className="notice-text">{result.user_action}</div>
        )}
      </div>
    </div>
  );
}
