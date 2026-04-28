"""Assignment 4.31 — Understanding Data Shapes and Column Data Types.

Author: Bhargav Kalambhe (Frontend & ML, covering Analyst)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

After loading a CSV (4.29) and running the standard inspection
routine (4.30), the next question every fresh DataFrame needs to
answer is: *what is the actual shape of this thing, and are the column
types what I expected?* These two questions decide whether your next
operation will work or silently corrupt the analysis.

Two failure modes this assignment is designed to expose:

    1. Wrong assumptions about size  -> off-by-one rows / dropped header
    2. Wrong assumptions about types -> numeric-looking columns that
                                        are actually strings; arithmetic
                                        silently concatenates instead
                                        of adding.

To make these failures visible, the script builds a deliberately
*messy* frame -- the kind of input you actually receive from a real
CSV that nobody cleaned -- and walks through how `shape`, `ndim`,
`size`, and `dtypes` reveal the problems before they become bugs.

Coverage:

    1. Shape, ndim, size                    -> how big is this frame?
    2. Rows = observations, cols = features -> what does each axis mean?
    3. dtypes per column                    -> what type did Pandas infer?
    4. Type-issue detection                 -> which columns are lying?
    5. Type-issue fixes                     -> to_numeric / astype repairs

Run:
    python3 src/dataframe_shape_types.py
"""

import io
from pathlib import Path

import numpy as np
import pandas as pd


BANNER_WIDTH = 72
SAMPLE_CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_job_postings.csv"
)

# A realistic-but-deliberately-broken CSV captured as a string. This is
# what you get from a hand-edited spreadsheet exported as CSV: salaries
# carry a currency prefix, missingness is encoded as `-` or `n/a`,
# yes/no flags are mixed-case strings, dates are slash-separated, and
# one numeric column has accidental string entries mixed in.
MESSY_POSTINGS_CSV = """job_id,job_title,sector,salary_lpa,is_remote,date_posted,experience_years
1,Data Scientist,Technology,"$12.5",Yes,2024-01-15,3
2,ML Engineer,Technology,"$18.0",no,2024-02-10,5
3,Data Analyst,Finance,"-",YES,2024-01-20,2
4,Backend Engineer,Finance,"$15.0",No,2024-03-05,unknown
5,Frontend Engineer,Retail,"n/a",yes,2024-03-22,4
6,Data Engineer,Healthcare,"$20.0",NO,2024-02-18,7
7,Research Scientist,Technology,"$22.5",Yes,2024-04-01,8
"""


# ---------------------------------------------------------------------------
# DATA HELPERS — load each frame in the state we want to study.
# ---------------------------------------------------------------------------
def load_clean_postings(path: Path) -> pd.DataFrame:
    """Load the bundled CSV with proper date parsing — the 'tidy' baseline."""
    return pd.read_csv(path, parse_dates=["date_posted"])


def load_messy_postings() -> pd.DataFrame:
    """Load the deliberately-broken CSV without any type coercion.

    No `parse_dates`, no `dtype=`, no `na_values=` — exactly what you
    get when someone hands you a CSV and says "just load it." This is
    what `dtypes` is supposed to reveal as wrong.
    """
    return pd.read_csv(io.StringIO(MESSY_POSTINGS_CSV))


def repair_messy_postings(messy: pd.DataFrame) -> pd.DataFrame:
    """Fix the messy frame's broken column types in-place-equivalent.

    Each repair is a single line plus a comment explaining the issue
    it solves; this is the canonical "type repair" recipe.
    """
    fixed = messy.copy()

    # salary: strip "$" and treat "-" / "n/a" as NaN, then coerce to float.
    fixed["salary_lpa"] = (
        fixed["salary_lpa"]
        .astype("string")
        .str.replace("$", "", regex=False)
        .replace({"-": pd.NA, "n/a": pd.NA, "NA": pd.NA})
    )
    fixed["salary_lpa"] = pd.to_numeric(fixed["salary_lpa"], errors="coerce")

    # is_remote: yes/no/YES/no -> proper boolean (with NaN fallback).
    truthy = {"yes", "y", "true", "1"}
    fixed["is_remote"] = (
        fixed["is_remote"]
        .astype("string")
        .str.strip()
        .str.lower()
        .map(lambda v: True if v in truthy else False if v else pd.NA)
        .astype("boolean")
    )

    # date_posted: explicit parse so dtype becomes datetime64[ns].
    fixed["date_posted"] = pd.to_datetime(fixed["date_posted"], errors="coerce")

    # experience_years: "unknown" mixed in with integers -> coerce to nullable int.
    fixed["experience_years"] = pd.to_numeric(
        fixed["experience_years"], errors="coerce"
    ).astype("Int64")

    return fixed


# ---------------------------------------------------------------------------
# INSPECTION HELPERS
# ---------------------------------------------------------------------------
def shape_report(frame: pd.DataFrame) -> str:
    """Return a multi-line shape report covering shape / ndim / size."""
    rows, cols = frame.shape
    return (
        f"  frame.shape -> {frame.shape}   ({rows} rows x {cols} columns)\n"
        f"  frame.ndim  -> {frame.ndim}   (a DataFrame is always 2-D)\n"
        f"  frame.size  -> {frame.size}   (rows * columns = total cell count)\n"
        f"  len(frame)  -> {len(frame)}   (row count, same as frame.shape[0])"
    )


def dtypes_report(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a small frame mapping each column to its dtype + a short hint.

    The hint encodes the rule a human normally checks by eye:
    'object on a numeric-named column = probably broken'.
    """
    rows = []
    for column, dtype in frame.dtypes.items():
        is_object = pd.api.types.is_object_dtype(dtype)
        name = column.lower()
        suspicious = ""
        # Numeric-sounding column name but dtype is object -> very likely
        # numbers stored as strings. This is the most common type bug.
        if is_object and any(
            token in name
            for token in ("salary", "price", "amount", "years", "count", "lpa")
        ):
            suspicious = (
                "<-- numeric-sounding column stored as object (probably strings)"
            )
        elif is_object and "date" in name:
            suspicious = "<-- date-sounding column not parsed (use pd.to_datetime)"
        elif is_object and "remote" in name:
            suspicious = "<-- yes/no flag stored as object (consider bool / category)"
        rows.append({"column": column, "dtype": str(dtype), "hint": suspicious})
    return pd.DataFrame(rows)


def detect_type_issues(frame: pd.DataFrame) -> list[str]:
    """Walk the frame and return a list of human-readable type warnings."""
    warnings = []
    for column in frame.columns:
        series = frame[column]
        if series.dtype == object:
            sample = series.dropna().astype(str).head(20)
            # Heuristic: if most non-null entries parse as numeric, the
            # column is *really* numeric and shouldn't be object.
            numeric_ok = pd.to_numeric(
                sample.str.replace("$", "", regex=False).replace(
                    {"-": np.nan, "n/a": np.nan}
                ),
                errors="coerce",
            ).notna()
            if numeric_ok.mean() > 0.6:
                warnings.append(
                    f"  '{column}' is dtype=object but {numeric_ok.mean():.0%} of "
                    f"sampled values parse as numeric -> coerce with pd.to_numeric()."
                )
    return warnings


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
    """Walk the shape-and-types lesson on a tidy frame and a messy one."""
    print_banner("Assignment 4.31 — DataFrame Shape and Column Data Types")

    clean = load_clean_postings(SAMPLE_CSV_PATH)
    messy = load_messy_postings()

    # ----- 1) Shape, ndim, size -----------------------------------------
    print_banner("1) Shape attributes — how big is the frame?")
    print_section("Tidy bundled CSV:", shape_report(clean))
    print_section("Messy in-memory CSV:", shape_report(messy))
    print(
        "\n   Reading: shape is the (rows, cols) tuple every later operation\n"
        "   sanity-checks against. ndim is always 2 for a DataFrame; size is\n"
        "   simply rows*cols and is useful for memory estimation."
    )

    # ----- 2) Rows = observations, cols = features ----------------------
    print_banner("2) What rows and columns mean in a tidy frame")
    print(
        "   Each row = one observation (here: one job posting).\n"
        "   Each column = one attribute of that observation\n"
        "                 (job_title, sector, salary_lpa, ...).\n\n"
        "   This 'tidy data' convention is what makes pandas operations\n"
        "   (filter, groupby, agg) read naturally:\n"
        "     filter(rows where sector == 'Finance')\n"
        "     groupby(column='sector').agg({'salary_lpa': 'mean'})"
    )

    # ----- 3) dtypes — what type did pandas infer? ----------------------
    print_banner("3) Column dtypes — what type did pandas infer?")
    print_section(
        "Tidy frame dtypes (parse_dates was used):",
        dtypes_report(clean).to_string(index=False),
    )
    print_section(
        "Messy frame dtypes (no parse_dates, no dtype=):",
        dtypes_report(messy).to_string(index=False),
    )
    print(
        "\n   Pandas dtype kinds you will meet most often:\n"
        "     int64           -> integers\n"
        "     float64         -> real numbers, also the home of NaN\n"
        "     bool            -> True / False (no NaN; use 'boolean' for nullable)\n"
        "     object          -> Python strings (or anything heterogeneous)\n"
        "     datetime64[ns]  -> timestamps with the .dt accessor\n"
        "     category        -> low-cardinality strings, memory-efficient"
    )

    # ----- 4) Detecting type issues -------------------------------------
    print_banner("4) Type-issue detection on the messy frame")
    issues = detect_type_issues(messy)
    if not issues:
        print("   No type issues detected.")
    else:
        print("   Heuristic warnings:")
        for line in issues:
            print(line)
    print(
        "\n   What goes wrong if you don't fix these:\n"
        "     messy['salary_lpa'].sum()  -> '$12.5$18.0-$15.0n/a$20.0$22.5'\n"
        "     (string concatenation, not arithmetic — a silent disaster.)"
    )

    # ----- 5) Repairing the types ---------------------------------------
    print_banner("5) Repair recipe — to_numeric / to_datetime / astype")
    fixed = repair_messy_postings(messy)
    print_section("Before (messy):", dtypes_report(messy).to_string(index=False))
    print_section("After  (fixed):", dtypes_report(fixed).to_string(index=False))

    print_section(
        "Same column, before and after — salary_lpa:",
        pd.DataFrame(
            {
                "before (object/strings)": messy["salary_lpa"].astype(str),
                "after  (float64, NaN where bad)": fixed["salary_lpa"],
            }
        ).to_string(),
    )

    # Now arithmetic actually works on the repaired column.
    fixed_total = fixed["salary_lpa"].sum()
    fixed_mean = fixed["salary_lpa"].mean()
    print(
        f"\n   fixed['salary_lpa'].sum()  -> {fixed_total:.2f}    "
        f"(real arithmetic, NaN ignored)"
        f"\n   fixed['salary_lpa'].mean() -> {fixed_mean:.2f}"
    )

    print_banner("Cheat sheet — shape and types every fresh frame needs")
    print(
        "   frame.shape       -> (rows, columns) tuple\n"
        "   frame.ndim        -> 2 for any DataFrame\n"
        "   frame.size        -> rows * columns\n"
        "   frame.dtypes      -> per-column type vector\n"
        "   pd.to_numeric()   -> coerce strings to numbers, errors='coerce'\n"
        "   pd.to_datetime()  -> coerce strings to timestamps\n"
        "   .astype('Int64')  -> nullable integer (keeps NaN)\n"
        "   .astype('boolean')-> nullable boolean\n"
        "   .astype('category')-> compact dtype for low-cardinality strings"
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
