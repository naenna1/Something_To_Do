import sqlite3

DB_PATH = "todo.db"

# Datenbankverbindung
def get_conn(db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")
    return con

# Datenbank initialisieren
def init_db(db_path=DB_PATH):
    con = get_conn(db_path)
    cur = con.cursor()

    # Users Tabelle
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users
        (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            alias           TEXT    NOT NULL UNIQUE,
            password_hash   TEXT    NOT NULL,
            is_admin        INTEGER NOT NULL DEFAULT 0,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked          INTEGER NOT NULL DEFAULT 0,
            created_at      TEXT    NOT NULL DEFAULT (DATE('now'))
        )
    """)

    # Category Tabelle
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category
        (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            description TEXT
        )
    """)

    # Task Tabelle
    cur.execute("""
        CREATE TABLE IF NOT EXISTS task
        (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT    NOT NULL,
            description   TEXT,
            creation_date TEXT    NOT NULL,
            completed     INTEGER NOT NULL CHECK (completed IN (0, 1)),
            due_date      TEXT,
            category_id   INTEGER,
            user_id       INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES category (id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    con.commit()
    con.close()