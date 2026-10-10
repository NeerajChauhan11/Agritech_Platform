import { apiClient } from "./client";
import type { Farm, Field } from "../types";

export async function getFarms(): Promise<Farm[]> {
  return apiClient<Farm[]>("/farms");
}

export async function getFarm(farmId: string): Promise<Farm> {
  return apiClient<Farm>(`/farms/${farmId}`);
}

export async function getFarmFields(farmId: string): Promise<Field[]> {
  return apiClient<Field[]>(`/farms/${farmId}/fields`);
}

export async function getField(farmId: string, fieldId: string): Promise<Field> {
  return apiClient<Field>(`/farms/${farmId}/fields/${fieldId}`);
}
