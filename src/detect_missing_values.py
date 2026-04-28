"""Assignment 4.33 — Detecting Missing Values in DataFrames.

Author: Bhargav Kalambhe (Frontend & ML, covering Analyst)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

Detection comes before cleaning. Before deciding *how* to handle
missing data (4.34: drop or fill), every workflow has to answer four
detection questions:

    1. Where is data missing?      -> isna() boolean mask
    2. How much is missing?        -> per-column count and proportion
    3. Which rows are affected?    -> any-axis row reduction
    4. Are missingness patterns    -> co-occurrence between columns
       random or correlated?

This script uses a 100-row synthetic postings frame with
*deliberately mixed* missingness patterns so all four questions
have non-trivial answers:

    - salary_lpa     -> ~15% NaN (random across rows)
    - date_posted    -> ~5%  NaT (random across rows)
    - perks          -> ~30% NaN, but heavily concentrated in
                        Manufacturing/Retail rows so the pattern
                        question has real signal.
    - benefits_score -> ~20% NaN, *correlated* with perks NaN
                        (when perks is missing, benefits_score is
                        usually missing too).

The script also clarifies the three "missing" sentinels Pandas uses
under the hood -- NaN (float), NaT (datetime), pd.NA (nullable
types) -- and shows that `isna()` answers truthfully for all three.

Run:
    python3 src/detect_missing_values.py
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
# DATA HELPERS
# ---------------------------------------------------------------------------
def generate_postings_with_missingness(
    n_rows: int = SYNTHETIC_ROW_COUNT, seed: int = SYNTHETIC_SEED
) -> pd.DataFrame:
    """Build a 100-row frame with deliberately-shaped missingness patterns.

    Random missingness on salary/date is the easy case. The interesting
    pattern is on `perks` and `benefits_score`: perks is mostly missing
    in Manufacturing and Retail postings (those companies don't list
    perks), and benefits_score is correlated -- when perks is missing,
    benefits_score is usually missing too. This gives the pattern-of-
    missingness question (#4 in the docstring) real signal to detect.
    """
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

    # Random NaN: salary (~15%), date (~5%).
    frame.loc[rng.random(n_rows) < 0.15, "salary_lpa"] = np.nan
    frame.loc[rng.random(n_rows) < 0.05, "date_posted"] = pd.NaT

    # Sector-driven NaN on perks: Manufacturing/Retail rows are 70%
    # likely to have perks=NaN; other sectors are only 8% likely.
    is_low_perks_sector = pd.Series(sectors).isin(("Manufacturing", "Retail")).values
    perks_missing_prob = np.where(is_low_perks_sector, 0.70, 0.08)
    perks_missing_mask = rng.random(n_rows) < perks_missing_prob
    frame.loc[perks_missing_mask, "perks"] = pd.NA

    # Correlated NaN on benefits_score: when perks is missing,
    # benefits_score is missing 80% of the time; otherwise 5%.
    benefits_missing_prob = np.where(perks_missing_mask, 0.80, 0.05)
    benefits_missing_mask = rng.random(n_rows) < benefits_missing_prob
    frame.loc[benefits_missing_mask, "benefits_score"] = np.nan

    return frame


# ---------------------------------------------------------------------------
# DETECTION HELPERS
# ---------------------------------------------------------------------------
def boolean_mask(frame: pd.DataFrame) -> pd.DataFrame:
    """`isna()` returns a same-shape boolean frame; True where missing."""
    return frame.isna()


def per_column_counts(frame: pd.DataFrame) -> pd.Series:
    """Count of missing entries per column. Pairs naturally with `info()`."""
    return frame.isna().sum().sort_values(ascending=False)


def per_column_proportions(frame: pd.DataFrame) -> pd.Series:
    """Fraction of each column that is missing — easier to compare than counts."""
    return frame.isna().mean().sort_values(ascending=False)


def total_missing(frame: pd.DataFrame) -> int:
    """Total number of missing cells across the whole frame."""
    return int(frame.isna().sum().sum())


def rows_with_any_missing(frame: pd.DataFrame) -> pd.DataFrame:
    """Subset of rows that have at least one missing value, anywhere."""
    return frame[frame.isna().any(axis=1)]


def rows_with_all_missing(frame: pd.DataFrame) -> pd.DataFrame:
    """Subset of rows where every column is missing (rare but worth checking)."""
    return frame[frame.isna().all(axis=1)]


def missing_count_per_row(frame: pd.DataFrame) -> pd.Series:
    """How many missing values each row has — useful for triage."""
    return frame.isna().sum(axis=1).sort_values(ascending=False)


def co_missing_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    """Pairwise count of rows where two columns are both missing.

    A high diagonal-off entry between two columns means they tend to
    be missing together -- which is the difference between random and
    structured missingness.
    """
    mask = frame.isna().astype(int)
    co_matrix = mask.T @ mask  # int co-occurrence matrix
    return co_matrix


def missingness_by_group(
    frame: pd.DataFrame, group_col: str, target_col: str
) -> pd.Series:
    """Per-group missing rate of `target_col`.

    e.g. `missingness_by_group(frame, "sector", "perks")` reveals
    whether `perks` is more likely to be missing in some sectors.
    """
    return (
        frame.groupby(group_col, observed=True)[target_col]
        .apply(lambda series: series.isna().mean())
        .sort_values(ascending=False)
    )


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


def severity_label(rate: float) -> str:
    """Human-readable severity for a missing-rate value."""
    if rate == 0:
        return "complete"
    if rate < 0.05:
        return "low"
    if rate < 0.20:
        return "moderate"
    if rate < 0.50:
        return "high"
    return "critical"


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Walk the four detection questions on a frame with shaped missingness."""
    print_banner("Assignment 4.33 — Detecting Missing Values in DataFrames")
    frame = generate_postings_with_missingness()
    print(
        f"\n  Working frame: {frame.shape[0]} rows x {frame.shape[1]} columns,\n"
        f"  total cells = {frame.size}.\n"
    )

    # ----- 1) The boolean mask --------------------------------------------
    print_banner("1) isna() — same-shape boolean mask, True where missing")
    mask_head = boolean_mask(frame).head(5)
    print_section("frame.isna().head(5):", mask_head.to_string())
    print(
        "\n  isna() and isnull() are the same function — Pandas keeps both\n"
        "  names for historical reasons. Pick one and use it consistently;\n"
        "  this script uses isna() throughout."
    )

    # ----- 2) Per-column counts and proportions ---------------------------
    print_banner("2) Per-column counts and proportions")
    counts = per_column_counts(frame)
    proportions = per_column_proportions(frame)
    summary = pd.DataFrame(
        {
            "missing_count": counts,
            "missing_rate": proportions.round(3),
            "severity": proportions.map(severity_label),
        }
    )
    print_section("Per-column missing summary (sorted by count):", summary.to_string())
    print(f"\n  Total missing cells = {total_missing(frame)}")
    print("  Severity bands: low <5%, moderate <20%, high <50%, critical >=50%.")

    # ----- 3) Row-level detection -----------------------------------------
    print_banner("3) Row-level detection — which rows are affected?")
    any_missing = rows_with_any_missing(frame)
    all_missing = rows_with_all_missing(frame)
    print(
        f"  Rows with ANY missing : {len(any_missing)} / {len(frame)} "
        f"({len(any_missing) / len(frame):.0%})"
    )
    print(f"  Rows with ALL missing : {len(all_missing)} / {len(frame)}")

    per_row = missing_count_per_row(frame)
    worst = per_row.head(5)
    print_section(
        "Rows ranked by missing-cell count (top 5 worst):",
        frame.loc[worst.index].assign(missing_count=worst).to_string(),
    )

    # ----- 4) Pattern of missingness — random or structured? --------------
    print_banner("4) Pattern of missingness — random vs structured")
    co = co_missing_matrix(frame)
    relevant = co.loc[
        ["salary_lpa", "perks", "benefits_score", "date_posted"],
        ["salary_lpa", "perks", "benefits_score", "date_posted"],
    ]
    print_section("Pairwise co-missing counts:", relevant.to_string())
    print(
        "\n  Read the diagonal as 'rows where THIS column is missing'.\n"
        "  Off-diagonal cells are 'rows where BOTH columns are missing'.\n"
        "  A high off-diagonal entry means structured (correlated) missingness."
    )

    by_sector = missingness_by_group(frame, "sector", "perks")
    print_section("Per-sector missing rate of `perks`:", by_sector.round(3).to_string())
    print(
        "\n  Manufacturing and Retail show much higher rates than the others —\n"
        "  that's structured missingness, not random. The cleaning strategy\n"
        "  in 4.34 should treat these differently from missing-at-random nulls."
    )

    # ----- 5) Three sentinels: NaN, NaT, pd.NA ----------------------------
    print_banner("5) The three missing sentinels — NaN, NaT, pd.NA")
    sentinels = pd.DataFrame(
        {
            "value": [
                frame["salary_lpa"].iloc[
                    frame["salary_lpa"].isna().to_numpy().argmax()
                ],
                frame["date_posted"].iloc[
                    frame["date_posted"].isna().to_numpy().argmax()
                ],
                frame["perks"].iloc[frame["perks"].isna().to_numpy().argmax()],
            ],
            "type": ["np.nan (float)", "pd.NaT (datetime)", "pd.NA (nullable string)"],
            "isna()_says": [True, True, True],
        },
        index=["salary_lpa", "date_posted", "perks"],
    )
    print(sentinels.to_string())
    print(
        "\n  Three different sentinels, three different dtypes, one consistent\n"
        "  detection method: isna() returns True for all of them. Never test\n"
        "  for missingness with `value == np.nan` -- that's always False."
    )

    # ----- 6) Reconnect to disk -------------------------------------------
    print_banner("Bundled CSV — same detection, on the on-disk frame")
    if SAMPLE_CSV_PATH.exists():
        bundled = pd.read_csv(SAMPLE_CSV_PATH, parse_dates=["date_posted"])
        print(f"  shape = {bundled.shape}")
        print_section("  bundled.isna().sum() :", bundled.isna().sum().to_string())
        print(
            "  (Bundled CSV has no missing values -- all zeros, which is a\n"
            "  legitimate detection outcome. The synthetic frame is what\n"
            "  exercises the real lesson.)"
        )
    else:
        print("  sample_job_postings.csv not found -- skipping disk demo.")

    # Cheat sheet
    print_banner("Detection cheat sheet")
    print(
        "  frame.isna() / isnull()      -> same-shape boolean mask\n"
        "  frame.isna().sum()           -> per-column count\n"
        "  frame.isna().mean()          -> per-column proportion\n"
        "  frame.isna().sum().sum()     -> total missing cells\n"
        "  frame.isna().any(axis=1)     -> rows with at least one missing\n"
        "  frame.isna().all(axis=1)     -> rows where everything is missing\n"
        "  frame.isna().sum(axis=1)     -> missing count per row\n"
        "  frame.groupby(g)[c].apply(lambda s: s.isna().mean())\n"
        "                               -> per-group missing rate (pattern read)"
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
