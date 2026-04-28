"""Assignment 4.41 — Identifying Trends Over Time Using Line Plots.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

A line plot is the canonical chart for *ordered* data: x is time,
y is the metric, and the line connects consecutive points. The
shape of that line is the trend, and unusual peaks or dips are the
anomalies that summary statistics by themselves would never have
told you about.

This script generates a 180-day synthetic stream of job postings
**with a deliberately seasonal trend and an injected anomaly week**
so the line plot has something real to surface, then walks four
patterns:

    1. postings_daily_line.png
       Raw daily count + a 7-day rolling mean overlay -- the
       canonical noise-vs-trend separation.

    2. postings_weekly_line.png
       Weekly aggregation (resample('W')). Smoother story; same
       data, different time granularity.

    3. postings_per_sector_line.png
       Multi-line per sector -- compare temporal patterns across
       groups on one axis.

    4. postings_anomaly_line.png
       Daily count with rolling-mean band; days more than 2 stds
       away from the rolling baseline are highlighted in red.

Files are written to `outputs/figures/` (gitignored).

Run:
    python3 src/visualize_line_plots.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BANNER_WIDTH = 72
FIGURES_DIR = Path(__file__).resolve().parent.parent / "outputs" / "figures"

DAYS_OF_HISTORY = 180
SYNTHETIC_SEED = 47
SECTORS = ("Technology", "Finance", "Healthcare", "Retail", "Manufacturing")
ROLES = (
    "Data Scientist",
    "ML Engineer",
    "Data Analyst",
    "Backend Engineer",
    "Frontend Engineer",
    "Data Engineer",
)


# ---------------------------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------------------------
def generate_postings_stream(
    days: int = DAYS_OF_HISTORY, seed: int = SYNTHETIC_SEED
) -> pd.DataFrame:
    """Generate a stream of postings across `days` days, with built-in trend.

    Daily volume is a slow upward ramp (8 -> ~16 postings/day) plus
    weekday seasonality (lower on weekends), plus a 7-day anomaly
    window in the middle where volume drops to ~3/day -- so the line
    plot has a clear trend, a clear cycle, and a clear anomaly all
    at once. The mid-week dip lets the rolling-mean overlay show the
    smoothing/de-noising trick clearly.
    """
    rng = np.random.default_rng(seed)
    base_date = pd.Timestamp("2024-01-01")
    dates_list: list[pd.Timestamp] = []
    sector_list: list[str] = []
    salary_list: list[float] = []
    title_list: list[str] = []

    anomaly_window = (60, 67)  # day indices
    for day in range(days):
        # baseline volume slowly ramps up
        baseline = 8 + 8.0 * (day / days)
        # weekend dip
        date = base_date + pd.Timedelta(days=day)
        if date.dayofweek >= 5:
            baseline *= 0.55
        # injected anomaly week
        if anomaly_window[0] <= day < anomaly_window[1]:
            baseline *= 0.25

        n_today = max(0, int(rng.poisson(lam=baseline)))
        for _ in range(n_today):
            sector = rng.choice(SECTORS)
            sector_list.append(sector)
            dates_list.append(date)
            title_list.append(rng.choice(ROLES))
            # mild upward trend in salary too, sector-flavoured
            mu = 2.4 + 0.10 * (day / days)
            sigma = 0.5
            salary_list.append(round(rng.lognormal(mu, sigma), 1))

    return pd.DataFrame(
        {
            "date_posted": pd.to_datetime(dates_list),
            "sector": sector_list,
            "job_title": title_list,
            "salary_lpa": salary_list,
        }
    )


def daily_counts(frame: pd.DataFrame) -> pd.Series:
    """Postings per calendar day, sorted by date."""
    return (
        frame.groupby(frame["date_posted"].dt.date)
        .size()
        .rename("postings")
        .sort_index()
    )


def weekly_counts(frame: pd.DataFrame) -> pd.Series:
    """Postings per ISO calendar week (Mon-anchored)."""
    return frame.set_index("date_posted").resample("W-MON").size().rename("postings")


def per_sector_daily(frame: pd.DataFrame) -> pd.DataFrame:
    """Daily postings split by sector. Wide-format, dates as index."""
    return (
        frame.groupby([frame["date_posted"].dt.date, "sector"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )


# ---------------------------------------------------------------------------
# PLOT HELPERS
# ---------------------------------------------------------------------------
def ensure_figures_dir() -> Path:
    """Idempotently create the output directory."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR


def plot_daily_with_rolling(daily: pd.Series, path: Path) -> Path:
    """Raw daily count + 7-day rolling mean -- noise vs trend."""
    rolling = daily.rolling(window=7, min_periods=1).mean()
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(
        daily.index,
        daily.values,
        color="steelblue",
        linewidth=1.0,
        label="Daily count (raw)",
    )
    ax.plot(
        rolling.index,
        rolling.values,
        color="crimson",
        linewidth=2.0,
        label="7-day rolling mean",
    )
    ax.set_title("Daily postings — raw vs 7-day rolling mean")
    ax.set_ylabel("Postings")
    ax.set_xlabel("Date")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_weekly(weekly: pd.Series, path: Path) -> Path:
    """Weekly aggregate -- the smoother story."""
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(
        weekly.index,
        weekly.values,
        color="darkgreen",
        linewidth=2.0,
        marker="o",
        markersize=5,
    )
    ax.set_title("Weekly postings (resample('W-MON'))")
    ax.set_ylabel("Postings per week")
    ax.set_xlabel("Week (Mon-anchored)")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_per_sector(per_sector: pd.DataFrame, path: Path) -> Path:
    """One line per sector -- compare temporal patterns across groups."""
    fig, ax = plt.subplots(figsize=(10, 5))
    palette = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd")
    for color, sector in zip(palette, per_sector.columns):
        # Lightly smooth so the per-sector line is readable.
        smooth = per_sector[sector].rolling(window=7, min_periods=1).mean()
        ax.plot(smooth.index, smooth.values, label=sector, color=color, linewidth=1.6)
    ax.set_title("Daily postings per sector — 7-day rolling mean")
    ax.set_ylabel("Postings (rolling)")
    ax.set_xlabel("Date")
    ax.legend(title="sector", loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_anomalies(daily: pd.Series, path: Path) -> Path:
    """Daily count with rolling band; flag days >2 stds from the local mean."""
    rolling_mean = daily.rolling(window=14, min_periods=3, center=True).mean()
    rolling_std = daily.rolling(window=14, min_periods=3, center=True).std()
    deviation = (daily - rolling_mean).abs() / rolling_std.replace(0, np.nan)
    anomalies = daily[deviation > 2]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(
        daily.index, daily.values, color="steelblue", linewidth=1.0, label="Daily count"
    )
    ax.plot(
        rolling_mean.index,
        rolling_mean.values,
        color="grey",
        linewidth=1.5,
        linestyle="--",
        label="14-day centred mean",
    )
    ax.fill_between(
        rolling_mean.index,
        rolling_mean - 2 * rolling_std,
        rolling_mean + 2 * rolling_std,
        color="grey",
        alpha=0.15,
        label="±2 std band",
    )
    ax.scatter(
        anomalies.index,
        anomalies.values,
        color="crimson",
        s=40,
        zorder=5,
        label=f"Anomaly (>2 std): {len(anomalies)} day(s)",
    )
    ax.set_title("Daily postings — anomaly flag (>2 std from local mean)")
    ax.set_ylabel("Postings")
    ax.set_xlabel("Date")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def print_banner(title: str) -> None:
    """Print a fixed-width banner."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def report_saved(label: str, path: Path) -> None:
    """One-line confirmation that a figure was written to disk."""
    print(f"  saved -> {path.relative_to(FIGURES_DIR.parent.parent)}   ({label})")


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Generate the four time-series artefacts described in the docstring."""
    print_banner("Assignment 4.41 — Identifying Trends Over Time with Line Plots")
    ensure_figures_dir()

    frame = generate_postings_stream()
    daily = daily_counts(frame)
    weekly = weekly_counts(frame)
    per_sector = per_sector_daily(frame)

    print(
        f"\n  Working frame: {frame.shape[0]} rows across "
        f"{daily.index.min()} -> {daily.index.max()}.\n"
        f"  Daily series: {len(daily)} days. "
        f"Weekly series: {len(weekly)} weeks. "
        f"Sectors: {list(per_sector.columns)}.\n"
    )

    # 1) Daily + 7-day rolling
    print_banner("1) Daily count + 7-day rolling mean — noise vs trend")
    path = plot_daily_with_rolling(daily, FIGURES_DIR / "postings_daily_line.png")
    report_saved("daily + rolling", path)
    print(
        f"  Daily mean: {daily.mean():.1f} postings/day, "
        f"std: {daily.std():.1f}. The raw line is jittery from\n"
        "  weekend dips and Poisson noise; the 7-day rolling mean exposes\n"
        "  the slow upward trend across the 6-month window."
    )

    # 2) Weekly aggregate
    print_banner("2) Weekly aggregate — same data, smoother story")
    path = plot_weekly(weekly, FIGURES_DIR / "postings_weekly_line.png")
    report_saved("weekly resample", path)
    print(
        f"  Weekly mean: {weekly.mean():.0f} postings/week, "
        f"min: {weekly.min()}, max: {weekly.max()}.\n"
        "  Reading: weekly aggregation absorbs weekend cycle entirely;\n"
        "  the trend is the dominant signal at this granularity."
    )

    # 3) Per-sector multi-line
    print_banner("3) Per-sector lines — compare temporal patterns")
    path = plot_per_sector(per_sector, FIGURES_DIR / "postings_per_sector_line.png")
    report_saved("per-sector multi-line", path)
    sector_totals = per_sector.sum().sort_values(ascending=False)
    print("  Total postings per sector (over the window):")
    for sector, total in sector_totals.items():
        print(f"    {sector:<14} {total}")

    # 4) Anomaly highlight
    print_banner("4) Anomaly detection — >2 std from local rolling mean")
    path = plot_anomalies(daily, FIGURES_DIR / "postings_anomaly_line.png")
    report_saved("anomaly highlight", path)
    rolling_mean = daily.rolling(window=14, min_periods=3, center=True).mean()
    rolling_std = daily.rolling(window=14, min_periods=3, center=True).std()
    deviation = (daily - rolling_mean).abs() / rolling_std.replace(0, np.nan)
    anomalies = daily[deviation > 2]
    print(f"  Anomaly days flagged: {len(anomalies)}")
    if len(anomalies):
        print("  First few:")
        for d, v in anomalies.head(5).items():
            print(f"    {d} -> {v} postings")
        print(
            "  Reading: the script seeds an anomaly window around days 60-67 where\n"
            "  posting volume drops to ~25% of baseline; the 2-std flag should\n"
            "  light up around that window."
        )

    # Cheat sheet
    print_banner("Line-plot cheat sheet")
    print(
        "  ax.plot(x, y)                                -> basic line\n"
        "  series.rolling(window=7).mean()              -> noise reduction\n"
        "  series.resample('W-MON').sum()               -> change time granularity\n"
        "  ax.fill_between(x, low, high, alpha=0.2)     -> tolerance band\n"
        "  mdates.MonthLocator() + DateFormatter        -> readable date axis\n"
        "  fig.autofmt_xdate()                          -> rotate date ticks\n"
        "  ALWAYS sort by time before plotting; line plots assume ordered x.\n"
        "  Choose granularity (day/week/month) to match the question;\n"
        "  too fine -> noisy; too coarse -> hides the events you care about."
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
