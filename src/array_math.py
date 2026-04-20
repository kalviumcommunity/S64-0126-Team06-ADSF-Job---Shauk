"""Assignment 4.24 — Performing Basic Mathematical Operations on NumPy Arrays.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

4.22 created arrays; 4.23 explained their layout; this script puts
arithmetic on top of that layout. Every operation below is element-wise
and runs in vectorised C inside NumPy — no Python-level loop needed.

Covers:

    1. Element-wise +, -, *, / between two arrays of the same shape
    2. Scalar-to-array +, -, *, /, **
    3. Cross-type promotion (int + float -> float)
    4. A contrast with Python-list arithmetic so the element-wise
       rule is explicit, not assumed
    5. A domain mini-example: combining a "postings" array and a
       "candidates" array into a supply/demand ratio

Run:
    python3 src/array_math.py
"""

import numpy as np


BANNER_WIDTH = 60


# ---------------------------------------------------------------------------
# PURE HELPERS
# ---------------------------------------------------------------------------
def build_operand_arrays() -> tuple[np.ndarray, np.ndarray]:
    """Return two shape-matched 1-D arrays to operate on."""
    postings = np.array([120, 90, 40, 60, 20])
    candidates = np.array([80, 75, 35, 30, 15])
    return postings, candidates


def element_wise_operations(left: np.ndarray, right: np.ndarray) -> dict:
    """Return the four basic element-wise operations in one dict.

    Caller decides how to print them; this helper stays pure.
    """
    return {
        "add": left + right,
        "subtract": left - right,
        "multiply": left * right,
        "divide": left / right,
    }


def scalar_operations(array: np.ndarray, scalar: int) -> dict:
    """Return common scalar-to-array operations."""
    return {
        f"array + {scalar}": array + scalar,
        f"array - {scalar}": array - scalar,
        f"array * {scalar}": array * scalar,
        f"array / {scalar}": array / scalar,
        "array ** 2": array**2,
    }


def supply_demand_ratio(postings: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """Return `postings / candidates` — a market-demand lift per skill.

    Values > 1 mean demand exceeds supply (more postings than candidates);
    values < 1 mean the opposite. Division is element-wise so the ratio is
    computed for every position in one expression.
    """
    return postings / candidates


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def print_banner(title: str) -> None:
    """Print a fixed-width banner."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def print_labelled_results(title: str, results: dict) -> None:
    """Print a dict of `{label: array}` results under a title."""
    print(f"\n{title}")
    for label, value in results.items():
        print(f"  {label:<18} -> {value}")


def print_type_promotion_demo() -> None:
    """Show how mixing int and float promotes the result to float."""
    int_array = np.array([1, 2, 3])
    float_array = np.array([0.5, 0.5, 0.5])
    result = int_array + float_array
    print("\nType promotion:")
    print(f"  int_array        dtype = {int_array.dtype}")
    print(f"  float_array      dtype = {float_array.dtype}")
    print(f"  int + float      dtype = {result.dtype}   values = {result}")


def print_list_vs_array_demo() -> None:
    """Make the element-wise rule explicit next to Python list behaviour."""
    plain_list = [1, 2, 3]
    numpy_array = np.array([1, 2, 3])
    print("\nList vs array:")
    print(f"  [1,2,3] + [1,2,3]    -> {plain_list + plain_list}   (list concatenation)")
    print(f"  array  + array       -> {numpy_array + numpy_array} (element-wise add)")
    print(f"  [1,2,3] * 3          -> {plain_list * 3} (list repeat)")
    print(
        f"  array  * 3           -> {numpy_array * 3}           (element-wise multiply)"
    )


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Walk through element-wise, scalar, type-promotion, and domain examples."""
    postings, candidates = build_operand_arrays()

    print_banner("Assignment 4.24 — Basic Math on NumPy Arrays")

    print(f"\npostings   : {postings}")
    print(f"candidates : {candidates}")

    print_labelled_results(
        "Element-wise (two arrays, same shape):",
        element_wise_operations(postings, candidates),
    )

    print_labelled_results(
        "Scalar-to-array (scalar = 10):",
        scalar_operations(postings, 10),
    )

    print_type_promotion_demo()
    print_list_vs_array_demo()

    ratio = supply_demand_ratio(postings, candidates)
    print("\nSupply / demand lift (postings / candidates):")
    print(f"  {ratio}")
    print(f"  skills where demand exceeds supply: {np.sum(ratio > 1)} of {ratio.size}")

    print("=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
