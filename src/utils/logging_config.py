"""Structured logging: rich console handler + daily-rotating file handler."""

from __future__ import annotations

import logging
import logging.handlers
from datetime import date
from pathlib import Path

from rich.logging import RichHandler


def configure_logging(log_dir: str = "logs", level: str = "INFO") -> None:
    """Configure Python logging for the pipeline.

    Sets up two handlers:
    - Console: colorised via rich, human-friendly during development.
    - File:    plain-text, daily rotation, kept for 30 days.

    Safe to call multiple times — handlers are not duplicated.

    Args:
        log_dir: Directory for log files (created if absent).
        level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'.
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    log_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()

    # Guard against duplicate handler registration on repeated calls
    if root.handlers:
        return

    root.setLevel(log_level)

    # Console handler (rich)
    console_handler = RichHandler(
        level=log_level,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    root.addHandler(console_handler)

    # Rotating file handler
    log_file = log_path / f"pipeline_{date.today():%Y-%m-%d}.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )
    root.addHandler(file_handler)
