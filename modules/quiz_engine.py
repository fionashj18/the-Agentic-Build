"""Load questions, filter, score answers."""

from __future__ import annotations

import json
import re
from pathlib import Path

QUESTIONS_FILE = Path(__file__).resolve().parent.parent / "questions.json"


class QuestionsFileError(Exception):
    """questions.json is missing or invalid."""


def load_questions(path: Path | None = None) -> list[dict]:
    """Load and validate questions from JSON. Raises QuestionsFileError on failure."""
    p = path or QUESTIONS_FILE
    if not p.is_file():
        raise QuestionsFileError("The questions file is missing or invalid.")
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise QuestionsFileError("The questions file is missing or invalid.") from e
    if not isinstance(data, dict) or "questions" not in data:
        raise QuestionsFileError("The questions file is missing or invalid.")
    raw = data["questions"]
    if not isinstance(raw, list) or not raw:
        raise QuestionsFileError("The questions file is missing or invalid.")
    out: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        if "id" not in item or "question" not in item or "type" not in item:
            continue
        if "answer" not in item:
            continue
        out.append(item)
    if not out:
        raise QuestionsFileError("The questions file is missing or invalid.")
    return out


def get_categories(questions: list[dict]) -> list[str]:
    cats = set()
    for q in questions:
        c = q.get("category", "")
        if isinstance(c, str) and c.strip():
            cats.add(c.strip())
    return sorted(cats)


def filter_by_category(questions: list[dict], category: str | None) -> list[dict]:
    if not category or category.strip().lower() in ("all", "*"):
        return list(questions)
    cat = category.strip()
    return [q for q in questions if str(q.get("category", "")).strip() == cat]


def normalize_short_answer(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def parse_true_false(raw: str) -> str | None:
    t = raw.strip().lower()
    if t in ("true", "t", "yes", "y", "1"):
        return "true"
    if t in ("false", "f", "no", "n", "0"):
        return "false"
    return None


def check_answer(question: dict, user_raw: str) -> bool:
    qtype = str(question.get("type", "")).strip()
    correct = question.get("answer")
    if qtype == "multiple_choice":
        options = question.get("options") or []
        if not isinstance(options, list):
            options = []
        u = user_raw.strip()
        if u.isdigit():
            n = int(u)
            if 1 <= n <= len(options):
                return options[n - 1].strip() == str(correct).strip()
        return u.strip().lower() == str(correct).strip().lower()
    if qtype == "true_false":
        parsed = parse_true_false(user_raw)
        if parsed is None:
            return False
        return parsed == str(correct).strip().lower()
    if qtype == "short_answer":
        return normalize_short_answer(user_raw) == normalize_short_answer(str(correct))
    return False


def points_for_answer(correct: bool, hint_used: bool) -> int:
    if not correct:
        return 0
    if hint_used:
        return 5
    return 10
