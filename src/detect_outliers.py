"""Assignment 4.43 — Detecting Outliers Using Visual Inspection and Simple Rules.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

This is the synthesis assignment for the visualisation tranche.
Histograms (4.39) showed shape, boxplots (4.40) embedded the
1.5*IQR rule, line plots (4.41) flagged temporal anomalies,
scatter plots (4.42) introduced residual outliers. Each said
"outlier" while meaning *something different*. This script puts
the three numeric definitions side by side on one frame:

    1. IQR rule         -- |x - Q2| > 1.5 * IQR (univariate, robust)
    2. Z-score rule     -- |z| > 3 where z = (x - mean) / std
                            (univariate, classical, sensitive to
                             tails / can self-mask in heavy tails)
    3. Residual rule    -- |residual_z| > 2 from a regression of
                            y on x (bivariate; "unusual GIVEN x")

To make the comparison concrete, the script generates a 200-row
synthetic frame with **three distinct kinds of outliers seeded
in on purpose**:

    A) High-salary univariate outliers      (~5 rows)
       Pure salary spikes. Caught by IQR and z-score.

    B) Bivariate "underpaid for experience"  (~3 rows)
       Senior engineers paid like juniors. Caught by residual
       rule only -- their salary alone looks normal.

    C) Bivariate "overpaid for experience"   (~3 rows)
       Junior engineers paid like seniors. Same: residual-only.

The script then reports:
    - Which method caught which kinds.
    - The overlap matrix between methods.
    - Five PNG figures showing each method visually.

This is the "outliers depend on the question" lesson, made
concrete by counting agreements and disagreements.

Run:
    python3 src/detect_outliers.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BANNER_WIDTH = 76
FIGURES_DIR = Path(__file__).resolve().parent.parent / "outputs" / "figures"

SYNTHETIC_BASE_ROWS = 200
SYNTHETIC_SEED = 59
SECTORS = ("Technology", "Finance", "Healthcare", "Retail", "Manufacturing")


# ---------------------------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------------------------
def generate_postings_with_seeded_outliers(
    base_rows: int = SYNTHETIC_BASE_ROWS, seed: int = SYNTHETIC_SEED
) -> pd.DataFrame:
    """Build a frame with three distinct kinds of outliers injected on purpose."""
    rng = np.random.default_rng(seed)

    # ---- baseline: salary is a real function of experience plus noise ----
    n = base_rows
    sectors = rng.choice(SECTORS, size=n)
    experience = rng.integers(low=0, high=15, size=n)
    base = 6.0 + 0.9 * experience + rng.normal(0.0, 2.0, size=n)
    base = np.clip(base, 1.0, None)
    truth = np.array(["typical"] * n, dtype=object)

    frame = pd.DataFrame(
        {
            "job_id": np.arange(10001, 10001 + n, dtype="int64"),
            "sector": sectors,
            "experience_years": experience,
            "salary_lpa": base.round(1),
            "truth": truth,
        }
    )

    # ---- A) Univariate spikes: extremely high salaries (any experience) ---
    n_a = 5
    spike_idx = rng.choice(frame.index, size=n_a, replace=False)
    frame.loc[spike_idx, "salary_lpa"] = rng.uniform(45.0, 60.0, size=n_a).round(1)
    frame.loc[spike_idx, "truth"] = "univariate_spike"

    # ---- B) Underpaid-for-experience: senior + low salary -----------------
    n_b = 3
    seniors = frame.index[frame["experience_years"] >= 10].difference(spike_idx)
    underpaid_idx = rng.choice(seniors, size=min(n_b, len(seniors)), replace=False)
    frame.loc[underpaid_idx, "salary_lpa"] = rng.uniform(
        3.0, 6.0, size=len(underpaid_idx)
    ).round(1)
    frame.loc[underpaid_idx, "truth"] = "bivariate_underpaid"

    # ---- C) Overpaid-for-experience: junior + high (but not absurd) salary
    n_c = 3
    juniors = (
        frame.index[frame["experience_years"] <= 2]
        .difference(spike_idx)
        .difference(underpaid_idx)
    )
    overpaid_idx = rng.choice(juniors, size=min(n_c, len(juniors)), replace=False)
    frame.loc[overpaid_idx, "salary_lpa"] = rng.uniform(
        28.0, 38.0, size=len(overpaid_idx)
    ).round(1)
    frame.loc[overpaid_idx, "truth"] = "bivariate_overpaid"

    return frame


# ---------------------------------------------------------------------------
# DETECTION HELPERS — three simple rules, one boolean mask each.
# ---------------------------------------------------------------------------
def iqr_outlier_mask(values: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """|x - Q2| > multiplier * IQR -- the boxplot rule, robust to heavy tails."""
    q1, q3 = values.quantile(0.25), values.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - multiplier * iqr, q3 + multiplier * iqr
    return (values < low) | (values > high)


def zscore_outlier_mask(values: pd.Series, threshold: float = 3.0) -> pd.Series:
    """|z| > threshold -- classical rule, but z itself is pulled by outliers."""
    std = values.std()
    if std == 0:
        return pd.Series(False, index=values.index)
    z = (values - values.mean()) / std
    return z.abs() > threshold


def residual_outlier_mask(
    x: pd.Series, y: pd.Series, threshold: float = 2.0
) -> pd.Series:
    """Residual-based detection: 'unusual GIVEN x'. Bivariate."""
    slope, intercept = np.polyfit(x.to_numpy(dtype=float), y.to_numpy(dtype=float), 1)
    predicted = slope * x + intercept
    residuals = y - predicted
    std = residuals.std()
    if std == 0:
        return pd.Series(False, index=x.index)
    return residuals.abs() / std > threshold


# ---------------------------------------------------------------------------
# REPORTING / OVERLAP HELPERS
# ---------------------------------------------------------------------------
def overlap_table(masks: dict[str, pd.Series]) -> pd.DataFrame:
    """Build a method-by-method count table:

    diag = rows flagged by that method;
    off-diag = rows flagged by BOTH methods on the corresponding axes.
    """
    keys = list(masks.keys())
    table = pd.DataFrame(0, index=keys, columns=keys, dtype="int64")
    for a in keys:
        for b in keys:
            table.loc[a, b] = int((masks[a] & masks[b]).sum())
    return table


def per_truth_recall(frame: pd.DataFrame, masks: dict[str, pd.Series]) -> pd.DataFrame:
    """For each (seeded-truth, method) pair, count detections / total."""
    truths = sorted(frame["truth"].unique())
    rows = []
    for truth in truths:
        truth_mask = frame["truth"] == truth
        n_total = int(truth_mask.sum())
        row = {"truth": truth, "n_total": n_total}
        for name, mask in masks.items():
            row[name] = int((mask & truth_mask).sum())
        rows.append(row)
    return pd.DataFrame(rows).set_index("truth")


# ---------------------------------------------------------------------------
# PLOT HELPERS
# ---------------------------------------------------------------------------
def ensure_figures_dir() -> Path:
    """Idempotently create the output directory."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR


def plot_iqr_boxplot(series: pd.Series, mask: pd.Series, path: Path) -> Path:
    """Boxplot annotated with the IQR-flagged outlier count."""
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.boxplot(
        series.dropna(),
        vert=True,
        patch_artist=True,
        boxprops={"facecolor": "lightsteelblue"},
    )
    ax.set_xticklabels([series.name])
    ax.set_ylabel(series.name)
    ax.set_title(f"IQR rule on {series.name} — {int(mask.sum())} flagged outlier(s)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_zscore_lollipop(series: pd.Series, mask: pd.Series, path: Path) -> Path:
    """Lollipop view of z-scores; horizontal lines at ±3 mark the rule."""
    z = (series - series.mean()) / series.std()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.vlines(z.index, 0, z, color="lightgrey", linewidth=0.9)
    ax.scatter(
        z.index[~mask], z[~mask], s=14, alpha=0.55, color="steelblue", label="typical"
    )
    ax.scatter(
        z.index[mask],
        z[mask],
        s=45,
        alpha=0.85,
        color="crimson",
        edgecolor="black",
        label=f"|z| > 3: n={int(mask.sum())}",
    )
    ax.axhline(3, color="grey", linestyle="--", linewidth=0.8)
    ax.axhline(-3, color="grey", linestyle="--", linewidth=0.8)
    ax.axhline(0, color="grey", linestyle="-", linewidth=0.5)
    ax.set_ylabel("z-score")
    ax.set_xlabel("row index")
    ax.set_title(f"z-score view on {series.name} — ±3 sigma rule")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_residual_scatter(frame: pd.DataFrame, mask: pd.Series, path: Path) -> Path:
    """Scatter with regression line; flag points with residual >2 std."""
    x = frame["experience_years"].astype(float)
    y = frame["salary_lpa"].astype(float)
    slope, intercept = np.polyfit(x.to_numpy(), y.to_numpy(), 1)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.scatter(
        x[~mask],
        y[~mask],
        s=22,
        alpha=0.55,
        color="steelblue",
        edgecolor="white",
        label="typical",
    )
    ax.scatter(
        x[mask],
        y[mask],
        s=55,
        alpha=0.85,
        color="crimson",
        edgecolor="black",
        label=f"residual outlier: n={int(mask.sum())}",
    )
    x_line = np.linspace(x.min(), x.max(), 50)
    ax.plot(
        x_line,
        slope * x_line + intercept,
        color="grey",
        linewidth=1.5,
        linestyle="--",
        label="regression line",
    )
    ax.set_xlabel("experience_years")
    ax.set_ylabel("salary_lpa")
    ax.set_title("Residual rule — outliers GIVEN experience_years")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_method_comparison(
    frame: pd.DataFrame,
    masks: dict[str, pd.Series],
    path: Path,
) -> Path:
    """Scatter colour-coded by which method(s) flagged each row.

    Rows flagged by:
      0 methods -> grey/typical
      IQR only / Z only / Residual only / multiple methods -> distinct colour
    """

    # Build a label per row indicating which method(s) fired.
    def label_row(idx: int) -> str:
        firing = [name for name, m in masks.items() if m.loc[idx]]
        if not firing:
            return "typical"
        if len(firing) == 1:
            return firing[0]
        return "multiple"

    labels = pd.Series([label_row(idx) for idx in frame.index], index=frame.index)

    palette = {
        "typical": "lightgrey",
        "iqr": "#1f77b4",
        "zscore": "#ff7f0e",
        "residual": "#2ca02c",
        "multiple": "crimson",
    }

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for label, color in palette.items():
        mask = labels == label
        if not mask.any():
            continue
        ax.scatter(
            frame.loc[mask, "experience_years"],
            frame.loc[mask, "salary_lpa"],
            s=30 if label == "typical" else 60,
            alpha=0.6 if label == "typical" else 0.9,
            color=color,
            edgecolor="white" if label == "typical" else "black",
            label=f"{label} (n={int(mask.sum())})",
        )

    ax.set_xlabel("experience_years")
    ax.set_ylabel("salary_lpa")
    ax.set_title("Outlier detection comparison — IQR vs Z-score vs Residual")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_method_overlap_heatmap(overlap: pd.DataFrame, path: Path) -> Path:
    """Render the method-by-method overlap counts as an annotated heatmap."""
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    matrix = overlap.to_numpy()
    im = ax.imshow(matrix, cmap="Blues")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(
                j,
                i,
                str(matrix[i, j]),
                ha="center",
                va="center",
                color="black",
                fontsize=11,
            )
    ax.set_xticks(range(len(overlap.columns)))
    ax.set_xticklabels(overlap.columns)
    ax.set_yticks(range(len(overlap.index)))
    ax.set_yticklabels(overlap.index)
    ax.set_title("Overlap matrix — rows flagged by both methods")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
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
    """Compute three outlier masks, render five PNGs, report agreement."""
    print_banner("Assignment 4.43 — Detecting Outliers: Visual + Simple Rules")
    ensure_figures_dir()
    frame = generate_postings_with_seeded_outliers()
    print(
        f"\n  Frame: {frame.shape}, "
        f"seeded outliers per type: {frame['truth'].value_counts().to_dict()}\n"
    )

    masks = {
        "iqr": iqr_outlier_mask(frame["salary_lpa"]),
        "zscore": zscore_outlier_mask(frame["salary_lpa"]),
        "residual": residual_outlier_mask(
            frame["experience_years"], frame["salary_lpa"]
        ),
    }

    # ----- 1) IQR boxplot -----------------------------------------------
    print_banner("1) IQR rule on salary_lpa — the univariate baseline")
    path = plot_iqr_boxplot(
        frame["salary_lpa"],
        masks["iqr"],
        FIGURES_DIR / "outliers_iqr_boxplot.png",
    )
    report_saved("IQR rule visualised", path)
    print(
        f"  IQR-flagged: {int(masks['iqr'].sum())} of {len(frame)} rows\n"
        "  Reading: catches the univariate spikes (very high salaries) but\n"
        "  cannot see the bivariate underpaid/overpaid cases -- those are\n"
        "  *normal-looking* on the salary boxplot."
    )

    # ----- 2) Z-score lollipop ------------------------------------------
    print_banner("2) Z-score rule on salary_lpa — classical")
    path = plot_zscore_lollipop(
        frame["salary_lpa"],
        masks["zscore"],
        FIGURES_DIR / "outliers_zscore_lollipop.png",
    )
    report_saved("z-score lollipop", path)
    print(
        f"  Z-flagged: {int(masks['zscore'].sum())} of {len(frame)} rows\n"
        "  Reading: similar story to IQR but z is *pulled by outliers* --\n"
        "  in a heavy-tailed column the very rows you want to flag inflate\n"
        "  the std and may push themselves below the threshold."
    )

    # ----- 3) Residual scatter ------------------------------------------
    print_banner("3) Residual rule — bivariate outliers (unusual GIVEN x)")
    path = plot_residual_scatter(
        frame, masks["residual"], FIGURES_DIR / "outliers_residual_scatter.png"
    )
    report_saved("residual rule scatter", path)
    print(
        f"  Residual-flagged: {int(masks['residual'].sum())} of {len(frame)} rows\n"
        "  Reading: this is the only method that catches the seeded\n"
        "  underpaid-for-experience and overpaid-for-experience cases."
    )

    # ----- 4) Comparison scatter ----------------------------------------
    print_banner("4) Method comparison — colour-coded scatter")
    path = plot_method_comparison(
        frame, masks, FIGURES_DIR / "outliers_method_comparison_scatter.png"
    )
    report_saved("method comparison", path)

    # ----- 5) Overlap heatmap -------------------------------------------
    print_banner("5) Overlap matrix — agreements and disagreements")
    overlap = overlap_table(masks)
    print(overlap.to_string())
    path = plot_method_overlap_heatmap(
        overlap, FIGURES_DIR / "outliers_overlap_heatmap.png"
    )
    report_saved("method overlap heatmap", path)

    # ----- Per-truth recall report -------------------------------------
    print_banner("Per-seeded-truth detection — which method caught what")
    recall = per_truth_recall(frame, masks)
    print(recall.to_string())
    print(
        "\n  Reading: 'univariate_spike' rows are caught by IQR (and usually\n"
        "  z-score). 'bivariate_underpaid' and 'bivariate_overpaid' rows are\n"
        "  caught only by the residual rule -- their salary alone looks\n"
        "  unremarkable, so univariate detectors miss them entirely."
    )

    # ----- Cheat sheet -------------------------------------------------
    print_banner("Outlier-detection cheat sheet")
    print(
        "  iqr_outlier_mask(values, 1.5)         -> boxplot rule, robust\n"
        "  zscore_outlier_mask(values, 3.0)      -> classical, sensitive\n"
        "  residual_outlier_mask(x, y, 2.0)      -> bivariate, GIVEN-x\n"
        "  WHEN TO USE WHICH\n"
        "    Skewed univariate column         -> IQR (z is pulled by tails)\n"
        "    Roughly-normal univariate column -> Z-score is fine\n"
        "    Two related variables            -> Residual rule\n"
        "    Time series                      -> Rolling mean ±2σ (4.41)\n"
        "  RULES OF THUMB\n"
        "    1. Outliers depend on the question being asked.\n"
        "    2. Detection != deletion -- investigate before removing.\n"
        "    3. Combine visual inspection with a numeric rule, never one alone."
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
