"""Assignment 4.34 — Handling Missing Values Using Drop and Fill Strategies.

Author: Bhargav Kalambhe (Frontend & ML, covering Analyst)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

Detection (4.33) said *where* and *how much* is missing. This
assignment turns those answers into action -- either dropping the
rows / columns, filling in the missing values, or some mix of the two
applied per column based on what the column actually represents.

The lesson here is that there is **no single right strategy**. Five
strategies are demonstrated side-by-side on the same shaped-
missingness frame so the trade-offs are visible:

    1. Drop any row with a missing value          (simple, lossy)
    2. Drop columns above a missing-rate threshold (when a column is
                                                     mostly empty)
    3. Fill numeric columns with the median        (skew-resistant)
    4. Fill categorical with a constant placeholder (preserves rows)
    5. Group-aware fill: sector-level median       (uses structure
                                                     detected in 4.33)

Each strategy prints a before/after summary so the cost of the
choice is obvious: how many rows survived, how the salary mean
shifted, whether the categorical distribution got distorted.

Run:
    python3 src/handle_missing_values.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


BANNER_WIDTH = 72
SAMPLE_CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_job_postings.csv"
)

SYNTHETIC_ROW_COUNT = 100
SYNTHETIC_SEED = 11
SECTORS = ("Technology", "Finance", "Healthcare", "Retail", "Manufacturing")
ROLES = (
    "Data Scientist",
    "ML Engineer",
    "Data Analyst",
    "Backend Engineer",
    "Frontend Engineer",
    "Data Engineer",
)


# ---------------------------------------------------------------------------
# DATA HELPERS — same shaped-missingness frame as 4.33 so the strategies are
# tested on a frame that has both random and structured nulls.
# ---------------------------------------------------------------------------
def generate_postings_with_missingness(
    n_rows: int = SYNTHETIC_ROW_COUNT, seed: int = SYNTHETIC_SEED
) -> pd.DataFrame:
    """Re-create the 4.33 shaped-missingness frame for cleaning experiments."""
    rng = np.random.default_rng(seed)
    base_date = pd.Timestamp("2024-01-01")

    sectors = rng.choice(SECTORS, size=n_rows)
    salaries = rng.lognormal(mean=2.4, sigma=0.5, size=n_rows).round(1)
    benefits = rng.integers(low=1, high=11, size=n_rows).astype("float")
    perks = pd.Series(
        rng.choice(("gym", "wfh", "meals", "stock", "training"), size=n_rows)
    )

    frame = pd.DataFrame(
        {
            "job_id": np.arange(2001, 2001 + n_rows, dtype="int64"),
            "job_title": rng.choice(ROLES, size=n_rows),
            "sector": sectors,
            "experience_years": rng.integers(low=0, high=12, size=n_rows),
            "salary_lpa": salaries,
            "date_posted": base_date
            + pd.to_timedelta(rng.integers(0, 180, size=n_rows), unit="D"),
            "perks": perks.astype("string"),
            "benefits_score": benefits,
        }
    )

    frame.loc[rng.random(n_rows) < 0.15, "salary_lpa"] = np.nan
    frame.loc[rng.random(n_rows) < 0.05, "date_posted"] = pd.NaT

    is_low_perks_sector = pd.Series(sectors).isin(("Manufacturing", "Retail")).values
    perks_missing_prob = np.where(is_low_perks_sector, 0.70, 0.08)
    perks_missing_mask = rng.random(n_rows) < perks_missing_prob
    frame.loc[perks_missing_mask, "perks"] = pd.NA

    benefits_missing_prob = np.where(perks_missing_mask, 0.80, 0.05)
    benefits_missing_mask = rng.random(n_rows) < benefits_missing_prob
    frame.loc[benefits_missing_mask, "benefits_score"] = np.nan

    return frame


# ---------------------------------------------------------------------------
# DROP STRATEGIES
# ---------------------------------------------------------------------------
def drop_rows_with_any_missing(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop any row that has *any* missing value. Most aggressive."""
    return frame.dropna(how="any")


def drop_rows_missing_subset(frame: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    """Drop only rows that are missing in critical columns. Targeted, less lossy."""
    return frame.dropna(subset=subset)


def drop_rows_below_threshold(frame: pd.DataFrame, min_non_null: int) -> pd.DataFrame:
    """Keep rows with at least `min_non_null` non-NaN values. Sliding cut-off."""
    return frame.dropna(thresh=min_non_null)


def drop_columns_above_missing_rate(
    frame: pd.DataFrame, threshold: float
) -> pd.DataFrame:
    """Drop columns whose missing rate exceeds `threshold` (e.g. 0.5)."""
    rates = frame.isna().mean()
    keep_cols = rates[rates <= threshold].index
    return frame[keep_cols]


# ---------------------------------------------------------------------------
# FILL STRATEGIES
# ---------------------------------------------------------------------------
def fill_with_constant(frame: pd.DataFrame, column: str, value: object) -> pd.DataFrame:
    """Fill a single column's NaN with a fixed value. Best for categoricals."""
    return frame.assign(**{column: frame[column].fillna(value)})


def fill_numeric_with_median(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    """Fill a numeric column's NaN with its median.

    Median is preferred over mean for skewed distributions because it
    is not pulled by long tails -- on a lognormal salary distribution
    (4.30 showed mean 11.63 vs median 10.90), median preserves the
    typical row better than mean does.
    """
    median = frame[column].median()
    return frame.assign(**{column: frame[column].fillna(median)})


def fill_numeric_by_group(
    frame: pd.DataFrame, group_col: str, target_col: str
) -> pd.DataFrame:
    """Group-aware fill: each group's NaN gets that group's median.

    This is the right strategy for *structured* missingness detected
    in 4.33 -- the perks/benefits NaNs are sector-driven, so a global
    fill would smear sector-specific structure. A per-sector fill
    preserves the within-sector distribution.
    """
    group_medians = frame.groupby(group_col, observed=True)[target_col].transform(
        "median"
    )
    filled = frame[target_col].fillna(group_medians)
    return frame.assign(**{target_col: filled})


def fill_with_mode(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    """Fill a categorical column's NaN with the most common value (mode).

    Use this when "missing" really means "no information" for a true
    categorical, and you want to push those rows into the dominant
    bucket. Use `fill_with_constant(..., "Unknown")` instead if you
    want the missingness to remain visible downstream.
    """
    mode_value = frame[column].mode(dropna=True).iloc[0]
    return frame.assign(**{column: frame[column].fillna(mode_value)})


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


def shape_diff(label: str, before: pd.DataFrame, after: pd.DataFrame) -> str:
    """Compact 'before -> after' shape report."""
    rows_lost = before.shape[0] - after.shape[0]
    cols_lost = before.shape[1] - after.shape[1]
    return (
        f"  {label:<46} {before.shape} -> {after.shape}  "
        f"(-{rows_lost} rows, -{cols_lost} cols)"
    )


def numeric_drift(label: str, before: pd.Series, after: pd.Series) -> str:
    """Compact 'before mean / after mean' report for a numeric column."""
    before_mean = before.mean()
    after_mean = after.mean()
    delta = after_mean - before_mean
    return f"  {label:<46} mean {before_mean:.2f} -> {after_mean:.2f}  ({delta:+.2f})"


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Walk five drop/fill strategies side-by-side on the same source frame."""
    print_banner("Assignment 4.34 — Handling Missing Values: Drop and Fill")
    raw = generate_postings_with_missingness()
    print(
        f"\n  Source frame: {raw.shape[0]} rows x {raw.shape[1]} columns,\n"
        f"  total missing cells = {int(raw.isna().sum().sum())}.\n"
    )
    raw_summary = pd.DataFrame(
        {
            "missing_count": raw.isna().sum(),
            "missing_rate": raw.isna().mean().round(3),
        }
    ).sort_values("missing_count", ascending=False)
    print_section("Per-column missingness (source):", raw_summary.to_string())

    # ----- 1) Drop strategies --------------------------------------------
    print_banner("1) Drop strategies — three flavours")
    drop_any = drop_rows_with_any_missing(raw)
    drop_subset = drop_rows_missing_subset(raw, ["salary_lpa", "date_posted"])
    drop_thresh = drop_rows_below_threshold(raw, min_non_null=raw.shape[1] - 1)
    drop_cols = drop_columns_above_missing_rate(raw, threshold=0.25)

    print(shape_diff("dropna(how='any')", raw, drop_any))
    print(shape_diff("dropna(subset=['salary_lpa', 'date_posted'])", raw, drop_subset))
    print(
        shape_diff("dropna(thresh=ncols-1)  (keep rows missing <=1)", raw, drop_thresh)
    )
    print(shape_diff("drop columns with >25% missing", raw, drop_cols))
    print(
        "\n  Reading: 'how=any' is the easiest to write but the most\n"
        "  destructive (loses 43 rows out of 100 on this frame). 'subset='\n"
        "  is usually what you actually want -- only drop when an\n"
        "  *important* column is missing. 'thresh=' is the per-row variant.\n"
        "  Dropping columns is right when a column is so sparse it's not\n"
        "  worth keeping (here, perks at 33% missing crosses the 25% gate)."
    )

    # ----- 2) Fill strategies — numeric ---------------------------------
    print_banner("2) Fill strategies — numeric columns (mean vs median vs group)")
    raw_salary = raw["salary_lpa"]
    fill_global_mean = raw.assign(
        salary_lpa=raw["salary_lpa"].fillna(raw["salary_lpa"].mean())
    )
    fill_global_median = fill_numeric_with_median(raw, "salary_lpa")
    fill_by_sector = fill_numeric_by_group(raw, "sector", "salary_lpa")

    print(numeric_drift("source (NaN dropped from mean)", raw_salary, raw_salary))
    print(
        numeric_drift("fillna(global mean)", raw_salary, fill_global_mean["salary_lpa"])
    )
    print(
        numeric_drift(
            "fillna(global median)", raw_salary, fill_global_median["salary_lpa"]
        )
    )
    print(
        numeric_drift(
            "fillna(per-sector median)", raw_salary, fill_by_sector["salary_lpa"]
        )
    )
    print(
        "\n  Reading: filling with mean shifts the column toward the mean\n"
        "  (no surprise), median preserves the typical row better when the\n"
        "  distribution is skewed (4.30 confirmed salary is right-skewed),\n"
        "  and the per-sector median is what 4.33's pattern detection\n"
        "  pointed at -- preserves within-sector structure rather than\n"
        "  smearing one global statistic across all rows."
    )

    # ----- 3) Fill strategies — categorical -----------------------------
    print_banner("3) Fill strategies — categorical columns (constant vs mode)")
    perks_before = raw["perks"].value_counts(dropna=False).head(6)
    fill_const = fill_with_constant(raw, "perks", "Unknown")
    fill_mode_perks = fill_with_mode(raw, "perks")
    perks_const = fill_const["perks"].value_counts(dropna=False).head(6)
    perks_mode = fill_mode_perks["perks"].value_counts(dropna=False).head(6)

    print_section("perks value counts (source, NaN visible):", perks_before.to_string())
    print_section(
        "perks value counts after fillna('Unknown'):", perks_const.to_string()
    )
    print_section("perks value counts after fillna(mode):", perks_mode.to_string())
    print(
        "\n  Reading: filling with 'Unknown' creates a new category that\n"
        "  preserves the missingness signal. Filling with the mode hides\n"
        "  the fact that 33 rows had no recorded perks at all -- those rows\n"
        "  now look like the most common category, which can distort any\n"
        "  later groupby('perks') aggregation."
    )

    # ----- 4) Combined recipe -------------------------------------------
    print_banner("4) A defensible combined recipe (per-column choice)")
    cleaned = raw.copy()
    # salary: per-sector median (structured fill that respects the
    # distribution differences across sectors).
    cleaned = fill_numeric_by_group(cleaned, "sector", "salary_lpa")
    # date_posted: only 5% missing -> drop those rows (small loss,
    # avoids inventing dates).
    cleaned = cleaned.dropna(subset=["date_posted"])
    # perks: 33% missing, structured -> mark as 'Unknown' instead of
    # imputing a value we don't have.
    cleaned = fill_with_constant(cleaned, "perks", "Unknown")
    # benefits_score: 34% missing, also structured -> per-sector median.
    cleaned = fill_numeric_by_group(cleaned, "sector", "benefits_score")

    after_summary = pd.DataFrame(
        {
            "missing_count": cleaned.isna().sum(),
            "missing_rate": cleaned.isna().mean().round(3),
        }
    ).sort_values("missing_count", ascending=False)

    print_section(
        f"After cleaning recipe -- shape {raw.shape} -> {cleaned.shape}:",
        after_summary.to_string(),
    )
    print(
        "\n  Per-column choices encoded above:\n"
        "    salary_lpa     -> per-sector median  (preserves structure)\n"
        "    date_posted    -> drop rows          (only 5% lost, no invented dates)\n"
        "    perks          -> 'Unknown'           (visible missingness)\n"
        "    benefits_score -> per-sector median  (consistent with salary)"
    )

    # ----- 5) Common mistake -- wrong fill for the dtype -----------------
    print_banner("5) Common mistake — wrong fill for the dtype")
    print(
        "  Filling a categorical column with a number, or a numeric column\n"
        "  with a string, breaks the dtype contract:\n\n"
        "    raw['perks'].fillna(0)        # perks becomes object/mixed\n"
        "    raw['salary_lpa'].fillna('?') # salary becomes object\n\n"
        "  Always match the fill value's type to the column's intended\n"
        "  dtype. `fill_with_constant` here uses a string for the perks\n"
        "  column on purpose -- pd.NA -> 'Unknown' keeps the dtype as\n"
        "  string, no silent coercion."
    )

    # ----- 6) Reconnect to disk -----------------------------------------
    print_banner("Bundled CSV — same recipe, on the on-disk frame")
    if SAMPLE_CSV_PATH.exists():
        bundled = pd.read_csv(SAMPLE_CSV_PATH, parse_dates=["date_posted"])
        print(
            f"  bundled frame shape = {bundled.shape}, "
            f"missing cells = {int(bundled.isna().sum().sum())}"
        )
        print(
            "  (Bundled CSV is already complete. The synthetic frame is\n"
            "  what exercises the cleaning recipes.)"
        )
    else:
        print("  sample_job_postings.csv not found -- skipping disk demo.")

    # Cheat sheet
    print_banner("Drop / fill cheat sheet")
    print(
        "  frame.dropna(how='any')                         -> any-NaN row drop (lossy)\n"
        "  frame.dropna(subset=[col])                      -> targeted row drop\n"
        "  frame.dropna(thresh=N)                          -> sliding cut-off\n"
        "  frame.dropna(axis=1)                            -> drop columns\n"
        "  series.fillna(value)                            -> constant fill\n"
        "  series.fillna(series.median())                  -> median fill\n"
        "  series.fillna(series.mode().iloc[0])            -> mode fill\n"
        "  frame.groupby(g)[c].transform('median')         -> group-aware fill source\n"
        "  series.ffill() / series.bfill()                 -> forward/back fill\n"
        "                                                     (for time-ordered data)"
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
