import os
import sqlite3
import bcrypt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "todo.db")


def _hash_pw(plain: str) -> str:
    """Lokale Passwort-Hash Funktion (vermeidet Zirkularimport mit auth.py)."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def get_conn(db_path=DB_PATH):
    return sqlite3.connect(db_path)


def init_db(db_path=DB_PATH):
    con = get_conn(db_path)
    cur = con.cursor()

    # Tabellen erstellen
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            locked INTEGER NOT NULL DEFAULT 0,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            creation_date DATE NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            due_date DATE,
            category_id INTEGER,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES category(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    # Bootstrap Admin ggf. anlegen
    ensure_bootstrap_admin(cur)

    con.commit()
    con.close()


def ensure_bootstrap_admin(cur):
    """Legt Standard-Admin an, wenn keine User existieren."""
    if os.getenv("AUTO_BOOTSTRAP_ADMIN", "1") != "1":
        return

    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    if count > 0:
        return

    alias = os.getenv("BOOTSTRAP_ALIAS", "admin")
    pw = os.getenv("BOOTSTRAP_PASSWORD", "admin")

    cur.execute("""
        INSERT INTO users (alias, password_hash, is_admin, locked, failed_attempts)
        VALUES (?, ?, 1, 0, 0)
    """, (alias, _hash_pw(pw)))

    print(f"✅ Bootstrap-Admin angelegt: alias='{alias}', password='{pw}'")
