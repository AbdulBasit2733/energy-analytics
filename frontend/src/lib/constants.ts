export const CHART_COLORS = {
  forecast: "var(--color-chart-forecast)",
  actual: "var(--color-chart-actual)",
  error: "var(--color-chart-error)",
  bias: "var(--color-chart-bias)",
} as const;

export const CHART_COLORS_HEX = {
  forecast: "#3b82f6",
  actual: "#22c55e",
  error: "#ef4444",
  bias: "#f59e0b",
} as const;

// Use environment variable or fallback to relative /api
export const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : "/api";

export const ANALYSIS_PERIOD = "January 2026";

export const NAV_ITEMS = [
  { path: "/", label: "Dashboard", icon: "LayoutDashboard" },
  { path: "/timeseries", label: "Time Series", icon: "LineChart" },
  { path: "/accuracy", label: "Accuracy Analysis", icon: "Target" },
  { path: "/procurement", label: "Procurement Insight", icon: "TrendingUp" },
  { path: "/methodology", label: "Data & Methodology", icon: "Info" },
] as const;
