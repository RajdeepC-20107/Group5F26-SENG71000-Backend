"""Driving score calculation, done on the backend so the Android and iOS apps
always get the same result for the same drive.

The app detects penalty events from the phone's sensors and uploads them; this
module turns those events into a 0-100 score and short scoring notes.

PLACEHOLDER WEIGHTS: the penalty types and point deductions below are a first
draft for the team to agree on. Change them here and nowhere else.
"""

from collections import Counter
from typing import Iterable, Literal

MAX_SCORE = 100
MIN_SCORE = 0

# Penalty types the app may send. Keep in sync with PENALTY_WEIGHTS and PENALTY_LABELS
# (tests/test_scoring.py checks this).
PenaltyType = Literal["hard_brake", "hard_acceleration", "sharp_turn", "speeding", "phone_use"]

# Points taken off the score for each event of a given type
PENALTY_WEIGHTS: dict[str, int] = {
    "hard_brake": 5,
    "hard_acceleration": 5,
    "sharp_turn": 4,
    "speeding": 8,
    "phone_use": 10,
}

# Wording used in the scoring notes, as (singular, plural)
PENALTY_LABELS = {
    "hard_brake": ("harsh braking event", "harsh braking events"),
    "hard_acceleration": ("hard acceleration", "hard accelerations"),
    "sharp_turn": ("sharp turn", "sharp turns"),
    "speeding": ("speeding event", "speeding events"),
    "phone_use": ("phone use event", "phone use events"),
}


def calculate_score(penalty_types: Iterable[str]) -> tuple[int, str]:
    """Return (score, scoring_notes) for a drive with the given penalty events."""
    counts = Counter(penalty_types)

    unknown = set(counts) - set(PENALTY_WEIGHTS)
    if unknown:
        raise ValueError(f"Unknown penalty type(s): {', '.join(sorted(unknown))}")

    deduction = sum(PENALTY_WEIGHTS[ptype] * n for ptype, n in counts.items())
    score = max(MIN_SCORE, MAX_SCORE - deduction)

    if not counts:
        return score, "No penalties"

    parts = []
    # Biggest deductions first so the notes lead with what cost the most
    for ptype, n in sorted(counts.items(), key=lambda kv: -PENALTY_WEIGHTS[kv[0]] * kv[1]):
        singular, plural = PENALTY_LABELS[ptype]
        parts.append(f"{n} {singular if n == 1 else plural}")
    return score, ", ".join(parts)
