#!/usr/bin/env python3
"""Quiz application — main entry point."""

from __future__ import annotations

import sys
from getpass import getpass

from modules import auth, feedback, quiz_engine, stats

INVALID_MSG = "Invalid input. Please try again."


def _print_invalid() -> None:
    print(INVALID_MSG)


def _prompt_line(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        print()
        sys.exit(0)


def _auth_screen() -> str | None:
    """Return username when logged in, or None if quit."""
    while True:
        print("\n--- Welcome ---")
        print("1) Log in")
        print("2) Create an account")
        print("3) Quit")
        choice = _prompt_line("Choose (1–3): ")
        if choice == "1":
            u = _prompt_line("Username: ")
            pw = getpass("Password: ")
            ok, msg = auth.login(u, pw)
            print(msg)
            if ok:
                return u.strip()
        elif choice == "2":
            u = _prompt_line("Choose a username: ")
            pw = getpass("Password: ")
            pw2 = getpass("Confirm password: ")
            if pw != pw2:
                print("Passwords do not match.")
                continue
            ok, msg = auth.register(u, pw)
            print(msg)
            if ok:
                return u.strip()
        elif choice == "3":
            return None
        else:
            _print_invalid()


def _main_menu(username: str, all_questions: list[dict]) -> None:
    while True:
        print(f"\n--- Main menu ({username}) ---")
        print("1) Take a quiz")
        print("2) View your stats")
        print("3) Log out")
        c = _prompt_line("Choose (1–3): ")
        if c == "1":
            _run_quiz(username, all_questions)
        elif c == "2":
            print()
            print(stats.format_stats_screen(username))
        elif c == "3":
            print("You have been logged out.")
            return
        else:
            _print_invalid()


def _pick_category(questions: list[dict]) -> list[dict] | None:
    """Return filtered questions, or None if user aborts. Loops if category empty."""
    cats = quiz_engine.get_categories(questions)
    while True:
        print("\nCategories:")
        print("  0) All categories")
        for i, c in enumerate(cats, start=1):
            print(f"  {i}) {c}")
        raw = _prompt_line(
            f"Pick a category (0–{len(cats)}) or Q to cancel: "
        )
        if raw.upper() == "Q":
            return None
        if not raw.isdigit():
            _print_invalid()
            continue
        n = int(raw)
        if n == 0:
            return quiz_engine.filter_by_category(questions, "all")
        if 1 <= n <= len(cats):
            filtered = quiz_engine.filter_by_category(questions, cats[n - 1])
            if not filtered:
                print(
                    "No questions in that category. Pick a different category."
                )
                continue
            return filtered
        _print_invalid()


def _pick_question_count(available: int) -> int | None:
    while True:
        raw = _prompt_line(
            f"How many questions? (1–7, max {available} available) or Q to cancel: "
        )
        if raw.upper() == "Q":
            return None
        if not raw.isdigit():
            _print_invalid()
            continue
        n = int(raw)
        if n < 1 or n > 7:
            _print_invalid()
            continue
        if n > available:
            print(
                f"Only {available} question(s) available; using {available}."
            )
            return available
        return n


def _display_question(q: dict) -> None:
    print()
    print(q.get("question", ""))
    qtype = str(q.get("type", ""))
    if qtype == "multiple_choice":
        opts = q.get("options") or []
        for i, o in enumerate(opts, start=1):
            print(f"  {i}) {o}")
        print("Enter the option number (1–4) or type the answer.")


def _answer_loop(q: dict) -> tuple[str, bool]:
    """
    Collect answer; return (user_raw, hint_used).
    hint_used True if user revealed a hint before answering or skipping.
    """
    hint_text = q.get("hint")
    has_hint = isinstance(hint_text, str) and hint_text.strip()
    hint_revealed = False

    qtype = str(q.get("type", ""))

    while True:
        hint_part = (
            ", H for a hint" if has_hint and not hint_revealed else ""
        )
        if qtype == "multiple_choice":
            prompt = f"Your answer{hint_part}, or Q to skip: "
        elif qtype == "true_false":
            prompt = f"True or false?{hint_part}, or Q to skip: "
        else:
            prompt = f"Your answer{hint_part}, or Q to skip: "

        raw = _prompt_line(prompt)
        if raw.upper() == "Q":
            return "", hint_revealed

        if raw.upper() == "H":
            if not has_hint:
                _print_invalid()
                continue
            if hint_revealed:
                _print_invalid()
                continue
            print(f"Hint: {hint_text.strip()}")
            hint_revealed = True
            continue

        if qtype == "multiple_choice":
            opts = q.get("options") or []
            if raw.isdigit():
                num = int(raw)
                if 1 <= num <= len(opts):
                    return raw, hint_revealed
            # match full text
            low = raw.lower()
            for o in opts:
                if o.strip().lower() == low:
                    return raw, hint_revealed
            _print_invalid()
            continue

        if qtype == "true_false":
            if quiz_engine.parse_true_false(raw) is not None:
                return raw, hint_revealed
            _print_invalid()
            continue

        if qtype == "short_answer":
            if raw.strip():
                return raw, hint_revealed
            _print_invalid()
            continue

        _print_invalid()


def _rating_prompt() -> str | None:
    while True:
        r = _prompt_line("Rate this question — G (Good), B (Bad), S (Skip): ")
        u = r.upper()
        if u == "G":
            return "good"
        if u == "B":
            return "bad"
        if u == "S":
            return "skip"
        _print_invalid()


def _run_quiz(username: str, all_questions: list[dict]) -> None:
    pool = _pick_category(all_questions)
    if pool is None:
        return

    n = _pick_question_count(len(pool))
    if n is None:
        return

    selected = feedback.weighted_sample_without_replacement(pool, n, username)
    if not selected:
        print("No questions could be selected.")
        return

    total_score = 0
    correct_n = 0
    hints_used = 0

    for q in selected:
        _display_question(q)
        user_raw, hint_used = _answer_loop(q)
        skipped = user_raw == ""

        if hint_used:
            hints_used += 1

        if not skipped:
            ok = quiz_engine.check_answer(q, user_raw)
            pts = quiz_engine.points_for_answer(ok, hint_used)
            total_score += pts
            if ok:
                correct_n += 1
                print(f"Correct! +{pts} points.")
            else:
                print("Incorrect.")
                print(f"The correct answer is: {q.get('answer')}")
        else:
            print("Question skipped.")
            print(f"The correct answer was: {q.get('answer')}")

        qid = int(q["id"])
        rating = _rating_prompt()
        if rating:
            feedback.record_rating(username, qid, rating)

    total = len(selected)
    acc = (100.0 * correct_n / total) if total else 0.0

    print("\n--- Quiz complete ---")
    print(f"Score: {total_score}")
    print(f"Accuracy: {acc:.1f}% ({correct_n}/{total} correct)")
    print(f"Hints used: {hints_used}")

    stats.save_quiz_result(
        username,
        total_score,
        total,
        correct_n,
        hints_used,
        acc,
    )
    print("Results saved.")


def main() -> None:
    try:
        all_questions = quiz_engine.load_questions()
    except quiz_engine.QuestionsFileError:
        print(
            "Error: The questions file is missing or invalid. "
            "Ensure questions.json exists and contains valid data."
        )
        sys.exit(1)

    while True:
        user = _auth_screen()
        if user is None:
            print("Goodbye.")
            break
        _main_menu(user, all_questions)


if __name__ == "__main__":
    main()
