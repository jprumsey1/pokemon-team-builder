import { TYPE_COLORS, displayName } from "../lib/pokemon";

export function TypeChip({ type }: { type: string }) {
  return (
    <span
      className="rounded px-1.5 py-0.5 text-[10px] font-semibold text-white uppercase"
      style={{ backgroundColor: TYPE_COLORS[type] ?? "#94a3b8" }}
    >
      {displayName(type)}
    </span>
  );
}
