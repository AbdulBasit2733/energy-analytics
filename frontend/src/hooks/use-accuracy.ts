import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";

export function useAccuracySummary(from?: string, to?: string) {
  return useQuery({
    queryKey: ["accuracy-summary", from, to],
    queryFn: () => api.getAccuracySummary(from, to),
  });
}

export function useAccuracyDaily(from?: string, to?: string) {
  return useQuery({
    queryKey: ["accuracy-daily", from, to],
    queryFn: () => api.getAccuracyDaily(from, to),
  });
}

export function useErrorDistribution(
  binWidth?: number,
  from?: string,
  to?: string
) {
  return useQuery({
    queryKey: ["error-distribution", binWidth, from, to],
    queryFn: () => api.getErrorDistribution(binWidth, from, to),
  });
}
