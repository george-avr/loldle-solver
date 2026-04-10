"""
Internal helpers for "Top vs Bottom LoLdle champions" plot.
"""
from pathlib import Path
import pandas as pd

from solver.plots.loldle_plots import plot_best_worst
from solver.utils import paths
from solver.champ_pipeline.loader import load_champions
from solver.engine.guess_evaluation import (
    compute_pattern_id_matrix,
    get_pattern_counts_per_guess,
    compute_entropy,
)


def _get_best_worst(n: int = 10, *, champ_path: Path | str) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_champions = load_champions(champ_path)

    pattern_id_matrix = compute_pattern_id_matrix(all_champions, all_champions)
    counts_per_guess = get_pattern_counts_per_guess(pattern_id_matrix)
    entropy = compute_entropy(counts_per_guess)
    names = [champ.name for champ in all_champions]

    df = pd.DataFrame({
        "champion": names,
        "bits": entropy
    })

    best = df.nlargest(n, "bits").sort_values("bits", ascending=True)
    worst = df.nsmallest(n, "bits")

    return best, worst


if __name__ == "__main__":
    background_path = paths.resources / "plots_background_image.jpg"
    save_plot_to = paths.results / "loldle_top_bottom_guesses_plot.png"

    best_guesses, worst_guesses = _get_best_worst(champ_path=paths.champion_data)
    plot_best_worst(best_guesses, worst_guesses, image=background_path, save_path=save_plot_to)
