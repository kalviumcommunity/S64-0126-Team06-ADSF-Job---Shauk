"""Assignment 4.37 — Computing Basic Summary Statistics for Individual Columns.

Author: Bhargav Kalambhe (Frontend & ML, covering Analyst)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

Summary statistics are the first quantitative read of a numeric
column. Five small numbers -- count, mean, std, min, max -- plus
the quartiles tell you most of what you need to know about how a
column behaves *before* you reach for a chart or a model.

The trick is that the *same* set of statistics says different things
depending on the column's distribution shape. A right-skewed column
has mean > median; a heavy-tailed column has std much larger than
IQR; a uniform column has mean ~ median. The lesson is incomplete
if you only run `describe()` once on one column.

This script generates a 150-row synthetic frame with **five numeric
columns, each shaped on purpose to give a different story**:

    salary_lpa             -> lognormal       (right-skewed)
    experience_years       -> uniform integer (symmetric)
    applications_received  -> Poisson         (right-skewed counts)
    interview_score        -> normal (8.0, 1.2, clipped to [1,10])
                                              (symmetric, bounded)
    commute_minutes        -> exponential     (heavy right tail)

It then computes each statistic explicitly (not just `describe()`),
interprets the mean-vs-median gap, contrasts std with IQR for
robustness, and ranks columns by spread so you can see at a glance
which feature is the most volatile.

Run:
    python3 src/column_stats.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


BANNER_WIDTH = 76
SAMPLE_CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_job_postings.csv"
)

SYNTHETIC_ROW_COUNT = 150
SYNTHETIC_SEED = 29


# ---------------------------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------------------------
def generate_postings_with_varied_distributions(
    n_rows: int = SYNTHETIC_ROW_COUNT, seed: int = SYNTHETIC_SEED
) -> pd.DataFrame:
    """Build a 150-row frame with five numeric columns of different shape.

    Each column is generated from a different distribution so the
    summary statistics point at distinct stories: skew vs symmetric,
    bounded vs heavy-tailed, low-spread vs high-spread.
    """
    rng = np.random.default_rng(seed)

    return pd.DataFrame(
        {
            "job_id": np.arange(5001, 5001 + n_rows, dtype="int64"),
            # Right-skewed numeric -> mean > median.
            "salary_lpa": rng.lognormal(mean=2.4, sigma=0.5, size=n_rows).round(1),
            # Uniform integer -> mean ~ median.
            "experience_years": rng.integers(low=0, high=12, size=n_rows),
            # Poisson counts -> right-skewed integer with hard floor at 0.
            "applications_received": rng.poisson(lam=8, size=n_rows),
            # Normal, bounded -> symmetric, low spread.
            "interview_score": np.clip(
                rng.normal(loc=8.0, scale=1.2, size=n_rows), 1, 10
            ).round(1),
            # Exponential -> heavy right tail; std >> IQR.
            "commute_minutes": rng.exponential(scale=35.0, size=n_rows).round(0),
        }
    )


# ---------------------------------------------------------------------------
# STATISTIC HELPERS — one function per statistic so each is named and testable.
# ---------------------------------------------------------------------------
def column_count(series: pd.Series) -> int:
    """Number of non-null values in the column."""
    return int(series.count())


def column_mean(series: pd.Series) -> float:
    """Arithmetic average. Pulled toward outliers / long tails."""
    return float(series.mean())


def column_median(series: pd.Series) -> float:
    """Middle value. Robust against outliers."""
    return float(series.median())


def column_min_max(series: pd.Series) -> tuple[float, float]:
    """Range endpoints — first place data-quality bugs surface (negative ages etc.)."""
    return float(series.min()), float(series.max())


def column_std(series: pd.Series) -> float:
    """Standard deviation — same units as the data; pulled by outliers."""
    return float(series.std())


def column_variance(series: pd.Series) -> float:
    """Variance — std squared. Squared units; rarely reported directly."""
    return float(series.var())


def column_quartiles(series: pd.Series) -> tuple[float, float, float]:
    """25th / 50th / 75th percentiles. Q2 (50%) is the median."""
    q1 = float(series.quantile(0.25))
    q2 = float(series.quantile(0.50))
    q3 = float(series.quantile(0.75))
    return q1, q2, q3


def column_iqr(series: pd.Series) -> float:
    """Inter-quartile range = Q3 - Q1. Robust spread metric, not pulled by tails."""
    q1, _, q3 = column_quartiles(series)
    return q3 - q1


def column_skewness_hint(series: pd.Series) -> str:
    """Mean-vs-median gap as a one-word direction.

    Symmetric distributions have mean ~ median; right-skewed have
    mean > median (long tail to the right); left-skewed reverse.
    """
    mean = column_mean(series)
    median = column_median(series)
    if mean - median > 0.05 * abs(median + 1e-9):
        return "right-skewed"
    if median - mean > 0.05 * abs(median + 1e-9):
        return "left-skewed"
    return "roughly symmetric"


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def per_column_summary(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Build the per-column summary table -- the lesson's main artefact."""
    rows = []
    for column in columns:
        series = frame[column]
        q1, q2, q3 = column_quartiles(series)
        rows.append(
            {
                "column": column,
                "count": column_count(series),
                "min": column_min_max(series)[0],
                "max": column_min_max(series)[1],
                "mean": round(column_mean(series), 2),
                "median": round(q2, 2),
                "std": round(column_std(series), 2),
                "iqr": round(q3 - q1, 2),
                "shape": column_skewness_hint(series),
            }
        )
    return pd.DataFrame(rows).set_index("column")


def print_banner(title: str) -> None:
    """Print a fixed-width banner."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def print_section(label: str, body: object) -> None:
    """Print a labelled section with the body underneath."""
    print(f"\n{label}")
    print(body)


def explain_statistic(label: str, value: float, unit: str = "") -> str:
    """Format a labelled statistic for print output."""
    return f"  {label:<28} {value:>10.2f}{(' ' + unit) if unit else ''}"


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Walk every statistic on one column, then compare across all columns."""
    print_banner("Assignment 4.37 — Summary Statistics for Individual Columns")
    frame = generate_postings_with_varied_distributions()

    numeric_columns = [
        "salary_lpa",
        "experience_years",
        "applications_received",
        "interview_score",
        "commute_minutes",
    ]
    print(
        f"\n  Working frame: {frame.shape[0]} rows x {frame.shape[1]} columns,\n"
        f"  numeric columns under study: {numeric_columns}\n"
    )

    # ----- 1) Single-column deep dive on salary_lpa ---------------------
    print_banner("1) Deep dive on salary_lpa (right-skewed lognormal)")
    salary = frame["salary_lpa"]
    q1, q2, q3 = column_quartiles(salary)
    sal_min, sal_max = column_min_max(salary)
    print(explain_statistic("count", column_count(salary)))
    print(explain_statistic("min", sal_min, "LPA"))
    print(explain_statistic("max", sal_max, "LPA"))
    print(explain_statistic("range  (max - min)", sal_max - sal_min, "LPA"))
    print(explain_statistic("mean", column_mean(salary), "LPA"))
    print(explain_statistic("median (Q2)", q2, "LPA"))
    print(explain_statistic("Q1 (25%)", q1, "LPA"))
    print(explain_statistic("Q3 (75%)", q3, "LPA"))
    print(explain_statistic("IQR (Q3 - Q1)", q3 - q1, "LPA"))
    print(explain_statistic("std", column_std(salary), "LPA"))
    print(explain_statistic("variance", column_variance(salary), "LPA^2"))
    print(
        f"\n  Read: mean ({column_mean(salary):.2f}) > median ({q2:.2f}) "
        f"-> {column_skewness_hint(salary)}.\n"
        f"  std = {column_std(salary):.2f} but IQR = {q3 - q1:.2f}; the\n"
        f"  std-vs-IQR gap is the standard fingerprint of a long right tail\n"
        f"  -- a few high earners pull the std up while the middle 50%% stays\n"
        f"  much tighter."
    )

    # ----- 2) Same statistics across all numeric columns -----------------
    print_banner("2) Per-column summary table — every numeric column at once")
    summary = per_column_summary(frame, numeric_columns)
    print(summary.to_string())

    # ----- 3) Mean-vs-median: skew read across columns -------------------
    print_banner("3) Mean vs median — distribution shape at a glance")
    skew_table = summary[["mean", "median", "shape"]].assign(
        gap=(summary["mean"] - summary["median"]).round(2)
    )
    print(skew_table.to_string())
    print(
        "\n  Read: salary_lpa and commute_minutes show mean > median (right-\n"
        "  skewed long tails). interview_score and experience_years are\n"
        "  roughly symmetric. applications_received tilts slightly right\n"
        "  because Poisson with low lam has a small right skew."
    )

    # ----- 4) std vs IQR: robust-vs-tail-sensitive spread ---------------
    print_banner("4) std vs IQR — which spread metric to trust here?")
    spread = summary[["std", "iqr"]].assign(
        ratio=(summary["std"] / summary["iqr"].replace(0, np.nan)).round(2)
    )
    print(spread.to_string())
    print(
        "\n  Reading: std/iqr ~ 0.74 is the symmetric-distribution fingerprint\n"
        "  (a normal distribution has std ~ 0.74 * IQR). Ratios well above 0.74\n"
        "  signal heavy tails (commute_minutes, salary_lpa) where the std is\n"
        "  inflated by outliers and the IQR is the more honest spread."
    )

    # ----- 5) Cross-column comparison and ranking -----------------------
    print_banner("5) Cross-column ranking — most volatile feature")
    by_iqr = summary[["mean", "iqr", "shape"]].sort_values("iqr", ascending=False)
    print_section("Columns sorted by IQR (descending):", by_iqr.to_string())
    print(
        "\n  IQR ranking is more honest than std ranking when distributions\n"
        "  are skewed -- it asks 'how spread out is the typical row?', not\n"
        "  'how much do the extremes pull the mean around?'."
    )

    # ----- 6) Reconnect to disk ------------------------------------------
    print_banner("Bundled CSV — same statistics, on the on-disk frame")
    if SAMPLE_CSV_PATH.exists():
        bundled = pd.read_csv(SAMPLE_CSV_PATH, parse_dates=["date_posted"])
        if "salary_lpa" in bundled.columns:
            print_section(
                "bundled[['salary_lpa']] summary:",
                per_column_summary(bundled, ["salary_lpa"]).to_string(),
            )
            print(
                "  (Only 3 rows -- the synthetic 150-row frame is what\n"
                "  exercises the per-distribution-shape lesson.)"
            )
    else:
        print("  sample_job_postings.csv not found -- skipping disk demo.")

    # Cheat sheet
    print_banner("Statistics cheat sheet")
    print(
        "  series.count()              -> non-null count\n"
        "  series.min(), series.max()  -> range endpoints\n"
        "  series.mean()               -> arithmetic average (outlier-sensitive)\n"
        "  series.median()             -> middle value (outlier-robust)\n"
        "  series.std(), series.var()  -> spread in original / squared units\n"
        "  series.quantile([.25,.5,.75]) -> quartiles\n"
        "  Q3 - Q1                     -> IQR (robust spread)\n"
        "  series.describe()           -> count + mean + std + min + 25/50/75 + max\n"
        "  WHEN TO PREFER WHICH\n"
        "    symmetric distribution -> mean + std are fine\n"
        "    skewed / heavy-tailed  -> median + IQR are more honest"
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
