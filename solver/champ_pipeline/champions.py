"""
Internal module for converting champion data into a dataclass for
easier internal comparisons
"""
from typing import TypeAlias
from dataclasses import dataclass
from re import split

from solver.utils.champ_data_defs import ChampionDict, CHAMPION_ALIASES
from solver.utils.champ_data_internals import norm_property


Champions: TypeAlias = list["Champion"]

@dataclass(slots=True, frozen=True)
class Champion:
    """
    Helper class for storing champion data and accessing them
    with clean object-oriented design (e.g. `champion.release_year`).
    """
    name: str
    gender: str
    positions: frozenset[str]
    species: frozenset[str]
    resource: str
    range_type: frozenset[str]
    regions: frozenset[str]
    release_year: int

    def __str__(self):
        return self.name

    def aliases(self) -> frozenset[str]:
        champ_name = self.name.lower()
        parts = split(r"\W+", champ_name)
        nicknames = CHAMPION_ALIASES.get(champ_name, set())

        aliases_set = {p for p in parts if p and len(p) > 1} | {champ_name} | nicknames

        if len(parts) > 1:
            initials = ''.join(part[0] for part in parts if part)
            aliases_set.add(initials)

        return frozenset(aliases_set)

    @classmethod
    def properties(cls, normalize: bool = False) -> tuple[str, ...]:
        """
        Class method of ``Champion`` class that returns a sequence of all champion
        properties (except champion.name), for property comparisons between champions.

        If `normalize` is ``True``, the champion properties are capitalized underscores
        are converted to whitespace (e.g. "release_year" becomes "Release year").
        """
        return tuple(
            norm_property(p) if normalize else p
            for p in cls.__annotations__ if p != 'name'
        )

    @classmethod
    def from_dict(cls, champ_properties: ChampionDict) -> Champion:
        """
        Class method of ``Champion`` class that returns a new Champion
        instance from a ChampionDict dictionary.

        Converts `positions`, `species`, `range_type` and `regions`
        values into ``frozenset`` for cleaner set comparisons.
        """
        return _convert_to_champion(champ_properties)


def _convert_to_champion(champ_dict: ChampionDict) -> Champion:
    return Champion(
        name=champ_dict["championName"],
        gender=champ_dict["gender"],
        positions=frozenset(champ_dict["positions"]),
        species=frozenset(champ_dict["species"]),
        resource=champ_dict["resource"],
        range_type=frozenset(champ_dict["range_type"]),
        regions=frozenset(champ_dict["regions"]),
        release_year=champ_dict["release_date"],
    )
