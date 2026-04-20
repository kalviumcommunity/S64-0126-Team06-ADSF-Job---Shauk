"""Assignment 4.21 — Structuring Python Code for Readability and Reuse.

Author: Bhargav Kalambhe (Frontend & ML)
Team:   Team 06 — Job-ही-Shauk (Sprint 3)

Where 4.20 focused on *naming* and *comments*, this script focuses on
*structure*: how a Python file is laid out so a reader can follow it
top-to-bottom without jumping around. The file is organised in five
clearly labelled sections so the flow of control is obvious:

    1. Imports
    2. Constants / configuration
    3. Pure helper functions (no side effects)
    4. Reporting / I/O functions
    5. Orchestration inside main() + entry-point guard

Each function does exactly one thing. The top-level is clean: `main()`
composes the pieces, and nothing else runs at import time.

Run:
    python3 src/code_structure.py
"""

# ---------------------------------------------------------------------------
# 1. IMPORTS — stdlib first, third-party next, local last (PEP 8).
# ---------------------------------------------------------------------------
from statistics import mean, median


# ---------------------------------------------------------------------------
# 2. CONSTANTS / CONFIGURATION — pulled out of logic so thresholds are
#    visible, greppable, and changeable in one place.
# ---------------------------------------------------------------------------
TRENDING_MENTION_THRESHOLD = 5
REPORT_WIDTH = 60


# ---------------------------------------------------------------------------
# 3. PURE HELPER FUNCTIONS — deterministic, no printing, no file I/O.
#    Easy to test and reuse in other scripts / notebooks.
# ---------------------------------------------------------------------------
def load_sample_skill_data() -> list[dict]:
    """Return a small hard-coded dataset so the demo is self-contained.

    In real pipelines this function would read from `data/raw/*.csv`;
    keeping the signature stable means the rest of the script does not
    change when the data source changes.
    """
    return [
        {"skill": "python", "mentions": 12},
        {"skill": "sql", "mentions": 9},
        {"skill": "excel", "mentions": 4},
        {"skill": "tableau", "mentions": 6},
        {"skill": "pytorch", "mentions": 2},
        {"skill": "pandas", "mentions": 11},
        {"skill": "aws", "mentions": 7},
        {"skill": "docker", "mentions": 3},
    ]


def filter_trending_skills(
    skill_records: list[dict], threshold: int = TRENDING_MENTION_THRESHOLD
) -> list[dict]:
    """Return only the records whose mention count meets the threshold."""
    return [record for record in skill_records if record["mentions"] >= threshold]


def compute_mention_stats(skill_records: list[dict]) -> dict:
    """Return summary statistics across all skill mention counts."""
    counts = [record["mentions"] for record in skill_records]
    return {
        "total_skills": len(counts),
        "total_mentions": sum(counts),
        "average_mentions": mean(counts),
        "median_mentions": median(counts),
        "max_mentions": max(counts),
        "min_mentions": min(counts),
    }


def rank_skills_by_mentions(skill_records: list[dict]) -> list[dict]:
    """Return the records sorted descending by mention count."""
    return sorted(skill_records, key=lambda record: record["mentions"], reverse=True)


# ---------------------------------------------------------------------------
# 4. REPORTING FUNCTIONS — side-effecting (print) and intentionally
#    separated from the pure helpers above.
# ---------------------------------------------------------------------------
def print_section_header(title: str) -> None:
    """Print a banner so long reports stay scannable."""
    print("=" * REPORT_WIDTH)
    print(title)
    print("=" * REPORT_WIDTH)


def print_stats_block(stats: dict) -> None:
    """Print a formatted summary of the statistics dictionary."""
    print(f"  Total skills tracked : {stats['total_skills']}")
    print(f"  Total mentions       : {stats['total_mentions']}")
    print(f"  Average mentions     : {stats['average_mentions']:.2f}")
    print(f"  Median  mentions     : {stats['median_mentions']}")
    print(f"  Max / Min            : {stats['max_mentions']} / {stats['min_mentions']}")


def print_skill_ranking(ranked_records: list[dict]) -> None:
    """Print a ranked list of skills with mention counts."""
    for position, record in enumerate(ranked_records, start=1):
        print(f"  {position:>2}. {record['skill']:<10} — {record['mentions']} mentions")


# ---------------------------------------------------------------------------
# 5. ORCHESTRATION — main() composes the helpers in reading order so
#    the file tells a story: load -> filter -> summarise -> report.
# ---------------------------------------------------------------------------
def main() -> None:
    """Compose the helpers to produce the full mini-report."""
    skill_records = load_sample_skill_data()

    trending_records = filter_trending_skills(skill_records)
    overall_stats = compute_mention_stats(skill_records)
    ranked_records = rank_skills_by_mentions(skill_records)

    print_section_header("Assignment 4.21 — Structured Skill Report")

    print("\nOverall statistics:")
    print_stats_block(overall_stats)

    print("\nSkills ranked by mentions:")
    print_skill_ranking(ranked_records)

    print(f"\nTrending skills (>= {TRENDING_MENTION_THRESHOLD} mentions):")
    print_skill_ranking(rank_skills_by_mentions(trending_records))

    print("=" * REPORT_WIDTH)


if __name__ == "__main__":
    main()
