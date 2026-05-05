"""Unit and property-based tests for the join module (TC-21 + Property 14)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.utils.join import build_sector_skill_matrix, build_skill_demand_supply_table  # noqa: E402

# ---------------------------------------------------------------------------
# Helper builders
# ---------------------------------------------------------------------------


def make_jobs(
    canonical_skills_col: list[list[str]], sectors: list[str] | None = None
) -> pd.DataFrame:
    n = len(canonical_skills_col)
    return pd.DataFrame(
        {
            "job_id": list(range(1, n + 1)),
            "sector": sectors if sectors else ["Technology"] * n,
            "canonical_skills": canonical_skills_col,
        }
    )


def make_placements(
    canonical_skills_col: list[list[str]],
    placed_col: list[int],
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "candidate_id": list(range(1, len(canonical_skills_col) + 1)),
            "canonical_skills": canonical_skills_col,
            "placed": placed_col,
        }
    )


# ---------------------------------------------------------------------------
# TC-21  build_skill_demand_supply_table — outer join semantics
# ---------------------------------------------------------------------------
def test_build_skill_demand_supply_table_outer_join():
    """Jobs with ['python','sql'], placements with ['sql','r'] → 3 rows."""
    df_jobs = make_jobs([["python", "sql"]])
    df_placements = make_placements([["sql", "r"]], [1])

    result = build_skill_demand_supply_table(df_jobs, df_placements)
    skills_in_result = set(result["canonical_skill"])
    assert "python" in skills_in_result
    assert "sql" in skills_in_result
    assert "r" in skills_in_result
    assert len(result) == 3  # python ∪ sql ∪ r


def test_build_skill_demand_supply_table_demand_count():
    """demand_count reflects how many job postings require a skill."""
    df_jobs = make_jobs([["python"], ["python", "sql"], ["r"]])
    df_placements = make_placements([["python"]], [1])

    result = build_skill_demand_supply_table(df_jobs, df_placements)
    python_row = result[result["canonical_skill"] == "python"].iloc[0]
    assert python_row["demand_count"] == 2


def test_build_skill_demand_supply_table_supply_count():
    """supply_count reflects how many candidates have a skill."""
    df_jobs = make_jobs([["python"]])
    df_placements = make_placements([["python"], ["python", "sql"], ["r"]], [1, 0, 1])

    result = build_skill_demand_supply_table(df_jobs, df_placements)
    python_row = result[result["canonical_skill"] == "python"].iloc[0]
    assert python_row["supply_count"] == 2


def test_build_skill_demand_supply_table_placed_counts():
    """placed_with_skill + unplaced_with_skill == supply_count for every row."""
    df_jobs = make_jobs([["python", "sql"], ["python"]])
    df_placements = make_placements(
        [["python", "sql"], ["python"], ["sql"]],
        [1, 0, 1],
    )
    result = build_skill_demand_supply_table(df_jobs, df_placements)
    for _, row in result.iterrows():
        assert row["placed_with_skill"] + row["unplaced_with_skill"] == row["supply_count"]


def test_build_skill_demand_supply_table_lift_non_negative():
    """Lift must be >= 0 for every row."""
    df_jobs = make_jobs([["python", "sql"]])
    df_placements = make_placements([["python", "sql"]], [1])
    result = build_skill_demand_supply_table(df_jobs, df_placements)
    assert (result["lift"] >= 0).all()


def test_build_skill_demand_supply_table_wilson_ci_valid():
    """Wilson CI: 0 <= ci_low <= skill_placement_rate <= ci_high <= 1."""
    df_jobs = make_jobs([["python", "sql"], ["python"]])
    df_placements = make_placements(
        [["python", "sql"], ["python"], ["sql"]],
        [1, 1, 0],
    )
    result = build_skill_demand_supply_table(df_jobs, df_placements)
    for _, row in result[result["supply_count"] > 0].iterrows():
        assert 0 <= row["wilson_ci_low"] <= row["skill_placement_rate"]
        assert row["skill_placement_rate"] <= row["wilson_ci_high"] <= 1


def test_build_skill_demand_supply_table_empty_raises():
    df_jobs = pd.DataFrame()
    df_placements = make_placements([["python"]], [1])
    with pytest.raises(ValueError):
        build_skill_demand_supply_table(df_jobs, df_placements)


# ---------------------------------------------------------------------------
# build_sector_skill_matrix
# ---------------------------------------------------------------------------
def test_build_sector_skill_matrix_shape():
    df_jobs = make_jobs(
        [["python", "sql"], ["python"], ["r"]],
        sectors=["Tech", "Finance", "Tech"],
    )
    df_placements = make_placements([["python"]], [1])
    matrix = build_sector_skill_matrix(df_jobs, df_placements)
    # 2 sectors (Tech, Finance), 3 skills (python, sql, r)
    assert matrix.shape[0] == 2
    assert matrix.shape[1] == 3


def test_build_sector_skill_matrix_no_negative():
    df_jobs = make_jobs([["python", "sql"]], sectors=["Tech"])
    df_placements = make_placements([["python"]], [1])
    matrix = build_sector_skill_matrix(df_jobs, df_placements)
    assert (matrix >= 0).all().all()


def test_build_sector_skill_matrix_missing_cells_zero():
    df_jobs = make_jobs(
        [["python"], ["r"]],
        sectors=["Tech", "Finance"],
    )
    df_placements = make_placements([["python"]], [1])
    matrix = build_sector_skill_matrix(df_jobs, df_placements)
    # Finance should have 0 for python
    assert matrix.loc["Finance", "python"] == 0


# ---------------------------------------------------------------------------
# Property 14: demand-supply table preserves outer join semantics
# ---------------------------------------------------------------------------
def test_demand_supply_outer_join_row_count():
    """Row count == |skills_jobs ∪ skills_placements|."""
    jobs_skills = [["python", "sql"], ["r"]]
    placement_skills = [["sql", "java"], ["python"]]
    df_jobs = make_jobs(jobs_skills)
    df_placements = make_placements(placement_skills, [1, 0])

    expected = {s for lst in jobs_skills for s in lst} | {
        s for lst in placement_skills for s in lst
    }
    result = build_skill_demand_supply_table(df_jobs, df_placements)
    assert len(result) == len(expected)
