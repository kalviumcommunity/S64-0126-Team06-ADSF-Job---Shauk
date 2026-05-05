"""Unit and property-based tests for the canonicalize module (TC-13 – TC-17).

Covers load_skill_vocabulary, canonicalize_skill, canonicalize_skill_list.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.utils.canonicalize import (  # noqa: E402
    canonicalize_skill,
    canonicalize_skill_list,
    load_skill_vocabulary,
)

VOCAB_YAML = ROOT / "configs" / "skills_canonical.yaml"

# A minimal in-memory vocabulary for deterministic unit tests
MINI_VOCAB: dict[str, str] = {
    "python": "python",
    "python3": "python",
    "py": "python",
    "sql": "sql",
    "mysql": "sql",
    "machine_learning": "machine_learning",
    "ml": "machine_learning",
}


# ---------------------------------------------------------------------------
# TC-13  canonicalize_skill — exact match
# ---------------------------------------------------------------------------
def test_canonicalize_skill_exact_match():
    assert canonicalize_skill("python", MINI_VOCAB) == "python"
    assert canonicalize_skill("ml", MINI_VOCAB) == "machine_learning"
    assert canonicalize_skill("MySQL", MINI_VOCAB) == "sql"  # case-insensitive


# ---------------------------------------------------------------------------
# TC-14  canonicalize_skill — fuzzy match (typo 'pythn')
# ---------------------------------------------------------------------------
def test_canonicalize_skill_fuzzy_match():
    result = canonicalize_skill("pythn", MINI_VOCAB, fuzzy_threshold=80.0)
    assert result == "python"


# ---------------------------------------------------------------------------
# TC-15  canonicalize_skill — no match → None
# ---------------------------------------------------------------------------
def test_canonicalize_skill_no_match():
    result = canonicalize_skill("xyz123completelyrandom", MINI_VOCAB)
    assert result is None


def test_canonicalize_skill_empty_string():
    assert canonicalize_skill("", MINI_VOCAB) is None
    assert canonicalize_skill("   ", MINI_VOCAB) is None


def test_canonicalize_skill_none_input():
    assert canonicalize_skill(None, MINI_VOCAB) is None  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# TC-16  load_skill_vocabulary — valid YAML → flat alias dict
# ---------------------------------------------------------------------------
def test_load_skill_vocabulary_returns_flat_dict():
    vocab = load_skill_vocabulary(str(VOCAB_YAML))
    assert isinstance(vocab, dict)
    assert len(vocab) > 0
    # Canonical names themselves must be in the dict
    assert "python" in vocab
    assert vocab["python"] == "python"


def test_load_skill_vocabulary_aliases_resolve():
    vocab = load_skill_vocabulary(str(VOCAB_YAML))
    assert "ml" in vocab
    assert vocab["ml"] == "machine_learning"


# ---------------------------------------------------------------------------
# TC-17  load_skill_vocabulary — missing 'canonical_skills' key → KeyError
# ---------------------------------------------------------------------------
def test_load_skill_vocabulary_missing_key_raises():
    bad_yaml = {"version": "1.0"}  # missing canonical_skills
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as fh:
        yaml.dump(bad_yaml, fh)
        tmp_path = fh.name
    with pytest.raises(KeyError, match="canonical_skills"):
        load_skill_vocabulary(tmp_path)


def test_load_skill_vocabulary_missing_version_raises():
    bad_yaml = {"canonical_skills": {}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as fh:
        yaml.dump(bad_yaml, fh)
        tmp_path = fh.name
    with pytest.raises(KeyError, match="version"):
        load_skill_vocabulary(tmp_path)


# ---------------------------------------------------------------------------
# canonicalize_skill_list — policy tests
# ---------------------------------------------------------------------------
def test_canonicalize_skill_list_drop_unmatched():
    skills = ["python", "xyz_unknown"]
    result = canonicalize_skill_list(skills, MINI_VOCAB, unmatched_policy="drop")
    assert "xyz_unknown" not in result
    assert "python" in result


def test_canonicalize_skill_list_keep_raw():
    skills = ["python", "xyz_unknown"]
    result = canonicalize_skill_list(skills, MINI_VOCAB, unmatched_policy="keep_raw")
    assert "python" in result
    assert "xyz_unknown" in result


def test_canonicalize_skill_list_no_duplicates():
    """Canonical names are deduplicated even when multiple aliases map to the same name."""
    skills = ["python", "python3", "py", "ml", "machine_learning"]
    result = canonicalize_skill_list(skills, MINI_VOCAB)
    assert len(result) == len(set(result))
    assert result.count("python") == 1
    assert result.count("machine_learning") == 1


def test_canonicalize_skill_list_empty_input():
    assert canonicalize_skill_list([], MINI_VOCAB) == []


# ---------------------------------------------------------------------------
# Property 13: output is always canonical or None
# ---------------------------------------------------------------------------
@given(raw=st.text(min_size=0, max_size=30))
@settings(max_examples=200)
def test_canonicalize_skill_output_valid(raw: str):
    """canonicalize_skill returns None or a value in vocab.values()."""
    result = canonicalize_skill(raw, MINI_VOCAB)
    assert result is None or result in MINI_VOCAB.values()


@given(raw=st.text(min_size=0, max_size=30))
@settings(max_examples=200)
def test_canonicalize_skill_does_not_mutate_vocab(raw: str):
    """canonicalize_skill must not mutate the vocab dict."""
    original = dict(MINI_VOCAB)
    canonicalize_skill(raw, MINI_VOCAB)
    assert MINI_VOCAB == original
