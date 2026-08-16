import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import * as api from "./client";
import type { StatMetricName } from "./types";

export const useMe = () =>
  // retry: false, or three retries of a 401 hold the sign-in form back.
  useQuery({ queryKey: ["me"], queryFn: api.getMe, retry: false });

export const usePokemon = () =>
  useQuery({
    queryKey: ["pokemon"],
    queryFn: api.getPokemon,
    staleTime: Infinity,
  });

export function useTeams() {
  // Teams depend on user logged in
  const me = useMe();
  return useQuery({
    queryKey: ["teams"],
    queryFn: api.getTeams,
    enabled: !!me.data,
  });
}

export const useAlerts = () =>
  useQuery({ queryKey: ["alerts"], queryFn: api.getAlerts });

export function useSignIn() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: api.signIn,
    // SignIn renders its own failure, so skip the global mutation alert.
    meta: { handled: true },
    onSuccess: () => client.invalidateQueries(),
  });
}

export function useSignOut() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: api.signOut,
    // clear() on sign out so new user does not see the previous user's data
    onSuccess: () => client.clear(),
  });
}

/** Every team write invalidates alerts and teams. The team roster is what decides who is alerted. */
function useTeamMutation<TArgs, TResult>(
  mutationFn: (args: TArgs) => Promise<TResult>,
) {
  const client = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["teams"] });
      client.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
}

export const useCreateTeam = () => useTeamMutation(api.createTeam);

export const useRenameTeam = () =>
  useTeamMutation(({ teamId, name }: { teamId: number; name: string }) =>
    api.renameTeam(teamId, name),
  );

export const useDeleteTeam = () => useTeamMutation(api.deleteTeam);

export const useSetTeamMembers = () =>
  useTeamMutation(
    ({ teamId, pokemonIds }: { teamId: number; pokemonIds: number[] }) =>
      api.setTeamMembers(teamId, pokemonIds),
  );

export const useCounterTeam = () =>
  useMutation({
    mutationFn: ({
      teamId,
      statMetric,
    }: {
      teamId: number;
      statMetric: StatMetricName;
    }) => api.counterTeam(teamId, statMetric),
    meta: { handled: true },
  });
