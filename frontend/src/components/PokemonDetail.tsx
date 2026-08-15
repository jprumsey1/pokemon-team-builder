import type { Pokemon } from "../api/types";
import { STATS, displayName, getPokemonTypes } from "../lib/pokemon";
import { PokemonSprite } from "./PokemonSprite";
import { StatBar } from "./StatBar";
import { TypeChip } from "./TypeChip";

export function PokemonDetail({ pokemon }: { pokemon: Pokemon }) {
  return (
    <div className="space-y-3 border-t border-slate-200 pt-3">
      <div className="flex items-center gap-2">
        <PokemonSprite pokemon={pokemon} size="md" />
        <div className="min-w-0">
          <div className="truncate font-semibold text-slate-900">
            {displayName(pokemon.name)}
          </div>
          <div className="flex gap-1">
            {getPokemonTypes(pokemon).map((type) => (
              <TypeChip key={type} type={type} />
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-1">
        {STATS.map(({ key, label }) => (
          <StatBar key={key} label={label} value={pokemon[key]} showLabel />
        ))}
      </div>
    </div>
  );
}
