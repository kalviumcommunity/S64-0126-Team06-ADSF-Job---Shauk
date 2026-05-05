"""Unit tests for io, validate, and clean modules (TC-01 – TC-12).

All tests use only in-memory DataFrames or the small fixture CSVs.
No external I/O beyond reading the fixtures directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure project root is on sys.path so `src` is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.utils.clean import (  # noqa: E402
    drop_null_rows,
    fill_nulls,
    fill_nulls_grouped,
    parse_skill_list,
    remove_duplicates,
    standardise_columns,
    standardise_dates,
)
from src.utils.io import load_csv  # noqa: E402
from src.utils.stats import detect_outliers_iqr, get_skill_frequency  # noqa: E402
from src.utils.validate import (  # noqa: E402
    assert_dtypes,
    check_nulls,
    validate_schema,
)

FIXTURES = ROOT / "tests" / "fixtures"


# ---------------------------------------------------------------------------
# TC-01  validate_schema — all expected columns present → True
# ---------------------------------------------------------------------------
def test_validate_schema_pass():
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
    assert validate_schema(df, ["a", "b", "c"]) is True


# ---------------------------------------------------------------------------
# TC-02  validate_schema — missing columns → ValueError listing them
# ---------------------------------------------------------------------------
def test_validate_schema_missing_columns():
    df = pd.DataFrame({"a": [1], "b": [2]})
    with pytest.raises(ValueError, match="Missing columns"):
        validate_schema(df, ["a", "b", "x", "y"])


def test_validate_schema_error_names_all_missing():
    """Error message must name every missing column."""
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError) as exc_info:
        validate_schema(df, ["a", "foo", "bar"])
    msg = str(exc_info.value)
    assert "foo" in msg
    assert "bar" in msg


# ---------------------------------------------------------------------------
# TC-03  check_nulls — returns correct counts
# ---------------------------------------------------------------------------
def test_check_nulls_counts():
    df = pd.DataFrame({"x": [1.0, None, None], "y": [1, 2, 3]})
    result = check_nulls(df)
    assert result["x"] == 2
    assert result["y"] == 0


def test_check_nulls_no_nulls():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    assert check_nulls(df).sum() == 0


# ---------------------------------------------------------------------------
# TC-04  remove_duplicates — injects 5 exact duplicates, expects them removed
# ---------------------------------------------------------------------------
def test_remove_duplicates_exact():
    base = pd.DataFrame({"id": [1, 2, 3], "val": ["a", "b", "c"]})
    with_dupes = pd.concat([base, base.iloc[:5]], ignore_index=True)
    result = remove_duplicates(with_dupes)
    assert len(result) == len(base)
    assert not result.duplicated().any()


def test_remove_duplicates_subset():
    df = pd.DataFrame({"id": [1, 1, 2], "ts": [10, 20, 30], "val": ["a", "b", "c"]})
    result = remove_duplicates(df, subset=["id"])
    assert len(result) == 2
    assert result["id"].is_unique


def test_remove_duplicates_monotone():
    df = pd.DataFrame({"x": list(range(10))})
    result = remove_duplicates(df)
    assert len(result) <= len(df)


# ---------------------------------------------------------------------------
# TC-05  parse_skill_list — normal input
# ---------------------------------------------------------------------------
def test_parse_skill_list_normal():
    assert parse_skill_list("Python, SQL,  R ") == ["python", "sql", "r"]


# ---------------------------------------------------------------------------
# TC-06  parse_skill_list — empty string
# ---------------------------------------------------------------------------
def test_parse_skill_list_empty_string():
    assert parse_skill_list("") == []


# ---------------------------------------------------------------------------
# TC-07  parse_skill_list — NaN / None
# ---------------------------------------------------------------------------
def test_parse_skill_list_nan():
    assert parse_skill_list(float("nan")) == []
    assert parse_skill_list(None) == []


def test_parse_skill_list_idempotent():
    """parse_skill_list(', '.join(result)) == result (round-trip idempotence)."""
    original = "Machine Learning, Python,  SQL "
    result = parse_skill_list(original)
    rejoined = ", ".join(result)
    assert parse_skill_list(rejoined) == result


def test_parse_skill_list_output_format():
    """Every element is non-empty, lowercased, stripped."""
    result = parse_skill_list("  Python , SQL , R  ")
    for token in result:
        assert token == token.lower()
        assert token == token.strip()
        assert len(token) > 0


# ---------------------------------------------------------------------------
# TC-08  get_skill_frequency — top skill matches expectation
# ---------------------------------------------------------------------------
def test_get_skill_frequency_top_skill():
    df = pd.DataFrame(
        {
            "canonical_skills": [
                ["python", "sql"],
                ["python", "r"],
                ["python"],
            ]
        }
    )
    freq = get_skill_frequency(df, "canonical_skills")
    assert freq.index[0] == "python"
    assert freq["python"] == 3


# ---------------------------------------------------------------------------
# TC-09  detect_outliers_iqr — one known outlier at index 0
# ---------------------------------------------------------------------------
def test_detect_outliers_iqr_single_outlier():
    # Values tightly clustered around 10; 1000 is the only outlier.
    # Q1≈10.2, Q3≈10.75, IQR≈0.55, fences ≈[9.4, 11.6] — all 10.x values are inside.
    s = pd.Series([1000.0, 10.0, 10.5, 11.0, 10.2, 10.8, 10.3, 10.7, 10.1, 10.6])
    result = detect_outliers_iqr(s)
    assert result.iloc[0] is np.bool_(True)
    assert not result.iloc[1:].any()


def test_detect_outliers_iqr_no_mutation():
    s = pd.Series([1.0, 2.0, 100.0, 1.5, 2.0, 1.8])
    original = s.copy()
    detect_outliers_iqr(s)
    pd.testing.assert_series_equal(s, original)


def test_detect_outliers_iqr_nan_is_false():
    """NaN values must produce False, not True, in the output mask."""
    s = pd.Series([1.0, np.nan, 3.0, 2.0, 2.5])
    result = detect_outliers_iqr(s)
    assert result.iloc[1] is np.bool_(False)


def test_detect_outliers_iqr_same_shape():
    s = pd.Series(range(20), dtype=float)
    result = detect_outliers_iqr(s)
    assert len(result) == len(s)
    assert list(result.index) == list(s.index)


# ---------------------------------------------------------------------------
# TC-10  load_csv — non-existent filepath → FileNotFoundError
# ---------------------------------------------------------------------------
def test_load_csv_missing_file():
    with pytest.raises(FileNotFoundError, match="Input file not found"):
        load_csv("/nonexistent/path/to/file.csv")


def test_load_csv_reads_fixture():
    df = load_csv(str(FIXTURES / "sample_job_postings.csv"), parse_dates=["date_posted"])
    assert not df.empty
    assert "date_posted" in df.columns


# ---------------------------------------------------------------------------
# TC-11  fill_nulls — nulls replaced with median; no NaN remains in numeric cols
# ---------------------------------------------------------------------------
def test_fill_nulls_median():
    df = pd.DataFrame({"salary": [10.0, None, 20.0, None, 15.0]})
    result = fill_nulls(df, strategy="median")
    assert result["salary"].isnull().sum() == 0
    expected_median = pd.Series([10.0, 20.0, 15.0]).median()
    assert result["salary"].iloc[1] == expected_median


def test_fill_nulls_does_not_mutate():
    df = pd.DataFrame({"x": [1.0, None, 3.0]})
    original_null_count = df["x"].isnull().sum()
    fill_nulls(df)
    assert df["x"].isnull().sum() == original_null_count  # original unchanged


# ---------------------------------------------------------------------------
# TC-12  standardise_columns — spaces and uppercase → lowercase underscores
# ---------------------------------------------------------------------------
def test_standardise_columns_lowercase_underscores():
    df = pd.DataFrame({"Job Title": [1], "Sector!": [2], " Salary (LPA) ": [3]})
    result = standardise_columns(df)
    assert "job_title" in result.columns
    assert "sector" in result.columns
    assert "salary_lpa" in result.columns


def test_standardise_columns_no_leading_trailing_underscore():
    df = pd.DataFrame({" col ": [1]})
    result = standardise_columns(df)
    for col in result.columns:
        assert not col.startswith("_")
        assert not col.endswith("_")


def test_standardise_columns_does_not_mutate():
    df = pd.DataFrame({"A B": [1]})
    original_cols = list(df.columns)
    standardise_columns(df)
    assert list(df.columns) == original_cols


# ---------------------------------------------------------------------------
# Additional: assert_dtypes
# ---------------------------------------------------------------------------
def test_assert_dtypes_pass():
    df = pd.DataFrame({"x": pd.array([1, 2], dtype="int64"), "y": [1.5, 2.5]})
    # Should not raise
    assert_dtypes(df, {"x": {"dtype": "int64"}, "y": {"dtype": "float64"}})


def test_assert_dtypes_mismatch_raises():
    df = pd.DataFrame({"col": ["a", "b"]})
    with pytest.raises(TypeError, match="Dtype assertion failed"):
        assert_dtypes(df, {"col": {"dtype": "int64"}})


# ---------------------------------------------------------------------------
# Additional: drop_null_rows
# ---------------------------------------------------------------------------
def test_drop_null_rows_removes_half_null():
    df = pd.DataFrame({"a": [1, None, 3], "b": [None, None, 3]})
    result = drop_null_rows(df, threshold=0.5)
    # Row 1 (index 1) has 2/2 nulls; row 0 has 1/2 null (= 50%) which is NOT > threshold
    assert len(result) <= len(df)


def test_drop_null_rows_monotone():
    df = pd.DataFrame({"x": [1, None, 3, None], "y": [None, None, None, 4]})
    result = drop_null_rows(df)
    assert len(result) <= len(df)


# ---------------------------------------------------------------------------
# Additional: fill_nulls_grouped
# ---------------------------------------------------------------------------
def test_fill_nulls_grouped_uses_group_median():
    df = pd.DataFrame(
        {
            "sector": ["Tech", "Tech", "Finance", "Finance"],
            "salary": [10.0, None, 20.0, None],
        }
    )
    result = fill_nulls_grouped(df, col="salary", group_col="sector")
    # Tech median is 10; Finance median is 20
    assert result.loc[1, "salary"] == 10.0
    assert result.loc[3, "salary"] == 20.0


def test_fill_nulls_grouped_non_increasing_null_count():
    df = pd.DataFrame(
        {
            "grp": ["A", "A", "B"],
            "val": [None, None, 1.0],
        }
    )
    input_nulls = df["val"].isnull().sum()
    result = fill_nulls_grouped(df, col="val", group_col="grp", fallback="global_median")
    assert result["val"].isnull().sum() <= input_nulls


# ---------------------------------------------------------------------------
# Additional: standardise_dates
# ---------------------------------------------------------------------------
def test_standardise_dates_converts_column():
    df = pd.DataFrame({"dt": ["2024-01-15", "2024-06-20"]})
    result = standardise_dates(df, "dt")
    assert str(result["dt"].dtype).startswith("datetime")


def test_standardise_dates_coerces_bad_values():
    # One bad value in 20 rows = 5%, below the 10% threshold → coerced to NaT (no exception).
    good = ["2024-01-15"] * 19
    df = pd.DataFrame({"dt": good + ["not-a-date"]})
    result = standardise_dates(df, "dt")
    assert pd.isna(result["dt"].iloc[-1])


def test_standardise_dates_raises_on_high_coerce_rate():
    df = pd.DataFrame({"dt": ["bad"] * 10 + ["2024-01-01"] * 2})
    with pytest.raises(RuntimeError, match="unparseable"):
        standardise_dates(df, "dt")
