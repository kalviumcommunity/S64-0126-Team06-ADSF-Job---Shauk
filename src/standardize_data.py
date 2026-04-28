"""Assignment 4.36 — Standardizing Column Names and Data Formats.

Author: Bhargav Kalambhe (Frontend & ML, covering Analyst)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

The single biggest source of avoidable bugs in a Pandas pipeline is
inconsistent labels and inconsistent casing. A column named
``"Job Title"`` and a column named ``"job_title"`` look identical
to a human and are completely different to the framework. A sector
encoded as ``"Technology"`` in some rows, ``"TECHNOLOGY"`` in others,
and ``"  technology "`` in a few will produce three "different"
groups when you call ``groupby("sector")`` -- and a wrong analysis.

Standardisation is the cleaning step that erases these *cosmetic*
differences so that downstream code can treat semantically-equal
values as equal. This script demonstrates the full standardisation
recipe on a deliberately dirty 60-row frame:

    Column-name issues:
      "Job ID", "Job  Title" (double space), "Sector!", "Salary (LPA)",
      " EXPERIENCE_YEARS ", "Date Posted"

    Value issues:
      sector       -> "Technology", "TECHNOLOGY", "  tech ", "Tech."
      job_title    -> trailing/leading whitespace, mixed case
      salary_lpa   -> currency-prefixed strings ("$12.5") and bare floats
      date_posted  -> mixed YYYY-MM-DD and DD/MM/YYYY

The script then walks:

    1. standardize_columns()   -> snake_case, no special chars
    2. standardize_text()      -> strip + lowercase + canonical mapping
    3. standardize_numerics()  -> strip currency, coerce to float
    4. standardize_dates()     -> mixed formats -> datetime64[ns]
    5. apply_full_recipe()     -> one call; before/after metrics

Run:
    python3 src/standardize_data.py
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


BANNER_WIDTH = 72
SAMPLE_CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_job_postings.csv"
)

SYNTHETIC_ROW_COUNT = 60
SYNTHETIC_SEED = 23

# Canonical sector names. The standardiser collapses any case/spelling
# variant onto one of these via the SECTOR_ALIASES table below.
CANONICAL_SECTORS = ("technology", "finance", "healthcare", "retail", "manufacturing")
SECTOR_ALIASES = {
    "tech": "technology",
    "tech.": "technology",
    "it": "technology",
    "fin": "finance",
    "health": "healthcare",
    "mfg": "manufacturing",
}

# Surface-form variants intentionally seeded into the dirty frame.
DIRTY_SECTORS = (
    "Technology",
    "TECHNOLOGY",
    "  technology ",
    "Tech",
    "tech.",
    "Finance",
    "FINANCE",
    "  fin ",
    "Healthcare",
    "HEALTHCARE",
    "health",
    "Retail",
    "  retail ",
    "Manufacturing",
    "mfg",
    "MFG",
)

DIRTY_TITLES = (
    "Data Scientist",
    "  data scientist  ",
    "DATA SCIENTIST",
    "ML Engineer",
    "ml engineer",
    "Data Analyst",
    "  Data  Analyst  ",  # double internal space
    "Backend Engineer",
    "frontend engineer",
)


# ---------------------------------------------------------------------------
# DATA HELPERS — generate a frame whose dirtiness exercises every step.
# ---------------------------------------------------------------------------
def generate_dirty_frame(
    n_rows: int = SYNTHETIC_ROW_COUNT, seed: int = SYNTHETIC_SEED
) -> pd.DataFrame:
    """Build a 60-row frame with dirty column names + dirty values."""
    rng = np.random.default_rng(seed)
    base_date = pd.Timestamp("2024-01-01")

    # Mix YYYY-MM-DD and DD/MM/YYYY so the date standardiser has both
    # formats to handle.
    days = rng.integers(0, 180, size=n_rows)
    iso_dates = [str((base_date + pd.Timedelta(days=int(d))).date()) for d in days]
    eu_dates = [
        (base_date + pd.Timedelta(days=int(d))).strftime("%d/%m/%Y") for d in days
    ]
    date_strings = [iso_dates[i] if i % 2 == 0 else eu_dates[i] for i in range(n_rows)]

    # Salaries: half are bare floats, half are currency strings.
    raw_salaries = rng.lognormal(mean=2.4, sigma=0.5, size=n_rows).round(1)
    salary_strings = [
        f"${value}" if i % 3 == 0 else str(value)
        for i, value in enumerate(raw_salaries)
    ]

    return pd.DataFrame(
        {
            "Job ID": np.arange(4001, 4001 + n_rows, dtype="int64"),
            "Job  Title": rng.choice(DIRTY_TITLES, size=n_rows),  # double space
            "Sector!": rng.choice(DIRTY_SECTORS, size=n_rows),  # special char
            " EXPERIENCE_YEARS ": rng.integers(low=0, high=12, size=n_rows),
            "Salary (LPA)": salary_strings,
            "Date Posted": date_strings,
        }
    )


# ---------------------------------------------------------------------------
# COLUMN-NAME STANDARDISATION
# ---------------------------------------------------------------------------
_NON_ALPHANUMERIC = re.compile(r"[^0-9a-z]+")


def standardize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Lowercase, strip, collapse runs of non-alphanumerics into single `_`.

    Examples:
        "Job ID"             -> "job_id"
        "Job  Title"         -> "job_title"
        "Sector!"            -> "sector"
        "Salary (LPA)"       -> "salary_lpa"
        " EXPERIENCE_YEARS " -> "experience_years"
    """

    def normalise(name: str) -> str:
        lowered = name.strip().lower()
        squashed = _NON_ALPHANUMERIC.sub("_", lowered).strip("_")
        return squashed

    return frame.rename(columns={c: normalise(c) for c in frame.columns})


# ---------------------------------------------------------------------------
# VALUE STANDARDISATION — text, numeric, date
# ---------------------------------------------------------------------------
def standardize_text(
    series: pd.Series,
    aliases: dict[str, str] | None = None,
) -> pd.Series:
    """Strip whitespace, collapse repeated spaces, lowercase, then map aliases.

    The alias map is what closes the long tail of variants:
    `"tech"` and `"tech."` both fold onto the canonical `"technology"`.
    """
    cleaned = (
        series.astype("string")
        .str.strip()
        .str.replace(r"[.\s]+", " ", regex=True)  # repeated spaces / trailing dots
        .str.strip()
        .str.lower()
    )
    if aliases:
        cleaned = cleaned.replace(aliases)
    return cleaned


def standardize_numeric(series: pd.Series) -> pd.Series:
    """Strip currency / whitespace, coerce to float, NaN on failure."""
    cleaned = (
        series.astype("string")
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def standardize_dates(series: pd.Series) -> pd.Series:
    """Parse mixed-format date strings into datetime64[ns].

    Tries YYYY-MM-DD first; falls back to DD/MM/YYYY for rows that
    didn't match. Anything still unparseable becomes NaT.
    """
    iso = pd.to_datetime(series, format="%Y-%m-%d", errors="coerce")
    eu = pd.to_datetime(series, format="%d/%m/%Y", errors="coerce")
    return iso.fillna(eu)


# ---------------------------------------------------------------------------
# FULL RECIPE
# ---------------------------------------------------------------------------
def apply_full_recipe(frame: pd.DataFrame) -> pd.DataFrame:
    """Column-name + value standardisation in one call. Returns a fresh frame."""
    standardised = standardize_columns(frame).copy()
    standardised["job_title"] = standardize_text(standardised["job_title"])
    standardised["sector"] = standardize_text(
        standardised["sector"], aliases=SECTOR_ALIASES
    )
    standardised["salary_lpa"] = standardize_numeric(standardised["salary_lpa"])
    standardised["date_posted"] = standardize_dates(standardised["date_posted"])
    return standardised


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def print_banner(title: str) -> None:
    """Print a fixed-width banner."""
    print("=" * BANNER_WIDTH)
    print(title)
    print("=" * BANNER_WIDTH)


def print_section(label: str, body: object) -> None:
    """Print a labelled section with the body underneath."""
    print(f"\n{label}")
    print(body)


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def main() -> None:
    """Walk the standardisation recipe step by step on a dirty source frame."""
    print_banner("Assignment 4.36 — Standardising Column Names and Data Formats")
    dirty = generate_dirty_frame()
    print(f"\n  Source frame: {dirty.shape[0]} rows x {dirty.shape[1]} columns.\n")

    # ----- 1) Column-name standardisation -------------------------------
    print_banner("1) Column names — snake_case, no special chars, no spaces")
    print_section("Before:", list(dirty.columns))
    renamed = standardize_columns(dirty)
    print_section("After:", list(renamed.columns))
    print(
        "\n  Rule applied: strip(), lower(), collapse non-[a-z0-9] runs to '_',\n"
        "  trim leading/trailing '_'. Reversible? No -- aliases like 'IT' for\n"
        "  'Information Technology' need a separate map; the column-name\n"
        "  standardiser is purely lexical."
    )

    # ----- 2) Text-value standardisation --------------------------------
    print_banner("2) Categorical text — strip + lowercase + alias map")
    sector_before = renamed["sector"].value_counts(dropna=False).head(10)
    sector_after = standardize_text(
        renamed["sector"], aliases=SECTOR_ALIASES
    ).value_counts()

    side_by_side = (
        pd.concat(
            [
                sector_before.rename("count_before"),
                sector_after.rename("count_after"),
            ],
            axis=1,
        )
        .fillna(0)
        .astype("Int64")
    )
    print_section(
        "sector value counts (before vs after standardisation):",
        side_by_side.to_string(),
    )
    print(
        f"\n  Distinct values: {sector_before.size} -> {sector_after.size}\n"
        "  Reading: case/whitespace/abbreviation variants collapse onto\n"
        f"  the {len(CANONICAL_SECTORS)} canonical sector labels. Without this,\n"
        "  groupby('sector') would create a separate group for every\n"
        "  surface form -- inflating the apparent number of sectors."
    )

    job_title_before = renamed["job_title"].value_counts(dropna=False).head(10)
    job_title_after = standardize_text(renamed["job_title"]).value_counts().head(10)
    print_section("job_title before:", job_title_before.to_string())
    print_section("job_title after:", job_title_after.to_string())

    # ----- 3) Numeric-value standardisation -----------------------------
    print_banner("3) Numeric — strip currency, coerce to float")
    salary_before_dtype = renamed["salary_lpa"].dtype
    salary_clean = standardize_numeric(renamed["salary_lpa"])
    salary_after_dtype = salary_clean.dtype
    print(
        f"  salary dtype before -> {salary_before_dtype}\n"
        f"  salary dtype after  -> {salary_after_dtype}\n"
        f"  example before -> {renamed['salary_lpa'].head(5).tolist()}\n"
        f"  example after  -> {salary_clean.head(5).tolist()}\n"
        f"  arithmetic now works: salary_clean.sum() = {salary_clean.sum():.2f}"
    )

    # ----- 4) Date-value standardisation --------------------------------
    print_banner("4) Date — mixed YYYY-MM-DD and DD/MM/YYYY -> datetime64[ns]")
    date_before_dtype = renamed["date_posted"].dtype
    date_clean = standardize_dates(renamed["date_posted"])
    date_after_dtype = date_clean.dtype
    print(
        f"  date dtype before -> {date_before_dtype}\n"
        f"  date dtype after  -> {date_after_dtype}\n"
        f"  examples before   -> {renamed['date_posted'].head(4).tolist()}\n"
        f"  examples after    -> {date_clean.head(4).tolist()}\n"
        f"  unparseable rows  -> {int(date_clean.isna().sum())}"
    )

    # ----- 5) Full recipe + before/after summary -------------------------
    print_banner("5) Full recipe — one call, before/after summary")
    cleaned = apply_full_recipe(dirty)
    print_section(
        "Cleaned dtypes:",
        pd.DataFrame({"dtype": cleaned.dtypes.astype(str)}).to_string(),
    )
    print_section("Cleaned head(5):", cleaned.head(5).to_string(index=False))
    print(
        f"\n  Source columns -> {list(dirty.columns)}\n"
        f"  Cleaned columns -> {list(cleaned.columns)}\n"
        f"  Sector distinct: {dirty['Sector!'].nunique()} -> "
        f"{cleaned['sector'].nunique()}\n"
        f"  Salary numeric : {salary_before_dtype} -> {cleaned['salary_lpa'].dtype}\n"
        f"  Date numeric   : {date_before_dtype}  -> {cleaned['date_posted'].dtype}"
    )

    # ----- 6) Reconnect to disk ------------------------------------------
    print_banner("Bundled CSV — column names already snake_case, dates clean")
    if SAMPLE_CSV_PATH.exists():
        bundled = pd.read_csv(SAMPLE_CSV_PATH, parse_dates=["date_posted"])
        bundled_std = apply_full_recipe(bundled)
        print(f"  bundled columns -> {list(bundled.columns)}")
        print(f"  cleaned columns -> {list(bundled_std.columns)}")
        print(
            "  (Bundled CSV is mostly clean; the synthetic frame is what\n"
            "  exercises the recipe.)"
        )
    else:
        print("  sample_job_postings.csv not found -- skipping disk demo.")

    # Cheat sheet
    print_banner("Standardisation cheat sheet")
    print(
        "  COLUMN NAMES\n"
        "    frame.rename(columns=normalise) where normalise =\n"
        "      strip + lower + non-alnum -> '_' + trim '_'\n"
        "  TEXT VALUES\n"
        "    series.str.strip().str.lower() then .replace(alias_map)\n"
        "  NUMERIC\n"
        "    series.str.replace('$', '').str.replace(',', '')\n"
        "    pd.to_numeric(..., errors='coerce')\n"
        "  DATES\n"
        "    pd.to_datetime(..., format='%Y-%m-%d', errors='coerce')\n"
        "      .fillna(pd.to_datetime(..., format='%d/%m/%Y', errors='coerce'))\n"
        "  RULE OF THUMB\n"
        "    Keep an explicit alias dict for categorical canonicalisation;\n"
        "    purely-lexical normalisation cannot infer 'IT' == 'Technology'."
    )

    print("\n" + "=" * BANNER_WIDTH)


if __name__ == "__main__":
    main()
