
import sqlite3
import json
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
    """Create or safely reuse either historical career-goal schema."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS career_goals (
                user_id INTEGER PRIMARY KEY,
                career_goal TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(career_goals)").fetchall()}
        if "career_goal" not in columns and "target_career" not in columns:
            conn.execute("ALTER TABLE career_goals ADD COLUMN career_goal TEXT")
        elif "career_goal" not in columns:
            conn.execute("ALTER TABLE career_goals ADD COLUMN career_goal TEXT")
            conn.execute("UPDATE career_goals SET career_goal=target_career WHERE career_goal IS NULL")
        elif "target_career" in columns:
            conn.execute("UPDATE career_goals SET career_goal=target_career WHERE (career_goal IS NULL OR career_goal='') AND target_career IS NOT NULL")


def get_career_goal(user_id):
    ensure_career_goals_table()
    with get_connection() as conn:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(career_goals)").fetchall()}
        column = "career_goal" if "career_goal" in columns else "target_career"
        row = conn.execute(
            f"SELECT {column} AS career_goal FROM career_goals WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return row["career_goal"] if row and row["career_goal"] else None


def save_career_goal(user_id, target_career):
    ensure_career_goals_table()
    with get_connection() as conn:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(career_goals)").fetchall()}
        if "career_goal" in columns and "target_career" in columns:
            conn.execute("""
                INSERT INTO career_goals (user_id, career_goal, target_career)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    career_goal=excluded.career_goal,
                    target_career=excluded.target_career,
                    updated_at=CURRENT_TIMESTAMP
            """, (user_id, target_career, target_career))
        else:
            column = "career_goal" if "career_goal" in columns else "target_career"
            conn.execute(
                f"INSERT INTO career_goals (user_id, {column}) VALUES (?, ?) "
                f"ON CONFLICT(user_id) DO UPDATE SET {column}=excluded.{column}, "
                "updated_at=CURRENT_TIMESTAMP",
                (user_id, target_career)
            )


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
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)


def save_assessment(user_id, career_goal, score, total, answers_json):
    init_assessments_table()
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO assessment_history (
                user_id, career_goal, score, total_questions, answers_json
            ) VALUES (?, ?, ?, ?, ?)
        """, (user_id, career_goal, score, total, answers_json))


def get_assessment_history(user_id):
    init_assessments_table()
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT career_goal, score, total_questions, attempted_at
            FROM assessment_history
            WHERE user_id = ? ORDER BY id DESC
        """, (user_id,)).fetchall()
    return [dict(row) for row in rows]


# =========================================================
# CAREER AGENT: MISSIONS, EVIDENCE, MISTAKE MEMORY AND CHAT
# =========================================================

def init_agent_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                career_goal TEXT NOT NULL,
                skill TEXT NOT NULL,
                title TEXT NOT NULL,
                instructions TEXT NOT NULL,
                rubric_json TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'assigned',
                attempts INTEGER NOT NULL DEFAULT 0,
                last_feedback TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mission_id INTEGER,
                event_type TEXT NOT NULL,
                skill TEXT DEFAULT '',
                submission TEXT DEFAULT '',
                score INTEGER DEFAULT 0,
                feedback TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (mission_id) REFERENCES agent_missions(id) ON DELETE SET NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS skill_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                career_goal TEXT NOT NULL,
                skill TEXT NOT NULL,
                evidence_level TEXT NOT NULL,
                evidence_source TEXT NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)


def get_current_agent_mission(user_id):
    init_agent_tables()
    with get_connection() as conn:
        row = conn.execute("""
            SELECT * FROM agent_missions
            WHERE user_id=? AND status IN ('assigned', 'completed')
            ORDER BY id DESC LIMIT 1
        """, (user_id,)).fetchone()
    if not row:
        return None
    import json
    item = dict(row)
    try:
        item["rubric"] = json.loads(item.pop("rubric_json"))
    except (TypeError, ValueError):
        item["rubric"] = []
    return item


def create_agent_mission(user_id, career_goal, skill, title, instructions, rubric):
    import json
    init_agent_tables()
    with get_connection() as conn:
        conn.execute("UPDATE agent_missions SET status='superseded', updated_at=CURRENT_TIMESTAMP WHERE user_id=? AND status='assigned'", (user_id,))
        cur = conn.execute("""
            INSERT INTO agent_missions (user_id, career_goal, skill, title, instructions, rubric_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, career_goal, skill, title, instructions, json.dumps(rubric)))
        mission_id = cur.lastrowid
        conn.execute("""
            INSERT INTO agent_events (user_id, mission_id, event_type, skill, feedback)
            VALUES (?, ?, 'mission_assigned', ?, ?)
        """, (user_id, mission_id, skill, title))
    return mission_id


def record_agent_attempt(user_id, mission_id, skill, submission, score, feedback, evidence_level):
    init_agent_tables()
    with get_connection() as conn:
        conn.execute("""
            UPDATE agent_missions SET attempts=attempts+1, last_feedback=?,
                status=?, updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?
        """, (feedback, "completed" if int(score) >= 60 else "assigned", mission_id, user_id))
        conn.execute("""
            INSERT INTO agent_events (user_id, mission_id, event_type, skill, submission, score, feedback)
            VALUES (?, ?, 'mission_attempt', ?, ?, ?, ?)
        """, (user_id, mission_id, skill, submission[:12000], int(score), feedback[:4000]))
        conn.execute("""
            INSERT INTO skill_evidence (user_id, career_goal, skill, evidence_level, evidence_source, score, notes)
            SELECT user_id, career_goal, skill, ?, 'Career Mission', ?, ?
            FROM agent_missions WHERE id=? AND user_id=?
        """, (evidence_level, int(score), feedback[:2000], mission_id, user_id))


def get_agent_summary(user_id):
    init_agent_tables()
    with get_connection() as conn:
        events = conn.execute("SELECT event_type, skill, score, feedback, created_at FROM agent_events WHERE user_id=? ORDER BY id DESC LIMIT 30", (user_id,)).fetchall()
        evidence = conn.execute("SELECT skill, evidence_level, evidence_source, score, notes, created_at FROM skill_evidence WHERE user_id=? ORDER BY id DESC LIMIT 50", (user_id,)).fetchall()
        missions = conn.execute("SELECT COUNT(*) AS total, SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) AS completed FROM agent_missions WHERE user_id=?", (user_id,)).fetchone()
    return {
        "events": [dict(row) for row in events],
        "evidence": [dict(row) for row in evidence],
        "missions_total": int(missions["total"] or 0),
        "missions_completed": int(missions["completed"] or 0)
    }


def save_agent_chat(user_id, role, message):
    init_agent_tables()
    with get_connection() as conn:
        conn.execute("INSERT INTO agent_chat_history (user_id, role, message) VALUES (?, ?, ?)", (user_id, role, message[:12000]))


def get_agent_chat(user_id, limit=12):
    init_agent_tables()
    with get_connection() as conn:
        rows = conn.execute("SELECT role, message FROM agent_chat_history WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, int(limit))).fetchall()
    return [dict(row) for row in reversed(rows)]


def init_agent_tables():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS agent_missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                career_goal TEXT,
                skill TEXT,
                title TEXT,
                instructions TEXT,
                rubric TEXT,
                status TEXT DEFAULT 'assigned',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS agent_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mission_id INTEGER,
                skill TEXT,
                score INTEGER,
                evidence_level TEXT,
                notes TEXT,
                evidence_source TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS agent_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT,
                skill TEXT,
                feedback TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS agent_chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT,
                message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)


def get_agent_summary(user_id):
    init_agent_tables()
    with get_connection() as conn:
        missions = conn.execute(
            "SELECT COUNT(*) FROM agent_missions WHERE user_id=? AND status='completed'",
            (user_id,)
        ).fetchone()[0]
        evidence = conn.execute(
            "SELECT * FROM agent_evidence WHERE user_id=? ORDER BY id DESC",
            (user_id,)
        ).fetchall()
        events = conn.execute(
            "SELECT * FROM agent_events WHERE user_id=? ORDER BY id DESC",
            (user_id,)
        ).fetchall()
    return {
        "missions_completed": missions,
        "evidence": [dict(r) for r in evidence],
        "events": [dict(r) for r in events]
    }


def get_current_agent_mission(user_id):
    init_agent_tables()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM agent_missions WHERE user_id=? AND status='assigned' ORDER BY id DESC LIMIT 1",
            (user_id,)
        ).fetchone()
    if not row:
        return None
    mission = dict(row)
    import json
    try:
        mission["rubric"] = json.loads(mission.get("rubric") or "[]")
    except (ValueError, TypeError):
        mission["rubric"] = []
    return mission


def create_agent_mission(user_id, career_goal, skill, title, instructions, rubric):
    init_agent_tables()
    import json
    with get_connection() as conn:
        conn.execute(
            "UPDATE agent_missions SET status='archived' WHERE user_id=? AND status='assigned'",
            (user_id,)
        )
        conn.execute("""
            INSERT INTO agent_missions
            (user_id, career_goal, skill, title, instructions, rubric)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, career_goal, skill, title, instructions, json.dumps(rubric)))


def record_agent_attempt(user_id, mission_id, skill, submission, score, feedback, level):
    init_agent_tables()
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO agent_evidence
            (user_id, mission_id, skill, score, evidence_level, notes, evidence_source)
            VALUES (?, ?, ?, ?, ?, ?, 'Career Agent Mission')
        """, (user_id, mission_id, skill, score, level, submission))
        conn.execute("""
            INSERT INTO agent_events (user_id, event_type, skill, feedback)
            VALUES (?, 'mission_attempt', ?, ?)
        """, (user_id, skill, feedback))
        if score >= 70:
            conn.execute(
                "UPDATE agent_missions SET status='completed' WHERE id=? AND user_id=?",
                (mission_id, user_id)
            )


def save_agent_chat(user_id, role, message):
    init_agent_tables()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO agent_chats (user_id, role, message) VALUES (?, ?, ?)",
            (user_id, role, message)
        )


def get_agent_chat(user_id, limit=10):
    init_agent_tables()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, message FROM agent_chats WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
    return [dict(r) for r in reversed(rows)]
