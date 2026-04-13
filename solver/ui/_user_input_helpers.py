"""
Private helper functions for Champion objects and user input.

Includes:

- Name normalization and lookup utilities
- Conversion from user input to Champion objects / internal Indicators
- Feedback indicator handling
- Simple presentation helpers (e.g., printing separator lines)
"""
from typing import Sized, TypeAlias
import difflib

from solver.utils.feedback_utils import PROPERTY_TO_INDICATORS_MAPPING, PropertyValue, Indicator
from solver.champ_pipeline.champions import Champion, Champions

DEFAULT_LINE_LEN: int = 100
ChampionLookup: TypeAlias = dict[frozenset[str], Champion]


def _champion_lookup(champions: Champions) -> ChampionLookup:
    """{ {possible names}: Champion object } mapping for consistent lookup."""
    champion_aliases_mapping: ChampionLookup = {}

    for champion in champions:
        champion_aliases_mapping[champion.aliases()] = champion

    return champion_aliases_mapping


def _convert_str_to_champion(user_input: str, lookup: ChampionLookup) -> Champion:
    """Return the Champion object from a champion name."""
    user_choice = user_input.lower().strip()

    if len(user_input) < 2:
        raise ValueError(f"Invalid champion: {user_input!r}")

    for champ_aliases in lookup:
        closest_match = difflib.get_close_matches(
            user_choice, champ_aliases, n=1, cutoff=0.9
        )
        if closest_match:
            # Return the Champion object of the closest match
            return lookup[champ_aliases]

    raise ValueError(f"Invalid champion: {user_input!r}")


def _get_valid_indicator(
        prop_name: str, user_indicator: str, prop_val: PropertyValue
) -> Indicator | None:
    """
    Get a valid string indicator from the user to build a FeedbackPattern with it.
    If `user_indicator` is invalid, return `None` to reprompt the user.
    """
    available_indicators = PROPERTY_TO_INDICATORS_MAPPING.get(prop_name, ())

    for indicator in available_indicators:
        if user_indicator and indicator.startswith(user_indicator):
            if isinstance(prop_val, frozenset) and indicator == "partial":
                if len(prop_val) == 1:
                    indicator = Indicator.PARTIAL_SUBSET
                else:
                    indicator = Indicator.PARTIAL_OVERLAP
            else:
                indicator = Indicator(indicator)
            return indicator
    return None


def _line(char: str = "=", length: int | Sized = DEFAULT_LINE_LEN) -> None:
    """Print a horizontal separator line using a character with a specified length."""
    if isinstance(length, int):
        print(char * length)
    else:
        print(char * len(length))
