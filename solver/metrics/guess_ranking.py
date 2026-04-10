"""
Module for LoLdle analysis.

Users may work with the loldle_df below.
"""
from pathlib import Path
import json

import pandas as pd

from solver.utils import paths
from solver.champ_pipeline.loader import load_champions
from solver.champ_pipeline.champions import Champion
from solver.engine.guess_evaluation import (
    compute_metrics,
    compute_pattern_id_matrix,
)

def create_csv_metrics(load: Path, output: Path) -> None:
    # ----------------------------
    # Load data
    # ----------------------------
    champions = load_champions(load)
    guess_ids = {champ.name: i for i, champ in enumerate(champions)}
    champ_map = {champ.name: champ for champ in champions}

    # ----------------------------
    # Compute metrics
    # ----------------------------
    pattern_id_matrix = compute_pattern_id_matrix(
        guesses=champions,
        targets=champions,
    )

    metrics_df = compute_metrics(pattern_id_matrix, guess_ids)

    # ----------------------------
    # Build final table
    # ----------------------------
    df = metrics_df.copy()

    df["champion"] = df.index
    df["rank"] = df["entropy"].rank(ascending=False, method="first").astype(int)

    props = list(Champion.properties())

    champ_map = {champ.name: champ for champ in champions}

    for prop in props:
        df[prop] = df["champion"].map(
            lambda name: _serialize_value(getattr(champ_map[name], prop))
        )

    df = df.sort_values("rank")[
        ["rank", "champion", "entropy", "expected_remaining"] + props
        ]


    # ----------------------------
    # Save
    # ----------------------------
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)


def _serialize_value(v):
    if v is None:
        return None
    if isinstance(v, frozenset):
        return json.dumps(sorted(v))
    return v


if __name__ == "__main__":
    output_path = paths.results / "guess_rankings.csv"
    create_csv_metrics(load=paths.champion_data, output=output_path)

    loldle_df = pd.read_csv(output_path)

    # Can do analysis with 'loldle_df'
