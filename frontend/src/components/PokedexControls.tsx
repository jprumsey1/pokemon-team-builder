import type { StatKey } from "../api/types";
import { STATS, TYPES, displayName } from "../lib/pokemon";

export type SortKey = "id" | "name" | StatKey;

export interface Filters {
  search: string;
  type: string;
  sort: SortKey;
  showAlternateForms: boolean;
}

export const DEFAULT_FILTERS: Filters = {
  search: "",
  type: "",
  sort: "id",
  showAlternateForms: false,
};

interface Props {
  filters: Filters;
  onChange: (patch: Partial<Filters>) => void;
  showing: number;
  total: number;
}

export function PokedexControls({
  filters,
  onChange,
  showing,
  total,
}: Props) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <input
        type="search"
        placeholder="Search…"
        className="field grow sm:grow-0"
        value={filters.search}
        onChange={(event) => onChange({ search: event.target.value })}
      />
      <select
        className="field"
        value={filters.type}
        onChange={(event) => onChange({ type: event.target.value })}
      >
        <option value="">All Types</option>
        {TYPES.map((type) => (
          <option key={type} value={type}>
            {displayName(type)}
          </option>
        ))}
      </select>
      <select
        className="field"
        value={filters.sort}
        onChange={(event) => onChange({ sort: event.target.value as SortKey })}
      >
        <option value="id">Pokédex Number</option>
        <option value="name">Name A–Z</option>
        {STATS.map(({ key, label }) => (
          <option key={key} value={key}>
            {label}
          </option>
        ))}
      </select>
      <label className="flex items-center gap-1.5 text-sm text-slate-600">
        <input
          type="checkbox"
          checked={filters.showAlternateForms}
          onChange={(event) =>
            onChange({ showAlternateForms: event.target.checked })
          }
        />
        Include Alternate Forms
      </label>
      <span className="ml-auto text-xs text-slate-500">
        {showing} of {total}
      </span>
    </div>
  );
}
