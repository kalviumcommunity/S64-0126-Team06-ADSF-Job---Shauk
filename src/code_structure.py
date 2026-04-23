"""Assignment 4.21 - Code structure for readability and reuse.

This script demonstrates:
1) clear sections (imports, constants, helpers, execution),
2) reusable functions to avoid duplication,
3) clean top-to-bottom flow with a main entry point.
"""

# 1) Imports
from datetime import datetime


# 2) Constants / configuration
REPORT_LINE = "-" * 52
TASKS = [
    {"title": "Write README summary", "minutes": 25, "completed": True},
    {"title": "Refactor helper function", "minutes": 30, "completed": False},
    {"title": "Prepare demo notes", "minutes": 20, "completed": True},
]


# 3) Reusable helper functions (pure logic)
def count_completed_tasks(task_items: list[dict]) -> int:
    """Return number of completed tasks."""
    return sum(1 for task_item in task_items if task_item["completed"])


def calculate_total_minutes(task_items: list[dict]) -> int:
    """Return total estimated minutes across all tasks."""
    return sum(task_item["minutes"] for task_item in task_items)


def calculate_completion_rate(task_items: list[dict]) -> float:
    """Return completion rate as percentage."""
    completed_count = count_completed_tasks(task_items)
    return (completed_count / len(task_items)) * 100


# 4) Output helpers (separated from pure logic)
def print_header(report_title: str) -> None:
    """Print a readable report header."""
    print(REPORT_LINE)
    print(report_title)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(REPORT_LINE)


def print_task_list(task_items: list[dict]) -> None:
    """Print tasks using a consistent row format."""
    for task_item in task_items:
        status_label = "done" if task_item["completed"] else "pending"
        print(f"{task_item['title']:<30} | {task_item['minutes']:>2} min | {status_label}")


def print_summary(task_items: list[dict]) -> None:
    """Print summary values computed by reusable helpers."""
    total_task_count = len(task_items)
    completed_task_count = count_completed_tasks(task_items)
    total_minutes = calculate_total_minutes(task_items)
    completion_rate = calculate_completion_rate(task_items)

    print(REPORT_LINE)
    print(f"Total tasks       : {total_task_count}")
    print(f"Completed tasks   : {completed_task_count}")
    print(f"Estimated minutes : {total_minutes}")
    print(f"Completion rate   : {completion_rate:.1f}%")
    print(REPORT_LINE)


# 5) Execution orchestration
def main() -> None:
    """Run report flow from top to bottom."""
    print_header("Assignment 4.21 - Structured Task Report")
    print_task_list(TASKS)
    print_summary(TASKS)


if __name__ == "__main__":
    main()
