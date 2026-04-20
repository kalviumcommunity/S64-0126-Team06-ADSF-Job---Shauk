"""Assignment 4.22 — Creating NumPy Arrays from Python Lists.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

This script is the first step out of plain-Python containers and into the
NumPy numerical stack. It demonstrates:

    1. Importing NumPy under the canonical alias `np`.
    2. Creating a 1D array from a flat Python list.
    3. Creating a 2D array from a nested (list-of-lists) Python list.
    4. Inspecting the four array properties every analyst checks first:
       shape, dtype, ndim, size.
    5. Contrasting element-wise array arithmetic with Python list behaviour.

Domain tie-in: the arrays model "skill mention counts" so the rest of
the sprint (4.23 shape/indexing, 4.24 arithmetic, 4.25 vectorisation,
4.26 broadcasting) can reuse the same numeric fixture.

Run:
    python3 src/numpy_arrays_from_lists.py
"""

# ---------------------------------------------------------------------------
# 1. IMPORTS — `np` is the universal NumPy alias. Use it even for one line
#    of NumPy code so readers do not have to guess the source of `array`.
# ---------------------------------------------------------------------------
import numpy as np


# ---------------------------------------------------------------------------
# 2. CONSTANTS
# ---------------------------------------------------------------------------
BANNER_WIDTH = 60


# ---------------------------------------------------------------------------
# 3. HELPERS — pure, no side effects, each does one thing.
# ---------------------------------------------------------------------------
def describe_array(label: str, array: np.ndarray) -> dict:
    """Return the four properties every NumPy user checks first."""
    return {
        "label": label,
        "values": array,
        "shape": array.shape,
        "ndim": array.ndim,
        "size": array.size,
        "dtype": array.dtype,
    }


def build_one_dimensional_array() -> np.ndarray:
    """Convert a flat Python list of skill mention counts into a 1D array."""
    mention_counts = [12, 9, 4, 6, 2, 11, 7, 3]
    return np.array(mention_counts)


def build_two_dimensional_array() -> np.ndarray:
    """Convert a nested list (rows = sectors, cols = skills) into a 2D array.

    Each row is one industry sector; each column is the same skill in the
    same position across sectors (python, sql, excel, tableau).
    """
    mentions_by_sector = [
        [12, 9, 4, 6],  # tech
        [5, 11, 8, 3],  # finance
        [2, 4, 10, 7],  # healthcare
    ]
    return np.array(mentions_by_sector)


# ---------------------------------------------------------------------------
# 4. REPORTING — side-effecting; kept separate from the helpers above.
# ---------------------------------------------------------------------------
def print_banner(title: str) -> None:
    """Print a fixed-width banner so sections stay visually distinct."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def print_array_description(description: dict) -> None:
    """Print the four key properties of an array in a uniform block."""
    print(f"\n{description['label']}")
    print(f"  values : {description['values']}")
    print(f"  shape  : {description['shape']}")
    print(f"  ndim   : {description['ndim']}")
    print(f"  size   : {description['size']}")
    print(f"  dtype  : {description['dtype']}")


def print_list_vs_array_contrast() -> None:
    """Demonstrate the difference between list `+` and array `+`."""
    plain_list = [1, 2, 3]
    numpy_array = np.array([1, 2, 3])

    print("\nWhy arrays, not lists, for numeric work:")
    print(f"  list  + list  -> {plain_list + plain_list}   (concatenation)")
    print(f"  array + array -> {numpy_array + numpy_array} (element-wise add)")
    print(f"  array * 3     -> {numpy_array * 3} (element-wise scale)")


# ---------------------------------------------------------------------------
# 5. ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Build the 1D and 2D arrays, describe them, then contrast with lists."""
    one_d = build_one_dimensional_array()
    two_d = build_two_dimensional_array()

    print_banner("Assignment 4.22 — NumPy Arrays from Python Lists")

    print_array_description(describe_array("1D array: skill mention counts", one_d))
    print_array_description(
        describe_array("2D array: mentions by sector x skill", two_d)
    )

    print_list_vs_array_contrast()

    print("=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
