import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface KPICardProps {
  label: string;
  value: string;
  subtitle?: string;
  icon?: ReactNode;
  trend?: "positive" | "negative" | "neutral";
  loading?: boolean;
}

export function KPICard({
  label,
  value,
  subtitle,
  icon,
  trend = "neutral",
  loading,
}: KPICardProps) {
  if (loading) {
    return (
      <Card>
        <CardContent className="p-4">
          <Skeleton className="h-4 w-24 mb-2" />
          <Skeleton className="h-8 w-32 mb-1" />
          <Skeleton className="h-3 w-20" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            {label}
          </span>
          {icon && (
            <span className="text-muted-foreground">{icon}</span>
          )}
        </div>
        <p
          className={cn(
            "text-2xl font-semibold font-mono tabular-nums tracking-tight",
            trend === "positive" && "text-chart-actual",
            trend === "negative" && "text-chart-error"
          )}
        >
          {value}
        </p>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  );
}
