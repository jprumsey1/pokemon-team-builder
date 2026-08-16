import type {
  Alert,
  Pokemon,
  StatMetricName,
  Team,
  TeamMember,
  User,
} from "./types";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    headers: init?.body ? { "Content-Type": "application/json" } : undefined,
    ...init,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message = typeof body?.detail === "string" ? body.detail : response.statusText;
    throw new ApiError(response.status, message);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

const body = (value: unknown) => ({ body: JSON.stringify(value) });

export const signIn = (username: string) =>
  request<User>("/session", { method: "POST", ...body({ username }) });

export const signOut = () => request<void>("/session", { method: "DELETE" });

export const getMe = () => request<User>("/session/me");

export const getPokemon = () => request<Pokemon[]>("/pokemon");

export const getTeams = () => request<Team[]>("/teams");

export const createTeam = (name: string) =>
  request<Team>("/teams", { method: "POST", ...body({ name }) });

export const renameTeam = (teamId: number, name: string) =>
  request<Team>(`/teams/${teamId}`, { method: "PATCH", ...body({ name }) });

export const deleteTeam = (teamId: number) =>
  request<void>(`/teams/${teamId}`, { method: "DELETE" });

export const setTeamMembers = (teamId: number, pokemonIds: number[]) =>
  request<Team>(`/teams/${teamId}/members`, {
    method: "PUT",
    ...body({ pokemon_ids: pokemonIds }),
  });

export const counterTeam = (teamId: number, statMetric: StatMetricName) =>
  request<TeamMember[]>(
    `/teams/${teamId}/counter?stat_metric=${statMetric}`,
    { method: "POST" },
  );

export const getAlerts = () => request<Alert[]>("/teams/alerts");
