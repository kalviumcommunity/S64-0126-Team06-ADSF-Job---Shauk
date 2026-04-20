"""Assignment 4.27 — Creating Pandas Series from Lists and Arrays.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

A Pandas Series is Pandas' one-dimensional labelled container — the
building block for every DataFrame column the project will touch.
Think of it as a NumPy array with an attached index, a name, and
label-aware arithmetic.

Five side-by-side cases:

    1. Series from a plain Python list             (default 0..N-1 index)
    2. Series from a NumPy array                   (dtype preserved)
    3. Series with explicit string labels          (custom index)
    4. Series from a dict                          (keys become the index)
    5. Label-aware arithmetic between two Series   (index alignment)

Run:
    python3 src/pandas_series.py
"""

import numpy as np
import pandas as pd


BANNER_WIDTH = 60


# ---------------------------------------------------------------------------
# PURE HELPERS — construct the series forms described above.
# ---------------------------------------------------------------------------
def series_from_list() -> pd.Series:
    """Build a Series from a plain Python list with Pandas' default index."""
    mention_counts = [12, 9, 4, 6, 2]
    return pd.Series(mention_counts, name="mentions_from_list")


def series_from_numpy_array() -> pd.Series:
    """Build a Series from a NumPy array so the dtype carries over."""
    mention_counts = np.array([12, 9, 4, 6, 2])
    return pd.Series(mention_counts, name="mentions_from_array")


def series_with_labels() -> pd.Series:
    """Build a Series with skill names as the index instead of 0..N-1."""
    mention_counts = [12, 9, 4, 6, 2]
    skills = ["python", "sql", "excel", "tableau", "pytorch"]
    return pd.Series(mention_counts, index=skills, name="mentions_by_skill")


def series_from_dict() -> pd.Series:
    """Build a Series from a dict — keys become the index automatically."""
    data = {"python": 12, "sql": 9, "excel": 4, "tableau": 6, "pytorch": 2}
    return pd.Series(data, name="mentions_from_dict")


def demonstrate_label_alignment() -> pd.Series:
    """Return the sum of two skill Series with *different* labels.

    Label-aware arithmetic is what makes Series different from arrays:
    missing labels on either side become NaN, they do not silently zero.
    """
    tech_mentions = pd.Series(
        {"python": 12, "sql": 9, "tableau": 6},
        name="tech",
    )
    finance_mentions = pd.Series(
        {"python": 5, "sql": 11, "excel": 8},
        name="finance",
    )
    return tech_mentions + finance_mentions


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def print_banner(title: str) -> None:
    """Print a fixed-width banner."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def print_series_block(label: str, series: pd.Series) -> None:
    """Print a uniform description of a Series."""
    print(f"\n{label}")
    print(series)
    print(f"  name   : {series.name}")
    print(f"  dtype  : {series.dtype}")
    print(f"  shape  : {series.shape}")
    print(f"  index  : {list(series.index)}")
    print(f"  values : {series.values.tolist()}")


def print_access_examples(series: pd.Series) -> None:
    """Contrast positional (iloc) vs label-based (loc) access."""
    print("\nAccess patterns on the labelled series:")
    print(f"  series.iloc[0]        -> {series.iloc[0]}   (positional, zero-based)")
    print(f'  series.loc["python"]  -> {series.loc["python"]}   (by label)')
    print(f"  series.iloc[-1]       -> {series.iloc[-1]}   (last position)")
    print(f"  series[series > 5]    -> \n{series[series > 5]}")


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Walk through the four construction patterns, then label arithmetic."""
    print_banner("Assignment 4.27 — Pandas Series from Lists and Arrays")

    list_series = series_from_list()
    array_series = series_from_numpy_array()
    labelled_series = series_with_labels()
    dict_series = series_from_dict()

    print_series_block(
        "1) Series from Python list (default 0..N-1 index):", list_series
    )
    print_series_block("2) Series from NumPy array (dtype preserved):", array_series)
    print_series_block("3) Series with custom string labels:", labelled_series)
    print_series_block("4) Series from a dict (keys become the index):", dict_series)

    print_access_examples(labelled_series)

    combined = demonstrate_label_alignment()
    print("\n5) Label-aware addition of two Series (aligned by index):")
    print(combined)
    print("  note: labels missing on either side become NaN, not 0")

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
