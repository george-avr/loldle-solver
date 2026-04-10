"""
Internal plot helpers.
"""
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import ast
import pandas as pd


def _safe_eval(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            return ast.literal_eval(x)
        except ValueError:
            return x
    return x


def _make_top_bottom_title(
    base_title: str,
    top_k: int | None = None,
    bottom_k: int | None = None,
) -> str:
    """
    Create a dynamic plot title depending on top_k / bottom_k filtering.
    """

    if top_k is not None and bottom_k is not None:
        raise ValueError("Use only one of top_k or bottom_k.")

    if top_k is not None:
        return f"Top {top_k} {base_title}"

    if bottom_k is not None:
        return f"Bottom {bottom_k} {base_title}"

    return base_title


def _finalize_plot(
    fig: plt.Figure,
    output_path,
    filename: str,
    save: bool = True,
    show: bool = True,
    dpi: int = 300,
):
    """
    Handle saving and/or displaying a matplotlib figure.

    Returns
    -------
    Path | None
        Path to saved file if save=True, otherwise None.
    """

    save_path = None

    if save:
        save_path = output_path / filename
        fig.savefig(save_path, dpi=dpi)

    if show:
        plt.show()
    else:
        plt.close(fig)

    return save_path


def _filter_rows(df: pd.DataFrame, top_k: int | None, bottom_k: int | None) -> pd.DataFrame:
    """
    Filters raw dataframe rows BEFORE any aggregation.
    """

    if top_k is not None and bottom_k is not None:
        raise ValueError("Use only one of top_k or bottom_k.")

    if top_k is not None:
        return df.head(top_k)

    if bottom_k is not None:
        return df.tail(bottom_k)

    return df


def _map_colors(categories, base_colors, default="#90A4AE"):
    return [base_colors.get(c, default) for c in categories]

# =========================
# STYLING HELPERS
# =========================
def _style_axes(ax):
    ax.margins(x=0)
    ax.set_axisbelow(True)
    ax.set_facecolor((0, 0, 0, 0.45))
    ax.set_zorder(1)

    # vertical grid only
    ax.xaxis.grid(True, linestyle='-', linewidth=0.8, alpha=0.3, color='white')
    ax.yaxis.grid(False)

    # remove borders
    for spine in ax.spines.values():
        spine.set_visible(False)

    # ticks
    ax.tick_params(axis='x', labelsize=14, colors='white')
    ax.tick_params(axis='y', labelsize=12, colors='white')
    ax.tick_params(axis='y', length=0)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_path_effects([
            pe.Stroke(linewidth=2, foreground="black"),
            pe.Normal()
        ])

def _styled_title(ax, text):
    title = ax.set_title(text, size=23, pad=15, color="white")
    title.set_path_effects([
        pe.Stroke(linewidth=3, foreground="black"),
        pe.Normal()
    ])


def _styled_xlabel(ax, text):
    label = ax.set_xlabel(
        text,
        size=18,
        labelpad=10,
        color="white"
    )
    label.set_path_effects([
        pe.Stroke(linewidth=1.5, foreground="black"),
        pe.Normal()
    ])


# =========================
# PLOTTING HELPERS
# =========================
def _barh_with_shadow(ax, y, x, color, shadow_color="black"):
    # shadow
    ax.barh(y, x, color=shadow_color, alpha=0.2, height=0.9, zorder=1)

    # main bars
    ax.barh(y, x, color=color, alpha=0.9, height=0.5, zorder=2)


# =========================
# BACKGROUND
# =========================
def _add_cover_background(fig, img):
    fig_w, fig_h = fig.get_size_inches()
    fig_ratio = fig_w / fig_h

    img_h, img_w = img.shape[:2]
    img_ratio = img_w / img_h

    # crop to match aspect ratio (CSS "cover")
    if img_ratio > fig_ratio:
        new_w = int(img_h * fig_ratio)
        start = (img_w - new_w) // 2
        cropped = img[:, start:start + new_w]
    else:
        new_h = int(img_w / fig_ratio)
        start = (img_h - new_h) // 2
        cropped = img[start:start + new_h, :]

    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.imshow(cropped, aspect='auto')
    ax_bg.axis("off")

    # dark overlay
    ax_bg.add_patch(
        plt.Rectangle(
            (0, 0), 1, 1,
            transform=ax_bg.transAxes,
            color="black",
            alpha=0.55,
            zorder=2
        )
    )
