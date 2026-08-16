import { useMemo, useState } from "react";

import { usePokemon } from "../api/queries";
import type { Pokemon, StatKey } from "../api/types";
import { getPokemonTypes } from "../lib/pokemon";
import {
  DEFAULT_FILTERS,
  PokedexControls,
  type Filters,
} from "./PokedexControls";
import { PokemonCard } from "./PokemonCard";

/** Variants sit directly under the base form they belong to. */
const byPokedexNumber = (a: Pokemon, b: Pokemon) =>
  a.species_id - b.species_id ||
  Number(b.is_default) - Number(a.is_default) ||
  a.id - b.id;

export function Pokedex({
  disabled,
  onAdd,
}: {
  disabled: boolean;
  onAdd: (p: Pokemon) => void;
}) {
  const pokemon = usePokemon();
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);

  const visible = useMemo(() => {
    const all = pokemon.data ?? [];
    const search = filters.search.trim().toLowerCase();
    const matches = all.filter(
      (p) =>
        (filters.showAlternateForms || p.is_default) &&
        (!filters.type || getPokemonTypes(p).includes(filters.type)) &&
        (!search || p.name.includes(search)),
    );
    const compare =
      filters.sort === "id"
        ? byPokedexNumber
        : filters.sort === "name"
          ? (a: Pokemon, b: Pokemon) => a.name.localeCompare(b.name)
          : // Stats sort highest first — nobody looks for the slowest Pokémon.
            (a: Pokemon, b: Pokemon) =>
              b[filters.sort as StatKey] - a[filters.sort as StatKey];
    return matches.sort(compare);
  }, [pokemon.data, filters]);

  return (
    <section className="flex min-w-0 flex-1 flex-col gap-3">
      <PokedexControls
        filters={filters}
        onChange={(patch) => setFilters({ ...filters, ...patch })}
        showing={visible.length}
        total={pokemon.data?.length ?? 0}
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
