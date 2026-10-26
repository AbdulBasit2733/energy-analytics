import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatMW(value: number | null | undefined): string {
  if (value == null) return "—";
  return `${value.toLocaleString("en-GB", { maximumFractionDigits: 0 })} MW`;
}

export function formatMWh(value: number | null | undefined): string {
  if (value == null) return "—";
  return `${value.toLocaleString("en-GB", { maximumFractionDigits: 0 })} MWh`;
}

export function formatPercent(value: number | null | undefined): string {
  if (value == null) return "—";
  return `${value.toFixed(1)}%`;
}

export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  });
}

export function formatDateShort(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    timeZone: "UTC",
  });
}

export function formatHour(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,  // Enable AM/PM
    timeZone: "UTC",
  });
}

export function formatHour24(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,  // 24-hour format
    timeZone: "UTC",
  });
}
