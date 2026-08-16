import { useMemo, useState } from "react";

import { usePokemon } from "../api/queries";
import type { Pokemon, StatKey } from "../api/types";
import { displayName, getPokemonTypes } from "../lib/pokemon";
import {
  DEFAULT_FILTERS,
  PokedexControls,
  type Filters,
} from "./PokedexControls";
import { PokemonCard } from "./PokemonCard";

export function Pokedex({
  disabled,
  onAdd,
}: {
  disabled: boolean;
  onAdd: (p: Pokemon) => void;
}) {
  const pokemon = usePokemon();
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);

  // The API already returns Pokédex order, and filter() preserves it.
  const inScope = useMemo(
    () =>
      (pokemon.data ?? []).filter(
        (p) => filters.showAlternateForms || p.is_default,
      ),
    [pokemon.data, filters.showAlternateForms],
  );

  const visible = useMemo(() => {
    // Search the displayed name, so "charizard mega" finds `charizard-mega-x`.
    const search = filters.search.trim().toLowerCase();
    const matches = inScope.filter(
      (p) =>
        (!filters.type || getPokemonTypes(p).includes(filters.type)) &&
        (!search || displayName(p.name).toLowerCase().includes(search)),
    );
    if (filters.sort === "id") return matches;
    return matches.sort(
      filters.sort === "name"
        ? (a: Pokemon, b: Pokemon) => a.name.localeCompare(b.name)
        : (a: Pokemon, b: Pokemon) =>
            b[filters.sort as StatKey] - a[filters.sort as StatKey],
    );
  }, [inScope, filters]);

  return (
    <section className="flex min-w-0 flex-1 flex-col gap-3">
      <PokedexControls
        filters={filters}
        onChange={(patch) => setFilters({ ...filters, ...patch })}
        showing={visible.length}
        total={inScope.length}
      />
      {pokemon.isPending && (
        <p className="text-sm text-slate-500">Loading the Pokédex…</p>
      )}
      {pokemon.isError && (
        <p className="text-sm text-red-600">Could not load the Pokédex.</p>
      )}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 2xl:grid-cols-8">
        {visible.map((p) => (
          <PokemonCard
            key={p.id}
            pokemon={p}
            disabled={disabled}
            onAdd={onAdd}
          />
        ))}
      </div>
    </section>
  );
}
