"""
Plotting functions for all champion properties.
"""
import matplotlib.transforms as mtransforms
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from solver.utils import paths
from solver.plots._plot_utils import (
    _map_colors,
    _filter_rows,
    _finalize_plot,
    _make_top_bottom_title,
    _safe_eval,
)


def plot_release_year_distribution(
        df: pd.DataFrame,
        *,
        output_path=paths.results,
        filename="loldle_release_year_distribution.png",
        ax=None,
        show=True,
        save=False,
        top_k=None,
        bottom_k=None,
        style="ggplot",
):
    """
    Vertical bar chart of champion release year distribution
    with median reference line.
    """

    # -----------------------
    # LOAD & FILTER
    # -----------------------
    df = _filter_rows(df, top_k, bottom_k)

    # Catch KeyError that is raised when the df has 'release_date' as the column instead
    try:
        df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
    except KeyError:
        df = df.rename(columns={"release_date": "release_year"})
        df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")

    df = df.dropna(subset=["release_year"])
    df["release_year"] = df["release_year"].astype(int)

    # -----------------------
    # FULL YEAR RANGE (IMPORTANT)
    # -----------------------
    years = np.arange(df["release_year"].min(), df["release_year"].max() + 1)

    yearly_counts = (
        df.groupby("release_year")
        .size()
        .reindex(years, fill_value=0)
    )

    total = len(df)
    max_val = yearly_counts.max()

    median_year = df["release_year"].median()
    mean_year = df["release_year"].mean()

    # -----------------------
    # STYLE & PLOT
    # -----------------------
    plt.style.use(style)

    if ax is None:
        fig, ax = plt.subplots(figsize=(14, 6))
        own_figure = True
    else:
        fig = ax.figure
        own_figure = False

    # -----------------------
    # BARS (single uniform color)
    # -----------------------
    bar_color = "#4FC3F7"

    ax.bar(
        years,
        yearly_counts.values,
        color=bar_color,
        alpha=0.75,
        width=0.85,
        label="Champions Released"
    )

    # -----------------------
    # AXES
    # -----------------------
    ax.set_xlabel("Release Year", labelpad=10)
    ax.set_ylabel("Number of Champions", size=14, labelpad=10)

    ax.set_xticks(years)
    ax.set_xticklabels(years)

    ax.set_ylim(0, max_val * 1.15)
    plt.margins(x=0.01)

    # -----------------------
    # LABELS
    # -----------------------
    for i, (year, v) in enumerate(yearly_counts.items()):
        if v == 0:
            continue

        pct = (v / total) * 100

        txt = ax.text(
            year,
            v + max_val * 0.02,
            f"{v}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=8,
            color="black",
        )

        txt.set_path_effects([
            path_effects.Stroke(linewidth=3, foreground="white"),
            path_effects.Normal()
        ])

    # -----------------------
    # MEDIAN + MEAN LINES
    # -----------------------
    ax.axvline(
        median_year,
        color="#E57373",
        linestyle="--",
        linewidth=2,
        label=f"Median Year ({median_year:.0f})"
    )

    ax.axvline(
        mean_year,
        color="#FFD54F",
        linestyle="--",
        linewidth=2,
        label=f"Mean Year ({mean_year:.1f})"
    )

    # -----------------------
    # TITLE + LEGEND
    # -----------------------
    title = _make_top_bottom_title(
        "Champion Release Year Distribution",
        top_k=top_k,
        bottom_k=bottom_k,
    )
    ax.set_title(title, size=18, pad=10)

    ax.legend()

    # -----------------------
    # SAVE & RETURN
    # -----------------------
    if own_figure:
        plt.tight_layout()
        return _finalize_plot(fig, output_path, filename, save, show)
    else:
        return ax


def plot_region_distribution(
        df: pd.DataFrame,
        *,
        output_path=paths.results,
        filename="loldle_region_distribution.png",
        ax=None,
        show=True,
        save=False,
        top_k=None,
        bottom_k=None,
        style="classic",
):
    """
    Horizontal bar chart of region distribution.
    Handles multi-region entries via explode.
    """

    # -----------------------
    # LOAD
    # -----------------------
    df = _filter_rows(df, top_k, bottom_k)

    # Convert stringified lists -> real lists
    df["regions"] = df["regions"].apply(_safe_eval)

    # -----------------------
    # EXPLODE (HANDLE OVERLAP)
    # -----------------------
    df_exploded = df.explode("regions")

    df_exploded["regions"] = (
        df_exploded["regions"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    # -----------------------
    # COUNT
    # -----------------------
    region_counts = df_exploded["regions"].value_counts()

    total = len(df_exploded)
    max_val = region_counts.max()

    # -----------------------
    # COLORS
    # -----------------------
    cmap = plt.get_cmap("tab20")
    colors = [cmap(i % 20) for i in range(len(region_counts))]

    # -----------------------
    # PLOT (HORIZONTAL)
    # -----------------------
    plt.style.use(style)

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, max(5, len(region_counts) * 0.5)))
        own_figure = True
    else:
        fig = ax.figure
        own_figure = False

    y_pos = range(len(region_counts))

    ax.barh(
        y_pos,
        region_counts.values,
        color=colors,
        height=0.75
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(region_counts.index)

    ax.invert_yaxis()
    ax.set_xlim(0, max_val * 1.15)

    plt.margins(y=0.01)

    # -----------------------
    # LABELS
    # -----------------------
    for i, (region, v) in enumerate(region_counts.items()):
        pct = (v / total) * 100

        ax.text(
            v + max_val * 0.02,
            i,
            f"{v} ({pct:.1f}%)",
            va="center",
            ha="left",
            fontsize=9
        )

    ax.set_xlabel("Occurrences", size=13)

    title = _make_top_bottom_title(
        "Champion Region Distribution",
        top_k=top_k, bottom_k=bottom_k
    )
    ax.set_title(title, size=15)

    # -----------------------
    # SAVE & SHOW
    # -----------------------
    if own_figure:
        plt.tight_layout()
        return _finalize_plot(fig, output_path, filename, save, show)
    else:
        return ax


def plot_range_type_distribution(
        df: pd.DataFrame,
        *,
        output_path=paths.results,
        filename="loldle_range_type_distribution.png",
        ax=None,
        show=True,
        save=False,
        top_k=None,
        bottom_k=None,
        style="classic"
):
    """
    Plot distribution of range_type column into 3 categories:
    Melee, Ranged, Both.
    """

    # -----------------------
    # LOAD
    # -----------------------
    df = _filter_rows(df, top_k, bottom_k)
    df["range_type"] = df["range_type"].apply(_safe_eval)

    # -----------------------
    # CLASSIFY
    # -----------------------
    def classify(rt):
        rt = set(rt)
        if rt == {"Melee"}:
            return "Melee"
        elif rt == {"Ranged"}:
            return "Ranged"
        else:
            return "Both"

    df["range_group"] = df["range_type"].apply(classify)

    counts = df["range_group"].value_counts().reindex(
        ["Melee", "Ranged", "Both"],
        fill_value=0
    )

    total = len(df)
    max_val = counts.max()

    # -----------------------
    # COLORS
    # -----------------------
    colors = ["#d95f02", "#1b9e77", "#7570b3"]

    # -----------------------
    # PLOT (HORIZONTAL)
    # -----------------------
    plt.style.use(style)

    if ax is None:
        fig, ax = plt.subplots(figsize=(3, 1))
        own_figure = True
    else:
        fig = ax.figure
        own_figure = False

    y_pos = range(len(counts))

    ax.barh(
        y_pos,
        counts.values,
        color=colors,
        height=0.6
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(counts.index)

    ax.invert_yaxis()
    ax.set_xlim(0, max_val * 1.15)

    # -----------------------
    # LABELS
    # -----------------------
    for i, (label, v) in enumerate(counts.items()):
        pct = (v / total) * 100
        ax.text(
            v + max_val * 0.02,
            i,
            f"{v} ({pct:.1f}%)",
            va="center",
            ha="left",
            fontsize=10
        )

    ax.set_xlabel("Number of Champions", size=12)

    title = _make_top_bottom_title(
        "Champion Range Type Distribution",
        top_k=top_k, bottom_k=bottom_k
    )
    ax.set_title(title, size=14)

    plt.tight_layout()

    # -----------------------
    # SAVE & SHOW
    # -----------------------
    if own_figure:
        plt.tight_layout()
        return _finalize_plot(fig, output_path, filename, save, show)
    else:
        return ax


def plot_resource_distribution(
        df: pd.DataFrame,
        *,
        output_path=paths.results,
        filename="loldle_resource_distribution.png",
        ax=None,
        show=True,
        save=False,
        top_k=None,
        bottom_k=None,
        style="classic",
):
    """
    Plot horizontal bar chart of the 'resource' column distribution.
    """

    # -----------------------
    # LOAD
    # -----------------------
    df = _filter_rows(df, top_k, bottom_k)
    df["resource"] = (
        df["resource"]
            .astype(str)
            .str.strip()
            .str.title()
    )

    # -----------------------
    # COUNT
    # -----------------------
    resource_counts = df["resource"].value_counts()

    total = len(df)
    max_val = resource_counts.max()

    # -----------------------
    # COLORS
    # -----------------------
    cmap = plt.get_cmap("tab20")
    colors = [cmap(i % 20) for i in range(len(resource_counts))]

    # -----------------------
    # PLOT
    # -----------------------
    plt.style.use(style)

    if ax is None:
        fig, ax = plt.subplots(figsize=(12, max(8, len(resource_counts) * 0.5)))
        own_figure = True
    else:
        fig = ax.figure
        own_figure = False

    y_pos = range(len(resource_counts))

    ax.barh(
        y_pos,
        resource_counts.values,
        color=colors,
        height=0.8
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(resource_counts.index)

    ax.invert_yaxis()  # highest value on top

    ax.set_xlim(0, max_val * 1.15)

    plt.margins(y=0.01)

    # -----------------------
    # LABELS
    # -----------------------
    for i, (resource, v) in enumerate(resource_counts.items()):
        pct = (v / total) * 100
        label = f"{v} ({pct:.1f}%)"

        ax.text(
            v + max_val * 0.02,
            i,
            label,
            va="center",
            ha="left",
            fontsize=9,
        )

    ax.set_xlabel("Count", size=14, labelpad=10)
    title = _make_top_bottom_title(
        "Resource Distribution",
        top_k=top_k, bottom_k=bottom_k
    )
    ax.set_title(title, size=18, pad=10)

    # -----------------------
    # SAVE & SHOW
    # -----------------------
    if own_figure:
        plt.tight_layout()
        return _finalize_plot(fig, output_path, filename, save, show)
    else:
        return ax


def plot_species_distribution(
        df: pd.DataFrame,
        *,
        output_path=paths.results,
        filename="loldle_champion_species_distribution.png",
        ax=None,
        show=True,
        save=False,
        top_k=None,
        bottom_k=None,
        style="classic",
):
    """
    Plot vertical bar chart of champion distribution by species.
    Handles multi-species champions via explode.
    Groups singletons into 'Other'.
    """

    # -----------------------
    # LOAD & PREP
    # -----------------------
    df = _filter_rows(df, top_k, bottom_k)
    df["species"] = df["species"].apply(_safe_eval)
    df_exploded = df.explode("species")

    df_exploded["species"] = (
        df_exploded["species"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    species_counts = df_exploded["species"].value_counts()

    # -----------------------
    # GROUP RARE SPECIES
    # -----------------------

    common = species_counts[species_counts > 1].copy()
    rare = species_counts[species_counts == 1]

    # Add "Others" if needed for only 1 counts
    if not rare.empty:
        common.loc["Others"] = rare.sum()

    species_counts = common.sort_values(ascending=False)

    total = len(df)
    max_val = species_counts.max()

    # -----------------------
    # COLORS
    # -----------------------
    cmap = plt.get_cmap("tab20")
    colors = [cmap(i % 20) for i in range(len(species_counts))]

    # -----------------------
    # PLOT
    # -----------------------
    plt.style.use(style)

    if ax is None:
        fig, ax = plt.subplots(figsize=(max(12, len(species_counts) * 0.6), 6))
        own_figure = True
    else:
        fig = ax.figure
        own_figure = False

    x_pos = range(len(species_counts))

    ax.bar(x_pos, species_counts.values, color=colors,width=0.9)

    ax.set_xlim(-0.5, len(species_counts) - 0.5)
    ax.set_ylim(0, max_val * 1.15)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(species_counts.index, rotation=45, ha="right")

    dx = 6  # pixels

    # Species labels offset
    for label in ax.get_xticklabels():
        offset = mtransforms.ScaledTranslation(dx / 72, 0, fig.dpi_scale_trans)
        label.set_transform(label.get_transform() + offset)

    plt.margins(x=0.01)

    # Bar labels
    for i, (species, v) in enumerate(species_counts.items()):
        pct = (v / total) * 100

        label = f"{v}\n({pct:.1f}%)"

        ax.text(
            i,
            v + max_val * 0.02,
            label,
            ha="center",
            va="bottom",
            color="black",
            fontsize=9,
        )

    ax.set_ylabel("Number of Champions", size=14, labelpad=10)
    title = _make_top_bottom_title(
        "Champion Distribution by Species",
        top_k=top_k, bottom_k=bottom_k,
    )
    ax.set_title(title, size=18, pad=10)

    # -----------------------
    # SAVE & SHOW
    # -----------------------
    if own_figure:
        plt.tight_layout()
        return _finalize_plot(fig, output_path, filename, save, show)
    else:
        return ax


def plot_gender_distribution(
        df: pd.DataFrame,
        *,
        output_path=paths.results,
        filename="loldle_champion_gender_distribution.png",
        ax=None,
        show=True,
        save=False,
        top_k=None,
        bottom_k=None,
        style="classic",
):
    """
    Plot horizontal bar chart of champion distribution by gender.
    Dynamically handles new/unexpected gender categories.
    """

    # -----------------------
    # LOAD & PREP
    # -----------------------
    df = _filter_rows(df, top_k, bottom_k)
    gender_counts = df["gender"].value_counts().sort_values(ascending=True)

    total = len(df)
    max_val = gender_counts.max()

    # -----------------------
    # COLOR HANDLING
    # -----------------------
    base_colors = {
        "Male": "#64B5F6",
        "Female": "#E57373",
        "Other": "#BA68C8",
    }

    colors = _map_colors(gender_counts.index, base_colors)

    # -----------------------
    # PLOT
    # -----------------------
    plt.style.use(style)

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
        own_figure = True
    else:
        fig = ax.figure
        own_figure = False

    ax.barh(
        gender_counts.index,
        gender_counts.values,
        color=colors,
    )

    ax.set_xlim(0, max_val * 1.1)

    # Labels (adaptive)
    for i, v in enumerate(gender_counts.values):
        pct = (v / total) * 100
        label = f"{v} ({pct:.1f}%)"

        inside = v > max_val * 0.15

        ax.text(
            v - max_val * 0.02 if inside else v + max_val * 0.02,
            i,
            label,
            va="center",
            ha="right" if inside else "left",
            color="white" if inside else "black",
            fontsize=12,
            fontweight="bold" if inside else None,
        )

    ax.set_xlabel("Number of Champions", size=15, labelpad=10)
    title = _make_top_bottom_title(
        "Champion Distribution by Gender",
        top_k=top_k,
        bottom_k=bottom_k,
    )
    ax.set_title(title, size=18, pad=10)

    # -----------------------
    # SAVE & SHOW
    # -----------------------
    if own_figure:
        plt.tight_layout()
        return _finalize_plot(fig, output_path, filename, save, show)
    else:
        return ax


def plot_position_distribution(
        df: pd.DataFrame,
        *,
        output_path=paths.results,
        filename="loldle_champion_position_distribution.png",
        ax=None,
        save=False,
        show=True,
        top_k: int | None = None,
        bottom_k: int | None = None,
        style="fivethirtyeight",
):
    """
    Plot horizontal bar chart of champion distribution by position.
    """

    # -----------------------
    # LOAD
    # -----------------------
    df = _filter_rows(df, top_k, bottom_k)
    df["positions"] = df["positions"].apply(_safe_eval)

    # -----------------------
    # EXPLODE AFTER FILTERING
    # -----------------------
    df_exploded = df.explode("positions")

    order = ["Support", "Bottom", "Middle", "Jungle", "Top"]

    position_counts = df_exploded["positions"].value_counts()

    # keep full categorical order if no filtering bias is needed
    if top_k is None and bottom_k is None:
        position_counts = position_counts.reindex(order)

    position_counts = position_counts.sort_values(ascending=True)

    total = len(df_exploded)
    max_val = position_counts.max()

    # -----------------------
    # PLOT
    # -----------------------
    plt.style.use(style)

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
        own_figure = True
    else:
        fig = ax.figure
        own_figure = False

    colors = {
        "Top": "#E57373",
        "Jungle": "#81C784",
        "Middle": "#BA68C8",
        "Bottom": "#64B5F6",
        "Support": "#FFD54F"
    }

    ax.barh(
        position_counts.index,
        position_counts.values,
        color=[colors.get(pos, "#999999") for pos in position_counts.index],
    )

    ax.set_xlim(0, max_val * 1.1)

    for i, v in enumerate(position_counts.values):
        pct = (v / total) * 100
        label = f"{v} ({pct:.1f}%)"

        inside = v > max_val * 0.15

        ax.text(
            v - max_val * 0.02 if inside else v + max_val * 0.02,
            i,
            label,
            va="center",
            ha="right" if inside else "left",
            color="white" if inside else "black",
            fontsize=12,
            fontweight="bold" if inside else None,
        )

    ax.set_xlabel("Number of Champions", size=15, labelpad=10)
    title = _make_top_bottom_title(
        "Champion Distribution by Position",
        top_k=top_k,
        bottom_k=bottom_k,
    )
    ax.set_title(title, size=18, pad=10)

    if own_figure:
        plt.tight_layout()
        return _finalize_plot(fig, output_path, filename, save, show)
    else:
        return ax
