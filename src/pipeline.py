"""Job-ही-Shauk v2 — main pipeline orchestrator.

Run from the project root:
    python3 src/pipeline.py

Six stages:
    1. Ingestion       — load + validate raw CSVs
    2. Cleaning        — null handling, deduplication, standardisation
    3. Canonicalization — skill vocabulary mapping via YAML + fuzzy matching
    4. Join            — demand-supply table, sector-skill matrix
    5. Analysis        — lift, Wilson CI, stratified rates, trends, correlations
    6. Visualisation   — 7 chart exports to outputs/figures/

On success, writes a run manifest JSON to configs/.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import socket
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# --- resolve project root so this script works from any CWD ---
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from configs.schemas import JOB_POSTINGS_SCHEMA, PLACEMENT_OUTCOMES_SCHEMA  # noqa: E402
from src.utils import (  # noqa: E402
    build_sector_skill_matrix,
    build_skill_demand_supply_table,
    canonicalize_skill_list,
    compute_placement_lift,
    configure_logging,
    correlation_matrix,
    detect_outliers_iqr,
    drop_null_rows,
    fill_nulls,
    fill_nulls_grouped,
    get_skill_frequency,
    get_top_skills,
    inspect_dataframe,
    load_csv,
    load_skill_vocabulary,
    parse_skill_list,
    plot_correlation_heatmap,
    plot_placement_lift,
    plot_salary_distribution,
    plot_salary_vs_experience,
    plot_skill_boxplot,
    plot_skill_trend,
    plot_top_skills,
    remove_duplicates,
    select_temporal_granularity,
    skill_trend_over_time,
    standardise_columns,
    standardise_dates,
    stratified_placement_analysis,
    validate_schema,
)
from src.utils.canonicalize import canonicalize_skill  # noqa: E402

# --- path constants ---
DATA_RAW = ROOT / "data" / "raw"
DATA_INTERIM = ROOT / "data" / "interim"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_OUTPUT = ROOT / "data" / "output"
FIGURES = ROOT / "outputs" / "figures"
INTERACTIVE = ROOT / "outputs" / "interactive"
CONFIGS = ROOT / "configs"
LOGS = ROOT / "logs"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _get_git_sha() -> str:
    try:
        import subprocess  # noqa: PLC0415

        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"


def _ensure_dirs() -> None:
    for d in (DATA_INTERIM, DATA_PROCESSED, DATA_OUTPUT, FIGURES, INTERACTIVE, LOGS):
        d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# pipeline
# ---------------------------------------------------------------------------


def run_pipeline() -> None:
    """Execute the full 6-stage Job-ही-Shauk pipeline."""

    # ── Stage 0: Setup ────────────────────────────────────────────────────
    configure_logging(str(LOGS), level="INFO")
    logger = logging.getLogger(__name__)

    with (CONFIGS / "pipeline.yaml").open() as fh:
        config = yaml.safe_load(fh)

    seed: int = config["random_seed"]
    np.random.seed(seed)
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

    _ensure_dirs()
    stage_times: dict[str, int] = {}
    total_start = time.perf_counter()
    logger.info("=== Job-ही-Shauk v2 Pipeline Starting ===")

    # ── Stage 1: Ingestion ────────────────────────────────────────────────
    t0 = time.perf_counter()
    logger.info("Stage 1: Ingestion")

    df_jobs = load_csv(str(DATA_RAW / "sample_job_postings.csv"), parse_dates=["date_posted"])
    df_placements = load_csv(
        str(DATA_RAW / "placement_outcomes.csv"), parse_dates=["placement_date"]
    )

    validate_schema(df_jobs, list(JOB_POSTINGS_SCHEMA.keys()))
    validate_schema(df_placements, list(PLACEMENT_OUTCOMES_SCHEMA.keys()))
    inspect_dataframe(df_jobs)
    inspect_dataframe(df_placements)

    stage_times["ingestion"] = int((time.perf_counter() - t0) * 1000)

    # ── Stage 2: Cleaning ────────────────────────────────────────────────
    t0 = time.perf_counter()
    logger.info("Stage 2: Cleaning")

    df_jobs = standardise_columns(df_jobs)
    df_placements = standardise_columns(df_placements)

    df_jobs = drop_null_rows(df_jobs, threshold=config["null_thresholds"]["drop_row"])
    if "sector" in df_jobs.columns and "salary_lpa" in df_jobs.columns:
        df_jobs = fill_nulls_grouped(
            df_jobs,
            col="salary_lpa",
            group_col="sector",
            strategy="median",
            fallback="global_median",
        )
    df_jobs = remove_duplicates(df_jobs, subset=["job_id"])
    df_jobs = standardise_dates(df_jobs, "date_posted")

    df_placements = drop_null_rows(df_placements, threshold=config["null_thresholds"]["drop_row"])
    df_placements = fill_nulls(df_placements, strategy="median")
    df_placements = remove_duplicates(df_placements, subset=["candidate_id"])

    df_jobs["skills_list"] = df_jobs["skills_required"].apply(parse_skill_list)
    df_placements["skills_list"] = df_placements["skills"].apply(parse_skill_list)

    df_jobs.to_csv(DATA_INTERIM / "jobs_cleaned.csv", index=False)
    df_placements.to_csv(DATA_INTERIM / "placements_cleaned.csv", index=False)

    stage_times["cleaning"] = int((time.perf_counter() - t0) * 1000)

    # ── Stage 3: Canonicalization ────────────────────────────────────────
    t0 = time.perf_counter()
    logger.info("Stage 3: Canonicalization")

    vocab = load_skill_vocabulary(str(CONFIGS / "skills_canonical.yaml"))
    unmatched_policy: str = config.get("canonicalize", {}).get("unmatched_policy", "keep_raw")

    df_jobs["canonical_skills"] = df_jobs["skills_list"].apply(
        lambda skills: canonicalize_skill_list(skills, vocab, unmatched_policy=unmatched_policy)
    )
    df_placements["canonical_skills"] = df_placements["skills_list"].apply(
        lambda skills: canonicalize_skill_list(skills, vocab, unmatched_policy=unmatched_policy)
    )

    # Build canonicalization audit report
    all_raw: list[str] = []
    for skill_list in list(df_jobs["skills_list"]) + list(df_placements["skills_list"]):
        all_raw.extend(skill_list)

    raw_counts = Counter(all_raw)
    report_rows: list[dict] = []
    from rapidfuzz import process as rf  # noqa: PLC0415

    for raw_skill, count in raw_counts.items():
        canonical = canonicalize_skill(raw_skill, vocab)
        if canonical is not None:
            if raw_skill.lower() in vocab:
                tier, score = "exact", None
            else:
                m = rf.extractOne(raw_skill.lower(), vocab.keys(), score_cutoff=0)
                tier = "fuzzy"
                score = m[1] if m else None
        else:
            tier, score, canonical = "unmatched", None, None
        report_rows.append(
            {
                "raw_skill": raw_skill,
                "canonical_skill": canonical,
                "match_tier": tier,
                "match_score": score,
                "occurrence_count": count,
            }
        )

    canon_report = pd.DataFrame(report_rows)
    canon_report.to_csv(DATA_INTERIM / "canonicalization_report.csv", index=False)

    unmatched_ratio = (canon_report["match_tier"] == "unmatched").mean()
    warn_threshold: float = config.get("canonicalize", {}).get("unmatched_warn_threshold", 0.20)
    if unmatched_ratio > warn_threshold:
        logger.warning(
            "%.0f%% of raw skills are unmatched — review data/interim/canonicalization_report.csv",
            unmatched_ratio * 100,
        )

    df_jobs.to_csv(DATA_INTERIM / "jobs_canonicalized.csv", index=False)
    df_placements.to_csv(DATA_INTERIM / "placements_canonicalized.csv", index=False)

    stage_times["canonicalization"] = int((time.perf_counter() - t0) * 1000)

    # ── Stage 4: Join ────────────────────────────────────────────────────
    t0 = time.perf_counter()
    logger.info("Stage 4: Join")

    skill_demand_supply = build_skill_demand_supply_table(df_jobs, df_placements)
    sector_skill_matrix = build_sector_skill_matrix(df_jobs, df_placements)

    skill_demand_supply.to_csv(DATA_PROCESSED / "skill_demand_supply.csv", index=False)
    sector_skill_matrix.to_csv(DATA_PROCESSED / "sector_skill_matrix.csv")

    stage_times["join"] = int((time.perf_counter() - t0) * 1000)

    # ── Stage 5: Analysis ────────────────────────────────────────────────
    t0 = time.perf_counter()
    logger.info("Stage 5: Analysis")

    freq_series = get_skill_frequency(df_jobs, "canonical_skills")
    top_skills = get_top_skills(freq_series, n=20)

    min_support: int = config["min_support"]
    placement_lift = compute_placement_lift(skill_demand_supply, min_support=min_support)

    strat_rates = stratified_placement_analysis(df_placements, strat_col="years_of_experience")

    trend_df: pd.DataFrame | None = None
    try:
        granularity = select_temporal_granularity(df_jobs["date_posted"])
        trend_df = skill_trend_over_time(df_jobs, "date_posted", resample_rule=granularity)
        trend_df.to_csv(DATA_OUTPUT / "skill_trends.csv")
        logger.info("Trend analysis: granularity='%s', %d periods", granularity, len(trend_df))
    except ValueError as exc:
        logger.warning("Trend analysis skipped: %s", exc)

    numeric_cols = [
        c
        for c in ["years_of_experience", "offered_salary_lpa", "placed"]
        if c in df_placements.columns
    ]
    corr_df = correlation_matrix(df_placements, numeric_cols)

    salary_col = "salary_lpa"
    if salary_col in df_jobs.columns:
        outlier_mask = detect_outliers_iqr(df_jobs[salary_col].dropna())
        logger.info(
            "Salary outliers (IQR): %d / %d (%.1f%%)",
            int(outlier_mask.sum()),
            len(outlier_mask),
            outlier_mask.mean() * 100,
        )

    placement_lift.to_csv(DATA_OUTPUT / "placement_lift.csv", index=False)
    strat_rates.to_csv(DATA_OUTPUT / "stratified_rates.csv", index=False)

    stage_times["analysis"] = int((time.perf_counter() - t0) * 1000)

    # ── Stage 6: Visualisation ───────────────────────────────────────────
    t0 = time.perf_counter()
    logger.info("Stage 6: Visualisation")

    if not top_skills.empty:
        plot_top_skills(top_skills, str(FIGURES / "top_skills.png"))

    if trend_df is not None and not trend_df.empty:
        plot_skill_trend(trend_df, str(FIGURES / "skill_trend.png"))

    if not placement_lift.empty:
        plot_placement_lift(placement_lift, str(FIGURES / "placement_lift.png"))

    if salary_col in df_jobs.columns:
        plot_salary_distribution(df_jobs, salary_col, str(FIGURES / "salary_dist.png"))

    exp_col = "experience_min_yrs"
    if salary_col in df_jobs.columns and exp_col in df_jobs.columns:
        plot_salary_vs_experience(
            df_jobs, salary_col, exp_col, str(FIGURES / "salary_exp_scatter.png")
        )

    if "sector" in df_jobs.columns and "canonical_skills" in df_jobs.columns:
        df_jobs["skill_count"] = df_jobs["canonical_skills"].apply(len)
        plot_skill_boxplot(df_jobs, "sector", "skill_count", str(FIGURES / "skill_boxplot.png"))

    if len(corr_df) >= 2:
        plot_correlation_heatmap(corr_df, str(FIGURES / "corr_heatmap.png"))

    # Emit insights summary
    _write_insights(top_skills, placement_lift, strat_rates, df_jobs, df_placements)

    stage_times["visualisation"] = int((time.perf_counter() - t0) * 1000)

    # ── Run manifest ─────────────────────────────────────────────────────
    total_ms = int((time.perf_counter() - total_start) * 1000)
    manifest = {
        "git_sha": _get_git_sha(),
        "input_hashes": {
            "sample_job_postings.csv": _sha256_file(DATA_RAW / "sample_job_postings.csv"),
            "placement_outcomes.csv": _sha256_file(DATA_RAW / "placement_outcomes.csv"),
        },
        "stage_durations_ms": stage_times,
        "total_duration_ms": total_ms,
        "python_version": sys.version,
        "hostname": socket.gethostname(),
        "timestamp": datetime.now().isoformat(),
    }
    manifest_path = CONFIGS / f"run_manifest_{datetime.now():%Y-%m-%d_%H%M%S}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    logger.info("=== Pipeline complete in %d ms. Manifest: %s ===", total_ms, manifest_path.name)


def _write_insights(
    top_skills: pd.Series,
    placement_lift: pd.DataFrame,
    strat_rates: pd.DataFrame,
    df_jobs: pd.DataFrame,
    df_placements: pd.DataFrame,
) -> None:
    """Write a brief narrative insight summary to outputs/insights.md."""
    insights_path = ROOT / "outputs" / "insights.md"
    base_rate = float(df_placements["placed"].mean()) if "placed" in df_placements.columns else 0.0

    top3 = top_skills.head(3).index.tolist() if not top_skills.empty else []
    top3_lift = (
        placement_lift.head(3)[["skill", "lift"]].to_dict("records")
        if not placement_lift.empty
        else []
    )

    lines = [
        "# Job-ही-Shauk — Auto-generated Insights",
        "",
        f"*Generated: {datetime.now():%Y-%m-%d %H:%M}*",
        "",
        "## Key Findings",
        "",
        f"- **Overall placement rate**: {base_rate:.1%}",
        f"- **Total job postings analysed**: {len(df_jobs)}",
        f"- **Total candidates analysed**: {len(df_placements)}",
        "",
        "### Top 3 Most In-Demand Skills",
        "",
    ]
    for i, skill in enumerate(top3, 1):
        lines.append(f"{i}. `{skill}` — {int(top_skills[skill])} postings")
    lines += [
        "",
        "### Top 3 Skills by Placement Lift",
        "",
    ]
    for row in top3_lift:
        lines.append(f"- `{row['skill']}` — lift **{row['lift']:.2f}x** above baseline")
    lines += [
        "",
        "---",
        "*This file is auto-generated by `src/pipeline.py`. Do not edit manually.*",
    ]
    insights_path.write_text("\n".join(lines))


if __name__ == "__main__":
    run_pipeline()
