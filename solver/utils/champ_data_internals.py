"""
Internal service module for fetching, parsing, and validating
League of Legends champion data used by Loldle.

This module handles:

- Retrieving HTML or JS content from predefined URLs.
- Extracting champion data using regular expressions.
- Validating that all expected champions are present.

All functions are intended for internal use.
"""
import re
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from typing import Sequence, Literal, overload
from pathlib import Path
from datetime import date
from re import finditer
import json
import time

from solver.utils.errors import (
    MinifiedJSBundleNotFoundError,
    InvalidChampionCount,
    FetchURLError,
)
from solver.utils.champ_data_defs import (
    RegexPatterns,
    RegexMatchStr,
    RegexMatchDict,
    HTTPHeaders,
    URLs,
    LIST_FIELDS,
    ChampionDict
)
from solver.utils.champ_data_defs import ChampionsJson


def write_to_json(
        obj: ChampionsJson, filepath: Path | str, indent: int | None = 4,
) -> None:
    """
    Safely write a dictionary to a JSON file with UTF-8 encoding.
    """
    path = Path(filepath)

    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(obj, f, indent=indent)
    except (OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Failed to write JSON to {path}: {e}") from e



def parse_champion_data(
        js_text: str,
        pattern=RegexPatterns.CHAMPION_DATA,
        list_fields=LIST_FIELDS
) -> list[ChampionDict]:
    """
    Extract, normalize, and validate champion data from a minified JavaScript bundle.

    This function applies a regex pattern to locate champion entries within the
    provided JavaScript source, converts JSON-like string fields into Python
    objects, and normalizes primitive values (e.g., casting `release_year` to int).

    The resulting dataset is then validated against the expected total number
    of champions to ensure completeness and integrity of the champion roster.

    Args:
        js_text (str):
            Raw JavaScript bundle content.
        pattern (re.Pattern):
            Compiled regex pattern used to extract champion fields.
        list_fields (Sequence[str]):
            Field names that should be parsed from JSON-like strings into lists.

    Returns:
        list[ChampionDict:
            A list of dictionaries representing normalized champion data.

    Raises:
        InvalidChampionCount: If the number of parsed champions
            deviates beyond the allowed tolerance.
        FetchURLError: If retrieving the expected champion count fails.
    """
    champions = []
    expected_champions = 172

    matches = _find_matches(js_text, pattern, named_groups=True)
    for champ in matches:
        for field in list_fields:
            champ[field] = json.loads(champ[field])
        champ["release_date"] = int(champ["release_date"])
        champions.append(champ)

    _validate_champion_data(champions, expected_champions)
    return champions


def _validate_champion_data(champions: list[ChampionDict], expected: int) -> None:
    """
    Validate that all champions were parsed successfully.

    The total number of expected champions is considered within an
    allowed tolerance of ±1. This accounts for the possibility that
    a new champion has been added to the game but has not yet been
    updated in Loldle’s roster or in the source used to compute the total.
    """
    matched = len(champions)

    if matched == 0:
        raise MinifiedJSBundleNotFoundError(
            "Champion data could not be extracted."
            "\nThe regex pattern may be outdated or the "
            "JS bundle format has changed."
        )

    if matched < expected:
        raise InvalidChampionCount(matched)


def get_latest_date(
        js_text: str,
        date_pattern=RegexPatterns.DATE
) -> str | Literal["N/A"]:
    """
    Get the date of the last update of Loldle's Patch notes.

    Use a regex pattern to find all dates from `url` in DD/MM/YYYY
    format and return the most recent one.
    """
    date_matches = _find_matches(js_text, date_pattern)
    dates = [date.strptime(d, "%d/%m/%Y") for d in date_matches]

    if not dates:
        return "N/A"
    return max(dates).isoformat()


def fetch_url_text(url: str, *, headers=HTTPHeaders.DEFAULT,
                   max_retries=3, backoff=2) -> str:
    """
    Fetch the content of a url using the standard-lib module urllib with
    retry support.

    This function attempts to GET the given url, retrying on server-side
    errors (HTTP 5xx) or rate limiting (HTTP 429).

    Args:
        url (str): A URL to fetch.
        headers (dict): HTTP headers to include in the request.
        max_retries (int): Maximum number of attempts in case of network/server errors.
        backoff (int | float): Base number of seconds to wait between retries;
            multiplied exponentially by attempt number for backoff.

    Returns:
        str: The response text if the request succeeds.
    """
    for attempt in range(1, max_retries + 1):
        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=10) as response:
                return response.read().decode("utf-8")
        except HTTPError as e:
            wait = backoff * (2 ** (attempt - 1))
            if e.code >= 500 or e.code == 429:
                time.sleep(wait)
            else:
                raise FetchURLError(f"Failed to fetch {url}, Status code: {e.code}")
        except URLError:
            time.sleep(backoff * (2 ** (attempt - 1)))
    raise FetchURLError(f"Failed to fetch {url} after {max_retries} attempts")


def find_minified_jsbundle_urls(
        loldle_homepage=URLs.LOLDLE_HOMEPAGE,
        pattern=RegexPatterns.MINIFIED_JS_BUNDLE
) -> list[str]:
    """
    Auto-detect all minified JavaScript bundle URLs from the Loldle homepage
    that potentially contain complete champion data/properties.

    This function fetches the HTML of the Loldle homepage and searches
    for JavaScript bundle links matching the given regex pattern.
    It prepends the homepage URL to each relative match to form absolute URLs.

    Returns:
        list[str]: A list of absolute URLs pointing to candidate minified JS bundles
            containing champion data.

    Raises:
        MinifiedJSBundleNotFoundError: If no matching JS bundles are found
        on the homepage.

    Notes:
        - The returned URLs are absolute (homepage URL + relative path).
    """
    text = fetch_url_text(loldle_homepage)
    js_matches = _find_matches(text, pattern)
    urls = [loldle_homepage + match for match in js_matches]

    if not urls:
        raise MinifiedJSBundleNotFoundError(
            "Could not find any valid minified JavaScript bundles "
            "to fetch data from."
        )
    return urls


def find_data_from_loldle(matched_urls: list[str]) -> tuple[list[ChampionDict], str]:
    """
    Locate and extract champion data from a valid minified JS bundle.

    This function iterates over a list of potential JavaScript bundle URLs,
    fetching each one until it successfully identifies the bundle containing
    all champion data. Once found, it parses the champion information and
    extracts the last update date.

    Args:
        matched_urls (list[str]): A list of URLs pointing to potential minified JS bundles.

    Returns:
        tuple[list[ChampionDict, str]:
            - `ChampionsRoster`: Parsed data of all champions from the valid JS bundle.
            - `str`: The last update date of the champion data in YYYY-MM-DD format.

    Raises:
        FetchURLError: If fetching the JS bundle fails for all URLs.
        MinifiedJSBundleNotFoundError: If no valid minified JS bundle is found.
        InvalidChampionCount: If the parsed data does not contain the expected number of champions.
    """
    last_error = None

    for js_bundle in matched_urls:
        try:
            js_text = fetch_url_text(js_bundle)
            champions = parse_champion_data(js_text)
            last_update = get_latest_date(js_text)
            return champions, last_update
        except (
                FetchURLError,
                InvalidChampionCount,
                MinifiedJSBundleNotFoundError,
        ) as e:
            last_error = e
            continue
    raise last_error


def _get_total_champions(
        url=URLs.LEAGUE_OF_GRAPHS,
        pattern=RegexPatterns.LEAGUE_OF_GRAPHS_CHAMPION
) -> int:
    """
    Retrieve the current total number of champions in League of Legends as an int.

    This function fetches the HTML content from the specified
    url and counts the occurrences of champion entries using the
    provided regular expression pattern.

    It returns the total number of champions detected.
    """
    text = fetch_url_text(url)
    matches = _find_matches(text, pattern)
    return sum(1 for _ in matches)


def is_recent(date_str: str, *, days: int = 30) -> bool:
    """Return True if the given date string is within the last specified `days`."""
    try:
        latest_date = date.fromisoformat(date_str)
        today = date.today()
        return (today - latest_date).days < days
    except (TypeError, ValueError):
        return False


# Overloaded function signatures for _find_matches():
# Depending on the `named_groups` argument (a boolean literal),
# the return type changes:
# - If named_groups=True, yields dicts of named regex groups.
# - If named_groups=False (default), yields full match strings.
# These overloads help static type checkers understand the correct return type
# without needing 2 different functions

@overload
def _find_matches(text: str, pattern, named_groups: Literal[True]) -> RegexMatchDict: ...
@overload
def _find_matches(text: str, pattern, named_groups: Literal[False] = False) -> RegexMatchStr: ...

def _find_matches(text: str, pattern, named_groups=False):
    """
    Find all matches of a regex pattern in a string.

    Args:
        text (str):
            The string to search.
        pattern (re.Pattern):
            Compiled regular expression pattern.
        named_groups (bool):
            If True, yield dictionaries of named groups; else yield the full match strings.

    Yields:
        str or dict[str, str]
            Either the matched string or a dictionary of named groups.
    """
    for match in finditer(pattern, text):
        yield match.groupdict() if named_groups else match.group()


def norm_property(p: str) -> str:
    return p.replace("_", " ").capitalize()