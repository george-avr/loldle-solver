"""
Console-based helper utilities for the Loldle solver, including user input handling,
feedback collection, and result display formatting.
"""
import pandas as pd

from solver.champ_pipeline.champions import Champion, Champions
from solver.utils.feedback_utils import FeedbackPattern, Indicator
from solver.ui._user_input_helpers import (
    _convert_str_to_champion,
    _champion_lookup,
    _get_valid_indicator,
    _line,
)


def show_top_results(df: pd.DataFrame,
                     *, is_first_guess: bool, top: int) -> None:
    """Display the top guesses sorted by entropy and expected remaining champions."""
    if top < 1:
        raise ValueError(f"Expected a positive number, got {top}.")

    bits_col, remain_col = df.columns

    if is_first_guess:
        # Firstly sort by entropy
        df_sorted = df.sort_values(by=[bits_col, remain_col], ascending=False).head(top)
        print(f"\nTop {top} most informative guesses today:")
    else:
        # Then sort by expected size (break ties with entropy)
        df_sorted = df.sort_values(by=[remain_col, bits_col]).head(top)
        print(f"The next top {top} most informative guesses are:")

    col_width = 30
    name_width = col_width - 8

    _line("=")
    print(f"{'Champion Name':<{name_width}}| "
          f"{'Information (bits)':<{col_width}}| "
          "Expected Remaining Champions")
    _line("-")

    for i, (name, row) in enumerate(df_sorted.iterrows(), start=1):
        name = f"{i}) {name}"
        bits = row[bits_col]
        remain = row[remain_col]

        print(f"{name:<{name_width}}| {bits:<{col_width}}| {remain}")

    _line("-")


def input_champion(from_choices: Champions) -> Champion:
    """Get a valid Champion object from the user's input."""
    user_guess = input("Type any champion to continue: ")
    lookup = _champion_lookup(from_choices)

    try:
        return _convert_str_to_champion(user_guess, lookup)
    except ValueError:
        print(f"Invalid champion {user_guess!r}")
        return input_champion(from_choices)


def input_feedback(guess: Champion) -> FeedbackPattern:
    """
    Build a FeedbackPattern object used to filter incompatible patterns.

    This function builds a pattern based on the user feedback for each
    property (whether correct, incorrect, partial, etc.). It handles
    both scalar and set properties.

    Args:
        guess (Champion): The champion the user guessed.

    Returns:
        FeedbackPattern: A tuple representing the feedback pattern for
        the guess the user got.
    """
    answers_text = "Answer with:  'correct'  'incorrect'  'partial'  'higher'  'lower'"
    question_text = f"What indicator do you see for each property for {guess.name}?"

    _line("=")
    print(question_text)
    print(answers_text)
    _line("-", length=answers_text)

    pattern = []
    for prop_name in Champion.properties():
        prop_val = getattr(guess, prop_name)

        indicator_flag = True

        while indicator_flag:
            user_input = input(f"{prop_name.replace("_", " ").capitalize()}: ")
            valid_indicator = _get_valid_indicator(prop_name, user_input, prop_val)
            if valid_indicator:
                pattern.append(valid_indicator)
                indicator_flag = False
            else:
                print(f"Invalid indicator {user_input!r}")

    _line("=")
    return tuple(pattern)


def is_correct(feedback_pattern: FeedbackPattern) -> bool:
    """Return True if all properties are correct for a guess."""
    return all(indicator == Indicator.CORRECT for indicator in feedback_pattern)


def show_remaining_champions(remaining: Champions) -> None:
    """Showcase the remaining candidate champions that are left."""
    remaining_length = len(remaining)
    if remaining_length == 1:
        # Correct guess
        return

    msg = "The remaining champions left based on your guess:"
    print(msg)
    _line("-", length=msg)

    per_column = 5
    total = len(remaining)
    num_columns = (total + per_column - 1) // per_column  # ceil division

    # Convert to strings first
    items = [f"{i}) {champion}" for i, champion in enumerate(remaining, 1)]

    # Build columns
    columns = [
        items[i * per_column:(i + 1) * per_column]
        for i in range(num_columns)
    ]

    # Pad columns so they are equal length
    for col in columns:
        while len(col) < per_column:
            col.append("")

    # Compute column widths for alignment
    col_widths = [
        max(len(row) for row in col)
        for col in columns
    ]

    # Print row by row
    for row_idx in range(per_column):
        row_items = []
        for col_idx, col in enumerate(columns):
            item = col[row_idx]
            row_items.append(item.ljust(col_widths[col_idx] + 4))  # spacing
        print("".join(row_items))

    _line("-")


def two_remaining(candidates: Champions) -> bool:
    """Return True if there are only two remaining champions based on user's guess."""
    return len(candidates) == 2


def one_remaining(candidates: Champions) -> bool:
    """Return True if there are only one remaining champions based on user's guess."""
    return len(candidates) == 1


def welcome_user():
    _line("=")
    print(
        "Welcome to the Loldle solver using math!"

        "\n\nChoose a champion from the best guesses for maximum information, or choose any champion"
        "\nin Loldle and then enter the champion you chose here."
    )
