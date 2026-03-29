"""Persist and display quiz results."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SCORES_FILE = Path(__file__).resolve().parent.parent / "data" / "scores.dat"


def _ensure_file() -> None:
    SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not SCORES_FILE.is_file():
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def _load_records() -> list[dict]:
    _ensure_file()
    try:
        with open(SCORES_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_records(records: list[dict]) -> None:
    _ensure_file()
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def save_quiz_result(
    username: str,
    score: int,
    total_questions: int,
    correct: int,
    hints_used: int,
    accuracy_pct: float,
) -> None:
    records = _load_records()
    records.append(
        {
            "user": username,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "score": score,
            "total_questions": total_questions,
            "correct": correct,
            "hints_used": hints_used,
            "accuracy": round(accuracy_pct, 2),
        }
    )
    _save_records(records)


def get_records_for_user(username: str) -> list[dict]:
    u = username.strip()
    return [r for r in _load_records() if str(r.get("user", "")).strip() == u]


def format_stats_screen(username: str) -> str:
    rows = get_records_for_user(username)
    if not rows:
        return "No quiz results saved yet. Complete a quiz to see stats here.\n"
    lines = [f"--- Stats for {username} ---\n"]
    total_score = 0
    total_q = 0
    total_correct = 0
    total_hints = 0
    for i, r in enumerate(rows, start=1):
        lines.append(
            f"{i}. Score: {r.get('score', 0)} | "
            f"Correct: {r.get('correct', 0)}/{r.get('total_questions', 0)} | "
            f"Accuracy: {r.get('accuracy', 0)}% | "
            f"Hints: {r.get('hints_used', 0)} | "
            f"{r.get('timestamp', '')}"
        )
        total_score += int(r.get("score", 0))
        total_q += int(r.get("total_questions", 0))
        total_correct += int(r.get("correct", 0))
        total_hints += int(r.get("hints_used", 0))
    lines.append("")
    acc = (100.0 * total_correct / total_q) if total_q else 0.0
    lines.append(
        f"Totals — Quizzes: {len(rows)}, Points: {total_score}, "
        f"Questions: {total_q}, Hints used: {total_hints}, "
        f"Overall accuracy: {acc:.1f}%"
    )
    lines.append("")
    return "\n".join(lines)
