"""Shared utility package for the Job-ही-Shauk v2 pipeline.

Import everything from here — notebooks and pipeline.py never reach into sub-modules directly.
"""

from .canonicalize import canonicalize_skill, canonicalize_skill_list, load_skill_vocabulary
from .clean import (
    drop_null_rows,
    fill_nulls,
    fill_nulls_grouped,
    parse_skill_list,
    remove_duplicates,
    standardise_columns,
    standardise_dates,
)
from .io import inspect_dataframe, load_csv
from .join import build_sector_skill_matrix, build_skill_demand_supply_table
from .logging_config import configure_logging
from .stats import (
    compute_placement_lift,
    compute_placement_rate_by_skill,
    correlation_matrix,
    detect_outliers_iqr,
    get_skill_frequency,
    get_top_skills,
    select_temporal_granularity,
    skill_trend_over_time,
    stratified_placement_analysis,
    wilson_confidence_interval,
)
from .validate import assert_dtypes, check_duplicates, check_nulls, validate_schema
from .viz import (
    plot_correlation_heatmap,
    plot_placement_lift,
    plot_salary_distribution,
    plot_salary_vs_experience,
    plot_skill_boxplot,
    plot_skill_trend,
    plot_top_skills,
)

__all__ = [
    # io
    "load_csv",
    "inspect_dataframe",
    # validate
    "check_nulls",
    "check_duplicates",
    "validate_schema",
    "assert_dtypes",
    # clean
    "drop_null_rows",
    "fill_nulls",
    "fill_nulls_grouped",
    "remove_duplicates",
    "standardise_columns",
    "parse_skill_list",
    "standardise_dates",
    # canonicalize
    "load_skill_vocabulary",
    "canonicalize_skill",
    "canonicalize_skill_list",
    # join
    "build_skill_demand_supply_table",
    "build_sector_skill_matrix",
    # stats
    "get_skill_frequency",
    "get_top_skills",
    "compute_placement_lift",
    "compute_placement_rate_by_skill",
    "wilson_confidence_interval",
    "stratified_placement_analysis",
    "select_temporal_granularity",
    "skill_trend_over_time",
    "correlation_matrix",
    "detect_outliers_iqr",
    # viz
    "plot_top_skills",
    "plot_skill_trend",
    "plot_placement_lift",
    "plot_salary_distribution",
    "plot_salary_vs_experience",
    "plot_skill_boxplot",
    "plot_correlation_heatmap",
    # logging
    "configure_logging",
]
