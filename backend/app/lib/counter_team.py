"""Counter team generation."""

import random
from collections.abc import Callable, Sequence

from app.models import Pokemon

# chart[attacking][defending]. Missing entries are neutral (1.0).
type TypeMatchupChart = dict[str, dict[str, float]]

SUPER_EFFECTIVE = 2.0

STAT_BAND_START = 0.25
STAT_BAND_STEP = 0.05
MAX_ITERATIONS_UNTIL_RANDOM_PICK = 3

# A metric reduces a Pokemon to one comparable number.
# Can substitute for speed only, attack, any formula using base stats, etc.
# Pass to build_counter_team, no change to the selection logic itself.
StatMetric = Callable[[Pokemon], float]


def base_stat_total(pokemon: Pokemon) -> float:
    """Default StatMetric: sum of the six base stats."""
    return (
        pokemon.hp
        + pokemon.attack
        + pokemon.defense
        + pokemon.special_attack
        + pokemon.special_defense
        + pokemon.speed
    )


def _types(pokemon: Pokemon) -> tuple[str, ...]:
    return (
        (pokemon.type_1,)
        if pokemon.type_2 is None
        else (pokemon.type_1, pokemon.type_2)
    )


def has_type_advantage(
    candidate: Pokemon, opponent: Pokemon, chart: TypeMatchupChart
) -> bool:
    """True if a STAB move of either of the candidate's types is super-effective on opponent.

    TODO: for each of candidate's _types(), multiply chart.get(attacking_type, {}).get(
    defending_type, 1.0) across all of opponent's _types() (missing entries are neutral, 1.0;
    multiplying rather than averaging is what makes 4x/0.25x/immunity work). True if any
    candidate type's multiplier is >= SUPER_EFFECTIVE.
    """
    raise NotImplementedError


def within_stat_band(
    candidate: Pokemon, opponent: Pokemon, metric: StatMetric, band: float
) -> bool:
    """True if candidate's metric is within +/- `band` (e.g. 0.25) of opponent's.

    TODO: compare metric(candidate) to metric(opponent) * (1 +/- band).
    """
    raise NotImplementedError


def _pick_for(
    opponent: Pokemon,
    pool: Sequence[Pokemon],
    chart: TypeMatchupChart,
    rng: random.Random,
    metric: StatMetric,
) -> Pokemon:
    """Select one counter for `opponent` from `pool` (already excludes used picks).

    TODO:
    1. type_pool = [c for c in pool if has_type_advantage(c, opponent, chart)]
    2. band = STAT_BAND_START; up to MAX_BAND_WIDENINGS times: filter type_pool by
       within_stat_band(c, opponent, metric, band); if non-empty, rng.choice() it and stop;
       otherwise band += STAT_BAND_STEP and retry.
    3. Still nothing after all widenings? rng.choice(type_pool) — stat check dropped, type
       advantage kept.
    4. type_pool itself empty? rng.choice(pool) — last resort, guarantees a pick exists.
    """
    raise NotImplementedError


def build_counter_team(
    opposing: Sequence[Pokemon],
    candidates: Sequence[Pokemon],
    chart: TypeMatchupChart,
    rng: random.Random,
    metric: StatMetric = base_stat_total,
) -> list[Pokemon]:
    """One counter per Pokemon in `opposing`, matched slot for slot (by list position). No repeats.

    TODO: for each opponent in opposing, call _pick_for with candidates minus the ids already
    chosen so far, collect into the result list.
    """
    raise NotImplementedError
