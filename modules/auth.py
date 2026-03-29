"""Login, registration, and password hashing."""

from __future__ import annotations

import json
import os
from pathlib import Path

import bcrypt

USERS_FILE = Path(__file__).resolve().parent.parent / "data" / "users.json"


def _ensure_data_dir() -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_users() -> dict[str, str]:
    _ensure_data_dir()
    if not USERS_FILE.is_file():
        return {}
    with open(USERS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items()}


def _save_users(users: dict[str, str]) -> None:
    _ensure_data_dir()
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("ascii"))
    except (ValueError, TypeError):
        return False


def register(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not username:
        return False, "Username cannot be empty."
    if not password:
        return False, "Password cannot be empty."
    users = _load_users()
    if username in users:
        return False, "That username is already taken."
    users[username] = hash_password(password)
    _save_users(users)
    return True, "Account created."


def login(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not username or not password:
        return False, "Invalid username or password."
    users = _load_users()
    if username not in users:
        return False, "Invalid username or password."
    if not verify_password(password, users[username]):
        return False, "Invalid username or password."
    return True, "Logged in."
