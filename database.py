
import sqlite3
import hashlib
import secrets
import hmac
import re
from pathlib import Path

# Database file is created automatically beside this Python file
DB_PATH = Path(__file__).resolve().parent / "skillpath.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

# =========================================================
# SKILLFORGE XP - PERMANENT DATABASE STORAGE
# =========================================================

def get_skillforge_xp(user_id):
    """Load one student's XP data from the existing database."""
    import json

    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO skillforge_xp (user_id)
            VALUES (?)
        """, (user_id,))

        row = conn.execute("""
            SELECT xp, completed, history, last_claim_date, streak
            FROM skillforge_xp
            WHERE user_id = ?
        """, (user_id,)).fetchone()

    return {
        "xp": row["xp"],
        "completed": json.loads(row["completed"]),
        "history": json.loads(row["history"]),
        "last_claim_date": row["last_claim_date"],
        "streak": row["streak"]
    }


def save_skillforge_xp(user_id, data):
    """Save one student's XP data without affecting other tables."""
    import json

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO skillforge_xp (
                user_id, xp, completed, history,
                last_claim_date, streak
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                xp = excluded.xp,
                completed = excluded.completed,
                history = excluded.history,
                last_claim_date = excluded.last_claim_date,
                streak = excluded.streak
        """, (
            user_id,
            int(data.get("xp", 0)),
            json.dumps(data.get("completed", [])),
            json.dumps(data.get("history", [])),
            data.get("last_claim_date"),
            int(data.get("streak", 0))
        ))

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                college TEXT NOT NULL,
                branch TEXT NOT NULL,
                year TEXT NOT NULL,
                phone TEXT DEFAULT '',
                interests TEXT DEFAULT '',
                skills TEXT DEFAULT '',
                certifications TEXT DEFAULT '',
                projects TEXT DEFAULT '',
                resume_link TEXT DEFAULT '',
                github_url TEXT DEFAULT '',
                linkedin_url TEXT DEFAULT '',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS skillforge_xp (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER NOT NULL DEFAULT 0,
                completed TEXT NOT NULL DEFAULT '[]',
                history TEXT NOT NULL DEFAULT '[]',
                last_claim_date TEXT,
                streak INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

def validate_email(email):
    email = email.strip().lower()
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.fullmatch(pattern, email))


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200_000
    ).hex()


def register_user(email, password):
    email = email.strip().lower()

    if not validate_email(email):
        return False, "Enter a valid email address.", None

    if len(password) < 8 or not any(c.isalpha() for c in password) \
            or not any(c.isdigit() for c in password):
        return (
            False,
            "Password must have at least 8 characters, including a letter and a number.",
            None
        )

    salt = secrets.token_bytes(16).hex()
    password_hash = hash_password(password, salt)

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO users (email, password_hash, salt)
                   VALUES (?, ?, ?)""",
                (email, password_hash, salt)
            )
            user_id = cursor.lastrowid

        return True, "Account created successfully.", user_id

    except sqlite3.IntegrityError:
        return False, "This email already has an account. Please log in.", None


def verify_login(email, password):
    email = email.strip().lower()

    with get_connection() as conn:
        user = conn.execute(
            "SELECT id, password_hash, salt FROM users WHERE email = ?",
            (email,)
        ).fetchone()

    if user is None:
        return None

    entered_hash = hash_password(password, user["salt"])

    if hmac.compare_digest(entered_hash, user["password_hash"]):
        return user["id"]

    return None


def get_profile(user_id):
    with get_connection() as conn:
        profile = conn.execute(
            "SELECT * FROM profiles WHERE user_id = ?",
            (user_id,)
        ).fetchone()

    return dict(profile) if profile else None


def save_profile(user_id, data):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO profiles (
                user_id, full_name, college, branch, year, phone,
                interests, skills, certifications, projects,
                resume_link, github_url, linkedin_url, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name = excluded.full_name,
                college = excluded.college,
                branch = excluded.branch,
                year = excluded.year,
                phone = excluded.phone,
                interests = excluded.interests,
                skills = excluded.skills,
                certifications = excluded.certifications,
                projects = excluded.projects,
                resume_link = excluded.resume_link,
                github_url = excluded.github_url,
                linkedin_url = excluded.linkedin_url,
                updated_at = CURRENT_TIMESTAMP
        """, (
            user_id,
            data["full_name"],
            data["college"],
            data["branch"],
            data["year"],
            data.get("phone", ""),
            data.get("interests", ""),
            data.get("skills", ""),
            data.get("certifications", ""),
            data.get("projects", ""),
            data.get("resume_link", ""),
            data.get("github_url", ""),
            data.get("linkedin_url", "")
        ))

def ensure_career_goals_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS career_goals (
                user_id INTEGER PRIMARY KEY,
                target_career TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)


def get_career_goal(user_id):
    ensure_career_goals_table()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT target_career FROM career_goals WHERE user_id = ?",
            (user_id,)
        ).fetchone()

    return row["target_career"] if row else None


def save_career_goal(user_id, target_career):
    ensure_career_goals_table()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO career_goals (user_id, target_career)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                target_career = excluded.target_career,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, target_career))

def init_career_goals_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS career_goals (
                user_id INTEGER PRIMARY KEY,
                career_goal TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)


def get_career_goal(user_id):
    init_career_goals_table()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT career_goal FROM career_goals WHERE user_id = ?",
            (user_id,)
        ).fetchone()

    return row["career_goal"] if row else None


def save_career_goal(user_id, career_goal):
    init_career_goals_table()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO career_goals (user_id, career_goal)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                career_goal = excluded.career_goal,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, career_goal))

def init_assessments_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assessment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                career_goal TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                attempted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)


def save_assessment(user_id, career_goal, score, total, answers_json):
    init_assessments_table()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO assessment_history (
                user_id, career_goal, score,
                total_questions, answers_json
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id, career_goal, score, total, answers_json
        ))


def get_assessment_history(user_id):
    init_assessments_table()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT career_goal, score, total_questions, attempted_at
            FROM assessment_history
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)).fetchall()

    return [dict(row) for row in rows]

import json


def init_assessments_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assessment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                career_goal TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                attempted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)


def save_assessment(user_id, career_goal, score, total, answers_json):
    init_assessments_table()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO assessment_history (
                user_id, career_goal, score,
                total_questions, answers_json
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id, career_goal, score, total, answers_json
        ))


def get_assessment_history(user_id):
    init_assessments_table()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT career_goal, score, total_questions, attempted_at
            FROM assessment_history
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)).fetchall()

    return [dict(row) for row in rows]

import json


def init_assessments_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assessment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                career_goal TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                attempted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)


def save_assessment(user_id, career_goal, score, total, answers_json):
    init_assessments_table()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO assessment_history (
                user_id, career_goal, score,
                total_questions, answers_json
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id, career_goal, score, total, answers_json
        ))


def get_assessment_history(user_id):
    init_assessments_table()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT career_goal, score, total_questions, attempted_at
            FROM assessment_history
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)).fetchall()

    return [dict(row) for row in rows]

import json


def init_assessments_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assessment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                career_goal TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                attempted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)


def save_assessment(user_id, career_goal, score, total, answers_json):
    init_assessments_table()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO assessment_history (
                user_id, career_goal, score,
                total_questions, answers_json
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id, career_goal, score, total, answers_json
        ))


def get_assessment_history(user_id):
    init_assessments_table()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT career_goal, score, total_questions, attempted_at
            FROM assessment_history
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)).fetchall()

    return [dict(row) for row in rows]
