"""Assignment 4.39 — Visualizing Data Distributions Using Histograms.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

A histogram is the cheapest way to look at a distribution -- bin the
values, count what falls into each bin, draw a bar per bin. The
shape of the resulting bars tells you what no summary statistic
can: peaks, modes, gaps, asymmetry, the long tail you suspected
existed.

Five histogram patterns are produced and saved to
`outputs/figures/`:

    1. salary_distribution_hist.png
       Single column, default bin count -- baseline.

    2. salary_bin_comparison_hist.png
       Same column at 5 / 30 / 80 bins side-by-side. Shows that
       bin count is *itself* an analytical choice: too few hides
       structure, too many turns into noise.

    3. multi_column_distributions_hist.png
       2x3 grid, one histogram per numeric column, so the five
       different distribution shapes from 4.37 / 4.38 can be
       compared at a glance.

    4. salary_per_sector_hist.png
       Overlaid translucent histograms, one per sector. The same
       cross-group comparison the table from 4.38 told us, drawn.

    5. salary_with_central_tendency_hist.png
       Single histogram with mean and median lines drawn on top.
       The mean-vs-median gap from 4.37 becomes a visible offset.

Files are written to `outputs/figures/` (gitignored) so each
contributor regenerates them locally.

Run:
    python3 src/visualize_histograms.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BANNER_WIDTH = 72
FIGURES_DIR = Path(__file__).resolve().parent.parent / "outputs" / "figures"

SYNTHETIC_ROW_COUNT = 300
SYNTHETIC_SEED = 37

# Same per-sector lognormal parameters as 4.38 so the visual story
# matches the tabular comparison the reader has just seen.
SECTOR_SALARY_PARAMS: dict[str, tuple[float, float]] = {
    "Technology": (2.7, 0.45),
    "Finance": (2.6, 0.55),
    "Healthcare": (2.3, 0.35),
    "Retail": (2.0, 0.30),
    "Manufacturing": (2.1, 0.40),
}


# ---------------------------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------------------------
def generate_postings(
    n_rows: int = SYNTHETIC_ROW_COUNT, seed: int = SYNTHETIC_SEED
) -> pd.DataFrame:
    """300-row frame; salary sector-conditioned, plus 4 other shape variants."""
    rng = np.random.default_rng(seed)
    sectors = rng.choice(list(SECTOR_SALARY_PARAMS.keys()), size=n_rows)

    salaries = np.empty(n_rows, dtype="float64")
    for sector, (mu, sigma) in SECTOR_SALARY_PARAMS.items():
        mask = sectors == sector
        if mask.any():
            salaries[mask] = rng.lognormal(mu, sigma, size=mask.sum()).round(1)

    return pd.DataFrame(
        {
            "job_id": np.arange(7001, 7001 + n_rows, dtype="int64"),
            "sector": sectors,
            "experience_years": rng.integers(low=0, high=12, size=n_rows),
            "salary_lpa": salaries,
            "applications_received": rng.poisson(lam=8, size=n_rows),
            "interview_score": np.clip(
                rng.normal(loc=8.0, scale=1.2, size=n_rows), 1, 10
            ).round(1),
            "commute_minutes": rng.exponential(scale=35.0, size=n_rows).round(0),
        }
    )


# ---------------------------------------------------------------------------
# PLOT HELPERS — one figure per call, each call returns the path it wrote.
# ---------------------------------------------------------------------------
def ensure_figures_dir() -> Path:
    """Make sure the output directory exists; idempotent."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR


def plot_single_histogram(series: pd.Series, title: str, path: Path) -> Path:
    """Default-bin histogram for a single numeric Series."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(series.dropna(), bins="auto", color="steelblue", edgecolor="white")
    ax.set_title(title)
    ax.set_xlabel(series.name)
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_bin_comparison(series: pd.Series, path: Path) -> Path:
    """Same data at three bin counts -- shows that bin count is a *choice*."""
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    for ax, n_bins, label in zip(
        axes,
        (5, 30, 80),
        ("Under-binned (5)", "Reasonable (30)", "Over-binned (80)"),
    ):
        ax.hist(series.dropna(), bins=n_bins, color="steelblue", edgecolor="white")
        ax.set_title(f"{label}")
        ax.set_xlabel(series.name)
    axes[0].set_ylabel("Frequency")
    fig.suptitle(
        f"Bin count is an analytical choice — same column ({series.name}), three views",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_multi_column_grid(frame: pd.DataFrame, columns: list[str], path: Path) -> Path:
    """One histogram per numeric column in a 2x3 grid."""
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    for ax, column in zip(axes.flat, columns):
        ax.hist(
            frame[column].dropna(), bins="auto", color="steelblue", edgecolor="white"
        )
        ax.set_title(column)
        ax.set_xlabel(column)
        ax.set_ylabel("Frequency")
    # Hide any unused axes (in case columns < 6).
    for ax in axes.flat[len(columns) :]:
        ax.set_visible(False)
    fig.suptitle("Per-column distributions — five shapes at a glance", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_overlaid_per_group(
    frame: pd.DataFrame, group_col: str, target_col: str, path: Path
) -> Path:
    """Per-group histograms overlaid with transparency on the same axes."""
    fig, ax = plt.subplots(figsize=(8, 5))
    palette = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd")
    groups = sorted(frame[group_col].dropna().unique())
    for color, group in zip(palette, groups):
        ax.hist(
            frame.loc[frame[group_col] == group, target_col].dropna(),
            bins=24,
            alpha=0.45,
            label=group,
            color=color,
            edgecolor="white",
        )
    ax.set_title(f"{target_col} distribution per {group_col}")
    ax.set_xlabel(target_col)
    ax.set_ylabel("Frequency")
    ax.legend(title=group_col)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_with_central_tendency(series: pd.Series, path: Path) -> Path:
    """Histogram with mean and median drawn as vertical reference lines."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(series.dropna(), bins=30, color="steelblue", edgecolor="white")
    mean = float(series.mean())
    median = float(series.median())
    ax.axvline(
        mean, color="crimson", linestyle="--", linewidth=2, label=f"mean = {mean:.2f}"
    )
    ax.axvline(
        median,
        color="darkorange",
        linestyle="-",
        linewidth=2,
        label=f"median = {median:.2f}",
    )
    ax.set_title(f"{series.name} — mean vs median (gap = {mean - median:+.2f})")
    ax.set_xlabel(series.name)
    ax.set_ylabel("Frequency")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def print_banner(title: str) -> None:
    """Print a fixed-width banner."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def report_saved(label: str, path: Path) -> None:
    """One-line confirmation that a figure was written to disk."""
    print(f"  saved -> {path.relative_to(FIGURES_DIR.parent.parent)}   ({label})")


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Generate the five histogram artefacts described in the module docstring."""
    print_banner("Assignment 4.39 — Visualising Distributions with Histograms")
    ensure_figures_dir()

    frame = generate_postings()
    print(
        f"\n  Working frame: {frame.shape[0]} rows x {frame.shape[1]} columns,\n"
        f"  output dir: {FIGURES_DIR}\n"
    )

    numeric_cols = [
        "salary_lpa",
        "experience_years",
        "applications_received",
        "interview_score",
        "commute_minutes",
    ]

    # 1) Single histogram, default bins
    print_banner("1) Single histogram — default bin count")
    path = plot_single_histogram(
        frame["salary_lpa"],
        title="salary_lpa — default histogram (auto bins)",
        path=FIGURES_DIR / "salary_distribution_hist.png",
    )
    report_saved("baseline single histogram", path)
    print(
        "  Read: salary_lpa is right-skewed -- a single tall block on the\n"
        "  left and a long thin tail to the right. The shape is the story\n"
        "  the lognormal mean-vs-median gap from 4.37 was telling you."
    )

    # 2) Same data, three bin counts
    print_banner("2) Bin-count comparison — same data, three views")
    path = plot_bin_comparison(
        frame["salary_lpa"],
        path=FIGURES_DIR / "salary_bin_comparison_hist.png",
    )
    report_saved("5-bin / 30-bin / 80-bin contrast", path)
    print(
        "  Read: 5 bins hides the right tail (looks like one big lump);\n"
        "  30 bins shows the tail and the peak together; 80 bins introduces\n"
        "  spurious gaps from sample-size noise. 'auto' is a defensible\n"
        "  default (Pandas / matplotlib use Sturges or Freedman-Diaconis)."
    )

    # 3) 2x3 grid -- five distributions side by side
    print_banner("3) Multi-column grid — five distribution shapes at a glance")
    path = plot_multi_column_grid(
        frame,
        numeric_cols,
        path=FIGURES_DIR / "multi_column_distributions_hist.png",
    )
    report_saved("2x3 grid of all numeric columns", path)
    print(
        "  Read: salary and commute have visible right tails; experience\n"
        "  is a flat-ish uniform; interview_score is clipped at 10 and\n"
        "  bunches against the upper bound; applications_received looks\n"
        "  like a Poisson with a single peak around 8."
    )

    # 4) Overlaid per-sector
    print_banner("4) Overlaid per-sector — comparing distributions on one axis")
    path = plot_overlaid_per_group(
        frame,
        group_col="sector",
        target_col="salary_lpa",
        path=FIGURES_DIR / "salary_per_sector_hist.png",
    )
    report_saved("translucent overlay per sector", path)
    print(
        "  Read: Retail / Manufacturing concentrate at the lower end;\n"
        "  Finance / Technology peak higher and have visible right tails.\n"
        "  This is the picture that makes the 4.38 per-sector table click."
    )

    # 5) Histogram with mean and median lines
    print_banner("5) Single histogram + central-tendency reference lines")
    path = plot_with_central_tendency(
        frame["salary_lpa"],
        path=FIGURES_DIR / "salary_with_central_tendency_hist.png",
    )
    report_saved("mean and median annotated", path)
    mean_value = float(frame["salary_lpa"].mean())
    median_value = float(frame["salary_lpa"].median())
    print(
        f"  Annotated values: mean = {mean_value:.2f}, "
        f"median = {median_value:.2f}, "
        f"gap = {mean_value - median_value:+.2f}.\n"
        "  Read: when mean > median the dashed line sits to the *right*\n"
        "  of the solid line -- exactly the visual fingerprint of a\n"
        "  right-skewed distribution."
    )

    # Cheat sheet
    print_banner("Histogram cheat sheet")
    print(
        "  ax.hist(series, bins='auto')              -> default histogram\n"
        "  ax.hist(series, bins=N)                   -> explicit bin count\n"
        "  ax.hist(series, bins=[edges])             -> explicit bin edges\n"
        "  ax.hist(group, alpha=0.45, label=name)    -> overlay per group\n"
        "  ax.axvline(mean,  linestyle='--')         -> annotate central tendency\n"
        "  fig, axes = plt.subplots(2, 3, ...)       -> grid for many columns\n"
        "  fig.savefig(path, dpi=120); plt.close()   -> always close to free memory\n"
        "  WHEN TO PREFER WHICH BIN COUNT\n"
        "    small N           -> few bins (5-15)\n"
        "    medium-large N    -> 'auto' or 20-40\n"
        "    huge N (millions) -> use a KDE or a 2-D heatmap, not a histogram"
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
