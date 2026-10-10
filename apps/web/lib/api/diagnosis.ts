import type { DiagnosisResult } from "../types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/** Upload a leaf photo; the server identifies the crop and picks its disease model. */
export async function diagnoseCrop(file: File): Promise<DiagnosisResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/diagnose`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorJson = await response.json().catch(() => null);
    throw new Error(errorJson?.error?.message || `Diagnosis failed with status ${response.status}`);
  }

  const json = await response.json();
  return json.data;
}
