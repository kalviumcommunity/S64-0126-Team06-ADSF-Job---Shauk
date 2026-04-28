"""Assignment 4.40 — Visualizing Data Distributions Using Boxplots.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

A boxplot is a histogram's older, more compact cousin. Where a
histogram shows you *how* the values fall, a boxplot shows you
*where* the quartiles sit and *which* points sit outside the
typical spread -- a 5-summary picture (min within whiskers, Q1,
median, Q3, max within whiskers) plus the outlier dots.

The killer feature is *side-by-side group comparison*: ten
sectors fit on one axis as ten boxes; the same data drawn as ten
overlaid histograms is unreadable. This script demonstrates that
plus the standard 1.5×IQR outlier rule that boxplots embed by
default.

Five boxplot patterns are produced and saved to
`outputs/figures/`:

    1. salary_boxplot.png
       Single-column boxplot -- the 5-summary view.

    2. multi_column_z_boxplot.png
       Five numeric columns z-scored (mean=0, std=1) so they
       share an axis -- compare spread across different units.

    3. salary_per_sector_boxplot.png
       One box per sector, sorted by median. The killer
       comparison view.

    4. salary_outlier_count_boxplot.png
       Boxplot annotated with the count of 1.5*IQR outliers
       per box -- detection without a separate table.

    5. salary_boxplot_with_jitter.png
       Boxplot + jittered scatter overlay, so the *density* the
       box hides is also visible. Useful when n is small enough.

Files are written to `outputs/figures/` (gitignored).

Run:
    python3 src/visualize_boxplots.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BANNER_WIDTH = 72
FIGURES_DIR = Path(__file__).resolve().parent.parent / "outputs" / "figures"

SYNTHETIC_ROW_COUNT = 300
SYNTHETIC_SEED = 41

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
    """300-row frame with sector-conditioned salary + 4 other distributions."""
    rng = np.random.default_rng(seed)
    sectors = rng.choice(list(SECTOR_SALARY_PARAMS.keys()), size=n_rows)

    salaries = np.empty(n_rows, dtype="float64")
    for sector, (mu, sigma) in SECTOR_SALARY_PARAMS.items():
        mask = sectors == sector
        if mask.any():
            salaries[mask] = rng.lognormal(mu, sigma, size=mask.sum()).round(1)

    return pd.DataFrame(
        {
            "job_id": np.arange(8001, 8001 + n_rows, dtype="int64"),
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


def count_iqr_outliers(values: pd.Series) -> int:
    """Number of values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR] -- the boxplot rule."""
    q1, q3 = values.quantile(0.25), values.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return int(((values < low) | (values > high)).sum())


# ---------------------------------------------------------------------------
# PLOT HELPERS
# ---------------------------------------------------------------------------
def ensure_figures_dir() -> Path:
    """Idempotently create the output directory."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR


def plot_single_boxplot(series: pd.Series, path: Path) -> Path:
    """Single-column boxplot showing the 5-summary + IQR outliers."""
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.boxplot(
        series.dropna(),
        vert=True,
        patch_artist=True,
        boxprops={"facecolor": "lightsteelblue"},
    )
    ax.set_xticklabels([series.name])
    ax.set_ylabel(series.name)
    ax.set_title(f"{series.name} — 5-summary boxplot")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_multi_column_z_boxplot(
    frame: pd.DataFrame, columns: list[str], path: Path
) -> Path:
    """Z-score every column (mean=0, std=1) so they share the y-axis."""
    z = frame[columns].apply(lambda s: (s - s.mean()) / s.std())
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.boxplot(
        [z[c].dropna() for c in columns],
        labels=columns,
        patch_artist=True,
        boxprops={"facecolor": "lightsteelblue"},
    )
    ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax.set_ylabel("z-score (std away from column mean)")
    ax.set_title("Cross-column spread comparison — every column z-scored")
    plt.setp(ax.get_xticklabels(), rotation=12, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_per_group_boxplot(
    frame: pd.DataFrame, group_col: str, target_col: str, path: Path
) -> Path:
    """One box per group, sorted by median (descending) so high earners are first."""
    grouped = (
        frame.groupby(group_col, observed=True)[target_col]
        .apply(lambda s: s.dropna().to_numpy())
        .sort_index()
    )
    medians = {g: float(np.median(arr)) for g, arr in grouped.items()}
    order = sorted(grouped.index, key=lambda g: -medians[g])

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.boxplot(
        [grouped.loc[g] for g in order],
        labels=order,
        patch_artist=True,
        boxprops={"facecolor": "lightsteelblue"},
    )
    ax.set_ylabel(target_col)
    ax.set_xlabel(group_col)
    ax.set_title(f"{target_col} per {group_col} — sorted by median (high first)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_per_group_with_outlier_counts(
    frame: pd.DataFrame, group_col: str, target_col: str, path: Path
) -> Path:
    """Per-group boxplot annotated with the 1.5*IQR outlier count over each box."""
    grouped = frame.groupby(group_col, observed=True)[target_col].apply(
        lambda s: s.dropna().to_numpy()
    )
    order = sorted(grouped.index)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.boxplot(
        [grouped.loc[g] for g in order],
        labels=order,
        patch_artist=True,
        boxprops={"facecolor": "lightsteelblue"},
    )

    # Annotate the count of IQR outliers above each box.
    y_top = max(np.max(grouped.loc[g]) for g in order)
    for i, group in enumerate(order, start=1):
        outliers = count_iqr_outliers(pd.Series(grouped.loc[group]))
        ax.text(
            i,
            y_top * 1.04,
            f"out: {outliers}",
            ha="center",
            va="bottom",
            fontsize=9,
            color="firebrick",
        )

    ax.set_ylabel(target_col)
    ax.set_xlabel(group_col)
    ax.set_title(
        f"{target_col} per {group_col} — 1.5*IQR outlier count per box (in red)"
    )
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_boxplot_with_jitter(series: pd.Series, path: Path) -> Path:
    """Boxplot + jittered scatter so the density behind the box is visible."""
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.boxplot(
        series.dropna(),
        vert=True,
        patch_artist=True,
        boxprops={"facecolor": "lightsteelblue"},
        widths=0.4,
    )
    rng = np.random.default_rng(0)
    jitter = rng.normal(loc=1.0, scale=0.06, size=len(series.dropna()))
    ax.scatter(
        jitter,
        series.dropna(),
        s=8,
        alpha=0.45,
        color="darkblue",
    )
    ax.set_xticklabels([series.name])
    ax.set_ylabel(series.name)
    ax.set_title(
        f"{series.name} — boxplot + jittered points (n={len(series.dropna())})"
    )
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
    """Generate the five boxplot artefacts described in the docstring."""
    print_banner("Assignment 4.40 — Visualising Distributions with Boxplots")
    ensure_figures_dir()
    frame = generate_postings()
    numeric_cols = [
        "salary_lpa",
        "experience_years",
        "applications_received",
        "interview_score",
        "commute_minutes",
    ]
    print(
        f"\n  Working frame: {frame.shape[0]} rows x {frame.shape[1]} columns,\n"
        f"  output dir:    {FIGURES_DIR}\n"
    )

    # 1) Single-column boxplot
    print_banner("1) Single-column boxplot — the 5-summary view")
    path = plot_single_boxplot(frame["salary_lpa"], FIGURES_DIR / "salary_boxplot.png")
    report_saved("single column", path)
    iqr_outliers = count_iqr_outliers(frame["salary_lpa"])
    median_value = float(frame["salary_lpa"].median())
    q1 = float(frame["salary_lpa"].quantile(0.25))
    q3 = float(frame["salary_lpa"].quantile(0.75))
    print(
        f"  median = {median_value:.2f}, Q1 = {q1:.2f}, Q3 = {q3:.2f}, "
        f"IQR = {q3 - q1:.2f}\n"
        f"  1.5*IQR outliers: {iqr_outliers} dots above the upper whisker.\n"
        "  Read: a boxplot is a 5-number summary -- min(within), Q1, median,\n"
        "  Q3, max(within) -- plus the dots that fall outside 1.5*IQR."
    )

    # 2) Multi-column z-score boxplot
    print_banner("2) Multi-column z-score boxplot — comparable spread")
    path = plot_multi_column_z_boxplot(
        frame, numeric_cols, FIGURES_DIR / "multi_column_z_boxplot.png"
    )
    report_saved("z-scored cross-column spread", path)
    print(
        "  Why z-score: salary in LPA and commute in minutes can't share an\n"
        "  axis directly. After (x - mean) / std, every column is on the same\n"
        "  unit-free scale and the boxplot widths are honestly comparable."
    )

    # 3) Per-sector boxplot
    print_banner("3) Per-sector boxplot — comparing groups within one column")
    path = plot_per_group_boxplot(
        frame, "sector", "salary_lpa", FIGURES_DIR / "salary_per_sector_boxplot.png"
    )
    report_saved("per-sector salary", path)
    per_sector = (
        frame.groupby("sector", observed=True)["salary_lpa"]
        .agg(["median", "count"])
        .round(2)
        .sort_values("median", ascending=False)
    )
    print("\n  Per-sector medians (sorted high -> low):")
    print(per_sector.to_string())

    # 4) Per-sector boxplot with outlier counts annotated
    print_banner("4) Per-sector boxplot + 1.5*IQR outlier count annotations")
    path = plot_per_group_with_outlier_counts(
        frame,
        "sector",
        "salary_lpa",
        FIGURES_DIR / "salary_outlier_count_boxplot.png",
    )
    report_saved("outlier count per sector", path)
    per_sector_outliers = {
        sector: count_iqr_outliers(frame.loc[frame["sector"] == sector, "salary_lpa"])
        for sector in sorted(frame["sector"].unique())
    }
    for sector, count in per_sector_outliers.items():
        print(f"  {sector:<14} -> {count} IQR outlier(s)")
    print(
        "  Read: outlier count is a quick anomaly screen per group. Sectors\n"
        "  with disproportionately many outliers either have heavy-tailed\n"
        "  distributions or genuine data-quality issues worth investigating."
    )

    # 5) Boxplot + jitter overlay
    print_banner("5) Boxplot + jittered points — what the box hides")
    path = plot_boxplot_with_jitter(
        frame["salary_lpa"], FIGURES_DIR / "salary_boxplot_with_jitter.png"
    )
    report_saved("box + jitter overlay", path)
    print(
        "  Read: the box collapses 300 rows into a 5-summary; the jitter\n"
        "  shows you the underlying density. Where points crowd, the\n"
        "  distribution has a peak; where points thin, a gap. Use jitter\n"
        "  whenever n is small enough that individual points are still\n"
        "  meaningful (under a few thousand)."
    )

    # Cheat sheet
    print_banner("Boxplot cheat sheet")
    print(
        "  ax.boxplot(values)                          -> single box\n"
        "  ax.boxplot([v1, v2, v3], labels=[...])      -> multi-box\n"
        "  ax.boxplot(values, patch_artist=True,\n"
        "            boxprops={'facecolor': ...})      -> filled colour\n"
        "  Q1 - 1.5*IQR / Q3 + 1.5*IQR                 -> matplotlib whiskers\n"
        "  count_iqr_outliers(series)                  -> numeric anomaly count\n"
        "  jittered scatter on top                     -> density behind the box\n"
        "  WHEN HISTOGRAM, WHEN BOXPLOT?\n"
        "    histogram -> shape detail (peaks, modes, gaps)\n"
        "    boxplot   -> compact comparison across many columns or groups"
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
