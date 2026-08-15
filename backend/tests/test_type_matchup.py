from app.services.type_matchup import get_damage_multiplier

# A cut-down chart: only the entries these tests care about. Everything absent is neutral,
# which is how the real chart starts before the sync overwrites from the attacking side.
CHART = {
    "rock": {"fire": 2.0, "flying": 2.0, "water": 1.0, "grass": 1.0, "ground": 1.0},
    "water": {"fire": 2.0, "flying": 1.0, "rock": 2.0, "grass": 0.5, "ground": 2.0},
    "grass": {"fire": 0.5, "flying": 0.5, "water": 2.0, "rock": 2.0, "ground": 2.0},
    "ground": {"fire": 2.0, "flying": 0.0, "water": 1.0, "grass": 1.0, "rock": 2.0},
    "fire": {"fire": 0.5, "flying": 1.0, "water": 0.5, "grass": 2.0, "rock": 0.5},
    "flying": {"fire": 1.0, "flying": 1.0, "water": 1.0, "grass": 2.0, "rock": 0.5},
}


def test_get_damage_multiplier_stacks_across_both_defending_types():
    # Arrange — rock is 2x on fire and 2x on flying

    # Act
    multiplier = get_damage_multiplier("rock", ("fire", "flying"), CHART)

    # Assert — multiplied, not averaged: this is where 4x comes from
    assert multiplier == 4.0


def test_get_damage_multiplier_stacks_resistances_the_same_way():
    # Arrange — grass is 0.5x on fire and 0.5x on flying

    # Act
    multiplier = get_damage_multiplier("grass", ("fire", "flying"), CHART)

    # Assert
    assert multiplier == 0.25


def test_get_damage_multiplier_cancels_a_weakness_against_a_resistance():
    # Arrange — water is 2x on fire but 0.5x on grass

    # Act
    multiplier = get_damage_multiplier("water", ("fire", "grass"), CHART)

    # Assert — back to neutral, so it is neither a weakness nor a resistance
    assert multiplier == 1.0


def test_get_damage_multiplier_lets_an_immunity_absorb_the_other_type():
    # Arrange — ground is 2x on fire but 0x on flying

    # Act
    multiplier = get_damage_multiplier("ground", ("fire", "flying"), CHART)

    # Assert — 0 x 2, not 1: a Flying type takes no Ground damage at all
    assert multiplier == 0.0
