import { Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/app-layout";
import { AccuracyPage } from "./pages/accuracy-page";
import { DashboardPage } from "./pages/dashboard-page";
import { MethodologyPage } from "./pages/methodology-page";
import { NotFoundPage } from "./pages/not-found-page";
import { ProcurementPage } from "./pages/procurement-page";
import { TimeseriesPage } from "./pages/timeseries-page";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/timeseries" element={<TimeseriesPage />} />
        <Route path="/accuracy" element={<AccuracyPage />} />
        <Route path="/procurement" element={<ProcurementPage />} />
        <Route path="/methodology" element={<MethodologyPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
