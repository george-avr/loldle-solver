"""
Internal module for easier path handling within the project.
"""
from pathlib import Path

base = Path(__file__).resolve().parents[2]

resources = base / "resources"
results = base / "results"

champion_data = resources / "champions.json"
rankings = results / "guess_rankings.csv"