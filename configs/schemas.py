"""Schema definitions for Job-ही-Shauk data contracts.

Each schema maps column names to a dict with:
  - dtype: expected pandas dtype string (use 'datetime' for any datetime64 variant)
  - nullable: whether the column allows null values
"""

from __future__ import annotations

JOB_POSTINGS_SCHEMA: dict[str, dict] = {
    "job_id": {"dtype": "int64", "nullable": False},
    "job_title": {"dtype": "object", "nullable": False},
    "company": {"dtype": "object", "nullable": True},
    "sector": {"dtype": "object", "nullable": True},
    "location": {"dtype": "object", "nullable": True},
    "skills_required": {"dtype": "object", "nullable": False},
    "date_posted": {"dtype": "datetime", "nullable": False},
    "experience_min_yrs": {"dtype": "float64", "nullable": True},
    "salary_lpa": {"dtype": "float64", "nullable": True},
}

PLACEMENT_OUTCOMES_SCHEMA: dict[str, dict] = {
    "candidate_id": {"dtype": "int64", "nullable": False},
    "skills": {"dtype": "object", "nullable": False},
    "education": {"dtype": "object", "nullable": True},
    "years_of_experience": {"dtype": "float64", "nullable": True},
    "placed": {"dtype": "int64", "nullable": False},
    "placement_date": {"dtype": "datetime", "nullable": True},
    "offered_salary_lpa": {"dtype": "float64", "nullable": True},
    "sector_placed_in": {"dtype": "object", "nullable": True},
}

EXPLODED_SKILLS_SCHEMA: dict[str, dict] = {
    "job_id": {"dtype": "int64", "nullable": False},
    "skill": {"dtype": "object", "nullable": False},
    "sector": {"dtype": "object", "nullable": True},
    "date_posted": {"dtype": "datetime", "nullable": False},
}

CANONICALIZED_SKILLS_SCHEMA: dict[str, dict] = {
    "raw_skill": {"dtype": "object", "nullable": False},
    "canonical_skill": {"dtype": "object", "nullable": True},
    "match_tier": {"dtype": "object", "nullable": False},
    "match_score": {"dtype": "float64", "nullable": True},
    "occurrence_count": {"dtype": "int64", "nullable": False},
}

SKILL_DEMAND_SUPPLY_SCHEMA: dict[str, dict] = {
    "canonical_skill": {"dtype": "object", "nullable": False},
    "demand_count": {"dtype": "int64", "nullable": False},
    "supply_count": {"dtype": "int64", "nullable": False},
    "placed_with_skill": {"dtype": "int64", "nullable": False},
    "unplaced_with_skill": {"dtype": "int64", "nullable": False},
    "demand_supply_ratio": {"dtype": "float64", "nullable": True},
    "base_placement_rate": {"dtype": "float64", "nullable": False},
    "skill_placement_rate": {"dtype": "float64", "nullable": False},
    "lift": {"dtype": "float64", "nullable": False},
    "wilson_ci_low": {"dtype": "float64", "nullable": False},
    "wilson_ci_high": {"dtype": "float64", "nullable": False},
}

# Required columns for validation (keys from schemas above)
REQUIRED_JOB_COLS: list[str] = list(JOB_POSTINGS_SCHEMA.keys())
REQUIRED_PLACEMENT_COLS: list[str] = list(PLACEMENT_OUTCOMES_SCHEMA.keys())
