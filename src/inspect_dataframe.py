"""Assignment 4.30 — Inspecting DataFrames Using head(), info(), and describe().

Author: Bhargav Kalambhe (Frontend & ML, covering Analyst)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

Once a CSV is loaded (4.29), the very next question is always: *what
did I actually get?* Three Pandas methods answer that question from
three different angles, and used together they form the standard
"inspect-before-you-touch" routine for any new DataFrame:

    head() / tail()  -> a visual preview of the rows
    info()           -> the structural skeleton (columns, dtypes, nulls)
    describe()       -> a numeric snapshot (count / mean / std / quantiles)

This script demonstrates the routine on **two** frames so the lesson
holds at both ends of the size spectrum:

    Small frame   - the 3-row bundled `sample_job_postings.csv`,
                    which is how a learner first meets these methods.
    Realistic frame - a 120-row synthetic job-postings frame with
                    NaN injected into salary and date_posted, so the
                    output of info() and describe() is actually
                    informative (non-null counts < row count, real
                    spread, real quartiles, visible skew).

Each call is followed by a one-paragraph interpretation pointing at
the specific cells that matter. Skipping inspection is the most
common cause of late-stage analysis bugs (wrong dtype, hidden nulls,
off-by-one row count) — this assignment turns the three calls into
a routine you run on every fresh frame.

Run:
    python3 src/inspect_dataframe.py
"""

import io
from pathlib import Path

import numpy as np
import pandas as pd


BANNER_WIDTH = 72
SAMPLE_CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_job_postings.csv"
)

# Realistic-frame generator parameters. Kept as constants so a reader
# can tweak the size or the missing-value rate without hunting through
# function bodies.
SYNTHETIC_ROW_COUNT = 120
SYNTHETIC_SEED = 42
MISSING_SALARY_RATE = 0.12  # ~12% of salary rows will be NaN
MISSING_DATE_RATE = 0.05  # ~5% of date_posted rows will be NaT
SECTORS = ("Technology", "Finance", "Healthcare", "Retail", "Manufacturing")
ROLES = (
    "Data Scientist",
    "ML Engineer",
    "Data Analyst",
    "Backend Engineer",
    "Frontend Engineer",
    "Data Engineer",
    "Research Scientist",
)


# ---------------------------------------------------------------------------
# DATA HELPERS — load the small disk CSV and synthesise a realistic frame.
# ---------------------------------------------------------------------------
def load_postings(path: Path) -> pd.DataFrame:
    """Load the bundled sample CSV with date parsing already applied."""
    return pd.read_csv(path, parse_dates=["date_posted"])


def generate_realistic_postings(
    n_rows: int = SYNTHETIC_ROW_COUNT,
    seed: int = SYNTHETIC_SEED,
) -> pd.DataFrame:
    """Build a synthetic 120-row job-postings frame with realistic spread.

    Why synthetic data here: the bundled CSV has only 3 rows, which is
    not enough for `describe()` to produce meaningful quartiles or for
    `info()` to demonstrate a non-null gap. A larger frame with NaN
    values injected on purpose gives the inspection methods something
    real to report on.

    The salary distribution is intentionally right-skewed (lognormal)
    because real-world pay distributions are — that lets `describe()`
    show a visible gap between `mean` and `50%` (median).
    """
    rng = np.random.default_rng(seed)

    # Lognormal salaries -> mean > median, long right tail (realistic).
    salaries = rng.lognormal(mean=2.4, sigma=0.5, size=n_rows).round(1)

    # Dates spread across ~6 months of 2024.
    base_date = pd.Timestamp("2024-01-01")
    date_offsets = rng.integers(low=0, high=180, size=n_rows)
    dates = base_date + pd.to_timedelta(date_offsets, unit="D")

    frame = pd.DataFrame(
        {
            "job_id": np.arange(1, n_rows + 1, dtype="int64"),
            "job_title": rng.choice(ROLES, size=n_rows),
            "sector": rng.choice(SECTORS, size=n_rows),
            "experience_years": rng.integers(low=0, high=12, size=n_rows),
            "salary_lpa": salaries,
            "date_posted": dates,
        }
    )

    # Inject NaN deliberately so info() and describe() have something
    # to report. Real-world frames almost always have missing values;
    # showing this in the demo prevents "but the docs said
    # non-null = row count!" surprises later.
    salary_mask = rng.random(n_rows) < MISSING_SALARY_RATE
    date_mask = rng.random(n_rows) < MISSING_DATE_RATE
    frame.loc[salary_mask, "salary_lpa"] = np.nan
    frame.loc[date_mask, "date_posted"] = pd.NaT

    return frame


# ---------------------------------------------------------------------------
# INSPECTION HELPERS — one per method so each is independently testable.
# ---------------------------------------------------------------------------
def preview_head(frame: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Return the first `n` rows — Pandas defaults to 5."""
    return frame.head(n)


def preview_tail(frame: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Return the last `n` rows — useful when files are appended chronologically."""
    return frame.tail(n)


def structural_summary(frame: pd.DataFrame) -> str:
    """Capture `frame.info()` output as a string instead of writing to stdout.

    `info()` writes directly to stdout by default, which makes it hard
    to embed inside a structured report or a unit test. Redirecting
    through StringIO gives us the same string, labelled and re-printed
    in our own format.
    """
    buffer = io.StringIO()
    frame.info(buf=buffer)
    return buffer.getvalue()


def numeric_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Standard `describe()` — numeric (and datetime) columns only by default."""
    return frame.describe()


def all_columns_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """`describe(include='all')` adds string/category columns to the summary.

    For non-numeric columns this gives `count`, `unique`, `top`, `freq`
    instead of mean/std/min/max — useful for a one-shot overview of a
    mixed-type frame.
    """
    return frame.describe(include="all")


def null_counts(frame: pd.DataFrame) -> pd.Series:
    """Per-column NaN counts. Pairs naturally with `info()` for double-checking."""
    return frame.isna().sum()


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


def explain_skewness(frame: pd.DataFrame, column: str) -> str:
    """Return a one-line interpretation of mean-vs-median for a numeric column.

    The mean / median gap is the simplest skewness signal. This helper
    formats the comparison so the report can call it out specifically
    instead of leaving the reader to scan the describe() table.
    """
    mean = frame[column].mean()
    median = frame[column].median()
    gap = mean - median
    direction = "right" if gap > 0 else "left" if gap < 0 else "no"
    return (
        f"  {column}: mean = {mean:.2f}, median = {median:.2f}, "
        f"gap = {gap:+.2f} -> {direction}-skewed distribution."
    )


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def inspect_frame(frame: pd.DataFrame, label: str) -> None:
    """Run the head / info / describe routine on a single frame and explain it."""
    print_banner(f"Inspecting: {label}  (shape = {frame.shape})")

    # 1) head() / tail() -- visual preview
    print_section(
        "1) head(3) -- first three rows:",
        preview_head(frame, n=3).to_string(index=True),
    )
    print(
        "   Use head() to confirm the file parsed correctly and to spot "
        "obvious shape problems (e.g. all data in one column = wrong sep)."
    )

    print_section(
        "1b) tail(3) -- last three rows (most recent for chronologically-appended files):",
        preview_tail(frame, n=3).to_string(index=True),
    )

    # 2) info() -- structural skeleton
    print_section(
        "2) info() -- columns, dtypes, non-null counts, memory:",
        structural_summary(frame).rstrip(),
    )
    print(
        "   The Non-Null Count column is the easiest way to spot missing data;\n"
        "   if it's lower than the total row count, that column has NaNs."
    )
    print_section(
        "2b) Cross-check with isna().sum() -- per-column NaN totals:",
        null_counts(frame).to_string(),
    )

    # 3) describe() -- numeric snapshot
    print_section(
        "3) describe() -- numeric (+ datetime) summary:",
        numeric_summary(frame).to_string(),
    )

    # 3b) include='all' -- extends to string columns
    print_section(
        "3b) describe(include='all') -- adds string columns (unique / top / freq):",
        all_columns_summary(frame).to_string(),
    )


def main() -> None:
    """Run the inspection routine on the small CSV and the synthetic frame."""
    print_banner("Assignment 4.30 -- Inspecting DataFrames: head / info / describe")
    print(
        "Two frames are inspected to show the same routine at two scales:\n"
        f"  - small disk CSV ({SAMPLE_CSV_PATH.name})\n"
        f"  - synthetic realistic frame ({SYNTHETIC_ROW_COUNT} rows, NaN injected)\n"
    )

    small = load_postings(SAMPLE_CSV_PATH)
    inspect_frame(small, "data/raw/sample_job_postings.csv (3 rows)")

    realistic = generate_realistic_postings()
    inspect_frame(realistic, "synthetic job-postings frame (120 rows, NaN injected)")

    # Skewness reading -- the payoff of describe() on a realistic distribution.
    print_banner("Distribution reading -- the payoff of describe() on real data")
    print("Mean vs median tells you about skew at a glance:")
    print(explain_skewness(realistic, "salary_lpa"))
    print(explain_skewness(realistic, "experience_years"))
    print("\n  Lognormal salary -> mean > median -> right-skewed (long high-pay tail).")
    print("  Uniform years    -> mean ~ median -> roughly symmetric distribution.")

    # Cheat sheet -- when to reach for which method.
    print_banner("Inspection cheat sheet -- three questions, three methods")
    print(
        "  head() / tail()       -> 'Did the file parse the way I expected?'\n"
        "  info()                -> 'What columns exist, what types, any nulls,\n"
        "                            how big in memory?'\n"
        "  describe()            -> 'What is the numeric distribution per column?'\n"
        "  describe(include='all') -> '... plus categorical: unique / top / freq.'\n"
        "  isna().sum()          -> 'Confirm info()'s null counts numerically.'"
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
