import { apiClient } from "./client";
import type { Alert } from "../types";

export interface AlertFilterParams {
  field_id?: string;
  severity?: string;
  category?: string;
}

export interface AlertAcknowledgeResult {
  id: string;
  acknowledged: boolean;
  message: string;
}

export async function getAlerts(params?: AlertFilterParams): Promise<Alert[]> {
  const queryParts: string[] = [];
  if (params?.field_id) queryParts.push(`field_id=${encodeURIComponent(params.field_id)}`);
  if (params?.severity) queryParts.push(`severity=${encodeURIComponent(params.severity)}`);
  if (params?.category) queryParts.push(`category=${encodeURIComponent(params.category)}`);

  const qs = queryParts.length > 0 ? `?${queryParts.join("&")}` : "";
  return apiClient<Alert[]>(`/alerts${qs}`);
}

export async function acknowledgeAlert(alertId: string): Promise<AlertAcknowledgeResult> {
  return apiClient<AlertAcknowledgeResult>(`/alerts/${alertId}/acknowledge`, {
    method: "PATCH",
  });
}
