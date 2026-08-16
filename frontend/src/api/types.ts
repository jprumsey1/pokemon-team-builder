/** Mirrors backend/app/schemas.py */

export type StatKey =
  "hp" | "attack" | "defense" | "special_attack" | "special_defense" | "speed";

/** Mirrors StatMetricName in backend/app/lib/counter_team.py */
export type StatMetricName =
  | "base_stat_total"
  | "offensive_stats"
  | "speed"
  | "defensive_stats"
  | "physical_bulk";

export interface Pokemon {
  id: number;
  name: string;
  species_id: number;
  is_default: boolean;
  type_1: string;
  type_2: string | null;
  hp: number;
  attack: number;
  defense: number;
  special_attack: number;
  special_defense: number;
  speed: number;
  sprite_url: string | null;
}

export interface User {
  id: number;
  username: string;
}

export interface TeamMember {
  position: number;
  pokemon: Pokemon;
}

export interface Team {
  id: number;
  name: string;
  members: TeamMember[];
}

export interface Change {
  field: string;
  from: string | number | null;
  to: string | number | null;
}

export interface Alert {
  pokemon: Pick<Pokemon, "id" | "name" | "sprite_url">;
  detected_at: string;
  changes: Change[];
}
