import { useState } from "react";

import { useCreateTeam } from "../api/queries";

export function NewTeamForm({
  onCreated,
}: {
  onCreated: (teamId: number) => void;
}) {
  const [name, setName] = useState("");
  const createTeam = useCreateTeam();

  return (
    <form
      className="flex gap-1"
      onSubmit={(event) => {
        event.preventDefault();
        createTeam.mutate(name.trim(), {
          onSuccess: (team) => {
            setName("");
            onCreated(team.id);
          },
        });
      }}
    >
      <input
        className="field min-w-0 grow"
        placeholder="Team name"
        value={name}
        onChange={(event) => setName(event.target.value)}
        autoFocus
      />
      <button
        type="submit"
        disabled={!name.trim() || createTeam.isPending}
        className="primary-button px-3 py-1.5 text-sm"
      >
        Create
      </button>
    </form>
  );
}
