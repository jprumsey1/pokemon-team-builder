import { useState } from "react";

import { useMe, useSetTeamMembers, useSignOut, useTeams } from "./api/queries";
import { AlertBanner } from "./components/AlertBanner";
import { CounterTeamPanel } from "./components/CounterTeamPanel";
import { Pokedex } from "./components/Pokedex";
import { SignIn } from "./components/SignIn";
import { TeamPanel } from "./components/TeamPanel";
import { TEAM_SIZE } from "./lib/pokemon";

export default function App() {
  const me = useMe();
  const signOut = useSignOut();
  const teams = useTeams();
  const setMembersMutation = useSetTeamMembers();
  const [activeTeamId, setActiveTeamId] = useState<number | null>(null);

  if (me.isPending) return <div className="min-h-dvh bg-slate-100" />;
  if (!me.data) return <SignIn />;

  const allTeams = teams.data ?? [];
  // Falls back to the first team
  const activeTeam =
    allTeams.find((team) => team.id === activeTeamId) ?? allTeams[0] ?? null;
  const memberIds = (activeTeam?.members ?? []).map((m) => m.pokemon.id);

  const setMembers = (pokemonIds: number[]) => {
    if (activeTeam)
      setMembersMutation.mutate({ teamId: activeTeam.id, pokemonIds });
  };

  return (
    <div id="top" className="min-h-dvh bg-slate-100">
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
          disabled={
            !activeTeam ||
            memberIds.length >= TEAM_SIZE ||
            setMembersMutation.isPending
          }
          onAdd={(pokemon) => setMembers([...memberIds, pokemon.id])}
        />
        <aside className="space-y-4 lg:sticky lg:top-4 lg:max-h-[calc(100dvh-2rem)] lg:w-80 lg:shrink-0 lg:self-start lg:overflow-y-auto">
          <TeamPanel
            // a slot index belongs to one team, so switching teams resets key
            key={`team-${activeTeam?.id}`}
            teams={allTeams}
            activeTeam={activeTeam}
            memberIds={memberIds}
            onSelectTeam={setActiveTeamId}
            onSetMembers={setMembers}
            saving={setMembersMutation.isPending}
          />
          {activeTeam && (
            <CounterTeamPanel
              key={`counter-${activeTeam.id}`}
              teamId={activeTeam.id}
              disabled={memberIds.length === 0}
            />
          )}
        </aside>
      </main>

      <footer className="border-t border-slate-200 px-4 py-6 text-center text-xs text-slate-500">
        Pokémon data from{" "}
        <a
          className="underline"
          href="https://pokeapi.co/"
          target="_blank"
        >
          PokéAPI
        </a>.
        Pokémon and Pokémon character names are trademarks of Nintendo.
      </footer>

      <a
        href="#top"
        aria-label="Back to top"
        className="fixed right-4 bottom-4 rounded-full border border-slate-300 bg-white px-3 py-2 text-sm shadow-md hover:bg-slate-50"
      >
        ↑ Top
      </a>
    </div>
  );
}
