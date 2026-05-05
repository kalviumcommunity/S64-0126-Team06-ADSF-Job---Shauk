"""Visualisation helpers: chart generation and file export.

Rules:
- No plt.show() — callers (notebooks) invoke that after importing results.
- No print() / logging to stdout.
- Every function saves the figure before closing and asserts the file exists.
- Returns the output path so callers can chain assertions.
"""

from __future__ import annotations

import logging
import os

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")  # non-interactive backend; safe for script execution

logger = logging.getLogger(__name__)

# Okabe-Ito: 8-colour palette that is safe for the three most common types of colour blindness
OKABE_ITO = [
    "#E69F00",
    "#56B4E9",
    "#009E73",
    "#F0E442",
    "#0072B2",
    "#D55E00",
    "#CC79A7",
    "#000000",
]


def _save_and_close(output_path: str, dpi: int = 150) -> str:
    """tight_layout → savefig → assert exists → close. Returns output_path."""
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    assert os.path.exists(output_path), f"Chart export failed: {output_path}"
    plt.close()
    logger.info("Saved chart → %s", output_path)
    return output_path


def plot_top_skills(
    freq_series: pd.Series,
    output_path: str,
    palette: str = "Okabe-Ito",
    title: str = "Top Skills by Frequency",
) -> str:
    """Horizontal bar chart of skill frequencies."""
    n = len(freq_series)
    colors = (
        OKABE_ITO * (n // len(OKABE_ITO) + 1)
        if palette == "Okabe-Ito"
        else list(sns.color_palette(palette, n))
    )
    _, ax = plt.subplots(figsize=(10, max(5, n * 0.35)))
    bars = ax.barh(freq_series.index[::-1], freq_series.values[::-1], color=colors[:n])
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_xlabel("Count")
    ax.set_title(title)
    return _save_and_close(output_path)


def plot_skill_trend(
    trend_df: pd.DataFrame,
    output_path: str,
    top_n: int = 10,
    palette: str = "tab10",
    title: str = "Skill Trend Over Time",
) -> str:
    """Line plot of top-*n* skill counts over time periods."""
    top_skills = trend_df.sum().nlargest(top_n).index
    colors = list(sns.color_palette(palette, len(top_skills)))
    _, ax = plt.subplots(figsize=(12, 6))
    for i, skill in enumerate(top_skills):
        ax.plot(trend_df.index.astype(str), trend_df[skill], label=skill, color=colors[i])
    ax.set_xlabel("Period")
    ax.set_ylabel("Count")
    ax.set_title(title)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
    plt.xticks(rotation=45, ha="right")
    return _save_and_close(output_path)


def plot_placement_lift(
    lift_df: pd.DataFrame,
    output_path: str,
    top_n: int = 20,
    palette: str = "RdBu_r",
    title: str = "Placement Lift by Skill",
) -> str:
    """Diverging bar chart of placement lift per skill (baseline = 1.0)."""
    data = lift_df.head(top_n).copy()
    cmap = plt.get_cmap(palette)
    colors = [cmap(0.85) if v >= 1.0 else cmap(0.15) for v in data["lift"]]
    _, ax = plt.subplots(figsize=(10, max(5, len(data) * 0.4)))
    ax.barh(data["skill"][::-1], data["lift"][::-1], color=colors[::-1])
    ax.axvline(1.0, color="gray", linestyle="--", linewidth=1, label="Baseline (lift=1)")
    ax.set_xlabel("Lift  (skill_placement_rate / base_rate)")
    ax.set_title(title)
    ax.legend()
    return _save_and_close(output_path)


def plot_salary_distribution(
    df: pd.DataFrame,
    salary_col: str,
    output_path: str,
    palette: str = "viridis",
    title: str = "Salary Distribution",
) -> str:
    """Histogram with mean and median reference lines."""
    valid = df[salary_col].dropna()
    _, ax = plt.subplots(figsize=(9, 5))
    ax.hist(valid, bins=30, color=plt.get_cmap(palette)(0.6), edgecolor="white")
    ax.axvline(float(valid.mean()), color="red", linestyle="--", label=f"Mean {valid.mean():.1f}")
    ax.axvline(
        float(valid.median()), color="blue", linestyle="--", label=f"Median {valid.median():.1f}"
    )
    ax.set_xlabel(salary_col)
    ax.set_ylabel("Frequency")
    ax.set_title(title)
    ax.legend()
    return _save_and_close(output_path)


def plot_salary_vs_experience(
    df: pd.DataFrame,
    salary_col: str,
    exp_col: str,
    output_path: str,
    palette: str = "plasma",
    title: str = "Salary vs Experience",
) -> str:
    """Scatter plot of salary against years of experience, coloured by salary."""
    valid = df[[salary_col, exp_col]].dropna()
    _, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(
        valid[exp_col],
        valid[salary_col],
        c=valid[salary_col],
        cmap=palette,
        alpha=0.6,
        edgecolors="none",
    )
    plt.colorbar(sc, ax=ax, label=salary_col)
    ax.set_xlabel(exp_col)
    ax.set_ylabel(salary_col)
    ax.set_title(title)
    return _save_and_close(output_path)


def plot_skill_boxplot(
    df: pd.DataFrame,
    sector_col: str,
    count_col: str,
    output_path: str,
    palette: str = "Set2",
    title: str = "Skill Count by Sector",
) -> str:
    """Boxplot of skill count distributions per sector."""
    sectors = sorted(df[sector_col].dropna().unique())
    data_by_sector = [df[df[sector_col] == s][count_col].dropna().values for s in sectors]
    colors = list(sns.color_palette(palette, len(sectors)))
    _, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(data_by_sector, labels=sectors, patch_artist=True)
    for patch, color in zip(bp["boxes"], colors, strict=False):
        patch.set_facecolor(color)
    ax.set_xlabel("Sector")
    ax.set_ylabel(count_col)
    ax.set_title(title)
    plt.xticks(rotation=30, ha="right")
    return _save_and_close(output_path)


def plot_correlation_heatmap(
    corr_df: pd.DataFrame,
    output_path: str,
    palette: str = "coolwarm",
    title: str = "Correlation Heatmap",
) -> str:
    """Seaborn annotated heatmap of a correlation matrix."""
    _, ax = plt.subplots(figsize=(max(6, len(corr_df)), max(5, len(corr_df))))
    sns.heatmap(
        corr_df,
        annot=True,
        fmt=".2f",
        cmap=palette,
        center=0,
        vmin=-1,
        vmax=1,
        ax=ax,
        linewidths=0.5,
    )
    ax.set_title(title)
    return _save_and_close(output_path)
