"""
Plotting functions for varius LoLdle analytics.
"""
from pathlib import Path
from collections import Counter
from itertools import combinations

from scipy.stats import gaussian_kde
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from solver.utils import paths
from solver.plots._plot_utils import (
    _add_cover_background,
    _barh_with_shadow,
    _styled_title,
    _style_axes,
    _styled_xlabel,
    _finalize_plot,
    _safe_eval,
)


def plot_best_worst(best: pd.DataFrame, worst: pd.DataFrame, *, save_path=None) -> None:
    background = paths.results_plots / "plots_background_image.jpg"
    img = mpimg.imread(background)

    fig, axes = plt.subplots(2, 1, figsize=(19.2, 10.8), sharex=True)
    fig.patch.set_facecolor("black")
    _add_cover_background(fig, img)

    # --- plot data ---
    if "championName" in best.columns:
        best = best.rename(columns={"championName": "champion"})
        worst = worst.rename(columns={"championName": "champion"})
    if "entropy" in best.columns:
        best = best.rename(columns={"entropy": "bits"})
        worst = worst.rename(columns={"entropy": "bits"})

    _barh_with_shadow(axes[0], best["champion"], best["bits"], color="#4da3ff")
    _barh_with_shadow(axes[1], worst["champion"], worst["bits"], color="#ff4d4d")

    # --- style axes ---
    for ax in axes:
        _style_axes(ax)

    # --- titles ---
    _styled_title(axes[0], "Top 10 initial guesses for LoLdle")
    _styled_title(axes[1], "Bottom 10 initial guesses for LoLdle")

    # --- x label ---
    _styled_xlabel(axes[1], "Information of guess (shannon bits)")

    # --- layout ---
    fig.subplots_adjust(
        top=0.92,
        bottom=0.10,
        left=0.20,
        right=0.85,
        hspace=0.30
    )

    # --- save ---
    if save_path is not None:
        save_in = Path(save_path)
        save_in.parent.mkdir(parents=True, exist_ok=True)

        fig.savefig(
            save_in,
            dpi=100,
            bbox_inches="tight",
            pad_inches=0
        )

    plt.show()


def plot_entropy_distribution(
        df: pd.DataFrame,
        *,
        output_path=paths.results_plots,
        filename="loldle_entropy_distribution.png",
        show=True,
        save=False,
        style="ggplot",
        bins="fd"
):
    """
    Plot histogram of entropy with KDE overlay.
    """
    entropy = df["entropy"]

    # -----------------------
    # PLOT
    # -----------------------
    plt.style.use(style)
    fig, ax = plt.subplots(figsize=(14, 8))

    # Histogram
    counts, bins_edges, _ = ax.hist(
        entropy,
        bins=bins,
        edgecolor="black",
        alpha=0.6,
        label="Histogram"
    )

    # KDE
    x = np.linspace(entropy.min(), entropy.max(), 500)
    kde = gaussian_kde(entropy)

    # Scale KDE to histogram counts
    bin_width = bins_edges[1] - bins_edges[0]
    ax.plot(
        x,
        kde(x) * len(entropy) * bin_width,
        linewidth=2,
        label="KDE"
    )

    # Labels & title
    ax.set_xlabel("Entropy (bits)", labelpad=10)
    ax.set_ylabel("Number of Champions", labelpad=10)
    ax.set_title("LoLdle Champion Entropy Distribution")

    # Legend
    ax.legend()

    plt.tight_layout()

    # -----------------------
    # SAVE & SHOW
    # -----------------------
    return _finalize_plot(fig, output_path, filename, save, show)


def plot_entropy_vs_remaining(
        df: pd.DataFrame,
        *,
        output_path=paths.results_plots,
        filename="loldle_entropy_vs_remaining_scatter.png",
        show=True,
        save=False,
        style="bmh"
):
    """
    Scatter plot of entropy vs expected remaining candidates.
    """

    # -----------------------
    # LOAD & PREP
    # -----------------------
    entropy = df["entropy"]
    remaining = df["expected_remaining"]

    # -----------------------
    # PLOT
    # -----------------------
    plt.style.use(style)
    fig, ax = plt.subplots(figsize=(12, 8))

    # Scatter
    ax.scatter(
        entropy,
        remaining,
        alpha=0.6,
        label="Champions"
    )

    # Reference lines
    ax.axvline(
        entropy.mean(),
        linestyle=":",
        color="black",
        alpha=0.5,
        label="Mean Entropy"
    )

    ax.axhline(
        remaining.mean(),
        linestyle=":",
        color="black",
        alpha=0.5,
        label="Mean Remaining"
    )

    # Labels & title
    ax.set_xlabel("Entropy (bits)", labelpad=10)
    ax.set_ylabel("Expected Remaining Candidates", labelpad=10)
    ax.set_title("LoLdle: Information Gain vs Candidate Reduction")

    ax.grid(True, alpha=0.3)

    # Legend
    ax.legend()

    plt.tight_layout()

    # -----------------------
    # SAVE & SHOW
    # -----------------------
    return _finalize_plot(fig, output_path, filename, save, show)


def plot_release_timeline_entropy(
        csv_path=paths.loldle_dataset,
        output_path=paths.results_plots,
        filename="loldle_champion_release_timeline_entropy_midpoint.png",
        show=True
):
    """
    Plot champion release counts and average entropy per year.

    Parameters
    ----------
    csv_path : str or Path
        Path to rankings CSV file.
    output_path : str or Path
        Directory to save the output image.
    filename : str
        Name of the saved plot file.
    show : bool
        Whether to display the plot.
    """

    # -----------------------
    # LOAD & PREP
    # -----------------------
    df: pd.DataFrame = pd.read_csv(csv_path)
    df["release_year"] = df["release_year"].astype(int)

    years = np.arange(df["release_year"].min(), df["release_year"].max() + 1)

    # -----------------------
    # METRICS
    # -----------------------
    yearly_counts = (
        df.groupby("release_year")
        .size()
        .reindex(years, fill_value=0)
    )

    yearly_entropy = (
        df.groupby("release_year")["entropy"]
        .mean()
        .reindex(years)
    )

    mean_year = df["release_year"].mean()
    median_year = df["release_year"].median()

    # -----------------------
    # PLOT
    # -----------------------
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Bars: releases
    ax1.bar(
        years,
        yearly_counts.values,
        color="#4FC3F7",
        alpha=0.6,
        width=0.8,
        label="Champions Released"
    )

    ax1.set_xlabel("Release Year", labelpad=10)
    ax1.set_ylabel("Champions Released", color="#4FC3F7", labelpad=15, size=15)
    ax1.tick_params(axis="y", labelcolor="#4FC3F7")

    ax1.set_xticks(years)
    ax1.set_xticklabels(years, rotation=45)

    # Line: entropy
    ax2 = ax1.twinx()
    ax2.plot(
        years,
        yearly_entropy.values,
        color="#FF7043",
        linewidth=2.5,
        marker="o",
        label="Average Entropy"
    )

    ax2.set_ylabel("Average Entropy", color="#FF7043", labelpad=15, size=15)
    ax2.tick_params(axis="y", labelcolor="#FF7043")

    # Reference lines
    ax1.axvline(
        mean_year,
        color="#FFD54F",
        linestyle="--",
        linewidth=2,
        label="Mean Release Year"
    )

    ax1.axvline(
        median_year,
        color="#E57373",
        linestyle="--",
        linewidth=2,
        label="Median Release Year"
    )

    # Title & legend
    plt.title(
        "League of Legends: Champion Release Timeline vs Entropy",
        size=20,
        pad=10
    )

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()

    ax1.legend(
        handles1 + handles2,
        labels1 + labels2,
        loc="upper right"
    )

    plt.tight_layout()

    # -----------------------
    # SAVE & SHOW
    # -----------------------
    save_path = output_path / filename
    plt.savefig(save_path, dpi=300)

    if show:
        plt.show()
    else:
        plt.close()

    return save_path


def plot_region_overlap_heatmap(
        df: pd.DataFrame,
        output_path=paths.results_plots,
        filename="loldle_region_overlap_heatmap.png",
        show=True,
):
    """
    Clean aesthetic heatmap of region overlaps (pairwise only).
    """

    # -----------------------
    # LOAD
    # -----------------------
    df["regions"] = df["regions"].apply(_safe_eval)

    df["regions"] = df["regions"].apply(
        lambda x: [r.strip().title() for r in x]
    )

    # -----------------------
    # PAIR COUNTS
    # -----------------------
    pair_counts = Counter()

    for regions in df["regions"]:
        unique = sorted(set(regions))
        for r1, r2 in combinations(unique, 2):
            pair_counts[(r1, r2)] += 1

    # -----------------------
    # MATRIX
    # -----------------------
    all_regions = sorted({r for row in df["regions"] for r in row})

    matrix = pd.DataFrame(0, index=all_regions, columns=all_regions)

    for (r1, r2), v in pair_counts.items():
        matrix.loc[r1, r2] = v
        matrix.loc[r2, r1] = v

    # -----------------------
    # PLOT
    # -----------------------

    fig, ax = plt.subplots(figsize=(11, 9))

    im = ax.imshow(
        matrix.values,
        cmap="coolwarm",
        interpolation="nearest"
    )

    # -----------------------
    # TICKS
    # -----------------------
    ax.set_xticks(np.arange(len(all_regions)))
    ax.set_yticks(np.arange(len(all_regions)))

    ax.set_xticklabels(all_regions, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(all_regions, fontsize=9)

    # -----------------------
    # REMOVE SPINES (clean look)
    # -----------------------
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.tick_params(length=0)

    # -----------------------
    # TEXT ANNOTATIONS (ONLY SIGNIFICANT VALUES)
    # -----------------------
    threshold = matrix.values.max() * 0.1  # only show strong overlaps

    for i in range(len(all_regions)):
        for j in range(len(all_regions)):
            val = matrix.iloc[i, j]
            if i != j and val >= threshold:
                ax.text(
                    j,
                    i,
                    str(val),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="black"
                )

    # -----------------------
    # TITLE + COLORBAR
    # -----------------------
    ax.set_title(
        "Region Overlap Heatmap",
        fontsize=15,
        pad=12
    )

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.outline.set_visible(False)

    plt.tight_layout()

    # -----------------------
    # SAVE & SHOW
    # -----------------------
    save_path = output_path / filename
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()

    return pair_counts, matrix
