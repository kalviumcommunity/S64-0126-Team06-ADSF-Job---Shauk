"""Assignment 4.32 — Selecting Rows and Columns Using Indexing and Slicing.

Author: Bhargav Kalambhe (Frontend & ML, covering Analyst)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

After loading (4.29), inspecting (4.30), and confirming shape + types
(4.31), the next thing every workflow does is *extract a subset*:
"give me only the Finance postings", "give me the salary column",
"give me the first ten rows for the demo." How that selection is
written determines whether the result is the rows you wanted, the
rows next to them, or a silent SettingWithCopyWarning that breaks
later writes.

This script demonstrates the full selection vocabulary on a 50-row
synthetic postings frame — small enough to read by eye, large enough
that boolean masks and slices return non-trivial sub-frames:

    1. Column selection by name           ->  df["col"], df[["a", "b"]]
    2. Row selection by position          ->  df.iloc[i], df.iloc[a:b]
    3. Row selection by label             ->  df.loc[label], df.loc[a:b]
    4. Combined (rows + columns)          ->  df.loc[rows, cols]
    5. Boolean masking                    ->  df[df["sector"] == "Finance"]
    6. Chained-indexing pitfall           ->  why df["col"][i] = x is wrong
    7. Out-of-range handling              ->  catching IndexError on iloc

The frame uses `job_id` as a *label* index (not a default RangeIndex)
so the iloc-vs-loc difference shows up in print output, not just in
the docs.

Run:
    python3 src/select_rows_columns.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


BANNER_WIDTH = 72
SAMPLE_CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_job_postings.csv"
)

# Generator parameters. Kept as constants so a reader can re-tune the
# frame without hunting through function bodies.
SYNTHETIC_ROW_COUNT = 50
SYNTHETIC_SEED = 7
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
def generate_postings(
    n_rows: int = SYNTHETIC_ROW_COUNT, seed: int = SYNTHETIC_SEED
) -> pd.DataFrame:
    """Build a 50-row synthetic frame indexed by `job_id` for label-based selection.

    Setting `job_id` as the index is what makes `loc` demonstrate
    *label* lookups (e.g. `loc[1001]`) distinct from `iloc[0]`. With
    a default RangeIndex the two would coincide on small frames and
    the lesson would be invisible.
    """
    rng = np.random.default_rng(seed)
    base_date = pd.Timestamp("2024-01-01")

    frame = pd.DataFrame(
        {
            "job_id": np.arange(1001, 1001 + n_rows, dtype="int64"),
            "job_title": rng.choice(ROLES, size=n_rows),
            "sector": rng.choice(SECTORS, size=n_rows),
            "experience_years": rng.integers(low=0, high=12, size=n_rows),
            "salary_lpa": rng.lognormal(mean=2.4, sigma=0.5, size=n_rows).round(1),
            "date_posted": base_date
            + pd.to_timedelta(rng.integers(0, 180, size=n_rows), unit="D"),
        }
    ).set_index("job_id")

    return frame


# ---------------------------------------------------------------------------
# SELECTION HELPERS — each pattern is one small, named function.
# ---------------------------------------------------------------------------
def select_one_column(frame: pd.DataFrame, column: str) -> pd.Series:
    """`df[column]` returns a Series — a single named column."""
    return frame[column]


def select_many_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """`df[[a, b]]` (note the *list* inside) returns a DataFrame."""
    return frame[columns]


def row_by_position(frame: pd.DataFrame, position: int) -> pd.Series:
    """`df.iloc[i]` — positional, zero-based, half-open like Python."""
    return frame.iloc[position]


def rows_by_position_slice(frame: pd.DataFrame, start: int, stop: int) -> pd.DataFrame:
    """`df.iloc[a:b]` — exclusive at the upper end (rows a..b-1)."""
    return frame.iloc[start:stop]


def row_by_label(frame: pd.DataFrame, label: int) -> pd.Series:
    """`df.loc[label]` — looks up by index *value*, not position."""
    return frame.loc[label]


def rows_by_label_slice(frame: pd.DataFrame, start: int, stop: int) -> pd.DataFrame:
    """`df.loc[a:b]` — INCLUSIVE on both ends (this is unlike pure Python)."""
    return frame.loc[start:stop]


def cells_by_label(frame: pd.DataFrame, rows: object, cols: list[str]) -> pd.DataFrame:
    """`df.loc[rows, cols]` — combined row+column label selection."""
    return frame.loc[rows, cols]


def filter_by_predicate(frame: pd.DataFrame, sector: str) -> pd.DataFrame:
    """`df[df['col'] == value]` — boolean-mask filtering."""
    mask = frame["sector"] == sector
    return frame[mask]


def safe_iloc(frame: pd.DataFrame, position: int) -> pd.Series | None:
    """Defensive `iloc` — returns None instead of raising IndexError."""
    if not 0 <= position < len(frame):
        return None
    return frame.iloc[position]


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
    """Walk the seven selection patterns on a label-indexed synthetic frame."""
    print_banner("Assignment 4.32 — Selecting Rows and Columns")

    frame = generate_postings()
    print(
        f"\n  Working frame: {frame.shape[0]} rows x {frame.shape[1]} columns,\n"
        f"  index = '{frame.index.name}' (job_ids {frame.index.min()}-{frame.index.max()}).\n"
    )

    # ----- 1) Column selection ------------------------------------------
    print_banner("1) Column selection — single name vs list of names")
    titles = select_one_column(frame, "job_title").head(5)
    print_section(
        "df['job_title'].head(5)  -> Series (one column):",
        titles.to_string(),
    )
    print(f"  type(...): {type(titles).__name__}")

    pair = select_many_columns(frame, ["job_title", "salary_lpa"]).head(5)
    print_section(
        "df[['job_title', 'salary_lpa']].head(5)  -> DataFrame (multiple columns):",
        pair.to_string(),
    )
    print(f"  type(...): {type(pair).__name__}")
    print(
        "\n  Why this matters: passing a string returns a Series, passing a\n"
        "  list returns a DataFrame. Many bugs are caused by accidentally\n"
        "  using df['x'] when df[['x']] was needed (or vice versa)."
    )

    # ----- 2) Row selection by position (iloc) --------------------------
    print_banner("2) Rows by POSITION — iloc[] (zero-based, exclusive upper bound)")
    print_section(
        "df.iloc[0]   -> first row, returned as a Series:",
        row_by_position(frame, 0).to_string(),
    )
    print_section(
        "df.iloc[0:3] -> first three rows (positions 0, 1, 2 — NOT 0..3):",
        rows_by_position_slice(frame, 0, 3).to_string(),
    )
    print_section(
        "df.iloc[-1]  -> last row (negative index works, like list/array):",
        row_by_position(frame, -1).to_string(),
    )

    # ----- 3) Row selection by label (loc) ------------------------------
    print_banner("3) Rows by LABEL — loc[] (looks up index *values*; inclusive)")
    first_label = frame.index[0]
    third_label = frame.index[2]
    print_section(
        f"df.loc[{first_label}] -> the row whose job_id == {first_label}:",
        row_by_label(frame, first_label).to_string(),
    )
    print_section(
        f"df.loc[{first_label}:{third_label}] -> INCLUSIVE on both ends "
        f"(returns 3 rows, not 2):",
        rows_by_label_slice(frame, first_label, third_label).to_string(),
    )
    print(
        "\n  Inclusive vs exclusive is the most common iloc/loc gotcha:\n"
        "    iloc[0:3] -> 3 rows  (positions 0, 1, 2)\n"
        "    loc[a:b]  -> N rows  where N = (b - a) + 1 if labels are dense\n"
        "  Choose loc when slicing by label, iloc when slicing by position."
    )

    # ----- 4) Combined row + column selection ---------------------------
    print_banner("4) Rows AND columns together — loc[rows, cols]")
    finance_rows = frame.index[frame["sector"] == "Finance"][:3]
    cells = cells_by_label(frame, finance_rows, ["job_title", "salary_lpa"])
    print_section(
        f"df.loc[{list(finance_rows)}, ['job_title', 'salary_lpa']]:",
        cells.to_string(),
    )
    print(
        "\n  This is the canonical 'give me these specific cells' form.\n"
        "  iloc has the same shape: df.iloc[row_positions, col_positions]."
    )

    # ----- 5) Boolean masking -------------------------------------------
    print_banner("5) Boolean masking — df[df['col'] <op> value]")
    finance = filter_by_predicate(frame, "Finance")
    print_section(
        "df[df['sector'] == 'Finance']  -> all rows where sector is Finance:",
        finance.head(5).to_string(),
    )
    print(
        f"\n  {len(finance)} of {len(frame)} rows matched. "
        "Multiple conditions combine with & and | (parentheses required):\n"
        "    df[(df['sector'] == 'Finance') & (df['salary_lpa'] > 15)]\n"
        "  '&' / '|' / '~' on Series — *not* Python's 'and' / 'or' / 'not'."
    )

    # ----- 6) Chained-indexing pitfall ----------------------------------
    print_banner("6) Why `df[col][row] = value` is the wrong way to assign")
    print(
        "  This is the canonical chained-indexing trap:\n"
        "      frame['salary_lpa'][1001] = 99   # raises SettingWithCopyWarning\n"
        "  The first [] returns a *copy* in some cases, so the assignment\n"
        "  to its [1001] cell may or may not stick on the original frame.\n\n"
        "  The safe form does the whole assignment through one .loc call:\n"
        "      frame.loc[1001, 'salary_lpa'] = 99   # always sticks, never warns\n\n"
        "  Rule of thumb: any *write* should use .loc / .iloc with both\n"
        "  axes specified together; never chain two separate [] subscripts."
    )

    # Demonstrate the safe form in action.
    target_label = frame.index[0]
    before = frame.loc[target_label, "salary_lpa"]
    frame.loc[target_label, "salary_lpa"] = 99.0
    after = frame.loc[target_label, "salary_lpa"]
    frame.loc[target_label, "salary_lpa"] = before  # restore for downstream reads
    print(f"\n  Verified write via .loc: before = {before}, after = {after}.")

    # ----- 7) Out-of-range handling -------------------------------------
    print_banner("7) Out-of-range handling — defensive iloc with safe_iloc()")
    out_of_range = safe_iloc(frame, len(frame) + 100)
    in_range = safe_iloc(frame, 0)
    print(f"  safe_iloc(frame, len(frame) + 100) -> {out_of_range}  (None, no crash)")
    print_section(
        "  safe_iloc(frame, 0) -> first row:",
        "" if in_range is None else in_range.to_string(),
    )

    # Cheat sheet
    print_banner("Selection cheat sheet — when to reach for which form")
    print(
        "  df['col']                  -> Series        (single column)\n"
        "  df[['a', 'b']]             -> DataFrame     (column subset)\n"
        "  df.iloc[i]                 -> Series        (i-th row, positional)\n"
        "  df.iloc[a:b]               -> DataFrame     (positions a..b-1)\n"
        "  df.loc[label]              -> Series        (row by index value)\n"
        "  df.loc[a:b]                -> DataFrame     (INCLUSIVE both ends)\n"
        "  df.loc[rows, cols]         -> DataFrame     (cells)\n"
        "  df[df['col'] == v]         -> DataFrame     (boolean mask)\n"
        "  df.loc[mask, 'col'] = v    -> safe write    (one-shot assignment)"
    )

    # Brief reuse of the bundled CSV so the lesson reconnects to disk data.
    print_banner("Bundled CSV — same patterns, on the on-disk frame")
    if SAMPLE_CSV_PATH.exists():
        bundled = pd.read_csv(SAMPLE_CSV_PATH, parse_dates=["date_posted"])
        print_section(
            "bundled[['job_title', 'salary_lpa']]:",
            bundled[["job_title", "salary_lpa"]].to_string(index=False),
        )
        print_section(
            "bundled[bundled['sector'] == 'Technology']:",
            bundled[bundled["sector"] == "Technology"].to_string(index=False),
        )
    else:
        print("  sample_job_postings.csv not found -- skipping disk demo.")

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
