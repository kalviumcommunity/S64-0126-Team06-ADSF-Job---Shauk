"""I/O utilities: CSV loading and DataFrame inspection.

No side-effects (no print, no plt.show). Callers are responsible for
presenting results.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def load_csv(filepath: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
    """Load a CSV file into a DataFrame.

    Args:
        filepath: Path to the .csv file.
        parse_dates: Column names to parse as datetime64.

    Returns:
        A non-empty pd.DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        pd.errors.EmptyDataError: If the file is empty.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}. Place raw CSVs in data/raw/.")
    df = pd.read_csv(filepath, parse_dates=parse_dates or [])
    logger.info("load_csv: read %d rows × %d cols from %s", *df.shape, path.name)
    return df


def inspect_dataframe(df: pd.DataFrame) -> None:
    """Log shape, dtypes, null summary, and descriptive stats.

    Designed to be called once per stage entry — never prints to stdout.
    """
    logger.info("  shape   : %s", df.shape)
    logger.info("  dtypes  :\n%s", df.dtypes.to_string())
    null_counts = df.isnull().sum()
    if null_counts.any():
        logger.info("  nulls   :\n%s", null_counts[null_counts > 0].to_string())
    else:
        logger.info("  nulls   : none")
    logger.debug("  describe:\n%s", df.describe(include="all").to_string())
