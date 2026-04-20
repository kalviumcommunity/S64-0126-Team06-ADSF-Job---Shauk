"""Assignment 4.28 — Creating Pandas DataFrames from Dictionaries and Files.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

A DataFrame is Pandas' 2-D labelled container — a dict of Series that
share the same row index. This is the form Harshita's cleaning pipeline
(4.29–4.38) will operate on, and the form Bhargav's visualisations
(4.39–4.43) will consume. The script walks through the four everyday
ways of creating a DataFrame and then inspects it with the standard
`head`/`info`/`describe` trio.

Four construction patterns:

    1. Dict of lists          -> each key is a column
    2. List of dicts          -> each element is a row
    3. Dict of Series         -> explicit column-level control
    4. CSV file via read_csv  -> the real-world entry point

Plus:
    - Inspect shape, columns, index, dtypes
    - Column selection (df["col"] and df[["a", "b"]])
    - Row selection (.iloc[i] and .loc[label])

Run:
    python3 src/pandas_dataframes.py
"""

from pathlib import Path

import numpy as np
import pandas as pd


BANNER_WIDTH = 60
SAMPLE_CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_job_postings.csv"
)


# ---------------------------------------------------------------------------
# PURE HELPERS — four construction patterns as small, testable functions.
# ---------------------------------------------------------------------------
def dataframe_from_dict_of_lists() -> pd.DataFrame:
    """Build a DataFrame where each dict key becomes a column."""
    data = {
        "skill": ["python", "sql", "excel", "tableau", "pytorch"],
        "mentions": [12, 9, 4, 6, 2],
        "sector": ["tech", "finance", "finance", "tech", "tech"],
    }
    return pd.DataFrame(data)


def dataframe_from_list_of_dicts() -> pd.DataFrame:
    """Build a DataFrame where each list element becomes a row."""
    rows = [
        {"skill": "python", "mentions": 12, "sector": "tech"},
        {"skill": "sql", "mentions": 9, "sector": "finance"},
        {"skill": "excel", "mentions": 4, "sector": "finance"},
    ]
    return pd.DataFrame(rows)


def dataframe_from_dict_of_series() -> pd.DataFrame:
    """Build a DataFrame from explicitly-named, explicitly-typed Series.

    Using Series instead of lists lets each column carry its own dtype
    and index, which Pandas then aligns when it assembles the frame.
    """
    columns = {
        "skill": pd.Series(["python", "sql", "excel"], dtype="string"),
        "mentions": pd.Series([12, 9, 4], dtype="int64"),
        "ratio": pd.Series([1.5, 1.2, 1.14], dtype="float64"),
    }
    return pd.DataFrame(columns)


def dataframe_from_csv() -> pd.DataFrame:
    """Load the bundled sample CSV. Returns an empty frame if missing."""
    if not SAMPLE_CSV_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(SAMPLE_CSV_PATH)


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
    print(frame.to_string(index=True))
    print(f"  shape   : {frame.shape}")
    print(f"  columns : {list(frame.columns)}")
    print(f"  index   : {list(frame.index)}")
    print("  dtypes  :")
    for column, dtype in frame.dtypes.items():
        print(f"    {column:<15} {dtype}")


def print_selection_examples(frame: pd.DataFrame) -> None:
    """Contrast column and row selection on a DataFrame."""
    print("\nColumn selection (returns a Series):")
    print(f"  frame['skill']        ->\n{frame['skill']}")

    print("\nMulti-column selection (returns a DataFrame):")
    print(f"  frame[['skill', 'mentions']] ->\n{frame[['skill', 'mentions']]}")

    print("\nRow selection:")
    print(f"  frame.iloc[0]         ->\n{frame.iloc[0]}")
    print(f"  frame.loc[0, 'skill'] -> {frame.loc[0, 'skill']}")


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Walk the four construction patterns and inspect the CSV-loaded frame."""
    print_banner("Assignment 4.28 — Pandas DataFrames from Dictionaries and Files")

    dict_of_lists = dataframe_from_dict_of_lists()
    list_of_dicts = dataframe_from_list_of_dicts()
    dict_of_series = dataframe_from_dict_of_series()
    csv_frame = dataframe_from_csv()

    print_frame_block(
        "1) DataFrame from a dict of lists (keys -> columns):", dict_of_lists
    )
    print_frame_block(
        "2) DataFrame from a list of dicts (list items -> rows):", list_of_dicts
    )
    print_frame_block(
        "3) DataFrame from a dict of Series (typed columns):", dict_of_series
    )

    if csv_frame.empty:
        print("\n4) CSV file: sample_job_postings.csv not found — skipped.")
    else:
        print_frame_block(
            "4) DataFrame from read_csv('data/raw/sample_job_postings.csv'):", csv_frame
        )
        print("\n  head(2):")
        print(csv_frame.head(2).to_string(index=False))

    print_selection_examples(dict_of_lists)

    # Confirm values array is a NumPy array, completing the 4.22 -> 4.28 arc.
    print("\nUnderlying storage:")
    print(f"  type(frame.values)    -> {type(dict_of_lists.values).__name__}")
    print(f"  isinstance ndarray?   -> {isinstance(dict_of_lists.values, np.ndarray)}")

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
