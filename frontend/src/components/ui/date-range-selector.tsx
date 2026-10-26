import { useState } from "react";

interface DateRange {
  from: string;
  to: string;
  label: string;
}

const PRESET_RANGES: DateRange[] = [
  { from: "2026-01-01", to: "2026-01-31", label: "January 2026" },
  { from: "2026-02-01", to: "2026-02-28", label: "February 2026" },
  { from: "2026-03-01", to: "2026-03-31", label: "March 2026" },
  { from: "2026-04-01", to: "2026-04-30", label: "April 2026" },
  { from: "2026-05-01", to: "2026-05-31", label: "May 2026" },
  { from: "2026-06-01", to: "2026-06-30", label: "June 2026" },
  { from: "2026-07-01", to: "2026-07-31", label: "July 2026" },
  { from: "2026-08-01", to: "2026-08-31", label: "August 2026" },
  { from: "2026-09-01", to: "2026-09-30", label: "September 2026" },
  { from: "2026-10-01", to: "2026-10-31", label: "October 2026" },
  { from: "2026-11-01", to: "2026-11-30", label: "November 2026" },
  { from: "2026-12-01", to: "2026-12-31", label: "December 2026" },
  { from: "2026-01-01", to: "2026-03-31", label: "Q1 2026" },
  { from: "2026-04-01", to: "2026-06-30", label: "Q2 2026" },
  { from: "2026-07-01", to: "2026-09-30", label: "Q3 2026" },
  { from: "2026-10-01", to: "2026-12-31", label: "Q4 2026" },
  { from: "2026-01-01", to: "2026-12-31", label: "Full Year 2026" },
];

interface DateRangeSelectorProps {
  onRangeChange: (from: string, to: string) => void;
  className?: string;
}

export function DateRangeSelector({ onRangeChange, className }: DateRangeSelectorProps) {
  const [from, setFrom] = useState("2026-01-01");
  const [to, setTo] = useState("2026-01-31");

  const handleFromChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFrom = e.target.value;
    setFrom(newFrom);
    if (newFrom && to) {
      if (newFrom > to) {
        console.warn("Start date must be before or equal to end date");
        return;
      }
      onRangeChange(newFrom, to);
    }
  };

  const handleToChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTo = e.target.value;
    setTo(newTo);
    if (from && newTo) {
      if (from > newTo) {
        console.warn("End date must be after or equal to start date");
        return;
      }
      onRangeChange(from, newTo);
    }
  };

  const handlePresetClick = (range: DateRange) => {
    setFrom(range.from);
    setTo(range.to);
    onRangeChange(range.from, range.to);
  };

  return (
    <div className={className}>
      <label className="text-sm font-medium text-muted-foreground block mb-2">
        Date Range
      </label>

      {/* Custom date inputs */}
      <div className="flex gap-2 mb-3">
        <div className="flex-1">
          <label htmlFor="date-from" className="text-xs text-muted-foreground block mb-1">
            From
          </label>
          <input
            id="date-from"
            type="date"
            value={from}
            onChange={handleFromChange}
            max={to}
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
        </div>
        <div className="flex-1">
          <label htmlFor="date-to" className="text-xs text-muted-foreground block mb-1">
            To
          </label>
          <input
            id="date-to"
            type="date"
            value={to}
            onChange={handleToChange}
            min={from}
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
        </div>
      </div>

      {/* Quick presets */}
      <div className="space-y-1">
        <p className="text-xs text-muted-foreground mb-2">Quick Select:</p>
        <div className="grid grid-cols-2 gap-1">
          {PRESET_RANGES.map((range, index) => (
            <button
              key={index}
              onClick={() => handlePresetClick(range)}
              className="text-xs px-2 py-1.5 rounded border border-input bg-transparent hover:bg-accent hover:text-accent-foreground transition-colors text-left"
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// Compact version for inline use
interface CompactDateSelectorProps {
  onRangeChange: (from: string, to: string) => void;
}

export function CompactDateSelector({ onRangeChange }: CompactDateSelectorProps) {
  const [mode, setMode] = useState<"preset" | "custom">("preset");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [from, setFrom] = useState("2026-01-01");
  const [to, setTo] = useState("2026-01-31");

  const handlePresetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const index = parseInt(e.target.value);
    if (index === -1) {
      setMode("custom");
      return;
    }

    // Validate index bounds
    if (index < 0 || index >= PRESET_RANGES.length) {
      console.error(`Invalid preset index: ${index}`);
      return;
    }

    setSelectedIndex(index);
    const range = PRESET_RANGES[index];
    setFrom(range.from);
    setTo(range.to);
    onRangeChange(range.from, range.to);
  };

  const handleFromChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFrom = e.target.value;
    setFrom(newFrom);
    if (newFrom && to) {
      if (newFrom > to) {
        console.warn("Start date must be before or equal to end date");
        return;
      }
      onRangeChange(newFrom, to);
    }
  };

  const handleToChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTo = e.target.value;
    setTo(newTo);
    if (from && newTo) {
      if (from > newTo) {
        console.warn("End date must be after or equal to start date");
        return;
      }
      onRangeChange(from, newTo);
    }
  };

  if (mode === "custom") {
    return (
      <div className="flex items-center gap-2">
        <input
          type="date"
          value={from}
          onChange={handleFromChange}
          max={to}
          className="flex h-9 w-[140px] rounded-md border border-input bg-card px-2 py-1 text-xs shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          aria-label="Start date"
        />
        <span className="text-xs text-muted-foreground">to</span>
        <input
          type="date"
          value={to}
          onChange={handleToChange}
          min={from}
          className="flex h-9 w-[140px] rounded-md border border-input bg-card px-2 py-1 text-xs shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          aria-label="End date"
        />
        <button
          onClick={() => setMode("preset")}
          className="text-xs px-2 py-1.5 rounded border border-input bg-card hover:bg-accent hover:text-accent-foreground transition-colors"
          aria-label="Switch to preset ranges"
        >
          Presets
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <select
        value={selectedIndex}
        onChange={handlePresetChange}
        className="flex h-9 rounded-md border border-input bg-card px-3 py-1 text-sm shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
        aria-label="Select date range"
      >
        {PRESET_RANGES.map((range, index) => (
          <option key={index} value={index}>
            {range.label}
          </option>
        ))}
        <option value={-1}>Custom Range...</option>
      </select>
    </div>
  );
}
