"""Cleaning utilities: null handling, deduplication, standardisation."""

from __future__ import annotations

import logging
import re

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def drop_null_rows(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Drop rows where the fraction of null values exceeds *threshold*.

    Args:
        threshold: Drop row if > threshold fraction of its values are null.

    Returns:
        Cleaned DataFrame with reset index. Does not mutate input.
    """
    min_valid = int(np.ceil(len(df.columns) * (1.0 - threshold)))
    result = df.dropna(thresh=min_valid).reset_index(drop=True)
    dropped = len(df) - len(result)
    if dropped:
        logger.info("drop_null_rows: removed %d rows (threshold=%.0f%%)", dropped, threshold * 100)
    return result


def fill_nulls(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
    """Fill nulls in every numeric column using *strategy* ('mean' or 'median').

    Does not mutate input.
    """
    result = df.copy()
    for col in result.select_dtypes(include="number").columns:
        if result[col].isnull().any():
            fill_value = result[col].mean() if strategy == "mean" else result[col].median()
            result[col] = result[col].fillna(fill_value)
    return result


def fill_nulls_grouped(
    df: pd.DataFrame,
    col: str,
    group_col: str,
    strategy: str = "median",
    fallback: str = "global_median",
) -> pd.DataFrame:
    """Fill nulls in *col* using per-group aggregates; fall back to global value.

    Args:
        col: Numeric column to fill.
        group_col: Categorical column to group by.
        strategy: 'mean' or 'median'.
        fallback: 'global_mean', 'global_median', or 'zero'.

    Returns:
        Copy of df with nulls in *col* filled. Does not mutate input.

    Postcondition: null count in col is <= original null count.
    """
    result = df.copy()
    agg_fn = "mean" if strategy == "mean" else "median"
    group_fills = result.groupby(group_col)[col].transform(agg_fn)

    if fallback == "global_mean":
        global_fill = float(result[col].mean())
    elif fallback == "zero":
        global_fill = 0.0
    else:
        global_fill = float(result[col].median())

    # Log groups where the entire group was null (must fall back to global)
    all_null_groups = result.groupby(group_col)[col].apply(lambda s: s.isnull().all())
    for grp in all_null_groups[all_null_groups].index:
        logger.info(
            "fill_nulls_grouped: group '%s' all-null in '%s'; using global %s (%.4f)",
            grp,
            col,
            strategy,
            global_fill,
        )

    result[col] = result[col].fillna(group_fills).fillna(global_fill)
    return result


def remove_duplicates(df: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    """Remove duplicate rows, keeping the first occurrence.

    Does not mutate input.
    """
    n_dupes = int(df.duplicated(subset=subset).sum())
    if n_dupes:
        logger.info("remove_duplicates: removed %d rows on subset=%s", n_dupes, subset)
    return df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase column names and replace non-alphanumeric runs with '_'.

    Example: 'Job  Title!' → 'job_title'

    Does not mutate input.
    """
    result = df.copy()
    result.columns = [
        re.sub(r"_+", "_", re.sub(r"[^0-9a-z]+", "_", c.strip().lower())).strip("_")
        for c in result.columns
    ]
    return result


def parse_skill_list(skill_str: object) -> list[str]:
    """Parse a comma-separated skill string into a cleaned list.

    Postconditions:
    - Empty string or NaN/None → []
    - Every element is lowercased and stripped
    - No element is an empty string
    - parse_skill_list(', '.join(parse_skill_list(s))) == parse_skill_list(s)  (idempotent)

    Example:
        'Python, SQL,  R ' → ['python', 'sql', 'r']
    """
    if not isinstance(skill_str, str) or not skill_str.strip():
        return []
    return [t for t in (t.strip().lower() for t in skill_str.split(",")) if t]


def standardise_dates(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Parse a string date column to datetime64, coercing failures to NaT.

    Raises:
        RuntimeError: If > 10% of rows fail to parse (indicates a format mismatch).

    Does not mutate input.
    """
    result = df.copy()
    original_nulls = int(result[col].isnull().sum())
    result[col] = pd.to_datetime(result[col], errors="coerce")
    new_nulls = int(result[col].isnull().sum())
    coerced = new_nulls - original_nulls
    if coerced > 0:
        pct = coerced / len(result)
        if pct > 0.10:
            raise RuntimeError(
                f"Date column '{col}' unparseable — {coerced} rows ({pct:.0%}) coerced to NaT. "
                "Check date format."
            )
        logger.warning("standardise_dates: %d rows coerced to NaT in '%s'", coerced, col)
    return result
