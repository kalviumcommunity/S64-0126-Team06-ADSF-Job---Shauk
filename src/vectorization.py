"""Assignment 4.25 — Applying Vectorized Operations Instead of Python Loops.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

4.24 showed that arithmetic on NumPy arrays is element-wise. This script
uses that rule to replace Python `for` loops with single array expressions —
the core mindset shift that makes NumPy code faster and more readable.

Three side-by-side comparisons:

    1. Scale every element by 1.1  (loop  vs  array * 1.1)
    2. Pairwise addition of two sequences  (loop  vs  a + b)
    3. Filter values above a threshold  (loop  vs  boolean mask)
    4. Apply a conditional transform  (loop  vs  np.where)

Each pair returns the same result; the script asserts this and then
prints a rough timing from `time.perf_counter` on 100 000 elements so
the performance gap is visible, not just claimed.

Run:
    python3 src/vectorization.py
"""

import time
from typing import Callable

import numpy as np


BANNER_WIDTH = 60
BENCH_SIZE = 100_000
THRESHOLD = 50


# ---------------------------------------------------------------------------
# LOOP-BASED IMPLEMENTATIONS — intentionally verbose; what we are replacing.
# ---------------------------------------------------------------------------
def loop_scale(values: list[int], factor: float) -> list[float]:
    """Multiply every element by `factor` using a Python loop."""
    result = []
    for value in values:
        result.append(value * factor)
    return result


def loop_pairwise_add(left: list[int], right: list[int]) -> list[int]:
    """Add two equal-length lists position by position."""
    result = []
    for index in range(len(left)):
        result.append(left[index] + right[index])
    return result


def loop_filter_above(values: list[int], threshold: int) -> list[int]:
    """Return only the elements strictly greater than `threshold`."""
    result = []
    for value in values:
        if value > threshold:
            result.append(value)
    return result


def loop_conditional_bonus(values: list[int], threshold: int) -> list[int]:
    """Double the element if it is above threshold, otherwise keep it."""
    result = []
    for value in values:
        if value > threshold:
            result.append(value * 2)
        else:
            result.append(value)
    return result


# ---------------------------------------------------------------------------
# VECTORISED IMPLEMENTATIONS — one expression each, element-wise in C.
# ---------------------------------------------------------------------------
def vectorised_scale(values: np.ndarray, factor: float) -> np.ndarray:
    """Multiply every element by `factor` — one array expression."""
    return values * factor


def vectorised_pairwise_add(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Element-wise addition — the whole loop collapses into `left + right`."""
    return left + right


def vectorised_filter_above(values: np.ndarray, threshold: int) -> np.ndarray:
    """Boolean-mask filtering — `values[values > threshold]`."""
    return values[values > threshold]


def vectorised_conditional_bonus(values: np.ndarray, threshold: int) -> np.ndarray:
    """`np.where(cond, if_true, if_false)` — the vectorised ternary."""
    return np.where(values > threshold, values * 2, values)


# ---------------------------------------------------------------------------
# BENCH HELPERS
# ---------------------------------------------------------------------------
def time_call(function: Callable, *args) -> tuple[float, object]:
    """Run `function(*args)` once and return (seconds_taken, result)."""
    start = time.perf_counter()
    result = function(*args)
    elapsed = time.perf_counter() - start
    return elapsed, result


def assert_equal_results(loop_result: object, vector_result: np.ndarray) -> bool:
    """True if the loop and vectorised outputs contain identical values."""
    return np.array_equal(np.asarray(loop_result), np.asarray(vector_result))


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def print_banner(title: str) -> None:
    """Print a fixed-width banner."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def print_comparison(
    label: str,
    loop_time: float,
    vector_time: float,
    results_match: bool,
) -> None:
    """Print a one-row timing + correctness comparison."""
    speedup = loop_time / vector_time if vector_time > 0 else float("inf")
    match_mark = "OK" if results_match else "MISMATCH"
    print(f"\n{label}")
    print(f"  loop       : {loop_time * 1000:8.2f} ms")
    print(f"  vectorised : {vector_time * 1000:8.2f} ms   (~{speedup:5.1f}x faster)")
    print(f"  equal?     : {match_mark}")


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the four loop-vs-vector comparisons on a 100 000-element dataset."""
    print_banner("Assignment 4.25 — Vectorised vs Loop")

    base_list = list(range(BENCH_SIZE))
    base_array = np.arange(BENCH_SIZE)

    # 1. scale
    loop_t, loop_r = time_call(loop_scale, base_list, 1.1)
    vec_t, vec_r = time_call(vectorised_scale, base_array, 1.1)
    print_comparison(
        "Scale every element by 1.1", loop_t, vec_t, assert_equal_results(loop_r, vec_r)
    )

    # 2. pairwise add
    other_list = list(range(BENCH_SIZE, 0, -1))
    other_array = np.arange(BENCH_SIZE, 0, -1)
    loop_t, loop_r = time_call(loop_pairwise_add, base_list, other_list)
    vec_t, vec_r = time_call(vectorised_pairwise_add, base_array, other_array)
    print_comparison(
        "Pairwise add two sequences", loop_t, vec_t, assert_equal_results(loop_r, vec_r)
    )

    # 3. filter above threshold
    loop_t, loop_r = time_call(loop_filter_above, base_list, THRESHOLD)
    vec_t, vec_r = time_call(vectorised_filter_above, base_array, THRESHOLD)
    print_comparison(
        f"Filter values > {THRESHOLD}",
        loop_t,
        vec_t,
        assert_equal_results(loop_r, vec_r),
    )

    # 4. conditional bonus
    loop_t, loop_r = time_call(loop_conditional_bonus, base_list, THRESHOLD)
    vec_t, vec_r = time_call(vectorised_conditional_bonus, base_array, THRESHOLD)
    print_comparison(
        f"Double value if > {THRESHOLD}, else keep",
        loop_t,
        vec_t,
        assert_equal_results(loop_r, vec_r),
    )

    print("\n" + "=" * BANNER_WIDTH)
    print("Takeaway: each vectorised version is one line, returns the same")
    print("values as the loop, and runs substantially faster on 100k elements.")
    print("=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
