"""Assignment 4.23 — Understanding Array Shape, Dimensions, and Index Positions.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

Builds on 4.22 (creating arrays) by focusing on **how the data is laid out**
inside those arrays. Every NumPy bug eventually traces back to one of four
questions:

    shape  — what are the axis lengths?
    ndim   — how many axes are there?
    size   — how many elements total?
    index  — what position am I actually addressing?

The script shows the 1-D and 2-D cases side by side, prints a small index
map for each, and demonstrates zero-based row/column access.

Run:
    python3 src/array_shape_indexing.py
"""

import numpy as np


BANNER_WIDTH = 60


# ---------------------------------------------------------------------------
# PURE HELPERS
# ---------------------------------------------------------------------------
def build_sample_arrays() -> tuple[np.ndarray, np.ndarray]:
    """Return a 1-D array (skill mentions) and a 2-D array (sector x skill).

    The two fixtures match 4.22 so the reader can focus on shape/indexing
    without re-learning the data.
    """
    one_d = np.array([12, 9, 4, 6, 2, 11, 7, 3])
    two_d = np.array(
        [
            [12, 9, 4, 6],  # row 0 — tech
            [5, 11, 8, 3],  # row 1 — finance
            [2, 4, 10, 7],  # row 2 — healthcare
        ]
    )
    return one_d, two_d


def describe_layout(array: np.ndarray) -> dict:
    """Return the four layout facts every NumPy user checks first."""
    return {
        "shape": array.shape,
        "ndim": array.ndim,
        "size": array.size,
        "dtype": array.dtype,
    }


def safe_get(array: np.ndarray, *indices: int) -> object:
    """Return `array[*indices]` or a helpful message if it would be out-of-range.

    Shows how to *check* an index against `shape` before accessing it —
    prevents the `IndexError` that hides most shape bugs.
    """
    for axis_position, index in enumerate(indices):
        axis_length = array.shape[axis_position]
        if index < 0 or index >= axis_length:
            return f"<out of range on axis {axis_position}: index {index}, length {axis_length}>"
    return array[indices]


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def print_banner(title: str) -> None:
    """Print a fixed-width banner."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def print_layout_block(label: str, array: np.ndarray) -> None:
    """Print shape / ndim / size / dtype for one array."""
    layout = describe_layout(array)
    print(f"\n{label}")
    print(f"  values : {array.tolist()}")
    print(f"  shape  : {layout['shape']}")
    print(f"  ndim   : {layout['ndim']}")
    print(f"  size   : {layout['size']}")
    print(f"  dtype  : {layout['dtype']}")


def print_one_d_index_map(array: np.ndarray) -> None:
    """Show each 1-D element paired with its integer index."""
    print("\n1-D index map (position -> value):")
    for position, value in enumerate(array):
        print(f"  [{position}] -> {value}")


def print_two_d_index_map(array: np.ndarray) -> None:
    """Show each 2-D element paired with its (row, col) index."""
    print("\n2-D index map ((row, col) -> value):")
    rows, cols = array.shape
    for row_index in range(rows):
        for col_index in range(cols):
            print(f"  [{row_index}, {col_index}] -> {array[row_index, col_index]}")


def print_access_examples(one_d: np.ndarray, two_d: np.ndarray) -> None:
    """Demonstrate zero-based access, the :-slice, and out-of-range handling."""
    print("\nAccess examples:")
    print(f"  one_d[0]          -> {one_d[0]}   (first element, zero-based)")
    print(f"  one_d[-1]         -> {one_d[-1]}   (last element, negative index)")
    print(f"  two_d[0]          -> {two_d[0].tolist()}   (entire first row)")
    print(f"  two_d[:, 0]       -> {two_d[:, 0].tolist()}   (entire first column)")
    print(f"  two_d[1, 2]       -> {two_d[1, 2]}   (row 1, col 2)")
    print(f"  two_d[9, 0] safe  -> {safe_get(two_d, 9, 0)}")


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Build the fixtures, describe their layout, and walk through indexing."""
    one_d, two_d = build_sample_arrays()

    print_banner("Assignment 4.23 — Array Shape, Dimensions, Index Positions")

    print_layout_block("1-D array: flat skill mention counts", one_d)
    print_layout_block("2-D array: mentions by sector x skill", two_d)

    print_one_d_index_map(one_d)
    print_two_d_index_map(two_d)

    print_access_examples(one_d, two_d)

    print("=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
