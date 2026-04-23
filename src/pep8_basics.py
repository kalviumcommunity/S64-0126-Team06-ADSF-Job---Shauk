"""Assignment 4.20 - Readable names and meaningful comments.

This script focuses on naming and comment quality, not complex logic.
Run: python3 src/pep8_basics.py
"""

PASSING_SCORE = 50


def calculate_average_score(student_scores: list[int]) -> float:
    """Return the average score for a class."""
    return sum(student_scores) / len(student_scores)


def get_result_label(score: int) -> str:
    """Return pass/fail label using a shared threshold constant."""
    # Keep the threshold in one place so policy updates need one edit.
    if score >= PASSING_SCORE:
        return "pass"
    return "fail"


def print_student_results(student_names: list[str], student_scores: list[int]) -> None:
    """Print each student's score with a readable status label."""
    for student_name, student_score in zip(student_names, student_scores):
        result_label = get_result_label(student_score)
        print(f"{student_name:<8} | score: {student_score:>3} | {result_label}")


def main() -> None:
    """Run a small readability-focused example."""
    student_names = ["Aarav", "Diya", "Kabir", "Meera", "Riya"]
    student_scores = [72, 45, 88, 51, 39]

    class_average_score = calculate_average_score(student_scores)

    print("Assignment 4.20 - PEP 8 Basics")
    print("-" * 45)
    print_student_results(student_names, student_scores)
    print("-" * 45)
    print(f"Class average score: {class_average_score:.2f}")


if __name__ == "__main__":
    main()
