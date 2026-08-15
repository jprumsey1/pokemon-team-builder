import type { Pokemon, StatKey, Team } from "../api/types";

export const STATS: { key: StatKey; label: string; short: string }[] = [
  { key: "hp", label: "HP", short: "HP" },
  { key: "attack", label: "Attack", short: "Atk" },
  { key: "defense", label: "Defense", short: "Def" },
  { key: "special_attack", label: "Sp. Attack", short: "SpA" },
  { key: "special_defense", label: "Sp. Defense", short: "SpD" },
  { key: "speed", label: "Speed", short: "Spe" },
];

/** Blissey's 255 HP is the highest base stat in the games, so bars scale against it. */
export const MAX_STAT = 255;

export const TEAM_SIZE = 6;

export const TYPES = [
  "normal",
  "fire",
  "water",
  "electric",
  "grass",
  "ice",
  "fighting",
  "poison",
  "ground",
  "flying",
  "psychic",
  "bug",
  "rock",
  "ghost",
  "dragon",
  "dark",
  "steel",
  "fairy",
];

export const TYPE_COLORS: Record<string, string> = {
  normal: "#A8A77A",
  fire: "#EE8130",
  water: "#6390F0",
  electric: "#F7D02C",
  grass: "#7AC74C",
  ice: "#96D9D6",
  fighting: "#C22E28",
  poison: "#A33EA1",
  ground: "#E2BF65",
  flying: "#A98FF3",
  psychic: "#F95587",
  bug: "#A6B91A",
  rock: "#B6A136",
  ghost: "#735797",
  dragon: "#6F35FC",
  dark: "#705746",
  steel: "#B7B7CE",
  fairy: "#D685AD",
};

/** `charizard-mega-x` → `Charizard Mega X` */
export const displayName = (name: string) =>
  name
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

export const getPokemonTypes = (pokemon: Pokemon) =>
  pokemon.type_2 ? [pokemon.type_1, pokemon.type_2] : [pokemon.type_1];

/** The API returns members ordered by `position`; this is the single source of that order. */
export const getMembers = (team: Team | null) => team?.members ?? [];

export const getMemberIds = (team: Team | null) =>
  getMembers(team).map((member) => member.pokemon.id);
