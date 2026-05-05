"""Unit and property-based tests for the stats module (TC-18 – TC-25).

Covers wilson_confidence_interval, compute_placement_lift,
stratified_placement_analysis, select_temporal_granularity, correlation_matrix.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.utils.join import build_skill_demand_supply_table  # noqa: E402
from src.utils.stats import (  # noqa: E402
    compute_placement_lift,
    correlation_matrix,
    get_top_skills,
    select_temporal_granularity,
    stratified_placement_analysis,
    wilson_confidence_interval,
)


# ---------------------------------------------------------------------------
# TC-18  wilson_confidence_interval — (10, 100, 0.95) contains 0.10
# ---------------------------------------------------------------------------
def test_wilson_ci_contains_proportion():
    lo, hi = wilson_confidence_interval(10, 100)
    assert lo <= 0.10 <= hi


def test_wilson_ci_bounds_valid():
    for s, t in [(0, 10), (5, 10), (10, 10), (1, 100)]:
        lo, hi = wilson_confidence_interval(s, t)
        assert 0 <= lo <= hi <= 1
        if t > 0:
            prop = s / t
            assert lo <= prop <= hi


# ---------------------------------------------------------------------------
# TC-19  wilson_confidence_interval — trials == 0 → ValueError
# ---------------------------------------------------------------------------
def test_wilson_ci_zero_trials_raises():
    with pytest.raises(ValueError):
        wilson_confidence_interval(0, 0)


def test_wilson_ci_successes_gt_trials_raises():
    with pytest.raises(ValueError):
        wilson_confidence_interval(5, 3)


# ---------------------------------------------------------------------------
# TC-20  compute_placement_lift — known distribution → correct lift
# ---------------------------------------------------------------------------
def _make_demand_supply_with_known_lift() -> pd.DataFrame:
    """Craft a demand-supply table where python has lift = 0.75/0.60 = 1.25."""
    # 10 candidates total; 6 placed (base rate = 0.60)
    # 4 candidates have python; 3 placed → skill_rate = 0.75
    jobs = pd.DataFrame(
        {
            "job_id": [1, 2],
            "sector": ["Tech", "Tech"],
            "canonical_skills": [["python", "sql"], ["python"]],
        }
    )
    placements = pd.DataFrame(
        {
            "candidate_id": list(range(1, 11)),
            "canonical_skills": [
                ["python"],
                ["python"],
                ["python"],
                ["python"],
                ["sql"],
                ["sql"],
                ["sql"],
                ["sql"],
                ["sql"],
                ["sql"],
            ],
            "placed": [1, 1, 1, 0, 1, 1, 1, 0, 0, 0],
            # python: 3/4 placed → rate=0.75
            # sql: 3/6 placed → rate=0.50
            # base rate: 6/10 = 0.60
        }
    )
    return build_skill_demand_supply_table(jobs, placements)


def test_compute_placement_lift_python_lift():
    demand_supply = _make_demand_supply_with_known_lift()
    lift_df = compute_placement_lift(demand_supply, min_support=2)

    python_row = lift_df[lift_df["skill"] == "python"].iloc[0]
    expected_lift = 0.75 / 0.60
    assert abs(python_row["lift"] - expected_lift) < 1e-6


def test_compute_placement_lift_sorted_descending():
    demand_supply = _make_demand_supply_with_known_lift()
    lift_df = compute_placement_lift(demand_supply, min_support=1)
    lifts = list(lift_df["lift"])
    assert lifts == sorted(lifts, reverse=True)


# ---------------------------------------------------------------------------
# TC-22  fill_nulls_grouped (covered in test_utils.py — duplicated here for TC numbering)
# ---------------------------------------------------------------------------
# (See test_utils.py — test_fill_nulls_grouped_uses_group_median)


# ---------------------------------------------------------------------------
# TC-24  select_temporal_granularity — 45-day span → 'W'
# ---------------------------------------------------------------------------
def test_select_temporal_granularity_weekly():
    dates = pd.Series(pd.date_range("2024-01-01", periods=45, freq="D"))
    result = select_temporal_granularity(dates)
    assert result == "W"


def test_select_temporal_granularity_monthly():
    dates = pd.Series(pd.date_range("2024-01-01", periods=200, freq="D"))
    result = select_temporal_granularity(dates)
    assert result == "ME"


def test_select_temporal_granularity_quarterly():
    dates = pd.Series(pd.date_range("2020-01-01", periods=800, freq="D"))
    result = select_temporal_granularity(dates)
    assert result == "QE"


def test_select_temporal_granularity_too_short_raises():
    dates = pd.Series(pd.date_range("2024-01-01", periods=5, freq="D"))
    with pytest.raises(ValueError, match="14 days"):
        select_temporal_granularity(dates)


def test_select_temporal_granularity_single_value_raises():
    dates = pd.Series([pd.Timestamp("2024-01-01")])
    with pytest.raises(ValueError):
        select_temporal_granularity(dates)


# ---------------------------------------------------------------------------
# TC-25  assert_dtypes — object column where datetime expected → TypeError
# ---------------------------------------------------------------------------
def test_assert_dtypes_object_for_datetime():
    from src.utils.validate import assert_dtypes

    df = pd.DataFrame({"dt": ["2024-01-01", "2024-06-01"]})  # object dtype
    with pytest.raises(TypeError, match="Dtype assertion failed"):
        assert_dtypes(df, {"dt": {"dtype": "datetime"}})


# ---------------------------------------------------------------------------
# stratified_placement_analysis
# ---------------------------------------------------------------------------
def test_stratified_placement_analysis_rates_valid():
    df = pd.DataFrame(
        {
            "years_of_experience": [1.0, 2.0, 1.5, 3.0, 2.5, 1.0, 4.0, 3.5] * 5,
            "placed": [1, 0, 1, 1, 0, 1, 0, 1] * 5,
        }
    )
    result = stratified_placement_analysis(df, strat_col="years_of_experience", min_support=3)
    assert not result.empty
    assert (result["placement_rate"] >= 0).all()
    assert (result["placement_rate"] <= 1).all()
    # CI bounds must contain the rate
    for _, row in result.iterrows():
        assert row["ci_low"] <= row["placement_rate"] <= row["ci_high"]


def test_stratified_placement_analysis_respects_min_support():
    df = pd.DataFrame(
        {
            "years_of_experience": [1.0, 1.0, 1.0, 1.0, 1.0, 8.0],  # last bin has only 1
            "placed": [1, 0, 1, 0, 1, 1],
        }
    )
    result = stratified_placement_analysis(df, strat_col="years_of_experience", min_support=3)
    # The bin containing only 8.0 should be excluded
    assert (result["count"] >= 3).all()


# ---------------------------------------------------------------------------
# compute_placement_lift — min_support contract
# ---------------------------------------------------------------------------
def test_compute_placement_lift_min_support():
    demand_supply = _make_demand_supply_with_known_lift()
    for min_s in [1, 2, 5]:
        lift_df = compute_placement_lift(demand_supply, min_support=min_s)
        assert (lift_df["support"] >= min_s).all()


# ---------------------------------------------------------------------------
# correlation_matrix
# ---------------------------------------------------------------------------
def test_correlation_matrix_is_square_and_symmetric():
    df = pd.DataFrame(
        {
            "a": [1.0, 2.0, 3.0, 4.0],
            "b": [4.0, 3.0, 2.0, 1.0],
            "c": [1.0, 3.0, 2.0, 4.0],
        }
    )
    result = correlation_matrix(df, ["a", "b", "c"])
    assert result.shape[0] == result.shape[1]
    # Symmetry: result[i,j] == result[j,i]
    for i in result.index:
        for j in result.columns:
            assert abs(result.loc[i, j] - result.loc[j, i]) < 1e-10


def test_correlation_matrix_diagonal_is_one():
    df = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [3.0, 1.0, 2.0]})
    result = correlation_matrix(df, ["x", "y"])
    for col in result.columns:
        assert abs(result.loc[col, col] - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# get_top_skills — Property 11
# ---------------------------------------------------------------------------
def test_get_top_skills_length_at_most_n():
    freq = pd.Series({"a": 10, "b": 5, "c": 3, "d": 1})
    for n in [1, 2, 3, 10]:
        result = get_top_skills(freq, n)
        assert len(result) <= n


def test_get_top_skills_sorted_descending():
    freq = pd.Series({"a": 10, "b": 5, "c": 3})
    result = get_top_skills(freq, n=3)
    values = list(result.values)
    assert values == sorted(values, reverse=True)


# ---------------------------------------------------------------------------
# Property 15: Wilson CI always contains the sample proportion
# ---------------------------------------------------------------------------
@given(
    successes=st.integers(min_value=0, max_value=100),
    trials=st.integers(min_value=1, max_value=100),
)
@settings(max_examples=300)
def test_wilson_ci_contains_sample_proportion(successes: int, trials: int):
    assume(successes <= trials)
    lo, hi = wilson_confidence_interval(successes, trials)
    proportion = successes / trials
    assert lo <= proportion <= hi
    assert 0 <= lo <= hi <= 1


# ---------------------------------------------------------------------------
# Property 16: compute_placement_lift respects min_support
# ---------------------------------------------------------------------------
def test_compute_placement_lift_all_rows_above_min_support():
    demand_supply = _make_demand_supply_with_known_lift()
    for min_s in range(1, 8):
        result = compute_placement_lift(demand_supply, min_support=min_s)
        assert (result["support"] >= min_s).all()
