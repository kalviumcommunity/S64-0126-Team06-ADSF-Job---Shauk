"""Assignment 4.35 — Identifying and Removing Duplicate Records.

Author: Bhargav Kalambhe (Frontend & ML, covering Analyst)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

Duplicate rows are the silent inflator of every aggregate metric:
counts double, averages stay roughly right, distributions look
plausible, and a downstream "we have 1,200 unique postings" turns
into a confidence-eroding "well, actually 1,043." Detection and
removal of duplicates is therefore one of the standard cleaning
steps -- but it's also one of the easiest to get wrong, because
"duplicate" means different things in different contexts.

This script demonstrates the full duplicate-handling vocabulary on
a 100-row synthetic frame **with two kinds of duplicates injected
on purpose**:

    1. EXACT duplicates    -> 8 rows are byte-identical re-appends
                              of an existing row (the easy case).
    2. LOGICAL duplicates  -> 6 rows have a different job_id but
                              identical (job_title, company, sector,
                              salary_lpa, date_posted) -- the same
                              job re-posted under a new id (a real
                              ATS pattern; harder to detect and the
                              decision of *whether* to dedupe these
                              is judgment-dependent).

The script then walks:

    1. duplicated() boolean mask              (where are duplicates?)
    2. duplicated().sum()                     (how many?)
    3. drop_duplicates() with keep variants   (which row to keep?)
    4. drop_duplicates(subset=...)            (logical-duplicate dedup)
    5. Before/after shape + integrity check   (verification)

Run:
    python3 src/dedup_records.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


BANNER_WIDTH = 72
SAMPLE_CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_job_postings.csv"
)

UNIQUE_ROW_COUNT = 100  # before duplicates are injected
EXACT_DUPLICATE_COUNT = 8
LOGICAL_DUPLICATE_COUNT = 6
SYNTHETIC_SEED = 17

SECTORS = ("Technology", "Finance", "Healthcare", "Retail", "Manufacturing")
COMPANIES = (
    "Acme Corp",
    "Beta Inc",
    "Gamma Ltd",
    "Delta Co",
    "Epsilon Group",
    "Zeta Holdings",
)
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
def generate_postings_with_duplicates(
    unique_rows: int = UNIQUE_ROW_COUNT,
    exact_dupes: int = EXACT_DUPLICATE_COUNT,
    logical_dupes: int = LOGICAL_DUPLICATE_COUNT,
    seed: int = SYNTHETIC_SEED,
) -> pd.DataFrame:
    """Build a frame with both exact and logical duplicates injected on purpose.

    The unique base is `unique_rows` rows of plausible postings. Then:
      - `exact_dupes` byte-identical copies of randomly chosen rows are
        appended (these are unambiguous duplicates).
      - `logical_dupes` rows are appended that share every field with
        an existing row EXCEPT job_id -- these represent the same job
        re-posted under a new internal id, which is what ATS systems
        actually do when a hiring manager edits and re-publishes.
    """
    rng = np.random.default_rng(seed)
    base_date = pd.Timestamp("2024-01-01")

    base = pd.DataFrame(
        {
            "job_id": np.arange(3001, 3001 + unique_rows, dtype="int64"),
            "job_title": rng.choice(ROLES, size=unique_rows),
            "company": rng.choice(COMPANIES, size=unique_rows),
            "sector": rng.choice(SECTORS, size=unique_rows),
            "experience_years": rng.integers(low=0, high=12, size=unique_rows),
            "salary_lpa": rng.lognormal(mean=2.4, sigma=0.5, size=unique_rows).round(1),
            "date_posted": base_date
            + pd.to_timedelta(rng.integers(0, 180, size=unique_rows), unit="D"),
        }
    )

    # 1) Exact duplicates: pick `exact_dupes` random rows and re-append.
    exact_idx = rng.choice(base.index, size=exact_dupes, replace=False)
    exact = base.loc[exact_idx].copy()

    # 2) Logical duplicates: pick `logical_dupes` rows, then re-issue
    #    them under fresh job_ids that don't collide with the base range.
    logical_idx = rng.choice(base.index, size=logical_dupes, replace=False)
    logical = base.loc[logical_idx].copy()
    next_id_start = base["job_id"].max() + 1
    logical["job_id"] = np.arange(
        next_id_start, next_id_start + logical_dupes, dtype="int64"
    )

    combined = pd.concat([base, exact, logical], ignore_index=True)
    # Shuffle so duplicates are not stuck at the bottom -- this is what
    # real datasets look like.
    combined = combined.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return combined


# ---------------------------------------------------------------------------
# DETECTION HELPERS
# ---------------------------------------------------------------------------
def duplicate_mask(frame: pd.DataFrame, subset: list[str] | None = None) -> pd.Series:
    """`duplicated()` -- True where the row matches an earlier row."""
    return frame.duplicated(subset=subset)


def duplicate_count(frame: pd.DataFrame, subset: list[str] | None = None) -> int:
    """Total number of duplicate rows (excluding the first occurrence)."""
    return int(frame.duplicated(subset=subset).sum())


def duplicate_groups(frame: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    """Return only the rows that participate in any duplicate group.

    `keep=False` flips the duplicated() flag on for *every* member of
    a duplicate group, including the first occurrence -- handy for
    inspecting what the duplicates look like before deciding to drop.
    """
    mask = frame.duplicated(subset=subset, keep=False)
    return frame[mask].sort_values(subset).reset_index(drop=True)


# ---------------------------------------------------------------------------
# REMOVAL HELPERS
# ---------------------------------------------------------------------------
def drop_exact_duplicates(frame: pd.DataFrame, keep: str = "first") -> pd.DataFrame:
    """Drop byte-identical duplicate rows. Keeps the first by default."""
    return frame.drop_duplicates(keep=keep)


def drop_by_subset(
    frame: pd.DataFrame, subset: list[str], keep: str = "first"
) -> pd.DataFrame:
    """Drop logical duplicates -- rows that match on `subset`, ignoring others.

    Use this when two rows differ only in a column that is NOT
    semantically meaningful (e.g. a system-generated job_id).
    """
    return frame.drop_duplicates(subset=subset, keep=keep)


def drop_all_duplicate_rows(
    frame: pd.DataFrame, subset: list[str] | None = None
) -> pd.DataFrame:
    """`keep=False` drops *every* row that participates in a duplicate group.

    Use this when a duplicate signals data corruption and none of the
    copies can be trusted.
    """
    return frame.drop_duplicates(subset=subset, keep=False)


# ---------------------------------------------------------------------------
# VERIFICATION HELPERS
# ---------------------------------------------------------------------------
def shape_and_residual_dupes(
    label: str, frame: pd.DataFrame, subset: list[str] | None = None
) -> str:
    """One-line shape + residual-duplicate count report."""
    return (
        f"  {label:<46} shape={frame.shape}  "
        f"residual_dupes={int(frame.duplicated(subset=subset).sum())}"
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


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Walk the duplicate-handling routine on a frame with two duplicate kinds."""
    print_banner("Assignment 4.35 — Identifying and Removing Duplicate Records")
    frame = generate_postings_with_duplicates()

    expected_total = UNIQUE_ROW_COUNT + EXACT_DUPLICATE_COUNT + LOGICAL_DUPLICATE_COUNT
    print(
        f"\n  Source frame: {frame.shape[0]} rows x {frame.shape[1]} columns "
        f"(constructed = {UNIQUE_ROW_COUNT} unique + {EXACT_DUPLICATE_COUNT} "
        f"exact + {LOGICAL_DUPLICATE_COUNT} logical = {expected_total}).\n"
    )

    # ----- 1) Detection: where are exact duplicates? --------------------
    print_banner("1) duplicated() — boolean mask of exact duplicates")
    exact_mask = duplicate_mask(frame)
    n_exact = int(exact_mask.sum())
    print(
        f"  frame.duplicated().sum()  -> {n_exact}  (expected: {EXACT_DUPLICATE_COUNT})"
    )

    print_section(
        "First few rows flagged as exact duplicates:",
        frame[exact_mask].head(3).to_string(),
    )
    print(
        "\n  duplicated() defaults to keep='first': it returns False for the\n"
        "  *first* occurrence of each row and True for every later copy."
    )

    # ----- 2) Detection: logical duplicates by subset --------------------
    print_banner("2) duplicated(subset=...) — logical duplicates ignoring job_id")
    business_keys = ["job_title", "company", "sector", "salary_lpa", "date_posted"]
    n_logical_total = duplicate_count(frame, subset=business_keys)
    print(
        f"  frame.duplicated(subset=business_keys).sum() -> {n_logical_total}\n"
        f"  (expected: {EXACT_DUPLICATE_COUNT} exact + {LOGICAL_DUPLICATE_COUNT} logical "
        f"= {EXACT_DUPLICATE_COUNT + LOGICAL_DUPLICATE_COUNT})"
    )

    groups = duplicate_groups(frame, subset=business_keys)
    print_section(
        f"All {len(groups)} rows that participate in a duplicate group "
        "(sorted to make pairs visible):",
        groups[["job_id", "job_title", "company", "sector", "salary_lpa"]]
        .head(8)
        .to_string(index=False),
    )
    print(
        "\n  Notice: pairs share job_title/company/sector/salary but have\n"
        "  *different* job_ids -- those are the logical duplicates that\n"
        "  the exact-duplicate detector missed."
    )

    # ----- 3) Removal — keep variants -----------------------------------
    print_banner("3) drop_duplicates() — three keep variants")
    keep_first = drop_exact_duplicates(frame, keep="first")
    keep_last = drop_exact_duplicates(frame, keep="last")
    keep_none = drop_all_duplicate_rows(frame)

    print(shape_and_residual_dupes("drop_duplicates(keep='first')", keep_first))
    print(shape_and_residual_dupes("drop_duplicates(keep='last')", keep_last))
    print(
        shape_and_residual_dupes(
            "drop_duplicates(keep=False)  (drops all duplicate rows)", keep_none
        )
    )
    print(
        "\n  Reading: keep='first' is the default and usually right (preserves\n"
        "  the earliest record). keep='last' matters when later rows have\n"
        "  more recent/corrected info. keep=False is the nuclear option for\n"
        "  data you cannot trust."
    )

    # ----- 4) Removal — subset-aware (logical duplicates) ---------------
    print_banner("4) drop_duplicates(subset=...) — collapse logical duplicates")
    logical_dedup = drop_by_subset(frame, subset=business_keys, keep="first")
    print(
        shape_and_residual_dupes(
            "drop_duplicates(subset=business_keys)", logical_dedup, subset=business_keys
        )
    )
    print(
        f"\n  Source rows: {len(frame)} "
        f"-> after subset dedup: {len(logical_dedup)}  "
        f"(removed {len(frame) - len(logical_dedup)})."
    )
    print(
        "  This is the only way to catch the 6 logical duplicates -- the\n"
        "  ones whose only difference was a fresh job_id."
    )

    # ----- 5) Verification — shape and integrity ------------------------
    print_banner("5) Verification — before/after shape and primary-key integrity")
    cleaned = drop_by_subset(frame, subset=business_keys, keep="first")
    print(
        f"  source.shape       = {frame.shape}\n"
        f"  cleaned.shape      = {cleaned.shape}\n"
        f"  rows_removed       = {len(frame) - len(cleaned)}  "
        f"(expected = {EXACT_DUPLICATE_COUNT + LOGICAL_DUPLICATE_COUNT})\n"
        f"  job_id is unique?  = {cleaned['job_id'].is_unique}  "
        "(integrity check on the natural key)\n"
        f"  cleaned.duplicated(subset=keys).any() = "
        f"{cleaned.duplicated(subset=business_keys).any()}  (must be False)"
    )

    # ----- 6) Reconnect to disk ------------------------------------------
    print_banner("Bundled CSV — same routine, on the on-disk frame")
    if SAMPLE_CSV_PATH.exists():
        bundled = pd.read_csv(SAMPLE_CSV_PATH, parse_dates=["date_posted"])
        print(
            f"  bundled shape = {bundled.shape}, "
            f"duplicated().sum() = {int(bundled.duplicated().sum())}"
        )
        print(
            "  (Bundled CSV has no duplicates by construction -- the synthetic\n"
            "  frame is what exercises the lesson.)"
        )
    else:
        print("  sample_job_postings.csv not found -- skipping disk demo.")

    # Cheat sheet
    print_banner("Dedup cheat sheet")
    print(
        "  frame.duplicated()                          -> mask of exact dupes\n"
        "  frame.duplicated(subset=cols)               -> mask by subset\n"
        "  frame.duplicated(keep=False)                -> mask flags ALL members\n"
        "  frame.duplicated().sum()                    -> count\n"
        "  frame.drop_duplicates()                     -> default keep='first'\n"
        "  frame.drop_duplicates(keep='last')          -> keep latest copy\n"
        "  frame.drop_duplicates(keep=False)           -> drop entire dupe groups\n"
        "  frame.drop_duplicates(subset=cols)          -> by subset (logical)\n"
        "  frame['key'].is_unique                      -> integrity assertion"
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
