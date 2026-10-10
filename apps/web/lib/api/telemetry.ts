import { apiClient } from "./client";
import type { TelemetryPoint, SensorReading } from "../types";

export async function getTelemetry(fieldId: string): Promise<TelemetryPoint[]> {
  return apiClient<TelemetryPoint[]>(`/telemetry/${fieldId}`);
}

export async function ingestTelemetry(
  deviceId: string,
  fieldId: string,
  reading: SensorReading
): Promise<SensorReading> {
  return apiClient<SensorReading>("/telemetry", {
    method: "POST",
    body: JSON.stringify({
      device_id: deviceId,
      field_id: fieldId,
      reading,
    }),
  });
}
