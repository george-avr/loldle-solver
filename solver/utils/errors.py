"""
Custom exceptions for champion data retrieval in Loldle.

This module defines exceptions that may occur when fetching, parsing,
or validating League of Legends champion data from Loldle's
minified JavaScript bundles.

These exceptions typically indicate network failures, missing or
invalid JS bundles, or inconsistencies in the extracted champion data.

Exceptions:
    MinifiedJSBundleNotFoundError
        Raised when a valid minified JS bundle cannot be found or fetched.
    FetchURLError
        Raised when a network or server error occurs during URL fetching.
    InvalidChampionCount
        Raised when the number of extracted champions does not match
        the expected total.
"""
from solver.utils.champ_data_defs import URLs


class LoldleError(Exception):
    """Base class for all Loldle-related errors."""
    pass


class MinifiedJSBundleNotFoundError(LoldleError):
    """
    Raised when the minified JavaScript bundle that has
    all champion data could not be fetched.
    """
    HELP = (
        f"\nTry finding a valid JavaScript bundle on: {URLs.LOLDLE_HOMEPAGE}"
        f"\nPass it to create_champions_json() as a keyword argument like:"
        "\nExample:\n"
        "  create_champions_json('data.json', "
        "from_jsbundle_url='https://loldle.net/js/index.xxx.js')"
    )

    def __init__(self, msg: str):
        super().__init__(msg + self.HELP)


class FetchURLError(LoldleError):
    """
    Raised when failing to fetch a URL because
    of network/server errors.
    """
    pass


class InvalidChampionCount(LoldleError):
    """
    Raised when more or less champions were fetched
    from a minified JS bundle with regex pattern matching.
    """

    def __init__(self, matched: int, expected: int, tolerance: int, difference: int):
        self.matched = matched
        self.expected = expected
        self.tolerance = tolerance
        self.difference = difference

        if difference > 0:
            reason = "Too many champions matched (regex likely too broad)"
        else:
            reason = "Too few champions matched (regex likely outdated)"

        super().__init__(
            f"Champion count mismatch: got {matched}, expected ~{expected} "
            f"(tolerance ±{tolerance}).\n{reason}."
        )