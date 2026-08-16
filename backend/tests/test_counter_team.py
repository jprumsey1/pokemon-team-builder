import random

from app.lib.counter_team import (
    base_stat_total,
    build_counter_team,
    has_type_advantage,
    is_within_stat_band,
)
from app.models import Pokemon
from tests.conftest import make_pokemon

# Only the entries these tests care about. Everything absent is neutral, which is how
# the real chart starts before the sync overwrites from the attacking side.
CHART = {
    "rock": {"fire": 2.0, "flying": 2.0, "water": 1.0, "grass": 1.0, "electric": 1.0},
    "water": {"fire": 2.0, "flying": 1.0, "rock": 1.0, "grass": 0.5, "electric": 1.0},
    "electric": {"fire": 1.0, "flying": 2.0, "rock": 1.0, "grass": 0.5, "water": 2.0},
    "grass": {"fire": 0.5, "flying": 0.5, "rock": 1.0, "electric": 1.0, "water": 2.0},
    "fire": {"fire": 0.5, "flying": 1.0, "water": 0.5, "grass": 2.0, "rock": 0.5},
    "flying": {"fire": 1.0, "flying": 1.0, "water": 1.0, "grass": 2.0, "rock": 0.5},
}


def test_has_type_advantage_true_when_either_candidate_type_is_super_effective():
    # Arrange — dual-typed candidate: water is neutral on fire/flying, but a hidden
    # rock typing would be super-effective on both
    candidate = make_pokemon(1, "candidate", "water", "rock")
    opponent = make_pokemon(2, "opponent", "fire", "flying")

    # Act
    advantage = has_type_advantage(candidate, opponent, CHART)

    # Assert — STAB from the rock half is what qualifies it
    assert advantage is True


def test_has_type_advantage_false_when_neither_type_is_super_effective():
    # Arrange — grass resists fire and flying on both counts
    candidate = make_pokemon(1, "candidate", "grass")
    opponent = make_pokemon(2, "opponent", "fire", "flying")

    # Act
    advantage = has_type_advantage(candidate, opponent, CHART)

    # Assert
    assert advantage is False


def test_within_stat_band_true_when_metric_is_within_the_band():
    # Arrange — candidate's total is 10% below opponent's, inside a 25% band
    candidate = make_pokemon(1, "candidate", "rock", speed=45, attack=54)
    opponent = make_pokemon(2, "opponent", "fire", "flying", speed=45, attack=64)

    # Act
    in_band = is_within_stat_band(candidate, opponent, base_stat_total, 0.25)

    # Assert
    assert in_band is True


def test_within_stat_band_false_when_metric_is_outside_the_band():
    # Arrange — candidate's total is roughly half the opponent's
    candidate = make_pokemon(1, "candidate", "rock", hp=25, attack=25, defense=25)
    opponent = make_pokemon(
        2, "opponent", "fire", "flying", hp=90, attack=90, defense=90
    )

    # Act
    in_band = is_within_stat_band(candidate, opponent, base_stat_total, 0.25)

    # Assert
    assert in_band is False


def test_build_counter_team_returns_one_pick_per_opponent_with_no_repeats():
    # Arrange — two opponents, only one qualifying counter apiece
    opposing = [
        make_pokemon(1, "opponent-fire-flying", "fire", "flying"),
        make_pokemon(2, "opponent-water", "water"),
    ]
    candidates = [
        make_pokemon(10, "rock-counter", "rock"),
        make_pokemon(11, "electric-counter", "electric"),
    ]

    # Act
    picks = build_counter_team(opposing, candidates, CHART, random.Random(0))

    # Assert
    assert len(picks) == len(opposing)
    assert len({pick.id for pick in picks}) == len(picks)
    assert all(isinstance(pick, Pokemon) for pick in picks)


def test_build_counter_team_prefers_a_type_and_stat_matched_candidate():
    # Arrange — against a fire/flying opponent, only the rock candidate qualifies;
    # the grass candidate resists both of the opponent's types and must never be picked
    opposing = [make_pokemon(1, "charizard-like", "fire", "flying")]
    candidates = [
        make_pokemon(10, "rock-counter", "rock"),
        make_pokemon(11, "grass-decoy", "grass"),
    ]

    # Act
    picks = build_counter_team(opposing, candidates, CHART, random.Random(0))

    # Assert
    assert picks[0].id == 10


def test_build_counter_team_widens_the_band_until_a_candidate_qualifies():
    # Arrange — the only type-advantaged candidate sits ~35% below the opponent's total,
    # outside the starting 20% band but inside the band after widening
    opponent = make_pokemon(
        1, "opponent", "fire", "flying", hp=90, attack=90, defense=90
    )
    far_candidate = make_pokemon(
        10, "rock-counter", "rock", hp=60, attack=60, defense=60
    )

    # Act
    picks = build_counter_team([opponent], [far_candidate], CHART, random.Random(0))

    # Assert
    assert picks[0].id == far_candidate.id


def test_build_counter_team_falls_back_to_random_when_no_candidate_is_in_any_band():
    # Arrange — type-advantaged, but nowhere near the opponent's stat total even after
    # 3 widenings (20% -> 35%); must still be picked rather than leaving a slot empty
    opponent = make_pokemon(
        1, "opponent", "fire", "flying", hp=90, attack=90, defense=90
    )
    tiny_candidate = make_pokemon(
        10, "rock-counter", "rock", hp=10, attack=10, defense=10
    )

    # Act
    picks = build_counter_team([opponent], [tiny_candidate], CHART, random.Random(0))

    # Assert
    assert picks[0].id == tiny_candidate.id
