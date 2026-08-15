import type { Pokemon } from "../api/types";
import { STATS, displayName, getPokemonTypes } from "../lib/pokemon";
import { PokemonSprite } from "./PokemonSprite";
import { StatBar } from "./StatBar";
import { TypeChip } from "./TypeChip";

interface Props {
  pokemon: Pokemon;
  /** Why this card can't be added, or undefined when it can. */
  disabledReason?: string;
  onAdd: (pokemon: Pokemon) => void;
}

export function PokemonCard({ pokemon, disabledReason, onAdd }: Props) {
  return (
    <button
      type="button"
      disabled={!!disabledReason}
      onClick={() => onAdd(pokemon)}
      title={disabledReason ?? `Add ${displayName(pokemon.name)} to team`}
      className="flex flex-col gap-1 rounded-lg border border-slate-200 bg-white p-2 text-left transition enabled:hover:border-slate-400 enabled:hover:shadow-sm disabled:opacity-40"
    >
      <div className="flex items-center justify-between text-[10px] text-slate-400">
        <span>#{pokemon.id}</span>
        {!pokemon.is_default && <span title="Alternate form">alt</span>}
      </div>
      <PokemonSprite pokemon={pokemon} size="lg" className="mx-auto" />
      <div className="truncate text-sm font-medium text-slate-900">
        {displayName(pokemon.name)}
      </div>
      <div className="flex flex-wrap gap-1">
        {getPokemonTypes(pokemon).map((type) => (
          <TypeChip key={type} type={type} />
        ))}
      </div>
      <div className="space-y-[2px]">
        {STATS.map(({ key, label }) => (
          <StatBar key={key} label={label} value={pokemon[key]} />
        ))}
      </div>
    </button>
  );
}
