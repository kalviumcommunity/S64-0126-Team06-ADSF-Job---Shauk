"""Canonicalization utilities: skill vocabulary mapping and fuzzy matching.

Three-tier resolution per raw skill:
  1. Exact match  — O(1) dict lookup
  2. Fuzzy match  — rapidfuzz.process.extractOne with configurable threshold
  3. Unmatched    — returns None; caller decides what to do (drop or keep_raw)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from rapidfuzz import process as rf_process

logger = logging.getLogger(__name__)


def load_skill_vocabulary(path: str) -> dict[str, str]:
    """Load the canonical skill vocabulary from a YAML file.

    Returns:
        Flat dict mapping every alias (lowercased) → canonical skill name.
        The canonical name itself is also included as an alias.

    Raises:
        KeyError: If required top-level keys ('version', 'canonical_skills') are missing.
        yaml.YAMLError: If the file is not valid YAML.
    """
    yaml_path = Path(path)
    with yaml_path.open("r", encoding="utf-8") as fh:
        data: dict[str, Any] = yaml.safe_load(fh)

    for required_key in ("version", "canonical_skills"):
        if required_key not in data:
            raise KeyError(
                f"Missing required key '{required_key}' in vocabulary file {yaml_path.name}"
            )

    vocab: dict[str, str] = {}
    for canonical_name, spec in data["canonical_skills"].items():
        # The canonical name itself is always a valid alias
        vocab[canonical_name.lower()] = canonical_name
        for alias in spec.get("aliases", []):
            vocab[alias.lower()] = canonical_name

    logger.info(
        "load_skill_vocabulary: %d aliases → %d canonical skills from %s (v%s)",
        len(vocab),
        len(data["canonical_skills"]),
        yaml_path.name,
        data.get("version", "?"),
    )
    return vocab


def canonicalize_skill(
    raw_skill: str,
    vocab: dict[str, str],
    fuzzy_threshold: float = 88.0,
) -> str | None:
    """Map a single raw skill string to its canonical form.

    Resolution order:
    1. Exact match (O(1) lookup in vocab)
    2. Fuzzy match via rapidfuzz (score >= fuzzy_threshold on 0–100 scale)
    3. Returns None if no match

    Args:
        raw_skill: Raw skill string (need not be pre-lowercased).
        vocab: Flat alias → canonical dict from load_skill_vocabulary().
        fuzzy_threshold: Minimum rapidfuzz score (0–100) to accept a fuzzy match.

    Postconditions:
        - Returns None or a string in vocab.values()
        - Does not mutate vocab
    """
    if not isinstance(raw_skill, str) or not raw_skill.strip():
        return None

    normalized = raw_skill.strip().lower()

    # Tier 1: exact match
    if normalized in vocab:
        return vocab[normalized]

    # Tier 2: fuzzy match
    match = rf_process.extractOne(normalized, vocab.keys(), score_cutoff=fuzzy_threshold)
    if match is not None:
        matched_alias, score, _ = match
        canonical = vocab[matched_alias]
        logger.debug(
            "canonicalize_skill: '%s' → '%s' via fuzzy (score=%.1f)", raw_skill, canonical, score
        )
        return canonical

    return None


def canonicalize_skill_list(
    skills: list[str],
    vocab: dict[str, str],
    unmatched_policy: str = "drop",
) -> list[str]:
    """Canonicalize a list of raw skill strings.

    Args:
        skills: List of raw skill strings (lowercased or not).
        vocab: Flat alias → canonical dict.
        unmatched_policy: 'drop' omits unmatched skills; 'keep_raw' retains them as-is.

    Returns:
        Deduplicated list of canonical (or raw) skill names.

    Postcondition: No duplicates in output.
    """
    result: list[str] = []
    seen: set[str] = set()

    for skill in skills:
        canonical = canonicalize_skill(skill, vocab)
        if canonical is not None:
            if canonical not in seen:
                result.append(canonical)
                seen.add(canonical)
        elif unmatched_policy == "keep_raw":
            raw = skill.strip().lower()
            if raw and raw not in seen:
                result.append(raw)
                seen.add(raw)

    return result
