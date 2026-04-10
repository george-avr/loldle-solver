"""
Simulation and evaluation utilities for Loldle guess strategies.

This module provides the champion data logic for comparing champions,
generating feedback patterns, filtering candidate targets, and evaluating
guesses using information-theoretic metrics such as Shannon entropy and
expected remaining candidates.

It is primarily used by the engine to rank guesses and narrow down the
set of possible champions.
"""
from functools import lru_cache
import pandas as pd
import numpy as np

from solver.champ_pipeline.champions import Champion, Champions
from solver.utils.feedback_utils import PropertyValue, Indicator, FeedbackPattern


def filter_candidates(
        champions: Champions,
        guess: Champion,
        user_pattern: FeedbackPattern
) -> Champions:
    """
    Filters out champions that do not produce the given feedback pattern
    when compared to the provided guess champion.

    Args:
        champions (Champions):
            List of all possible champions.
        guess (Champion):
            The guess champion to compare against.
        user_pattern (PatternFeedback):
            The feedback pattern produced by comparing the guess champion
            to the target.

    Returns:
        Champions:
            A list of champions that match the given feedback pattern
            when compared to the guess.
    """
    filtered_champions = []

    # Loop through all champions to compare them to the guess
    for champion in champions:
        feedback_pattern = compare_properties(champion, guess)

        # Keep the champions that match the generated feedback pattern
        if feedback_pattern == user_pattern:
            filtered_champions.append(champion)

    return filtered_champions


def compute_metrics(
        pattern_id_matrix: np.ndarray,
        guess_ids: dict[str, int]
) -> pd.DataFrame:
    """
    Compute Shannon entropy (in bits) and the Expected remaining candidates
    for each guess, in a DataFrame.
    """
    counts_per_guess = get_pattern_counts_per_guess(pattern_id_matrix)
    entropy_bits = compute_entropy(counts_per_guess)
    expected_remaining = compute_expected_size(counts_per_guess)

    champion_names = list(guess_ids.keys())

    return pd.DataFrame(
        {
            "entropy": entropy_bits,
            "expected_remaining": expected_remaining,
        },
        index=champion_names
    )


def compute_entropy(counts_per_guess: list[np.ndarray]) -> np.ndarray:
    """
    Compute Shannon entropy (in bits) for each guess.
    """
    entropy = np.zeros(len(counts_per_guess))

    for i, counts in enumerate(counts_per_guess):
        probabilities = counts / counts.sum()
        entropy[i] = -(probabilities * np.log2(probabilities)).sum()

    return entropy


def compute_expected_size(counts_per_guess: list[np.ndarray]) -> np.ndarray:
    """
    Compute expected remaining candidates for each guess.
    """
    expected_size = np.zeros(len(counts_per_guess))

    for i, counts in enumerate(counts_per_guess):
        expected_size[i] = (counts ** 2).sum() / counts.sum()

    return expected_size


def get_pattern_counts_per_guess(pattern_id_matrix: np.ndarray) -> list[np.ndarray]:
    """
    Extract counts of feedback patterns for each guess (column).

    Returns:
        list[np.ndarray]: Each element is an array of counts for one guess.
    """
    n_guesses = pattern_id_matrix.shape[1]
    counts_per_guess = []

    for col in range(n_guesses):
        column_patterns = pattern_id_matrix[:, col]

        # Exclude diagonal (-1)
        column_patterns = column_patterns[column_patterns != -1]

        _, counts = np.unique(column_patterns, return_counts=True)
        counts_per_guess.append(counts)

    return counts_per_guess


def compute_pattern_id_matrix(
        guesses: Champions,  # full champion set
        targets: Champions,  # filtered or full set
) -> np.ndarray:
    """
    Build a matrix of pattern IDs for all (target, guess) pairs.

    Each column corresponds to a guess and groups targets by the feedback
    pattern they produce. Each unique pattern is assigned a local integer ID.
    Diagonal entries (-1) are reserved for the target == guess case.

    Args:
        guesses (Champions):
            A list of champions to consider as possible guesses.
        targets (Champions):
            A list of champions to consider as possible targets.

    Returns:
        np.ndarray:
            Shape (n_targets, n_guesses). Entry [i, j] is the pattern ID
            of target i when guess j is used. Diagonal (-1) ignored.
    """
    n_targets = len(targets)
    n_guesses = len(guesses)
    guess_ids = {champ.name: i for i, champ in enumerate(guesses)}

    pattern_matrix = np.full((n_targets, n_guesses), -1, dtype=int)

    for guess in guesses:
        col_idx = guess_ids[guess.name]

        # Map unique feedback patterns to integer IDs (per guess)
        pattern_to_id: dict[FeedbackPattern, int] = {}
        next_id = 0

        for row_idx, target in enumerate(targets):
            if target == guess:
                continue  # diagonal

            pattern = compare_properties(target, guess)

            if pattern not in pattern_to_id:
                pattern_to_id[pattern] = next_id
                next_id += 1

            pattern_matrix[row_idx, col_idx] = pattern_to_id[pattern]

    return pattern_matrix


@lru_cache(maxsize=None)
def compare_properties(target: Champion, guess: Champion) -> FeedbackPattern:
    """
    Compare the properties of a target champion and a guessed champion,
    generating a feedback pattern.

    The feedback pattern is returned as a hashable tuple that can be used for:
        - Pattern ID mapping for entropy calculations.
        - Filtering candidates when narrowing down potential targets based on user feedback.

    Args:
        target (Champion): The correct champion (target) to compare against.
        guess (Champion): The champion being guessed.

    Returns:
        FeedbackPattern: A tuple of feedback for each property,
        ordered according to the properties of the champion.
    """
    pattern = []
    for prop in Champion.properties():
        target_value = getattr(target, prop)
        guess_value = getattr(guess, prop)
        feedback = _compare_values(target_value, guess_value)
        pattern.append(feedback)
    return FeedbackPattern(*pattern)


def _compare_values(target: PropertyValue, guess: PropertyValue) -> Indicator:
    """
    Compare two property values (target and guess) and return the appropriate indicator.

    This function handles the comparison of scalar values (integers and strings)
    and set values (frozensets).

    Args:
        target (PropertyValue): The correct value of the property.
        guess (PropertyValue): The guessed value of the property.

    Returns:
        Indicator: The indicator representing the relationship between
        the target and guess, such as CORRECT, HIGHER, LOWER, INCORRECT,
        PARTIAL_SUBSET, or PARTIAL_OVERLAP.
    """
    if target == guess:
        return Indicator.CORRECT

    match target, guess:
        case int() | np.integer(), int() | np.integer():
            return Indicator.HIGHER if target > guess else Indicator.LOWER
        case str(), str():
            return Indicator.INCORRECT
        case frozenset(), frozenset():
            intersection = target & guess
            if not intersection:
                return Indicator.INCORRECT
            return Indicator.PARTIAL_SUBSET if len(guess) == 1 else Indicator.PARTIAL_OVERLAP
        case _:
            raise ValueError(f"Cannot compare values: {target!r} vs {guess!r}")
