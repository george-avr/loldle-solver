"""
Constants, types, and regex patterns used internally for handling
League of Legends champion data in Loldle.

This module defines:

- TypedDicts and type aliases for champion data structures.
- URL endpoints and default HTTP headers for fetching resources.
- Precompiled regular expressions for parsing champion information
  and detecting relevant minified JavaScript bundles.

All definitions here are intended for internal use.
"""
import re
from typing import TypedDict, TypeAlias, Iterable, Generator, Any

RegexMatchDict: TypeAlias = Generator[dict[str, str | Any], Any, None]
RegexMatchStr: TypeAlias = Generator[str, Any, None]

CHAMPION_ALIASES: dict[str, set[str]] = {
    "alistar": {"ali"},
    "aurelion sol": {"asol"},
    "blitzcrank": {"blitz"},
    "caitlyn": {"cait"},
    "cassiopeia": {"cass"},
    "evelynn": {"eve"},
    "ezreal": {"ez"},
    "fiddlesticks": {"fiddle"},
    "gangplank": {"gp"},
    "hecarim": {"hec"},
    "heimerdinger": {"heimer", "donger"},
    "jarvan iv": {"j4"},
    "kassadin": {"kass", "kassa"},
    "katarina": {"kata", "kat"},
    "kha'zix": {"k6"},
    "lissandra": {"liss"},
    "malphite": {"malph"},
    "malzahar": {"malz"},
    "maokai": {"mao"},
    "mordekaiser": {"mord"},
    "morgana": {"morg"},
    "nautilus": {"naut"},
    "nidalee": {"nida"},
    "nocturne": {"noc"},
    "orianna": {"ori"},
    "pantheon": {"panth"},
    "sejuani": {"sej"},
    "seraphine": {"sera"},
    "shyvana": {"shyv"},
    "soraka": {"raka"},
    "tristana": {"trist"},
    "tryndamere": {"trynd", "trynda"},
    "vladimir": {"vlad"},
    "volibear": {"voli"},
    "warwick": {"ww"},
    "zilean": {"zil"},
}


class ChampionDict(TypedDict):
    """
    Dictionary format of each champion's properties and
    how champions will be parsed to JSON.
    """
    championName: str
    gender: str
    positions: list[str]
    species: list[str]
    resource: str
    range_type: list[str]
    regions: list[str]
    release_date: int


class ChampionsJson(TypedDict):
    latest_update: str
    champions: list[ChampionDict]


LIST_FIELDS: Iterable[str] = (
    "positions",
    "species",
    "range_type",
    "regions",
)


class URLs:
    LOLDLE_HOMEPAGE = "https://loldle.net/"
    LEAGUE_OF_GRAPHS = "https://www.leagueofgraphs.com/champions/winrates-by-xp"


class HTTPHeaders:
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    REFERER = "https://loldle.net/classic"
    ACCEPT = "*/*"

    DEFAULT = {
        "User-Agent": USER_AGENT,
        "Referer": REFERER,
        "Accept": ACCEPT,
    }


class RegexPatterns:
    CHAMPION_DATA = re.compile(
        r"""
        championName:\s*"(?P<championName>[^"]+)",\s*
        gender:\s*"(?P<gender>[^"]+)",\s*
        positions:\s*(?P<positions>\[[^]]+]),\s*
        species:\s*(?P<species>\[[^]]+]),\s*
        resource:\s*"(?P<resource>[^"]+)",\s*
        range_type:\s*(?P<range_type>\[[^]]+]),\s*
        regions:\s*(?P<regions>\[[^]]+]),\s*
        release_date:\s*"(?P<release_date>\d{4})[-/]\d{2}[-/]\d{2}"
        """,
        re.VERBOSE,
    )
    LEAGUE_OF_GRAPHS_CHAMPION = re.compile(r"<a href=\"/champions/builds/")
    DATE = re.compile(r"\d{2}[-/]\d{2}[-/]\d{4}")
    MINIFIED_JS_BUNDLE = re.compile(r"(?:js)?/(?:index|chunk)[^\"]+\.js")
