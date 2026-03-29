Review (numbered findings)
[PASS] AC1 — Missing questions.json. quiz_engine.load_questions() raises QuestionsFileError when the file is missing, unreadable, or not valid usable data (quiz_engine.py 19–20, 24–25, 26–27, 29–30, 40–41). main() catches it, prints a clear message, and exits with code 1 (quiz.py 283–291).

[PASS] AC2 — Login and accounts; passwords not plain text. Registration hashes with bcrypt and stores only the hash (auth.py 35–36, 55–56). Login verifies with bcrypt.checkpw (auth.py 39–43, 67–68). Password entry uses getpass (quiz.py 7, 36–37, 43–44). Plain passwords are not written to disk.

[PASS] AC3 — Scores saved and visible in stats. Each completed quiz appends a record via stats.save_quiz_result() (quiz.py 272–279; stats.py 35–55). The stats screen reads those records with get_records_for_user / format_stats_screen (stats.py 58–61, 63–92).

[PASS] AC4 — Hints cost points; hint count at end. Correct answers with a hint score 5; without a hint, 10 (quiz_engine.py 99–104). The summary prints total score, accuracy, and “Hints used” (quiz.py 241–247, 267–270). Hint use is tracked per question when the user reveals a hint before answering or skipping (quiz.py 166–174, 241–243).

[PASS] AC5 — Unexpected typed input loops instead of crashing. Menus and answer paths use _print_invalid() and continue (quiz.py 54–55, 90–92, 114–116, 118–120, 166–172, 187–188, etc.). _prompt_line handles EOFError cleanly (quiz.py 18–23).

[PASS] Spec — Error 1 (questions.json missing or broken). Covered by finding 1 (quiz_engine.py 16–42; quiz.py 283–291).

[PASS] Spec — Error 2 (invalid user input). Central message INVALID_MSG (quiz.py 11–15) and repeated invalid-input handling across prompts (e.g. quiz.py 54–55, 90–92, 114–120, 206–216).

[PASS] Spec — Error 3 (not enough questions / empty category). Requesting more than available caps with a warning and uses the available count (quiz.py 121–125). Empty category shows a message and asks for another choice (quiz.py 97–102).

[WARN] Missing error handling — data/users.json corrupt. _load_users calls json.load with no try/except (auth.py 22–23). Invalid JSON can raise and crash login/registration, which weakens resilience compared to stats._load_records() (stats.py 21–26).

[WARN] Missing error handling — data/feedback.json corrupt. _load_all opens and json.loads with no try/except (feedback.py 21–22). A bad file can crash rating load/save paths (e.g. record_rating, weighted_sample_without_replacement).

[WARN] Logic / data integrity — corrupt scores.dat. On JSON failure, _load_records returns [] (stats.py 25–26). The next save_quiz_result still runs _save_records and can overwrite the file with a list that only contains the new attempt (stats.py 43–55), silently dropping prior history.

[WARN] Robustness — question["id"] not validated as numeric. load_questions only checks that "id" exists (quiz_engine.py 35–36). JSON could legally use a non-numeric id; int(q["id"]) in the quiz and feedback paths would then raise (quiz.py 259; feedback.py 70).

[WARN] Code quality — unused import. import os in auth.py line 7 is unused.

[PASS] Security — file handling. Data files use fixed paths under the project (auth.py 11; quiz_engine.py 9; stats.py 9; feedback.py 9). Opens use encoding="utf-8". No user-controlled path traversal for reads/writes in this code. Passwords are hashed before storage (auth.py 35–36, 55–56).

[PASS] Behavior vs spec — weighted vs uniform random. The spec describes random selection and a separate feedback module for “which questions to show next.” The app uses weighted sampling without replacement (feedback.py 61–81), which matches that design rather than pure uniform randomness.

Summary: AC1–AC5 and the three spec error behaviors are implemented as intended in the main paths. The main gaps are unhandled JSON errors on users.json / feedback.json, possible silent truncation of history when scores.dat is corrupt, weak validation of id types, and a small unused import.