"""
Utilities for retrieving champion data/properties used by Loldle.

This module provides two high-level functions for fetching champion data from
a minified JavaScript bundle.

It then parses the JavaScript bundle and stores the data into a JSON file
which is used on the cli.py module to solve the guessing game,
but it can also be used independently to for any other reason.

Loldle often has Patch notes changing existing champion properties, or
adding new released champions to the roster, this module handles this
automatically and is always up to date.

Public API:
    ``create_champions_json(path)``
        Create a JSON file in the target path with all
        League of Legends champion properties used by Loldle.

    ``load_champions(path)`` -> Champions
        Load the JSON created by `create_champions_json`
        into memory, returning a list of champions each one
        being a custom Champion object (properties accessed
        via dot notation, e.g. champion.release_year).
"""
from typing import Literal, overload
from pathlib import Path
import json

from solver.utils.champ_data_defs import ChampionsJson
from solver.champ_pipeline.champions import Champion, Champions
from solver.utils.champ_data_internals import (
    is_recent,
    find_minified_jsbundle_urls,
    find_data_from_loldle,
    fetch_url_text,
    parse_champion_data,
    get_latest_date,
    write_to_json,
)


def create_champions_json(
        filepath: Path | str,
        *,
        from_jsbundle_url: str | None = None,
        indent: int | None = 4,
        overwrite: bool = False,
        refresh_if_old: bool = True,
        max_age_days: int = 30,
) -> None:
    """
    Create or update a JSON file with all champion data used by Loldle.

    By default, this function only updates the JSON if it is missing or
    older than `max_age_days`. You can override this behavior with
    the `overwrite` flag.

    Args:
        filepath (Path | str):
            Path to save the JSON file.
        from_jsbundle_url (str | None), optional:
            Direct URL of the JS bundle to fetch champion data from.
            Defaults to auto-detecting the latest bundle.
        indent (int | None), optional:
            Number of spaces for JSON formatting.
        overwrite (bool), optional:
            If True, always overwrite the JSON regardless of age.
        refresh_if_old (bool), optional:
            If True and `overwrite=False`, JSON will only be recreated
            if older than `max_age_days`.
        max_age_days (int), optional:
            Maximum allowed age of the JSON file in days before refreshing.

    Behavior:
        1. If `overwrite=True`, JSON is always recreated.
        2. If `overwrite=False` and `refresh_if_old=True`, JSON is recreated
           only if older than `max_age_days`.
        3. If JSON does not exist, it is always created.
    """
    path = Path(filepath)

    if path.suffix != ".json":
        raise ValueError(
            f"Invalid file type: {str(path)!r}. Only .json files are allowed."
        )

    # Skip recreation if not needed
    if path.exists() and not overwrite:
        if refresh_if_old:
            champ_data = load_champions(path, convert_champions=False)
            last_update = champ_data.get("latest_update")
            if last_update and is_recent(last_update, days=max_age_days):
                return  # JSON is recent, skip creation
        else:
            return  # JSON exists, and we don't want to refresh

    path.parent.mkdir(parents=True, exist_ok=True)

    if from_jsbundle_url is None:
        urls = find_minified_jsbundle_urls()
        champion_data, latest_update = find_data_from_loldle(urls)
    else:
        js_text = fetch_url_text(from_jsbundle_url)
        champion_data = parse_champion_data(js_text)
        latest_update = get_latest_date(js_text)

    obj: ChampionsJson = {
        "latest_update": latest_update,
        "champions": champion_data,
    }

    write_to_json(obj, path, indent=indent)


@overload
def load_champions(
    filepath: Path | str
) -> Champions: ...

@overload
def load_champions(
    filepath: Path | str, *,
    convert_champions: Literal[True]
) -> Champions: ...

@overload
def load_champions(
    filepath: Path | str, *,
    convert_champions: Literal[False]
) -> ChampionsJson: ...


def load_champions(
        filepath: Path | str, *, convert_champions: bool = True
) -> Champions | ChampionsJson:
    """
    Load champion data from a JSON file created by ``create_champions_json``.

    By default, this function unwraps the top-level "champions" key and converts
    each entry into a ``Champion`` object for a cleaner, attribute-based API.

    Args:
        filepath (Path | str):
            Path to the JSON file containing champion data.
        convert_champions (bool), optional:
            If True (default), returns a list of ``Champion`` objects.
            If False, returns the raw parsed JSON dictionary without modification.

    Returns:
        Champions | ChampionsJson:
            - If ``convert_champions=True``:
                A list of ``Champion`` instances.
            - If ``convert_champions=False``:
                The raw JSON structure as a dictionary with keys:
                {"latest_update": str, "champions": list[dict]}.

    Raises:
        FileNotFoundError:
            If the provided file does not exist.
        json.JSONDecodeError:
            If the file is not valid JSON.
        ValueError:
            If the JSON structure is invalid or missing expected keys.

    Notes:
        Only intended to be called after the `champions.json` has been
        created by ``create_champions_json``.
    """
    path = Path(filepath)

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    if not convert_champions:
        return data

    # Determine structure
    if isinstance(data, dict):
        champions_data = data.get("champions")
        if champions_data is None:
            raise ValueError("Invalid JSON format: missing 'champions' key.")
    elif isinstance(data, list):
        champions_data = data
    else:
        raise ValueError("Invalid JSON format: expected dict or list.")

    return [Champion.from_dict(champ) for champ in champions_data]
