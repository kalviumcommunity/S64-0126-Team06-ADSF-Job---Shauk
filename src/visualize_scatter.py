"""Assignment 4.42 — Exploring Relationships Between Variables Using Scatter Plots.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

A scatter plot is the right chart for the question "do these two
columns move together?" -- one observation per point, x and y
positions reflecting two variables, the cloud's shape telling you
the relationship's direction, strength, and any outliers.

This script generates a 250-row synthetic frame in which **salary
is a real function of experience plus sector premium plus noise**,
so the scatter actually has a positive correlation to find. Then
it walks four scatter patterns:

    1. experience_salary_scatter.png
       Basic two-variable scatter -- the relationship.

    2. experience_salary_per_sector_scatter.png
       Same scatter, colour-coded by sector. Cluster structure
       per group becomes visible.

    3. experience_salary_with_trendline_scatter.png
       Adds a least-squares trend line and reports Pearson r in
       the legend.

    4. experience_salary_outliers_scatter.png
       Highlights points whose y-distance from the trend line
       exceeds 2 std (residual outliers) -- the analogue of the
       boxplot's 1.5*IQR rule, applied to the *relationship*.

Files are written to `outputs/figures/` (gitignored).

Run:
    python3 src/visualize_scatter.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BANNER_WIDTH = 76
FIGURES_DIR = Path(__file__).resolve().parent.parent / "outputs" / "figures"

SYNTHETIC_ROW_COUNT = 250
SYNTHETIC_SEED = 53

# Sector premium (added to base salary mean, in LPA). Models the
# fact that the same experience is paid more in some sectors than
# others -- a real-world pattern the colour-coded scatter exposes.
SECTOR_PREMIUM_LPA: dict[str, float] = {
    "Technology": 5.0,
    "Finance": 4.0,
    "Healthcare": 1.5,
    "Manufacturing": 0.0,
    "Retail": -1.0,
}


# ---------------------------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------------------------
def generate_postings_with_experience_salary_link(
    n_rows: int = SYNTHETIC_ROW_COUNT, seed: int = SYNTHETIC_SEED
) -> pd.DataFrame:
    """Build a frame where salary = base + slope * experience + sector + noise.

    Slope of ~0.9 LPA per year of experience produces a clear positive
    correlation with realistic noise. Sector adds a vertical offset so
    the scatter's per-sector colouring shows parallel bands when the
    relationship is the same shape across groups.
    """
    rng = np.random.default_rng(seed)
    sectors = rng.choice(list(SECTOR_PREMIUM_LPA.keys()), size=n_rows)
    experience = rng.integers(low=0, high=15, size=n_rows)

    base = 6.0  # entry-level base in LPA
    slope = 0.90  # LPA gained per year of experience
    noise = rng.normal(loc=0.0, scale=2.5, size=n_rows)
    sector_offset = np.array([SECTOR_PREMIUM_LPA[s] for s in sectors])

    salaries = (base + slope * experience + sector_offset + noise).round(1)
    salaries = np.clip(salaries, 1.0, None)  # no negative pay

    return pd.DataFrame(
        {
            "job_id": np.arange(9001, 9001 + n_rows, dtype="int64"),
            "sector": sectors,
            "experience_years": experience,
            "salary_lpa": salaries,
        }
    )


def fit_linear_trend(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Return (slope, intercept, pearson_r) for a least-squares line."""
    slope, intercept = np.polyfit(x, y, deg=1)
    if x.std() == 0 or y.std() == 0:
        r = float("nan")
    else:
        r = float(np.corrcoef(x, y)[0, 1])
    return float(slope), float(intercept), r


def residual_outliers(
    x: pd.Series, y: pd.Series, slope: float, intercept: float, threshold: float = 2.0
) -> pd.Series:
    """Boolean mask: True for points whose residual is > threshold std away.

    'Residual' = y - predicted_y. Standardising residuals and keeping
    those past `threshold` std gives the relationship-aware analogue
    of the boxplot's 1.5*IQR rule.
    """
    predicted = slope * x + intercept
    residuals = y - predicted
    std = residuals.std()
    if std == 0:
        return pd.Series(False, index=x.index)
    return residuals.abs() / std > threshold


# ---------------------------------------------------------------------------
# PLOT HELPERS
# ---------------------------------------------------------------------------
def ensure_figures_dir() -> Path:
    """Idempotently create the output directory."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR


def plot_basic_scatter(frame: pd.DataFrame, path: Path) -> Path:
    """Plain x/y scatter."""
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.scatter(
        frame["experience_years"],
        frame["salary_lpa"],
        s=22,
        alpha=0.55,
        color="steelblue",
        edgecolor="white",
    )
    ax.set_xlabel("experience_years")
    ax.set_ylabel("salary_lpa")
    ax.set_title("salary_lpa vs experience_years — basic scatter")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_per_sector_scatter(frame: pd.DataFrame, path: Path) -> Path:
    """Same scatter, colour-coded by sector."""
    fig, ax = plt.subplots(figsize=(8, 5.5))
    palette = {
        "Technology": "#1f77b4",
        "Finance": "#ff7f0e",
        "Healthcare": "#2ca02c",
        "Manufacturing": "#d62728",
        "Retail": "#9467bd",
    }
    for sector, color in palette.items():
        sub = frame[frame["sector"] == sector]
        ax.scatter(
            sub["experience_years"],
            sub["salary_lpa"],
            s=24,
            alpha=0.6,
            color=color,
            edgecolor="white",
            label=f"{sector} (n={len(sub)})",
        )
    ax.set_xlabel("experience_years")
    ax.set_ylabel("salary_lpa")
    ax.set_title("salary_lpa vs experience_years — coloured by sector")
    ax.legend(title="sector", loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_with_trendline(frame: pd.DataFrame, path: Path) -> Path:
    """Scatter + least-squares line + Pearson r in the legend."""
    x = frame["experience_years"].to_numpy(dtype=float)
    y = frame["salary_lpa"].to_numpy(dtype=float)
    slope, intercept, r = fit_linear_trend(x, y)
    x_line = np.linspace(x.min(), x.max(), 50)
    y_line = slope * x_line + intercept

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.scatter(
        x,
        y,
        s=22,
        alpha=0.55,
        color="steelblue",
        edgecolor="white",
        label=f"observations (n={len(frame)})",
    )
    ax.plot(
        x_line,
        y_line,
        color="crimson",
        linewidth=2.0,
        label=f"trend: y = {slope:.2f}x + {intercept:.2f}, r = {r:.2f}",
    )
    ax.set_xlabel("experience_years")
    ax.set_ylabel("salary_lpa")
    ax.set_title("salary_lpa vs experience_years — with trend line")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_residual_outliers(frame: pd.DataFrame, path: Path) -> Path:
    """Highlight points whose residual is > 2 std from the regression line."""
    x = frame["experience_years"].astype(float)
    y = frame["salary_lpa"].astype(float)
    slope, intercept, _ = fit_linear_trend(x.to_numpy(), y.to_numpy())
    flagged = residual_outliers(x, y, slope, intercept, threshold=2.0)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.scatter(
        x[~flagged],
        y[~flagged],
        s=22,
        alpha=0.55,
        color="steelblue",
        edgecolor="white",
        label="typical",
    )
    ax.scatter(
        x[flagged],
        y[flagged],
        s=55,
        alpha=0.85,
        color="crimson",
        edgecolor="black",
        label=f"residual outlier (>2 std): n={int(flagged.sum())}",
    )
    x_line = np.linspace(x.min(), x.max(), 50)
    ax.plot(
        x_line,
        slope * x_line + intercept,
        color="grey",
        linewidth=1.5,
        linestyle="--",
        label="trend line",
    )
    ax.set_xlabel("experience_years")
    ax.set_ylabel("salary_lpa")
    ax.set_title("Residual outliers — points whose y is unusual *given x*")
    ax.legend(loc="upper left", fontsize=9)
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
    """Generate the four scatter artefacts described in the docstring."""
    print_banner("Assignment 4.42 — Scatter Plots: Relationships Between Variables")
    ensure_figures_dir()
    frame = generate_postings_with_experience_salary_link()
    print(
        f"\n  Working frame: {frame.shape[0]} rows.\n"
        f"  Columns: {list(frame.columns)}\n"
    )

    # 1) Basic scatter
    print_banner("1) Basic scatter — the relationship at a glance")
    path = plot_basic_scatter(frame, FIGURES_DIR / "experience_salary_scatter.png")
    report_saved("basic two-variable scatter", path)
    print(
        "  Read: salary rises as experience rises -- a clear positive\n"
        "  cloud sloping up to the right. The width of the cloud is the\n"
        "  noise; if the cloud were a thin line, salary would be a perfect\n"
        "  function of experience."
    )

    # 2) Per-sector scatter
    print_banner("2) Per-sector colour coding — what each colour reveals")
    path = plot_per_sector_scatter(
        frame, FIGURES_DIR / "experience_salary_per_sector_scatter.png"
    )
    report_saved("per-sector colour-coded scatter", path)
    sector_means = (
        frame.groupby("sector", observed=True)["salary_lpa"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
    )
    print("\n  Per-sector mean salary (highest -> lowest):")
    print(sector_means.to_string())
    print(
        "\n  Reading: same upward slope across sectors but different vertical\n"
        "  offsets -- Technology and Finance bands sit above Healthcare,\n"
        "  Manufacturing, and Retail. The colour-coded scatter shows that\n"
        "  the relationship is the same shape across groups; the *level*\n"
        "  is what differs by sector."
    )

    # 3) Trend line + Pearson r
    print_banner("3) Trend line + Pearson r — putting a number on the cloud")
    path = plot_with_trendline(
        frame, FIGURES_DIR / "experience_salary_with_trendline_scatter.png"
    )
    report_saved("trend line + Pearson r", path)
    x = frame["experience_years"].to_numpy(dtype=float)
    y = frame["salary_lpa"].to_numpy(dtype=float)
    slope, intercept, r = fit_linear_trend(x, y)
    print(
        f"  Linear fit: y = {slope:.2f}x + {intercept:.2f}\n"
        f"  Pearson r = {r:.2f}  (1 = perfect positive, 0 = no linear relation,\n"
        "                       -1 = perfect negative).\n"
        "  Reading: r captures the *strength* of the linear relationship.\n"
        "  Always pair the line with the scatter: r looks great until you\n"
        "  see the cloud has two clusters or a non-linear shape."
    )

    # 4) Residual outliers
    print_banner("4) Residual outliers — points whose y is unusual GIVEN x")
    path = plot_residual_outliers(
        frame, FIGURES_DIR / "experience_salary_outliers_scatter.png"
    )
    report_saved("residual outliers highlighted", path)
    flagged = residual_outliers(
        frame["experience_years"].astype(float),
        frame["salary_lpa"].astype(float),
        slope,
        intercept,
        threshold=2.0,
    )
    print(
        f"  Residual outliers (>2 std from the trend line): {int(flagged.sum())}\n"
        "  These are the points 'unusually high or low salary FOR THAT level\n"
        "  of experience' -- they're invisible on a single-variable boxplot\n"
        "  because their salary is normal-looking unless paired with their\n"
        "  experience level. Relationship outliers need relationship plots."
    )

    # Cheat sheet
    print_banner("Scatter cheat sheet")
    print(
        "  ax.scatter(x, y, s=22, alpha=0.55)            -> basic scatter\n"
        "  ax.scatter(..., c=group_codes, cmap='viridis')-> colour by group\n"
        "  np.polyfit(x, y, deg=1)                       -> least-squares line\n"
        "  np.corrcoef(x, y)[0, 1]                       -> Pearson r\n"
        "  residual = y - (slope*x + intercept)          -> per-point error\n"
        "  abs(residual) / residual.std() > 2            -> 2-std outlier rule\n"
        "  WHEN SCATTER, WHEN OTHER\n"
        "    two numeric variables           -> scatter\n"
        "    one numeric, one time           -> line plot (4.41)\n"
        "    one numeric, one categorical    -> boxplot per group (4.40)\n"
        "    one numeric, want shape detail  -> histogram (4.39)\n"
        "  CAUTION\n"
        "    correlation != causation; r is for *linear* relationships only;\n"
        "    inspect the cloud before quoting the number."
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
