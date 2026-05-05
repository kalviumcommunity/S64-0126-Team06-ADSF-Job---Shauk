"""Validation utilities: schema checks, dtype assertions, null / duplicate checks."""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def check_nulls(df: pd.DataFrame) -> pd.Series:
    """Return per-column null counts."""
    return df.isnull().sum()


def check_duplicates(df: pd.DataFrame, subset: list[str] | None = None) -> int:
    """Return the count of duplicate rows (optionally restricted to subset of columns)."""
    return int(df.duplicated(subset=subset).sum())


def validate_schema(df: pd.DataFrame, expected_cols: list[str]) -> bool:
    """Assert that all expected columns are present in df.

    Args:
        df: DataFrame to check.
        expected_cols: Column names that must exist.

    Returns:
        True if all columns are present.

    Raises:
        ValueError: Listing every missing column if any are absent.
    """
    missing = [col for col in expected_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Schema validation failed. Missing columns: {missing}")
    logger.info("validate_schema: OK — all %d expected columns present", len(expected_cols))
    return True


def assert_dtypes(df: pd.DataFrame, schema: dict[str, dict]) -> None:
    """Assert that column dtypes match the schema.

    Args:
        df: DataFrame to check.
        schema: Maps column names → {'dtype': str, ...}.
                Use 'datetime' to accept any datetime64 variant.

    Raises:
        TypeError: Listing all mismatched (col, expected, actual) triples.
    """
    mismatches: list[tuple[str, str, str]] = []
    for col, spec in schema.items():
        expected: str = spec.get("dtype", "") if isinstance(spec, dict) else str(spec)
        if col not in df.columns:
            continue
        actual = str(df[col].dtype)

        if expected in ("datetime", "datetime64[ns]") or expected.startswith("datetime"):
            if not actual.startswith("datetime"):
                mismatches.append((col, expected, actual))
        elif expected in ("int64", "Int64"):
            if actual not in ("int64", "Int64", "int32", "Int32"):
                mismatches.append((col, expected, actual))
        elif expected in ("float64", "Float64"):
            if actual not in ("float64", "Float64", "float32", "Float32"):
                mismatches.append((col, expected, actual))
        elif actual != expected:
            mismatches.append((col, expected, actual))

    if mismatches:
        details = "; ".join(f"{col}: expected {exp}, got {act}" for col, exp, act in mismatches)
        raise TypeError(f"Dtype assertion failed — {details}")
