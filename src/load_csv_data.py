"""Assignment 4.29 — Loading CSV Data into Pandas DataFrames.

Author: Bhargav Kalambhe (Frontend & ML, covering Analyst)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

Where 4.28 demonstrated *constructing* a DataFrame from in-memory
objects, this assignment focuses on the most common real-world entry
point for a data project: reading a CSV file from disk into a
DataFrame. Every later cleaning, analysis, and visualisation step
starts from a frame produced by `pd.read_csv`, so understanding its
arguments is what determines whether the rest of the pipeline gets
clean, typed, analysis-ready data — or a frame full of strings and
"NaN" surprises.

Six loading patterns walked through here:

    1. Plain load                      -> pd.read_csv(path)
    2. With date parsing               -> parse_dates=[...]
    3. With explicit dtype + na_values -> enforce types, mark sentinels
    4. Subset of columns + row index   -> usecols= and index_col=
    5. From an in-memory buffer        -> StringIO + custom separator
    6. With graceful error handling    -> try/except FileNotFoundError

Each pattern prints the resulting frame, its shape, and its dtypes so
you can see exactly what changed between the calls.

Run:
    python3 src/load_csv_data.py
"""

from io import StringIO
from pathlib import Path

import pandas as pd


BANNER_WIDTH = 64
SAMPLE_CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_job_postings.csv"
)

# A small in-memory CSV used to demonstrate non-default options
# (semicolon separator, sentinel value for missing data) without
# needing to write a second file to disk.
SEMICOLON_CSV = """skill;mentions;notes
python;12;
sql;9;-
excel;4;low-volume
"""


# ---------------------------------------------------------------------------
# PURE HELPERS — one loader per pattern, each returns a DataFrame.
# ---------------------------------------------------------------------------
def load_plain(path: Path) -> pd.DataFrame:
    """Baseline: let Pandas infer everything from the file."""
    return pd.read_csv(path)


def load_with_dates(path: Path) -> pd.DataFrame:
    """Parse the date column into datetime64 instead of leaving it as object."""
    return pd.read_csv(path, parse_dates=["date_posted"])


def load_with_explicit_types(path: Path) -> pd.DataFrame:
    """Force string columns to be string dtype and treat '-' as missing.

    Without this, Pandas falls back to the generic ``object`` dtype for
    text columns, which loses information and slows down downstream ops.
    """
    return pd.read_csv(
        path,
        dtype={"job_title": "string", "company": "string", "sector": "string"},
        na_values=["-", "n/a", "NA"],
    )


def load_subset(path: Path) -> pd.DataFrame:
    """Read only the columns we need and use job_id as the row index."""
    return pd.read_csv(
        path,
        usecols=["job_id", "job_title", "sector", "salary_lpa"],
        index_col="job_id",
    )


def load_from_buffer(text: str) -> pd.DataFrame:
    """Read a non-default-separator CSV directly from an in-memory string."""
    return pd.read_csv(StringIO(text), sep=";", na_values=[""])


def load_safely(path: Path) -> pd.DataFrame:
    """Return an empty frame instead of crashing if the file is missing."""
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def print_banner(title: str) -> None:
    """Print a fixed-width banner."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def print_frame_block(label: str, frame: pd.DataFrame) -> None:
    """Print a uniform description of a DataFrame: values + metadata."""
    print(f"\n{label}")
    if frame.empty:
        print("  (empty frame)")
        return
    print(frame.to_string())
    print(f"  shape   : {frame.shape}")
    print(f"  columns : {list(frame.columns)}")
    print("  dtypes  :")
    for column, dtype in frame.dtypes.items():
        print(f"    {column:<15} {dtype}")


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Walk through the six load patterns and contrast the resulting frames."""
    print_banner("Assignment 4.29 — Loading CSV Data into Pandas DataFrames")

    plain = load_plain(SAMPLE_CSV_PATH)
    with_dates = load_with_dates(SAMPLE_CSV_PATH)
    typed = load_with_explicit_types(SAMPLE_CSV_PATH)
    subset = load_subset(SAMPLE_CSV_PATH)
    buffered = load_from_buffer(SEMICOLON_CSV)

    print_frame_block(
        "1) Plain load — pd.read_csv(path):",
        plain,
    )
    print_frame_block(
        "2) Date-aware load — parse_dates=['date_posted']:",
        with_dates,
    )
    print_frame_block(
        "3) Explicit dtype + na_values — strings stay strings, '-' becomes NaN:",
        typed,
    )
    print_frame_block(
        "4) Column subset + index — usecols=[...], index_col='job_id':",
        subset,
    )
    print_frame_block(
        "5) In-memory buffer with sep=';' — StringIO + custom separator:",
        buffered,
    )

    # Error-handling demonstration: load a file that doesn't exist.
    missing = SAMPLE_CSV_PATH.parent / "does_not_exist.csv"
    safe = load_safely(missing)
    print_frame_block(
        "6) Safe load — missing file returns an empty frame, no crash:",
        safe,
    )

    # Contrast the *same* column under different load strategies.
    print("\nWhy it matters — same column, two dtypes:")
    print(f"  plain['date_posted'].dtype       -> {plain['date_posted'].dtype}")
    print(f"  with_dates['date_posted'].dtype  -> {with_dates['date_posted'].dtype}")
    print("  Only the parsed version supports .dt accessor and date arithmetic.")

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
