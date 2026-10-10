import { apiClient } from "./client";
import type { IrrigationRecommendation } from "../types";

export interface IrrigationConfirmResult {
  field_id: string;
  status: string;
  message: string;
  confirmed_at: string;
}

export async function getIrrigationRecommendations(): Promise<IrrigationRecommendation[]> {
  return apiClient<IrrigationRecommendation[]>("/irrigation/recommendations");
}

export async function confirmIrrigation(
  fieldId: string,
  durationMinutes?: number
): Promise<IrrigationConfirmResult> {
  return apiClient<IrrigationConfirmResult>("/irrigation/confirm", {
    method: "POST",
    body: JSON.stringify({
      field_id: fieldId,
      duration_minutes: durationMinutes,
    }),
  });
}
