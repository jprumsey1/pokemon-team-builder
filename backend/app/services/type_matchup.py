"""The type chart: what beats what. Pure: no session, no I/O."""

from collections.abc import Sequence

# chart[attacking][defending]. Missing entries are neutral (1.0).
type TypeMatchupChart = dict[str, dict[str, float]]

NEUTRAL = 1.0


def get_damage_multiplier(
    attacking_type: str, defending_types: Sequence[str], chart: TypeMatchupChart
) -> float:
    """Given attacking type and one or more defending types, return multiplier.

    Multiplying is what makes 4x and 0.25x possible, and what lets an immunity absorb
    everything else: Ground on a Flying/Steel defender is 0 x 2, not 1.
    """
    multiplier = NEUTRAL
    for defending_type in defending_types:
        multiplier *= chart.get(attacking_type, {}).get(defending_type, NEUTRAL)
    return multiplier
