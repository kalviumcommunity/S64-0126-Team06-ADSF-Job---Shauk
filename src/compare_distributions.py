"""Assignment 4.38 — Comparing Distributions Across Multiple Columns.

Author: Bhargav Kalambhe (Frontend & ML, covering Analyst)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

4.37 computed every statistic on five differently-shaped columns
side by side. This assignment goes one step further: it *compares*
those distributions, both **across columns** and **across groups
within a column**. Comparison is what turns a per-column summary
into an insight.

Two kinds of comparison are demonstrated:

    A) ACROSS COLUMNS (different units)
       You cannot say "salary is more variable than commute" by
       comparing the std values directly -- they're in different
       units. Two unit-free metrics handle this:
         * Coefficient of variation (CV = std / mean)
         * Z-score normalisation (puts every column on a common
           mean=0, std=1 scale)

    B) ACROSS GROUPS within one column (same units)
       Per-sector salary, per-role experience, etc. are the
       comparisons that surface real-world stories ("Manufacturing
       pays more than Retail, but with much higher variance").
       Demonstrated via groupby + the same statistical lens:
       central tendency, spread, robust spread, and an anomaly
       flag for groups whose distribution shape differs from the
       overall pattern.

The frame is a 200-row synthetic postings frame where salary is
deliberately sector-conditioned -- different sectors have different
salary distributions -- so the per-group comparison surfaces real
between-group differences instead of pure noise.

Run:
    python3 src/compare_distributions.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


BANNER_WIDTH = 76
SAMPLE_CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_job_postings.csv"
)

SYNTHETIC_ROW_COUNT = 200
SYNTHETIC_SEED = 31

# Per-sector lognormal parameters. Different sectors have different
# salary distributions on purpose -- this is what gives the per-group
# comparison something to compare.
SECTOR_SALARY_PARAMS: dict[str, tuple[float, float]] = {
    # mu, sigma  for np.random.lognormal
    "Technology": (2.7, 0.45),  # higher mean, moderate spread
    "Finance": (2.6, 0.55),  # high mean, wider spread
    "Healthcare": (2.3, 0.35),  # mid mean, tight spread
    "Retail": (2.0, 0.30),  # lower mean, tight
    "Manufacturing": (2.1, 0.40),  # lower mean, slightly wider
}


# ---------------------------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------------------------
def generate_postings_with_grouped_distributions(
    n_rows: int = SYNTHETIC_ROW_COUNT, seed: int = SYNTHETIC_SEED
) -> pd.DataFrame:
    """200-row frame; salary is sector-conditioned, other columns vary too."""
    rng = np.random.default_rng(seed)
    sectors = rng.choice(list(SECTOR_SALARY_PARAMS.keys()), size=n_rows)

    salaries = np.empty(n_rows, dtype="float64")
    for sector in SECTOR_SALARY_PARAMS:
        mask = sectors == sector
        if mask.any():
            mu, sigma = SECTOR_SALARY_PARAMS[sector]
            salaries[mask] = rng.lognormal(mu, sigma, size=mask.sum()).round(1)

    return pd.DataFrame(
        {
            "job_id": np.arange(6001, 6001 + n_rows, dtype="int64"),
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
# CROSS-COLUMN COMPARISON HELPERS (different units)
# ---------------------------------------------------------------------------
def coefficient_of_variation(series: pd.Series) -> float:
    """CV = std / mean. Unit-free; bigger means more variable RELATIVE to scale."""
    mean = float(series.mean())
    if mean == 0:
        return float("nan")
    return float(series.std()) / mean


def cross_column_summary(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Per-column summary in the same units the columns live in,
    plus a unit-free CV column for cross-column ranking."""
    rows = []
    for column in columns:
        series = frame[column]
        rows.append(
            {
                "column": column,
                "mean": round(float(series.mean()), 2),
                "median": round(float(series.median()), 2),
                "std": round(float(series.std()), 2),
                "iqr": round(
                    float(series.quantile(0.75) - series.quantile(0.25)),
                    2,
                ),
                "cv": round(coefficient_of_variation(series), 3),
            }
        )
    return pd.DataFrame(rows).set_index("column").sort_values("cv", ascending=False)


def z_score_frame(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Standardise each column to mean=0, std=1 so columns share a common scale.

    The min/max of the z-scored frame answers the question
    "how far from typical do extreme values reach?" comparably
    across columns of different units.
    """
    z = frame[columns].apply(lambda s: (s - s.mean()) / s.std())
    return z


# ---------------------------------------------------------------------------
# CROSS-GROUP COMPARISON HELPERS (same units, partitioned)
# ---------------------------------------------------------------------------
def per_group_summary(frame: pd.DataFrame, group_col: str, target: str) -> pd.DataFrame:
    """Summary of `target` distribution per group of `group_col`.

    Returns one row per group, with mean / median / std / IQR / count
    plus a `gap` = mean - median that flags within-group skew.
    """
    grouped = frame.groupby(group_col, observed=True)[target]
    summary = pd.DataFrame(
        {
            "count": grouped.count(),
            "mean": grouped.mean().round(2),
            "median": grouped.median().round(2),
            "std": grouped.std().round(2),
            "iqr": (grouped.quantile(0.75) - grouped.quantile(0.25)).round(2),
        }
    )
    summary["gap"] = (summary["mean"] - summary["median"]).round(2)
    return summary.sort_values("median", ascending=False)


def flag_anomalous_groups(
    per_group: pd.DataFrame, std_multiplier: float = 1.5
) -> pd.Series:
    """Flag groups whose mean is more than `std_multiplier` median-absolute-
    deviations from the median-of-group-means.

    This is the robust analogue of "is this group an outlier?" -- using the
    median and MAD instead of mean and std so that one extreme group cannot
    pull the threshold to itself and hide.
    """
    means = per_group["mean"]
    median_of_means = means.median()
    mad = (means - median_of_means).abs().median()
    if mad == 0:
        return pd.Series(["typical"] * len(means), index=means.index)
    distance = (means - median_of_means).abs() / mad
    flags = distance.where(distance >= std_multiplier).map(
        lambda d: "anomalous" if pd.notna(d) else "typical"
    )
    return flags


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def print_banner(title: str) -> None:
    """Print a fixed-width banner."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def print_section(label: str, body: object) -> None:
    """Print a labelled section with the body underneath."""
    print(f"\n{label}")
    print(body)


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Walk both kinds of comparison: across-column and across-group."""
    print_banner("Assignment 4.38 — Comparing Distributions Across Multiple Columns")
    frame = generate_postings_with_grouped_distributions()
    numeric_cols = [
        "salary_lpa",
        "experience_years",
        "applications_received",
        "interview_score",
        "commute_minutes",
    ]
    print(
        f"\n  Working frame: {frame.shape[0]} rows x {frame.shape[1]} columns,\n"
        f"  numeric columns: {numeric_cols}\n"
    )

    # ----- A) ACROSS COLUMNS (different units) ---------------------------
    print_banner("A1) Cross-column raw comparison — same units only")
    raw = cross_column_summary(frame, numeric_cols)
    print_section(
        "Per-column summary (raw values, sorted by CV descending):",
        raw.to_string(),
    )
    print(
        "\n  Why CV not std for cross-column ranking: salary std (~6.5) and\n"
        "  commute std (~36) are in different units -- LPA vs minutes -- so\n"
        "  a direct std comparison is meaningless. CV = std/mean is unit-\n"
        "  free, so the ranking actually reflects relative volatility."
    )

    print_banner("A2) Z-score normalisation — common scale for cross-column overlap")
    z = z_score_frame(frame, numeric_cols)
    z_summary = pd.DataFrame(
        {
            "z_min": z.min().round(2),
            "z_max": z.max().round(2),
            "z_range": (z.max() - z.min()).round(2),
        }
    ).sort_values("z_range", ascending=False)
    print_section(
        "After z-scoring (mean=0, std=1), how far do the extremes reach?",
        z_summary.to_string(),
    )
    print(
        "\n  Reading: every column is now on the same scale -- a value of 3\n"
        "  means 'three standard deviations from the column's mean' regardless\n"
        "  of unit. Columns whose z_range is much wider than ~6 (~+/-3 std)\n"
        "  have heavier tails than a normal distribution would produce."
    )

    # ----- B) ACROSS GROUPS within `salary_lpa` -------------------------
    print_banner("B1) Per-sector salary distribution — same column, grouped")
    per_sector = per_group_summary(frame, "sector", "salary_lpa")
    print(per_sector.to_string())
    print(
        "\n  Reading: sectors ranked by median salary (highest first). Notice\n"
        "  that sectors with higher medians can have wildly different IQRs --\n"
        "  Finance pays well *and* spreads pay widely; Healthcare pays moderately\n"
        "  but very tightly. Both halves of the comparison (centre + spread)\n"
        "  matter; ranking by median alone hides the spread story."
    )

    print_banner("B2) Anomaly flag — sectors whose mean is far from peer median")
    flags = flag_anomalous_groups(per_sector, std_multiplier=1.5)
    flagged = per_sector.assign(verdict=flags)
    print(flagged.to_string())
    print(
        "\n  Method: for each sector, compute |mean - median(peer means)| / MAD.\n"
        "  Flag as 'anomalous' when that distance >= 1.5. MAD-based outlier\n"
        "  detection is robust -- one extreme sector cannot pull the threshold\n"
        "  to itself and hide. This is the per-group analogue of the std-vs-IQR\n"
        "  robustness lesson from 4.37."
    )

    # ----- C) Comparing two columns directly via paired statistics ------
    print_banner("C) Paired column comparison — interview_score vs salary_lpa")
    paired = pd.DataFrame(
        {
            "interview_score": [
                frame["interview_score"].mean(),
                frame["interview_score"].median(),
                frame["interview_score"].std(),
                coefficient_of_variation(frame["interview_score"]),
            ],
            "salary_lpa": [
                frame["salary_lpa"].mean(),
                frame["salary_lpa"].median(),
                frame["salary_lpa"].std(),
                coefficient_of_variation(frame["salary_lpa"]),
            ],
        },
        index=["mean", "median", "std", "cv"],
    ).round(3)
    print(paired.to_string())
    print(
        "\n  Reading: even though interview_score has a tiny std (~1.2) versus\n"
        "  salary's much bigger std (~6.5), salary's CV is many times higher --\n"
        "  salary is genuinely more variable as a fraction of its scale.\n"
        "  Looking only at std would have given the wrong answer."
    )

    # ----- D) Ranges + percentile-based spread --------------------------
    print_banner("D) Robust spread comparison — P95 - P5 instead of max - min")
    p5 = frame[numeric_cols].quantile(0.05).round(2)
    p95 = frame[numeric_cols].quantile(0.95).round(2)
    robust_range = (p95 - p5).round(2)
    full_range = (frame[numeric_cols].max() - frame[numeric_cols].min()).round(2)

    range_table = pd.DataFrame(
        {
            "p5": p5,
            "p95": p95,
            "robust_range_p95_p5": robust_range,
            "full_range_max_min": full_range,
            "tail_inflation": (full_range / robust_range.replace(0, np.nan)).round(2),
        }
    ).sort_values("tail_inflation", ascending=False)
    print(range_table.to_string())
    print(
        "\n  Reading: tail_inflation = (max - min) / (P95 - P5). A value near 1\n"
        "  means the full range is roughly the middle-90% range; values >> 1\n"
        "  mean the most extreme observations sit far beyond the bulk of the\n"
        "  data. commute_minutes is the canonical heavy-tail offender here."
    )

    # ----- E) Reconnect to disk ------------------------------------------
    print_banner("Bundled CSV — same comparison framework, on the on-disk frame")
    if SAMPLE_CSV_PATH.exists():
        bundled = pd.read_csv(SAMPLE_CSV_PATH, parse_dates=["date_posted"])
        if "salary_lpa" in bundled.columns:
            print_section(
                "bundled per-sector salary summary:",
                per_group_summary(bundled, "sector", "salary_lpa").to_string(),
            )
            print(
                "  (Only 3 rows -- the synthetic 200-row frame is what\n"
                "  exercises the cross-group comparison.)"
            )
    else:
        print("  sample_job_postings.csv not found -- skipping disk demo.")

    # Cheat sheet
    print_banner("Comparison cheat sheet")
    print(
        "  ACROSS COLUMNS (different units)\n"
        "    coefficient of variation:   series.std() / series.mean()\n"
        "    z-score normalisation:      (series - series.mean()) / series.std()\n"
        "  ACROSS GROUPS (same units)\n"
        "    grouped = frame.groupby(g)[c]\n"
        "    grouped.mean(), .median(), .std(), .quantile([.25, .5, .75])\n"
        "    median - across - groups + MAD = robust outlier detection\n"
        "  ROBUST RANGE\n"
        "    P95 - P5 instead of max - min (avoids one outlier ruining\n"
        "    the comparison)\n"
        "  RULES OF THUMB\n"
        "    1. Comparing std across different units -> wrong; use CV.\n"
        "    2. Comparing groups by mean alone -> hides spread story; report\n"
        "       both centre AND spread.\n"
        "    3. Heavy-tailed columns -> use median + IQR + P95-P5 instead\n"
        "       of mean + std + max - min."
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
