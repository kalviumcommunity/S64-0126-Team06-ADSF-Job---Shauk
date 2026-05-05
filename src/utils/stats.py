"""Statistical engine: skill frequencies, lift, Wilson CI, stratified analysis.

All functions are pure (no I/O, no plt calls, no print). They accept DataFrames
and return DataFrames or scalars.
"""

from __future__ import annotations

import logging

import pandas as pd
from scipy.stats import binomtest

logger = logging.getLogger(__name__)


def get_skill_frequency(df: pd.DataFrame, skill_col: str) -> pd.Series:
    """Return per-skill occurrence counts sorted descending.

    Args:
        df: DataFrame with a column of skill lists.
        skill_col: Column name containing lists of skill strings.
    """
    return df[skill_col].explode().dropna().value_counts()


def get_top_skills(freq_series: pd.Series, n: int = 20) -> pd.Series:
    """Return the top-*n* skills by frequency, sorted descending.

    Postcondition: len(result) <= n and result is sorted descending.
    """
    return freq_series.nlargest(n)


def compute_placement_rate_by_skill(df: pd.DataFrame) -> pd.DataFrame:
    """Compute placement rate per skill from a placements DataFrame.

    Args:
        df: Must have 'skills_list' (list of str) and 'placed' (0/1) columns.

    Returns:
        DataFrame with columns: skill, placement_rate, count.
        Only skills with count >= 5 are included. Sorted by placement_rate descending.
    """
    min_support = 5
    exploded = (
        df[["skills_list", "placed"]]
        .explode("skills_list")
        .rename(columns={"skills_list": "skill"})
        .dropna(subset=["skill"])
    )
    grouped = (
        exploded.groupby("skill")
        .agg(count=("placed", "count"), placement_rate=("placed", "mean"))
        .reset_index()
    )
    result = (
        grouped[grouped["count"] >= min_support]
        .sort_values("placement_rate", ascending=False)
        .reset_index(drop=True)
    )
    return result


def compute_placement_lift(
    df: pd.DataFrame,
    skill_col: str = "canonical_skill",
    min_support: int = 5,
) -> pd.DataFrame:
    """Extract placement lift rows from a demand-supply table.

    Args:
        df: Output of build_skill_demand_supply_table.
        skill_col: Column containing skill names.
        min_support: Minimum supply_count to include a skill.

    Returns:
        DataFrame with columns: skill, lift, base_rate, skill_rate, support.
        Sorted by lift descending.

    Postcondition: Every row satisfies row.support >= min_support.
    """
    filtered = df[df["supply_count"] >= min_support].copy()
    result = filtered.rename(
        columns={
            skill_col: "skill",
            "skill_placement_rate": "skill_rate",
            "base_placement_rate": "base_rate",
            "supply_count": "support",
        }
    )[["skill", "lift", "base_rate", "skill_rate", "support"]]
    return result.sort_values("lift", ascending=False).reset_index(drop=True)


def wilson_confidence_interval(
    successes: int,
    trials: int,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Compute a Wilson binomial confidence interval.

    Uses scipy.stats.binomtest(...).proportion_ci(method='wilson').

    Args:
        successes: Number of successes (0 <= successes <= trials).
        trials: Total trials (must be > 0).
        confidence: Confidence level, e.g. 0.95.

    Returns:
        (low, high) bounds where 0 <= low <= successes/trials <= high <= 1.

    Raises:
        ValueError: If trials == 0 or successes > trials.
    """
    if trials == 0:
        raise ValueError("wilson_confidence_interval: trials must be > 0")
    if not (0 <= successes <= trials):
        raise ValueError(
            f"wilson_confidence_interval: invalid — successes={successes}, trials={trials}"
        )
    result = binomtest(int(successes), int(trials))
    ci = result.proportion_ci(method="wilson", confidence_level=confidence)
    return (float(ci.low), float(ci.high))


def stratified_placement_analysis(
    df: pd.DataFrame,
    strat_col: str,
    min_support: int = 5,
) -> pd.DataFrame:
    """Compute placement rates stratified by *strat_col*.

    Numeric strat_col values are binned into 5 equal-width bins before grouping.

    Args:
        df: Must have strat_col and 'placed' (0/1) columns.
        min_support: Strata smaller than this are excluded.

    Returns:
        DataFrame with: strat_col, placement_rate, count, ci_low, ci_high.
        Only strata with count >= min_support. Sorted by strat_col.
    """
    work = df.copy()
    if pd.api.types.is_numeric_dtype(work[strat_col]):
        work[strat_col] = pd.cut(work[strat_col], bins=5, precision=1)

    rows: list[dict] = []
    for stratum, group in work.groupby(strat_col, observed=True):
        count = len(group)
        if count < min_support:
            logger.debug(
                "stratified_placement_analysis: '%s' excluded (n=%d < %d)",
                stratum,
                count,
                min_support,
            )
            continue
        placements = int(group["placed"].sum())
        rate = placements / count
        try:
            ci_low, ci_high = wilson_confidence_interval(placements, count)
        except ValueError:
            ci_low, ci_high = 0.0, 1.0
        rows.append(
            {
                strat_col: stratum,
                "placement_rate": rate,
                "count": count,
                "ci_low": ci_low,
                "ci_high": ci_high,
            }
        )

    return pd.DataFrame(rows).sort_values(strat_col).reset_index(drop=True)


def select_temporal_granularity(date_series: pd.Series) -> str:
    """Auto-select a pandas resample rule based on date range span.

    Granularity rules:
        14–90 days  → 'W'  (weekly)
        91–730 days → 'ME' (month-end)
        > 730 days  → 'QE' (quarter-end)

    Raises:
        ValueError: If date range < 14 days (trend analysis is statistically meaningless).
        ValueError: If fewer than 2 non-null dates exist.
    """
    valid = date_series.dropna()
    if len(valid) < 2:
        raise ValueError("select_temporal_granularity: need at least 2 non-null dates")

    span_days = (valid.max() - valid.min()).days
    if span_days < 14:
        raise ValueError(
            f"Date range is {span_days} day(s) — less than 14 days; "
            "trend analysis is statistically meaningless."
        )
    if span_days <= 90:
        return "W"
    if span_days <= 730:
        return "ME"
    return "QE"


def skill_trend_over_time(
    df: pd.DataFrame,
    date_col: str,
    resample_rule: str | None = None,
) -> pd.DataFrame:
    """Compute per-skill occurrence counts per time period.

    Args:
        df: Must have date_col (datetime) and 'canonical_skills' (list of str) columns.
        resample_rule: Explicit pandas resample rule; auto-selected if None.

    Returns:
        DataFrame indexed by period. Columns = skills. Values = counts (int).
        Missing periods filled with 0.
    """
    work = df[[date_col, "canonical_skills"]].dropna(subset=[date_col]).copy()
    work = work.explode("canonical_skills").rename(columns={"canonical_skills": "skill"})
    work = work.dropna(subset=["skill"])
    work[date_col] = pd.to_datetime(work[date_col])
    work = work.set_index(date_col)

    rule = resample_rule or select_temporal_granularity(df[date_col])
    trend = (
        work.assign(count=1)
        .pivot_table(index=work.index, columns="skill", values="count", aggfunc="sum")
        .resample(rule)
        .sum()
        .fillna(0)
        .astype(int)
    )
    return trend


def correlation_matrix(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Compute Pearson correlation matrix for the specified columns.

    Postcondition: result is square and symmetric.
    """
    return df[cols].corr(method="pearson")


def detect_outliers_iqr(series: pd.Series) -> pd.Series:
    """Detect outliers using the IQR method (Tukey fences).

    Returns:
        Boolean pd.Series — True at index i iff series[i] is an outlier.
        NaN values → False (not flagged as outliers).
        Same length and index as input. Does not mutate input.

    Precondition: series has at least 4 non-null values.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return series.notna() & ((series < lower) | (series > upper))
