import { MAX_STAT } from "../lib/pokemon";

export function StatBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-20 shrink-0 text-slate-500">{label}</span>
      <span className="w-8 shrink-0 text-right tabular-nums text-slate-900">
        {value}
      </span>
      <span className="h-1.5 grow rounded-full bg-slate-200">
        <span
          className="block h-full rounded-full bg-slate-500"
          style={{ width: `${(value / MAX_STAT) * 100}%` }}
        />
      </span>
    </div>
  );
}
