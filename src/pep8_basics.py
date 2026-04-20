"""Assignment 4.20 — Writing Readable Variable Names and Comments (PEP8 Basics).

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

This script contrasts an unreadable "before" style with a PEP8-compliant "after"
style on the same tiny data-science task: summarising a list of candidate skill
counts across job postings. The two functions produce identical output; only
naming and comment discipline change.

Run:
    python3 src/pep8_basics.py
"""

from statistics import mean


# ---------------------------------------------------------------------------
# BEFORE — unreadable on purpose. DO NOT write code like this in real work.
# ---------------------------------------------------------------------------
def f(x):
    # loop
    a = 0
    b = 0
    for i in x:
        a = a + i  # add
        b = b + 1  # count
    c = a / b  # avg
    return c


# ---------------------------------------------------------------------------
# AFTER — PEP8-compliant, self-documenting.
# ---------------------------------------------------------------------------
MIN_MENTIONS_FOR_TRENDING = 5


def compute_average_mentions(skill_mention_counts: list[int]) -> float:
    """Return the mean number of times a skill is mentioned across postings.

    Using a descriptive parameter name plus a one-line docstring removes the
    need for inline "what it does" comments — the signature already explains.
    """
    return mean(skill_mention_counts)


def classify_skill(skill_name: str, mention_count: int) -> str:
    """Classify a skill as trending or niche based on its mention count.

    The threshold lives in a module-level UPPER_SNAKE_CASE constant so
    non-obvious magic numbers never appear mid-logic.
    """
    if mention_count >= MIN_MENTIONS_FOR_TRENDING:
        return f"{skill_name}: trending"
    return f"{skill_name}: niche"


def main() -> None:
    """Entry point — keeps top-level code out of import side effects."""
    skills = ["python", "sql", "excel", "tableau", "pytorch"]
    mention_counts = [12, 9, 4, 6, 2]

    # Side-by-side demonstration: both styles return the same number,
    # but only one survives a code review.
    legacy_average = f(mention_counts)
    clean_average = compute_average_mentions(mention_counts)

    print("=" * 60)
    print("Assignment 4.20 — PEP8 Basics")
    print("=" * 60)
    print(f"Legacy style avg : {legacy_average:.2f}")
    print(f"Clean  style avg : {clean_average:.2f}")
    print(f"Identical result : {legacy_average == clean_average}")
    print("-" * 60)
    print("Skill classification:")
    for skill_name, count in zip(skills, mention_counts):
        print(f"  {classify_skill(skill_name, count)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
