"""
Internal module for easier path handling within the project.
"""
from pathlib import Path

base = Path(__file__).resolve().parents[2]

resources = base / "resources"
results = base / "results"
results_plots = results / "plots"

champion_data = resources / "champions.json"