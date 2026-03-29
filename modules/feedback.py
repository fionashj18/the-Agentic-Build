"""Question ratings and weighted selection."""

from __future__ import annotations

import json
import random
from pathlib import Path

FEEDBACK_FILE = Path(__file__).resolve().parent.parent / "data" / "feedback.json"


def _ensure_file() -> None:
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not FEEDBACK_FILE.is_file():
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


def _load_all() -> dict:
    _ensure_file()
    with open(FEEDBACK_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def _save_all(data: dict) -> None:
    _ensure_file()
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def record_rating(username: str, question_id: int, rating: str) -> None:
    """rating is 'good', 'bad', or 'skip'."""
    r = rating.strip().lower()
    if r not in ("good", "bad", "skip"):
        return
    data = _load_all()
    user_key = username.strip()
    if user_key not in data:
        data[user_key] = {}
    qkey = str(question_id)
    if qkey not in data[user_key]:
        data[user_key][qkey] = {"good": 0, "bad": 0, "skip": 0}
    data[user_key][qkey][r] += 1
    _save_all(data)


def weight_for_question(username: str, question_id: int) -> float:
    """Higher weight = more likely to be selected."""
    data = _load_all()
    user_key = username.strip()
    counts = (data.get(user_key) or {}).get(str(question_id)) or {}
    good = int(counts.get("good", 0))
    bad = int(counts.get("bad", 0))
    skip = int(counts.get("skip", 0))
    # Favor questions rated good; de-emphasize bad; skip is neutral-slight boost
    w = 1.0 + good * 1.5 - bad * 2.0 + skip * 0.2
    return max(0.1, w)


def weighted_sample_without_replacement(
    items: list[dict], k: int, username: str
) -> list[dict]:
    """Randomly pick k items using per-user feedback weights."""
    if k <= 0 or not items:
        return []
    pool = list(items)
    chosen: list[dict] = []
    for _ in range(min(k, len(pool))):
        weights = [weight_for_question(username, int(q["id"])) for q in pool]
        total = sum(weights)
        r = random.uniform(0, total)
        acc = 0.0
        idx = 0
        for i, w in enumerate(weights):
            acc += w
            if r <= acc:
                idx = i
                break
        chosen.append(pool.pop(idx))
    return chosen
