import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";

export function useTimeseries(params?: {
  date?: string;
  from?: string;
  to?: string;
}) {
  return useQuery({
    queryKey: ["timeseries", params],
    queryFn: () => api.getTimeseries(params),
  });
}

export function useForecastHistory(date: string) {
  return useQuery({
    queryKey: ["forecast-history", date],
    queryFn: () => api.getForecastHistory(date),
    enabled: !!date,
  });
}
