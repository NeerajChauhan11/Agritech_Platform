import { apiClient } from "./client";
import type { YieldPrediction } from "../types";

export async function getYieldPredictions(fieldId?: string): Promise<YieldPrediction[]> {
  const query = fieldId ? `?field_id=${encodeURIComponent(fieldId)}` : "";
  return apiClient<YieldPrediction[]>(`/yield/predictions${query}`);
}

export async function predictYield(fieldId: string, crop?: string): Promise<YieldPrediction[]> {
  return apiClient<YieldPrediction[]>("/yield/predict", {
    method: "POST",
    body: JSON.stringify({ field_id: fieldId, crop }),
  });
}
