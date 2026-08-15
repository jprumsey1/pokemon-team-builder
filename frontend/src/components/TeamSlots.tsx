import type { TeamMember } from "../api/types";
import { TEAM_SIZE, displayName } from "../lib/pokemon";
import { PokemonSprite } from "./PokemonSprite";

interface Props {
  /** Ordered by `position` — slots below render members[position] directly. */
  members: TeamMember[];
  selected: number | null;
  onSelect: (position: number) => void;
  onRemove: (position: number) => void;
  onMove: (position: number, delta: number) => void;
  disabled: boolean;
}

const control =
  "rounded px-1.5 text-slate-500 enabled:hover:bg-slate-200 disabled:opacity-25";

export function TeamSlots({
  members,
  selected,
  onSelect,
  onRemove,
  onMove,
  disabled,
}: Props) {
  return (
    <ol className="space-y-1">
      {Array.from({ length: TEAM_SIZE }, (_, position) => {
        const member = members[position];
        if (!member) {
          return (
            <li
              key={position}
              className="flex h-11 items-center rounded-md border border-dashed border-slate-300 px-2 text-sm text-slate-400"
            >
              {position + 1}. Empty
            </li>
          );
        }
        return (
          <li
            key={position}
            className={`flex h-11 items-center gap-1 rounded-md border pr-1 ${
              selected === position
                ? "border-slate-900 bg-slate-100"
                : "border-slate-200 bg-white"
            }`}
          >
            <button
              type="button"
              onClick={() => onSelect(position)}
              className="flex min-w-0 grow items-center gap-2 px-2 py-1 text-left"
            >
              <span className="w-3 text-xs text-slate-400">{position + 1}</span>
              <PokemonSprite
                pokemon={member.pokemon}
                size="sm"
                className="shrink-0"
              />
              <span className="truncate text-sm">
                {displayName(member.pokemon.name)}
              </span>
            </button>
            <button
              type="button"
              className={control}
              disabled={disabled || position === 0}
              onClick={() => onMove(position, -1)}
              aria-label={`Move ${displayName(member.pokemon.name)} up`}
            >
              ↑
            </button>
            <button
              type="button"
              className={control}
              disabled={disabled || position === members.length - 1}
              onClick={() => onMove(position, 1)}
              aria-label={`Move ${displayName(member.pokemon.name)} down`}
            >
              ↓
            </button>
            <button
              type="button"
              className={`${control} enabled:hover:text-red-600`}
              disabled={disabled}
              onClick={() => onRemove(position)}
              aria-label={`Remove ${displayName(member.pokemon.name)}`}
            >
              ×
            </button>
          </li>
        );
      })}
    </ol>
  );
}
