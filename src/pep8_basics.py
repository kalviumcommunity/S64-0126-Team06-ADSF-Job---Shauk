"""Assignment 4.20 - Readable variable names and comments.

Run:
    python src/pep8_basics.py
"""

PASSING_SCORE_THRESHOLD = 50


def calculate_class_average(student_scores: list[int]) -> float:
    """Return the average score for all students."""
    return sum(student_scores) / len(student_scores)


def get_pass_fail_label(student_score: int) -> str:
    """Return pass/fail label using a shared threshold rule."""
    # Keeping this threshold in one constant avoids hidden magic numbers.
    if student_score >= PASSING_SCORE_THRESHOLD:
        return "pass"
    return "fail"


def print_student_report(student_names: list[str], student_scores: list[int]) -> None:
    """Print each student with score and pass/fail status."""
    for student_name, student_score in zip(student_names, student_scores):
        pass_fail_label = get_pass_fail_label(student_score)
        print(f"{student_name:<8} | score: {student_score:>3} | {pass_fail_label}")


def main() -> None:
    """Run a small, readability-focused example."""
    student_names = ["Aarav", "Diya", "Kabir", "Meera", "Riya"]
    student_scores = [72, 45, 88, 51, 39]

    class_average_score = calculate_class_average(student_scores)

    print("Assignment 4.20 - PEP 8 Basics")
    print("-" * 45)
    print_student_report(student_names, student_scores)
    print("-" * 45)
    print(f"Class average score: {class_average_score:.2f}")


if __name__ == "__main__":
    main()
