"""
Internal helpers for user feedbacks and LoLdle indicators.
"""
from numpy import integer

from typing import TypeAlias, NamedTuple
from enum import StrEnum, auto

PropertyValue: TypeAlias = frozenset[str] | str | int | integer

class FeedbackPattern(NamedTuple):
    name: Indicator
    positions: Indicator
    species: Indicator
    resource: Indicator
    range_type: Indicator
    regions: Indicator
    release_year: Indicator


PROPERTY_TO_INDICATORS_MAPPING: dict[str, tuple[str, ...]] = {
    "release_year": ("correct", "higher", "lower"),
    "gender": ("correct", "incorrect"),
    "resource": ("correct", "incorrect", "wrong"),
    "positions": ("correct", "incorrect", "partial"),
    "species": ("correct", "incorrect", "partial"),
    "range_type": ("correct", "incorrect", "partial"),
    "regions": ("correct", "incorrect", "partial"),
}


class Indicator(StrEnum):
    """Indicators used internally to signal correctness for each property."""
    CORRECT = auto()
    INCORRECT = auto()

    # For Release year
    HIGHER = auto()
    LOWER = auto()

    # Partial feedbacks
    PARTIAL_SUBSET = auto()  # Guess property size = 1, means Guess is a subset of Target
    PARTIAL_OVERLAP = auto()  # Target either overlaps, or is a subset of Guess (can't know for sure)
