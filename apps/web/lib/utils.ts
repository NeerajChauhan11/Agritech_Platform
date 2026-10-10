import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatValue(value: number, decimals = 1): string {
  return value.toFixed(decimals);
}

export function formatTimestamp(date: Date): string {
  return date.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function getHealthColor(score: number): string {
  if (score >= 80) return "var(--status-healthy)";
  if (score >= 60) return "var(--status-warning)";
  return "var(--status-danger)";
}

export function getHealthLabel(score: number): string {
  if (score >= 80) return "Healthy";
  if (score >= 60) return "Fair";
  return "Critical";
}

export function getMoistureStatus(moisture: number): "optimal" | "low" | "critical" {
  if (moisture >= 40) return "optimal";
  if (moisture >= 25) return "low";
  return "critical";
}

export function clampBetween(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function randomBetween(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

export function addJitter(base: number, jitter: number): number {
  return base + (Math.random() - 0.5) * jitter * 2;
}
