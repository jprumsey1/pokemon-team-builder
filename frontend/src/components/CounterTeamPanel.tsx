import { useState } from "react";

import { useCounterTeam } from "../api/queries";
import type { StatMetricName } from "../api/types";
import { displayName } from "../lib/pokemon";
import { PokemonDetail } from "./PokemonDetail";
import { PokemonSprite } from "./PokemonSprite";

// Names must match StatMetricName in backend/app/lib/counter_team.py.
const STAT_METRICS = {
  base_stat_total: {
    label: "Base Stat Total",
    description: "Sum of all six base stats.",
  },
  offensive_stats: {
    label: "Offensive Stats",
    description: "Higher of Attack and Special Attack.",
  },
  speed: { label: "Speed", description: "Speed only." },
  defensive_stats: {
    label: "Defensive Stats",
    description: "Higher of Defense and Special Defense.",
  },
  physical_bulk: {
    label: "Physical Bulk",
    description: "Defense multiplied by HP.",
  },
} satisfies Record<StatMetricName, { label: string; description: string }>;

const STAT_METRIC_NAMES = Object.keys(STAT_METRICS) as StatMetricName[];

interface Props {
  teamId: number;
  disabled: boolean;
}

export function CounterTeamPanel({ teamId, disabled }: Props) {
  const [statMetric, setStatMetric] = useState<StatMetricName>("base_stat_total");
  const [selected, setSelected] = useState<number | null>(null);
  const counterTeam = useCounterTeam();
  const selectedPick = counterTeam.data?.find(
    (member) => member.position === selected,
  );

  return (
    <div className="space-y-3 rounded-xl bg-white p-4 shadow-sm">
      <h2 className="font-semibold text-slate-900">Generate Counter Team</h2>

      <div className="space-y-1">
        {/* Own tooltip rather than `title`: native ones are slow, tiny to hit,
            and never appear on touch. Anchored to the row, not the icon, or it
            overflows the 320px panel and the aside clips it. opacity (not
            hidden) keeps the text in the a11y tree for aria-describedby. */}
        <div className="relative flex items-center gap-1">
          <label
            className="text-sm font-medium text-slate-700"
            htmlFor="stat-metric"
          >
            Select Matchups By:
          </label>
          <span aria-hidden="true" className="peer cursor-help text-slate-400">
            ⓘ
          </span>
          <span
            id="stat-metric-description"
            role="tooltip"
            className="pointer-events-none absolute top-full left-0 z-10 mt-1 w-56 rounded-md bg-slate-900 px-2 py-1 text-xs font-normal text-white opacity-0 transition-opacity peer-hover:opacity-100"
          >
            {STAT_METRICS[statMetric].description}
          </span>
        </div>
        <select
          id="stat-metric"
          aria-describedby="stat-metric-description"
          className="field w-full"
          value={statMetric}
          onChange={(event) =>
            setStatMetric(event.target.value as StatMetricName)
          }
        >
          {STAT_METRIC_NAMES.map((name) => (
            <option key={name} value={name}>
              {STAT_METRICS[name].label}
            </option>
          ))}
        </select>
      </div>

      <button
        type="button"
        className="primary-button w-full py-2 font-medium"
        disabled={disabled || counterTeam.isPending}
        onClick={() => {
          setSelected(null);
          counterTeam.mutate({ teamId, statMetric });
        }}
      >
        {counterTeam.isPending ? "Generating…" : "Generate"}
      </button>

      {counterTeam.isError && (
        <p className="text-sm text-red-600">{counterTeam.error.message}</p>
      )}

      {counterTeam.data && (
        <>
          <ol className="space-y-1">
            {counterTeam.data.map((member) => (
              <li key={member.position}>
                <button
                  type="button"
                  onClick={() => setSelected(member.position)}
                  className={`flex h-11 w-full items-center gap-2 rounded-md border px-2 text-left ${
                    selected === member.position
                      ? "border-slate-900 bg-slate-100"
                      : "border-slate-200 bg-white"
                  }`}
                >
                  <span className="w-3 text-xs text-slate-400">
                    {member.position + 1}
                  </span>
                  <PokemonSprite
                    pokemon={member.pokemon}
                    size="sm"
                    className="shrink-0"
                  />
                  <span className="truncate text-sm">
                    {displayName(member.pokemon.name)}
                  </span>
                </button>
              </li>
            ))}
          </ol>

          {selectedPick && <PokemonDetail pokemon={selectedPick.pokemon} />}
        </>
      )}

      <details className="border-t border-slate-200 pt-3">
        <summary className="cursor-pointer text-xs font-medium text-slate-500">
          How does this work?
        </summary>
        <p className="mt-2 text-xs text-slate-500">
          For each Pokémon on the team, we pick a counter that has a{" "}
          <a
            href="https://pokemondb.net/type"
            target="_blank"
            className="underline"
          >
            type advantage
          </a>{" "}
          and has similar strength based on the stat formula selected above.
        </p>
        <ul className="mt-2 list-disc space-y-1 pl-4 text-xs text-slate-500">
          <li>
            From every Pokémon with a type advantage, we pick one at random whose stat value is within 20% of the opponent's value.
          </li>
          <li>If none are that close, we widen the range to 25%, then 30%</li>
          <li>If still none, we pick any Pokémon with a type advantage at random</li>
          <li>If nothing has a type advantage, we pick any at random</li>
          <li>
            A Pokémon has a type advantage if <em>one</em> of its types deals at
            least 2× damage to the opponent, counting both of the opponent's types
            together. We only look at what the counter does to the opponent, not the other
            way around.
          </li>
          <li>No Pokémon is picked twice and a Pokémon cannot counter itself</li>
        </ul>
      </details>
    </div>
  );
}
