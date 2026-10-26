import {
  Info,
  LayoutDashboard,
  LineChart,
  Menu,
  Target,
  TrendingUp,
  Wind,
  X,
} from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { cn } from "@/lib/utils";

const navItems = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/timeseries", label: "Time Series", icon: LineChart },
  { path: "/accuracy", label: "Accuracy", icon: Target },
  { path: "/procurement", label: "Procurement", icon: TrendingUp },
  { path: "/methodology", label: "Methodology", icon: Info },
];

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex flex-col gap-1 p-3">
      {navItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          onClick={onNavigate}
          end={item.path === "/"}
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-colors",
              isActive
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )
          }
        >
          <item.icon className="h-4 w-4 shrink-0" />
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-40 border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/80">
        <div className="flex h-14 items-center gap-4 px-4 lg:px-6">
          <button
            type="button"
            className="lg:hidden p-1.5 rounded-md hover:bg-accent"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle navigation"
          >
            {mobileOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </button>
          <div className="flex items-center gap-2">
            <Wind className="h-5 w-5 text-primary" />
            <h1 className="text-base font-semibold tracking-tight">
              UK Wind Forecast Accuracy
            </h1>
          </div>
          <span className="ml-auto text-xs text-muted-foreground font-mono">
            January 2026
          </span>
        </div>
      </header>

      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <div className="flex">
        <aside
          className={cn(
            "fixed top-14 z-30 h-[calc(100vh-3.5rem)] w-56 border-r border-border bg-card transition-transform lg:sticky lg:translate-x-0",
            mobileOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          <SidebarContent onNavigate={() => setMobileOpen(false)} />
          <div className="absolute bottom-0 left-0 right-0 border-t border-border p-3">
            <p className="text-[10px] text-muted-foreground leading-tight">
              Data: Elexon BMRS
              <br />
              FUELHH &middot; WINDFOR
            </p>
          </div>
        </aside>

        <main className="flex-1 min-w-0 p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
