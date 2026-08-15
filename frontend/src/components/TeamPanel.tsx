import { useState } from "react";

import { useDeleteTeam, useRenameTeam } from "../api/queries";
import type { Team } from "../api/types";
import { field } from "../lib/styles";
import { getMembers } from "../lib/pokemon";
import { NewTeamForm } from "./NewTeamForm";
import { PokemonDetail } from "./PokemonDetail";
import { TeamSlots } from "./TeamSlots";

interface Props {
  teams: Team[];
  activeTeam: Team | null;
  memberIds: number[];
  onSelectTeam: (teamId: number) => void;
  onSetMembers: (pokemonIds: number[]) => void;
  saving: boolean;
}

export function TeamPanel({
  teams,
  activeTeam,
  memberIds,
  onSelectTeam,
  onSetMembers,
  saving,
}: Props) {
  const [creating, setCreating] = useState(false);
  // A slot index only means anything against the team it was picked in, so it lives
  // beside the roster and resets with it.
  const [selectedSlot, setSelectedSlot] = useState<number | null>(null);
  const renameTeam = useRenameTeam();
  const deleteTeam = useDeleteTeam();
  const members = getMembers(activeTeam);

  if (teams.length === 0) {
    return (
      <div className="space-y-2 rounded-xl bg-white p-4 shadow-sm">
        <h2 className="font-semibold text-slate-900">Create your first team</h2>
        <NewTeamForm onCreated={onSelectTeam} />
      </div>
    );
  }

  return (
    <div className="space-y-3 rounded-xl bg-white p-4 shadow-sm">
      <div className="flex gap-1">
        <select
          className={`${field} min-w-0 grow`}
          value={activeTeam?.id ?? ""}
          onChange={(event) => onSelectTeam(Number(event.target.value))}
          aria-label="Active team"
        >
          {teams.map((team) => (
            <option key={team.id} value={team.id}>
              {team.name}
            </option>
          ))}
        </select>
        <button
          type="button"
          className="rounded-md border border-slate-300 px-2.5 text-sm hover:bg-slate-50"
          onClick={() => setCreating(!creating)}
          aria-label="New team"
        >
          ＋
        </button>
      </div>

      {creating && (
        <NewTeamForm
          onCreated={(teamId) => {
            setCreating(false);
            onSelectTeam(teamId);
          }}
        />
      )}

      {activeTeam && (
        <>
          <div className="flex gap-1">
            <input
              // key: remount on team change, or the input keeps the previous team's name.
              key={activeTeam.id}
              className="min-w-0 grow rounded-md border border-transparent px-2 py-1 font-semibold text-slate-900 hover:border-slate-300 focus:border-slate-900 focus:outline-none"
              defaultValue={activeTeam.name}
              aria-label="Team name"
              onBlur={(event) => {
                const name = event.target.value.trim();
                if (!name) {
                  event.target.value = activeTeam.name;
                  return;
                }
                if (name !== activeTeam.name) {
                  renameTeam.mutate({ teamId: activeTeam.id, name });
                }
              }}
            />
            <button
              type="button"
              className="rounded-md px-2 text-slate-400 hover:bg-slate-100 hover:text-red-600"
              aria-label={`Delete ${activeTeam.name}`}
              onClick={() => {
                if (confirm(`Delete "${activeTeam.name}"?`))
                  deleteTeam.mutate(activeTeam.id);
              }}
            >
              🗑
            </button>
          </div>

          <TeamSlots
            members={members}
            selected={selectedSlot}
            onSelect={setSelectedSlot}
            disabled={saving}
            onRemove={(position) => {
              onSetMembers(memberIds.filter((_, index) => index !== position));
              if (selectedSlot === position) setSelectedSlot(null);
              else if (selectedSlot !== null && selectedSlot > position)
                setSelectedSlot(selectedSlot - 1);
            }}
            onMove={(position, delta) => {
              const other = position + delta;
              const next = [...memberIds];
              [next[position], next[other]] = [next[other], next[position]];
              onSetMembers(next);
              if (selectedSlot === position) setSelectedSlot(other);
              else if (selectedSlot === other) setSelectedSlot(position);
            }}
          />

          {selectedSlot !== null && members[selectedSlot] ? (
            <PokemonDetail pokemon={members[selectedSlot].pokemon} />
          ) : (
            <p className="border-t border-slate-200 pt-3 text-xs text-slate-400">
              Select a Pokémon to see its stats.
            </p>
          )}
        </>
      )}
    </div>
  );
}
