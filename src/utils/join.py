"""Join utilities: demand-supply table and sector-skill matrix."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .stats import wilson_confidence_interval

logger = logging.getLogger(__name__)


def build_skill_demand_supply_table(
    df_jobs: pd.DataFrame,
    df_placements: pd.DataFrame,
) -> pd.DataFrame:
    """Build a per-canonical-skill demand / supply / placement table.

    Preconditions:
        - df_jobs has 'canonical_skills' column (list of str)
        - df_placements has 'canonical_skills' (list of str) and 'placed' (0/1)
        - Both DataFrames are non-empty

    Returns:
        DataFrame with schema SKILL_DEMAND_SUPPLY_SCHEMA — one row per skill
        appearing in either dataset (outer-join semantics).

    Postconditions:
        - Row count == len(jobs_skills ∪ placement_skills)
        - placed_with_skill + unplaced_with_skill == supply_count for every row
        - 0 <= wilson_ci_low <= skill_placement_rate <= wilson_ci_high <= 1
    """
    if df_jobs.empty or df_placements.empty:
        raise ValueError("Both df_jobs and df_placements must be non-empty.")

    # --- Demand side: job postings ---
    jobs_exp = (
        df_jobs[["canonical_skills"]]
        .explode("canonical_skills")
        .rename(columns={"canonical_skills": "skill"})
        .dropna(subset=["skill"])
    )
    jobs_exp = jobs_exp[jobs_exp["skill"].str.strip() != ""]
    demand = jobs_exp.groupby("skill").size().reset_index(name="demand_count")

    # --- Supply side: candidate placements ---
    pl_exp = (
        df_placements[["canonical_skills", "placed"]]
        .explode("canonical_skills")
        .rename(columns={"canonical_skills": "skill"})
        .dropna(subset=["skill"])
    )
    pl_exp = pl_exp[pl_exp["skill"].str.strip() != ""]
    supply = pl_exp.groupby("skill").size().reset_index(name="supply_count")
    placed_agg = (
        pl_exp[pl_exp["placed"] == 1].groupby("skill").size().reset_index(name="placed_with_skill")
    )

    # --- Outer join ---
    result = demand.merge(supply, on="skill", how="outer")
    result = result.merge(placed_agg, on="skill", how="left")
    result["demand_count"] = result["demand_count"].fillna(0).astype(int)
    result["supply_count"] = result["supply_count"].fillna(0).astype(int)
    result["placed_with_skill"] = result["placed_with_skill"].fillna(0).astype(int)
    result["unplaced_with_skill"] = result["supply_count"] - result["placed_with_skill"]

    # --- Demand-supply ratio (null when supply == 0) ---
    result["demand_supply_ratio"] = np.where(
        result["supply_count"] > 0,
        result["demand_count"] / result["supply_count"],
        np.nan,
    )

    # --- Placement rates and lift ---
    base_rate = float(df_placements["placed"].mean())
    result["base_placement_rate"] = base_rate
    result["skill_placement_rate"] = np.where(
        result["supply_count"] > 0,
        result["placed_with_skill"] / result["supply_count"],
        0.0,
    )
    result["lift"] = np.where(
        base_rate > 0,
        result["skill_placement_rate"] / base_rate,
        0.0,
    )

    # --- Wilson confidence intervals ---
    ci_low_list: list[float] = []
    ci_high_list: list[float] = []
    for row in result.itertuples(index=False):
        if row.supply_count > 0:
            lo, hi = wilson_confidence_interval(int(row.placed_with_skill), int(row.supply_count))
        else:
            lo, hi = 0.0, 0.0
        ci_low_list.append(lo)
        ci_high_list.append(hi)
    result["wilson_ci_low"] = ci_low_list
    result["wilson_ci_high"] = ci_high_list

    result = result.rename(columns={"skill": "canonical_skill"})
    logger.info("build_skill_demand_supply_table: %d skills in output", len(result))
    return result


def build_sector_skill_matrix(
    df_jobs: pd.DataFrame,
    df_placements: pd.DataFrame,
) -> pd.DataFrame:
    """Build a sector × canonical_skill count pivot from job postings.

    Args:
        df_jobs: Must have 'sector' and 'canonical_skills' columns.
        df_placements: Accepted for API consistency; not used in this function.

    Returns:
        DataFrame indexed by sector with skill-count columns. Missing cells = 0.
    """
    jobs_exp = (
        df_jobs[["sector", "canonical_skills"]]
        .explode("canonical_skills")
        .rename(columns={"canonical_skills": "skill"})
        .dropna(subset=["skill", "sector"])
    )
    jobs_exp = jobs_exp[jobs_exp["skill"].str.strip() != ""]
    matrix = jobs_exp.groupby(["sector", "skill"]).size().unstack(fill_value=0)
    logger.info("build_sector_skill_matrix: %d sectors × %d skills", *matrix.shape)
    return matrix
