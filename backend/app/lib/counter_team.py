"""Counter team generation.

Given an opposing team, pick one counter for each of its members.

Each opponent is handled independently, in order:
1. Create a candidate pool of type-advantaged Pokemon. A candidate qualifies if one of
   its types deals at least 2x damage to the opponent.
2. Narrow that pool to candidates of comparable "strength" is within +/- 20% of the opponent's.
   If nobody qualifies, widen the band by 5% and retry (up to three times total).
3. If nobody qualifies, choose randomly from the pool of type-advantaged Pokemon.
4. If nobody qualifies even after the random pick, choose randomly from the entire candidate pool.

Duplicates are not allowed, and a Pokemon cannot oppose itself.

"Strength" is whatever the caller's StatMetric measures. Base stat total by default,
or speed, bulk, and so on. Callers select one by name (see STAT_METRICS).

Randomness comes from an injected `random.Random` so tests can seed it. Otherwise, the
same team may produce different results on each call.
"""

import random
from collections.abc import Callable, Sequence
from typing import Literal

from app.models import Pokemon

# chart[attacking][defending]. Missing entries are neutral (1.0).
type TypeMatchupChart = dict[str, dict[str, float]]

SUPER_EFFECTIVE = 2.0

STAT_BAND_START = 0.20
STAT_BAND_STEP = 0.05
MAX_ITERATIONS_UNTIL_RANDOM_PICK = 3

# A metric reduces a Pokemon to one comparable number.
# Can substitute for speed only, attack, or any formula
StatMetric = Callable[[Pokemon], float]

# StatMetric implementations:


def base_stat_total(pokemon: Pokemon) -> float:
    return (
        pokemon.hp
        + pokemon.attack
        + pokemon.defense
        + pokemon.special_attack
        + pokemon.special_defense
        + pokemon.speed
    )


def offensive_stats(pokemon: Pokemon) -> float:
    return max(pokemon.attack, pokemon.special_attack)


def speed(pokemon: Pokemon) -> float:
    return pokemon.speed


def defensive_stats(pokemon: Pokemon) -> float:
    return max(pokemon.defense, pokemon.special_defense)


def physical_bulk(pokemon: Pokemon) -> float:
    return pokemon.defense * pokemon.hp


# Client-selectable StatMetric formulas. Names are the wire format.
StatMetricName = Literal[
    "base_stat_total", "offensive_stats", "speed", "defensive_stats", "physical_bulk"
]

STAT_METRICS: dict[StatMetricName, StatMetric] = {
    "base_stat_total": base_stat_total,
    "offensive_stats": offensive_stats,
    "speed": speed,
    "defensive_stats": defensive_stats,
    "physical_bulk": physical_bulk,
}


def _get_types(pokemon: Pokemon) -> tuple[str, ...]:
    return (
        (pokemon.type_1,)
        if pokemon.type_2 is None
        else (pokemon.type_1, pokemon.type_2)
    )


def has_type_advantage(
    candidate: Pokemon, opponent: Pokemon, type_matchup_chart: TypeMatchupChart
) -> bool:
    """True if a move of either of the candidate's types is super-effective on opponent.

    Each per-type factor is one of 0 (immune), 0.5 (resistant), 1.0 (neutral),
    or 2.0 (super-effective) and the final damage multiplier is the product of these.
    """
    for candidate_type in _get_types(candidate):
        damage_multiplier = 1.0
        for opposing_type in _get_types(opponent):
            damage_multiplier *= type_matchup_chart.get(candidate_type, {}).get(
                opposing_type, 1.0
            )
        if damage_multiplier >= SUPER_EFFECTIVE:
            return True
    return False


def is_within_stat_band(
    candidate: Pokemon, opponent: Pokemon, stat_metric: StatMetric, band: float
) -> bool:
    """True if candidate's metric is within +/- `band` (e.g. 0.25) of opponent's."""
    return abs(stat_metric(candidate) - stat_metric(opponent)) <= band * stat_metric(
        opponent
    )


def _get_counter_pokemon(
    opponent: Pokemon,
    candidates: Sequence[Pokemon],
    type_matchup_chart: TypeMatchupChart,
    rng: random.Random,
    stat_metric: StatMetric,
) -> Pokemon:
    """Select one counter for `opponent` from `candidates` (already excludes used picks)."""
    # Filter candidates by type advantage first, then iteratively by stat band
    candidates_with_type_advantage = [
        c
        for c in candidates
        if has_type_advantage(c, opponent, type_matchup_chart) and c.id != opponent.id
    ]
    band = STAT_BAND_START
    for _ in range(MAX_ITERATIONS_UNTIL_RANDOM_PICK):
        candidates_within_stat_band = [
            c
            for c in candidates_with_type_advantage
            if is_within_stat_band(c, opponent, stat_metric, band)
        ]
        if candidates_within_stat_band:
            return rng.choice(candidates_within_stat_band)
        band += STAT_BAND_STEP
    # If we reach here, no candidates were within the stat band in any iteration
    if candidates_with_type_advantage:
        return rng.choice(candidates_with_type_advantage)
    # Otherwise, fall back to a random candidate
    return rng.choice(candidates)


def build_counter_team(
    opposing: Sequence[Pokemon],
    candidates: Sequence[Pokemon],
    chart: TypeMatchupChart,
    rng: random.Random,
    stat_metric: StatMetricName = "base_stat_total",
) -> list[Pokemon]:
    """Retrieve a counter Pokemon for each in `opposing`, with no repeats."""
    picks: list[Pokemon] = []
    chosen_ids: set[int] = set()
    for opponent in opposing:
        pool = [c for c in candidates if c.id not in chosen_ids]
        pick = _get_counter_pokemon(
            opponent, pool, chart, rng, STAT_METRICS[stat_metric]
        )
        picks.append(pick)
        chosen_ids.add(pick.id)
    return picks
