import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";

export function useDashboardKPIs(from?: string, to?: string) {
  return useQuery({
    queryKey: ["dashboard-kpis", from, to],
    queryFn: () => api.getDashboardKPIs(from, to),
  });
}

export function useMetadata() {
  return useQuery({
    queryKey: ["metadata"],
    queryFn: api.getMetadata,
  });
}
