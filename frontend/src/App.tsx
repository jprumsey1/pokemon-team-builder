import { useState } from "react";

import { useMe, useSetMembers, useSignOut, useTeams } from "./api/queries";
import { AlertBanner } from "./components/AlertBanner";
import { Pokedex } from "./components/Pokedex";
import { SignIn } from "./components/SignIn";
import { TeamPanel } from "./components/TeamPanel";
import { TEAM_SIZE, getMemberIds } from "./lib/pokemon";

export default function App() {
  const me = useMe();
  const signOut = useSignOut();
  const teams = useTeams();
  const setMembersMutation = useSetMembers();
  const [activeTeamId, setActiveTeamId] = useState<number | null>(null);

  if (me.isPending) return <div className="min-h-dvh bg-slate-100" />;
  if (!me.data) return <SignIn />;

  const all = teams.data ?? [];
  // Falls back to the first team so a deleted or never-chosen active id still lands somewhere.
  const activeTeam =
    all.find((team) => team.id === activeTeamId) ?? all[0] ?? null;
  const memberIds = getMemberIds(activeTeam);

  const setMembers = (pokemonIds: number[]) => {
    if (activeTeam)
      setMembersMutation.mutate({ teamId: activeTeam.id, pokemonIds });
  };

  return (
    <div className="min-h-dvh bg-slate-100">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3">
        <h1 className="font-bold text-slate-900">Pokémon Team Builder</h1>
        <div className="flex items-center gap-3 text-sm">
          <span className="text-slate-600">{me.data.username}</span>
          <button
            className="rounded-md border border-slate-300 px-3 py-1 hover:bg-slate-50"
            onClick={() => signOut.mutate()}
          >
            Sign out
          </button>
        </div>
      </header>

      <AlertBanner userId={me.data.id} />

      <main className="flex flex-col-reverse gap-4 p-4 lg:flex-row">
        <Pokedex
          disabledReason={
            !activeTeam
              ? "Create a team first"
              : memberIds.length >= TEAM_SIZE
                ? "Team is full"
                : setMembersMutation.isPending
                  ? "Saving…"
                  : undefined
          }
          onAdd={(pokemon) => setMembers([...memberIds, pokemon.id])}
        />
        <aside className="lg:w-80 lg:shrink-0">
          <TeamPanel
            // key: a slot index belongs to one team, so switching teams resets it.
            key={activeTeam?.id}
            teams={all}
            activeTeam={activeTeam}
            memberIds={memberIds}
            onSelectTeam={setActiveTeamId}
            onSetMembers={setMembers}
            saving={setMembersMutation.isPending}
          />
        </aside>
      </main>
    </div>
  );
}
