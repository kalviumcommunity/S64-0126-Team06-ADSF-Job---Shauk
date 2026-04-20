"""Assignment 4.26 — Understanding NumPy Broadcasting with Simple Examples.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

4.22 created arrays, 4.23 explained their layout, 4.24 introduced
element-wise arithmetic, and 4.25 replaced loops with vectorised
expressions. Broadcasting is the mechanism NumPy uses to let
arithmetic between *different-shaped* arrays "just work" without
copying data or writing a loop.

Four progressively less trivial examples:

    1. Scalar with a 1-D array            (5, ) + ()          -> (5,)
    2. Scalar with a 2-D array            (3, 4) + ()         -> (3, 4)
    3. 2-D array with a row vector        (3, 4) + (4,)       -> (3, 4)
    4. 2-D array with a column vector     (3, 4) + (3, 1)     -> (3, 4)

Plus one example of an *incompatible* pair, demonstrated via
`try/except` so the script can print the real error message
without crashing.

Run:
    python3 src/broadcasting.py
"""

import numpy as np


BANNER_WIDTH = 60


# ---------------------------------------------------------------------------
# PURE HELPERS
# ---------------------------------------------------------------------------
def build_base_arrays() -> dict:
    """Return the four shapes used throughout the demo."""
    return {
        "vector_5": np.array([1, 2, 3, 4, 5]),
        "matrix_3x4": np.array(
            [
                [10, 20, 30, 40],
                [50, 60, 70, 80],
                [90, 100, 110, 120],
            ]
        ),
        "row_vector_4": np.array([1, 2, 3, 4]),
        "column_vector_3": np.array([[1], [2], [3]]),
    }


def try_incompatible_broadcast() -> str:
    """Attempt a broadcast that must fail and return the error message.

    `(3,)` and `(4,)` have no shape-alignment rule that makes them compatible,
    so NumPy raises ValueError. Returning the message keeps the script
    robust — it demonstrates the failure mode without aborting the demo.
    """
    left = np.array([1, 2, 3])
    right = np.array([10, 20, 30, 40])
    try:
        _ = left + right
        return "no error (unexpected)"
    except ValueError as error:
        return str(error)


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def print_banner(title: str) -> None:
    """Print a fixed-width banner."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def print_broadcast_case(
    label: str,
    left: np.ndarray,
    right: np.ndarray,
    operator_name: str,
    operator_result: np.ndarray,
) -> None:
    """Print one broadcast case: operand shapes, operator, result shape."""
    left_shape = left.shape if hasattr(left, "shape") else ()
    right_shape = right.shape if hasattr(right, "shape") else ()
    print(f"\n{label}")
    print(f"  left  {left_shape}  : {np.asarray(left).tolist()}")
    print(f"  right {right_shape}  : {np.asarray(right).tolist()}")
    print(f"  {operator_name:<9} -> shape {operator_result.shape}")
    print(f"  values            : {operator_result.tolist()}")


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Walk through scalar, row-vector, column-vector, and failing cases."""
    arrays = build_base_arrays()
    vector_5 = arrays["vector_5"]
    matrix_3x4 = arrays["matrix_3x4"]
    row_vector_4 = arrays["row_vector_4"]
    column_vector_3 = arrays["column_vector_3"]

    print_banner("Assignment 4.26 — NumPy Broadcasting")

    # 1. scalar + 1-D vector
    print_broadcast_case(
        "1) Scalar + 1-D vector   shape (5,) + ()  -> (5,)",
        vector_5,
        10,
        "v + 10",
        vector_5 + 10,
    )

    # 2. scalar + 2-D matrix
    print_broadcast_case(
        "2) Scalar + 2-D matrix   shape (3, 4) + ()  -> (3, 4)",
        matrix_3x4,
        100,
        "m + 100",
        matrix_3x4 + 100,
    )

    # 3. 2-D matrix + 1-D row vector (stretched across rows)
    print_broadcast_case(
        "3) Matrix + row vector   shape (3, 4) + (4,)  -> (3, 4)",
        matrix_3x4,
        row_vector_4,
        "m + row",
        matrix_3x4 + row_vector_4,
    )

    # 4. 2-D matrix + 2-D column vector (stretched across columns)
    print_broadcast_case(
        "4) Matrix + column vec   shape (3, 4) + (3, 1)  -> (3, 4)",
        matrix_3x4,
        column_vector_3,
        "m + col",
        matrix_3x4 + column_vector_3,
    )

    # 5. incompatible broadcast
    print("\n5) Incompatible shapes   (3,) + (4,)  -> ValueError")
    print(f"  caught: {try_incompatible_broadcast()}")

    print("\n" + "=" * BANNER_WIDTH)
    print("Rule of thumb: align shapes from the right; each pair of axes")
    print("must be equal, or one of them must be 1. Otherwise, ValueError.")
    print("=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
