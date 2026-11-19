from typing import get_args

import pytest

from scoring import MAX_SCORE, PENALTY_LABELS, PENALTY_WEIGHTS, PenaltyType, calculate_score


def test_penalty_type_lists_match():
    assert set(get_args(PenaltyType)) == set(PENALTY_WEIGHTS) == set(PENALTY_LABELS)


def test_no_penalties_is_full_score():
    assert calculate_score([]) == (MAX_SCORE, "No penalties")


def test_each_penalty_deducts_its_weight():
    for ptype, weight in PENALTY_WEIGHTS.items():
        score, _ = calculate_score([ptype])
        assert score == MAX_SCORE - weight


def test_penalties_add_up():
    score, _ = calculate_score(["hard_brake", "hard_brake", "speeding"])
    assert score == MAX_SCORE - 2 * PENALTY_WEIGHTS["hard_brake"] - PENALTY_WEIGHTS["speeding"]


def test_score_never_below_zero():
    score, _ = calculate_score(["phone_use"] * 50)
    assert score == 0


def test_notes_count_and_pluralise():
    _, notes = calculate_score(["hard_brake", "hard_brake", "speeding"])
    assert "2 harsh braking events" in notes
    assert "1 speeding event" in notes


def test_unknown_penalty_type_rejected():
    with pytest.raises(ValueError):
        calculate_score(["texting_while_parked"])
