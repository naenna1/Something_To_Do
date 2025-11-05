import sqlite3
from datetime import datetime
import bcrypt
from typing import TypedDict, Optional

class LoggedInUser(TypedDict):
    id: int
    alias: str
    is_admin: bool

logged_in_user: Optional[LoggedInUser] = None

DB_PATH = "todo.db"

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

# Kategorie erstellen
def add_category(name, description=""):
    if not name.strip():
        raise ValueError("Category cannot be empty.")

    con = get_conn(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        INSERT INTO category (name, description)
        VALUES (?, ?)
    """, (name.strip(), description.strip()))

    con.commit()
    con.close()
    print(f"Category '{name}' has been created.")


# Kategorie erstellen ( in 'Create task')
def get_or_create_category(name):
    if name is None or name.strip() == "":
        return None

    name = name.strip()
    con = get_conn(DB_PATH)
    cur = con.cursor()

    # Kategorie suchen
    cur.execute("SELECT id FROM category WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        con.close()
        return row[0]

    cur.execute("INSERT INTO category (name) VALUES (?)", (name,))
    con.commit()
    category_id = cur.lastrowid
    con.close()
    print(f"Category '{name}' has been created.")
    return category_id


# Kategorien anzeigen/auflisten
def list_categories():
    con = get_conn(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT id, name, description FROM category ORDER BY id")

    rows = cur.fetchall()
    con.close()

    if not rows:
        print(f"No categories found.")
    else:
        print("\n=== Categories ===")
        for row in rows:
            print(f"{row[0]}: {row[1]}", f"- {row[2]}" if row[2] else "")
        print()


# Kategorie löschen (NUR wenn sie leer ist!)
def delete_category(category_id):
    con = get_conn(DB_PATH)
    cur = con.cursor()

    # Prüfen, ob Aufgaben diese Kategorie nutzen
    cur.execute("SELECT COUNT(*) FROM task WHERE category_id = ?",
                (category_id,))
    count = cur.fetchone()[0]

    if count > 0:
        con.close()
        print(
            f"Category cannot be deleted! There are still {count} tasks associated with it.")
        return

    # Kategorie löschen, wenn sie nicht verwendet wird
    cur.execute("DELETE FROM category WHERE id = ?", (category_id,))
    con.commit()
    con.close()
    print(f"Category with ID {category_id} has been deleted.")


# Datum überprüfen
def check_date(date_text, field_name):
    if date_text is None or date_text == "":
        return None  # leer ist erlaubt (z. B. due_date)
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return date_text
    except ValueError:
        raise ValueError(f"{field_name} must be in the format YYYY-MM-DD (2025-11-03).")


# Aufgabe erstellen
def create_task(title, category_id, description, creation_date, completed,
                due_date, user_id, db_path=DB_PATH):
    if title is None or str(title).strip() == "":
        raise ValueError("'title' cannot be empty.")
    title = title.strip()

    if category_id is not None:
        try:
            category_id = int(category_id)
        except ValueError:
            raise ValueError("'category_id' must be a number or None.")

    try:
        datetime.strptime(creation_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("'creation_date' must be in the format YYYY-MM-DD.")

    if due_date is not None:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("'due_date' must be in the format YYYY-MM-DD or None.")

    if completed in (True, False):
        completed_val = 1 if completed else 0
    else:
        try:
            completed_val = int(completed)
        except ValueError:
            raise ValueError("'completed' must be 0/1 or True/False.")
        if completed_val not in (0, 1):
            raise ValueError("'completed' must be 0 or 1.")

    con = get_conn(db_path)
    cur = con.cursor()
    try:
        cur.execute("""
            INSERT INTO task (title, description, creation_date, completed, due_date, category_id, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, description, creation_date, completed_val, due_date, category_id, user_id))
        con.commit()
    finally:
        con.close()


# Aufgabenliste anzeigen lassen
def list_tasks(user_id, db_path=DB_PATH):
    con = get_conn(db_path)
    cur = con.cursor()
    cur.execute("""
                SELECT task.id,
                       task.title,
                       category.name,
                       task.description,
                       task.creation_date,
                       task.completed,
                       task.due_date
                FROM task
                         LEFT JOIN category ON task.category_id = category.id
                WHERE task.user_id = ?
                ORDER BY task.completed,
                         COALESCE(task.due_date, '9999-12-31'), task.id
                """, (user_id,))
    rows = cur.fetchall()
    con.close()

    if len(rows) == 0:
        print("\nNo tasks found.\n")
        return

    print("\n=== Task List ===")
    for r in rows:
        task_id = r[0]
        title = r[1]
        category_name = r[2]
        description = r[3]
        creation_date = r[4]
        completed = r[5]
        due_date = r[6]

        status = "Done" if completed == 1 else "Open"

        line = f"{task_id}: {title}"
        if category_name:
            line += f" [{category_name}]"
        line += f" - {status} (created: {creation_date})"
        if due_date:
            line += f" | due: {due_date}"
        print(line)

        if description:
            print("   Description:", description)
    print()


# Aufgaben löschen
def delete_task(task_id, user_id, db_path=DB_PATH):
    con = get_conn(db_path)
    cur = con.cursor()

    # Gehört die Aufgabe zum User?
    cur.execute("SELECT id FROM task WHERE id = ? AND user_id = ?",
                (task_id, user_id))
    if cur.fetchone() is None:
        con.close()
        print("You cannot delete tasks that are not yours.")
        return

    cur.execute("DELETE FROM task WHERE id = ? AND user_id = ?",
                (task_id, user_id))
    con.commit()
    con.close()
    print("Task deleted.")


# Erledigt Status anpassen
def complete_task(task_id, user_id, db_path=DB_PATH):
    con = get_conn(db_path)
    cur = con.cursor()

    cur.execute("UPDATE task SET completed = 1 WHERE id = ? AND user_id = ?",
                (task_id, user_id))
    con.commit()

    if cur.rowcount == 0:
        print("Task not found or not owned by you.")
    else:
        print("Task marked as completed.")

    con.close()


# Aufgaben aktualisieren
def update_task(task_id, user_id, title=None, category_id=None, description=None, due_date=None, db_path=DB_PATH):
    con = get_conn(db_path)
    cur = con.cursor()

    # Besitzer prüfen
    # noinspection SqlNoDataSourceInspection,SqlDialectInspection,SqlResolve
    cur.execute("SELECT id FROM task WHERE id = ? AND user_id = ?", (task_id, user_id))
    if cur.fetchone() is None:
        con.close()
        print("You cannot edit tasks that are not yours.")
        return

    updates, values = [], []

    if title is not None:
        updates.append("title = ?")
        values.append(title.strip())

    if category_id is not None:
        updates.append("category_id = ?")
        values.append(category_id)

    if description is not None:
        updates.append("description = ?")
        values.append(description.strip())

    if due_date is not None:
        # validieren:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print("Please enter the date in the format YYYY-MM-DD.")
            con.close()
            return
        updates.append("due_date = ?")
        values.append(due_date)

    if not updates:
        print("No changes applied.")
        con.close()
        return

    values.extend([task_id, user_id])

    sql = f"UPDATE task SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
    cur.execute(sql, values)
    con.commit()
    con.close()
    print(f"Task {task_id} has been updated.")

# Eingabe definieren/Fehler ausschließen
def input_nonempty(prompt):
    while True:
        val = input(prompt).strip()
        if val != "":
            return val
        print("Input cannot be empty.")


def input_date_or_empty(prompt):
    val = input(prompt + " (YYYY-MM-DD, empty = nothing, 0 = back to menu): ").strip()
    if is_back(val):
        return "BACK"
    if val == "":
        return None
    try:
        datetime.strptime(val, "%Y-%m-%d")
        return val
    except ValueError:
        print("Please enter the date in the format YYYY-MM-DD.")
        return input_date_or_empty(prompt)


def input_completed(prompt="Completed? (0/1 or true/false) "):
    val = input(prompt).strip().lower()
    if val in ("1", "true", "ja", "y"):
        return 1
    if val in ("0", "false", "nein", "n", ""):
        return 0
    print("Please enter 0/1 or true/false.")
    return input_completed(prompt)


def is_back(val):
    return val.strip() == "0"


# Passwort-Nutzung
def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8")


def check_pw(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# User-Registrierung
def register_user(alias: str, password: str, db_path=DB_PATH):
    if not alias.strip():
        print("Alias cannot be empty.")
        return
    if not password:
        print("Password cannot be empty.")
        return
    con = get_conn(db_path)
    cur = con.cursor()

    cur.execute("SELECT 1 FROM users WHERE alias = ?", (alias.strip(),))
    if cur.fetchone():
        print("Alias already exists.")
        con.close()
        return

    cur.execute("INSERT INTO users (alias, password_hash) VALUES (?, ?)",
                (alias.strip(), hash_pw(password)))
    con.commit()
    con.close()
    print(f"User '{alias}' registered.")


# User-Login
def login_user(db_path=DB_PATH):
    while True:
        print("\n=== Login ===")
        print("1) Sign in")
        print("2) Register")
        print("0) Exit")
        choice = input("Choice: ").strip()
        if choice == "0":
            return None
        if choice == "2":
            alias = input("Alias (0 = back): ").strip()
            if alias == "0":
                continue
            pw = input("Password (0 = back): ").strip()
            if pw == "0":
                continue
            register_user(alias, pw, db_path)
            continue

        if choice == "1":
            alias = input("Alias (0 = back): ").strip()
            if alias == "0":
                continue
            pw = input("Password (0 = back): ").strip()
            if pw == "0":
                continue

            con = get_conn(db_path)
            cur = con.cursor()
            cur.execute("""
                        SELECT id,
                               password_hash,
                               failed_attempts,
                               locked,
                               is_admin
                        FROM users
                        WHERE alias = ?
                        """, (alias,))
            row = cur.fetchone()
            if not row:
                print("Alias not found.")
                con.close()
                continue

            uid, pw_hash, fails, locked, is_admin = row
            if locked:
                print("Account is locked. Please contact admin.")
                con.close()
                continue

            if check_pw(pw, pw_hash):
                cur.execute(
                    "UPDATE users SET failed_attempts = 0 WHERE id = ?",
                    (uid,))
                con.commit()
                con.close()
                print(f"Welcome, {alias}!")
                return {"id": uid, "alias": alias, "is_admin": bool(is_admin)}
            else:
                fails += 1
                if fails >= 3:
                    cur.execute(
                        "UPDATE users SET locked = 1, failed_attempts = ? WHERE id = ?",
                        (fails, uid))
                    print("Too many failed attempts. Account is now locked.")
                else:
                    cur.execute(
                        "UPDATE users SET failed_attempts = ? WHERE id = ?",
                        (fails, uid))
                    print(f"Wrong password. Attempts left: {3 - fails}")
                con.commit()
                con.close()
                continue
        else:
            print("Please choose 0–2.")


# Admin-Verwaltungsaufgaben
def admin_show_users(db_path=DB_PATH):
    con = get_conn(db_path)
    cur = con.cursor()
    cur.execute(
        "SELECT id, alias, locked, failed_attempts, is_admin FROM users ORDER BY id")
    rows = cur.fetchall()
    con.close()

    print("\n=== Users ===")
    for r in rows:
        status = []
        if r[4]:
            status.append("ADMIN")
        if r[2]:
            status.append("LOCKED")
        status_txt = " | ".join(status) if status else "-"
        print(f"{r[0]} | {r[1]} | {status_txt} | Fails: {r[3]}")
    print()


def admin_unlock_user(user_id, db_path=DB_PATH):
    con = get_conn(db_path)
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET locked = 0, failed_attempts = 0 WHERE id = ?",
        (user_id,))
    con.commit()
    con.close()
    print("✅ User unlocked!")


def admin_reset_password(user_id, new_password, db_path=DB_PATH):
    if not new_password.strip():
        print("Password cannot be empty.")
        return
    con = get_conn(db_path)
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (hash_pw(new_password), user_id)
    )
    con.commit()
    con.close()
    print("Password updated!")


def show_my_profile(db_path=DB_PATH):
    if not logged_in_user:
        print("Please login first.")
        return
    user = logged_in_user
    assert user is not None
    uid = user['id']

    con = get_conn(db_path)
    cur = con.cursor()

    # User-Info
    cur.execute("""
        SELECT alias, is_admin, locked, failed_attempts, created_at
        FROM users
        WHERE id = ?
    """, (uid,))
    row = cur.fetchone()

    # Task Statistik
    cur.execute("""
        SELECT SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END) AS open_cnt,
               SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) AS done_cnt
        FROM task
        WHERE user_id = ?
    """, (uid,))
    tstats = cur.fetchone()
    con.close()

    if not row:
        print("User not found.")
        return

    alias, is_admin, locked, fails, created_at = row
    open_cnt = tstats[0] or 0
    done_cnt = tstats[1] or 0

    print("\n=== My Profile ===")
    print(f"Alias:         {alias}")
    print(f"Role:          {'ADMIN' if is_admin else 'User'}")
    print(f"Locked:        {'Yes' if locked else 'No'}")
    print(f"Failed tries:  {fails}")
    print(f"Created at:    {created_at}")
    print(f"Tasks:         {open_cnt} open / {done_cnt} done")
    print()


def change_alias(db_path=DB_PATH):
    global logged_in_user
    if not logged_in_user:
        print("Please login first.")
        return
    user = logged_in_user
    assert user is not None

    new_alias = input("New alias (0 = back): ").strip()
    if is_back(new_alias):
        return
    if new_alias == "":
        print("Alias cannot be empty.")
        return

    con = get_conn(db_path)
    cur = con.cursor()

    # unique?
    cur.execute("SELECT 1 FROM users WHERE alias = ?", (new_alias,))
    if cur.fetchone():
        con.close()
        print("Alias already exists.")
        return

    cur.execute("UPDATE users SET alias = ? WHERE id = ?", (new_alias, user['id']))
    con.commit()
    con.close()

    logged_in_user = {**user, "alias": new_alias}
    print("Alias updated.")


def change_password(db_path=DB_PATH):
    if not logged_in_user:
        print("Please login first.")
        return
    user = logged_in_user
    assert user is not None

    current = input("Current password (0 = back): ").strip()
    if is_back(current):
        return

    con = get_conn(db_path)
    cur = con.cursor()
    cur.execute("SELECT password_hash FROM users WHERE id = ?", (user['id'],))
    row = cur.fetchone()
    if not row:
        con.close()
        print("User not found.")
        return
    if not check_pw(current, row[0]):
        con.close()
        print("Wrong current password.")
        return

    new1 = input("New password: ").strip()
    new2 = input("Repeat new password: ").strip()
    if new1 == "" or new2 == "":
        con.close()
        print("Password cannot be empty.")
        return
    if new1 != new2:
        con.close()
        print("Passwords do not match.")
        return

    cur.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_pw(new1), user['id']))
    con.commit()
    con.close()
    print("Password updated.")


def delete_own_account(db_path=DB_PATH):
    global logged_in_user
    if not logged_in_user:
        print("Please login first.")
        return
    user = logged_in_user
    assert user is not None

    print("\nThis will permanently delete your account and your tasks.")
    confirm = input("Type DELETE to confirm (0 = back): ").strip()
    if is_back(confirm):
        print("Canceled.")
        return
    if confirm != "DELETE":
        print("Confirmation failed. Canceled.")
        return

    pw = input("Enter your password to confirm: ").strip()
    con = get_conn(db_path)
    cur = con.cursor()
    cur.execute("SELECT password_hash FROM users WHERE id = ?", (user['id'],))
    row = cur.fetchone()
    if not row or not check_pw(pw, row[0]):
        con.close()
        print("Password check failed. Canceled.")
        return

    cur.execute("DELETE FROM users WHERE id = ?", (user['id'],))
    con.commit()
    con.close()

    logged_in_user = None
    print("Your account has been deleted. Goodbye!")


# Profil-Optionen
def profile_menu():
    while True:
        if not logged_in_user:
            print("Please login first.")
            return

        print("\n=== Profile Menu ===")
        print(f"Logged in as: {logged_in_user['alias']}")
        print("1) Show my profile")
        print("2) Change alias")
        print("3) Change password")
        print("4) Delete my account")
        print("0) Back")

        choice = input("Choice: ").strip()

        if choice == "1":
            show_my_profile()
        elif choice == "2":
            change_alias()
        elif choice == "3":
            change_password()
        elif choice == "4":
            delete_own_account()
            # If user deleted themselves, kick back to main
            if not logged_in_user:
                return
        elif choice == "0":
            return
        else:
            print("Invalid option.\n")


## MENÜ ##
def main_menu():
    global logged_in_user  # ← wegen Zuweisungen in "8" und "9" nach oben

    while True:
        print("\n===== SOMETHING TO-DO =====")
        print("Logged in as:",
              logged_in_user['alias'] if logged_in_user else "Nobody")

        print("\n--- Main Menu ---")
        print("1) Create task")
        print("2) Show tasks")
        print("3) Mark task as completed")
        print("4) Delete task")
        print("5) Update task")
        print("6) Create category")
        print("7) Show categories")
        print("8) Login / Switch user")
        print("9) Logout")
        print("10) Register new user")
        print("11) Profile")

        # Admin-Menü
        if logged_in_user and logged_in_user['is_admin']:
            print("\n--- Admin Menu ---")
            print("A) Show user list")
            print("B) Unlock account")
            print("C) Reset user password")

        print("0) Exit")

        choice = input("Choice: ").strip()

        # Ohne Login nichts aus 1–5
        if choice in ["1", "2", "3", "4", "5"] and not logged_in_user:
            print("Please login first!\n")
            continue

        if choice == "1":
            try:
                if not logged_in_user:
                    print("Please login first!\n")
                    continue
                user = logged_in_user
                assert user is not None

                title = input("Title (0 = back): ").strip()
                if is_back(title):
                    continue
                if title == "":
                    print("Title cannot be empty.")
                    continue

                category_name = input("Category name (0 = back): ").strip()
                if is_back(category_name):
                    continue
                category_id = get_or_create_category(category_name) if category_name else None

                description = input("Description (optional): ").strip() or None
                creation_date = datetime.now().strftime("%Y-%m-%d")
                completed = 0
                due_date = input_date_or_empty("Due on")
                if due_date == "BACK":
                    continue

                create_task(title, category_id, description, creation_date,
                            completed, due_date, user['id'])
                print("Task saved!\n")

            except ValueError as e:
                # konkret nur Eingabefehler abfangen
                print("Error:", e)

        elif choice == "2":
            if not logged_in_user:
                print("Please login first!\n")
                continue
            user = logged_in_user
            assert user is not None
            list_tasks(user['id'])

        elif choice == "3":
            if not logged_in_user:
                print("Please login first!\n")
                continue
            user = logged_in_user
            assert user is not None
            task = input("Task ID (0 = back): ").strip()
            if is_back(task):
                continue
            try:
                task_id = int(task)
            except ValueError:
                print("Invalid ID.")
                continue
            complete_task(task_id, user['id'])

        elif choice == "4":
            if not logged_in_user:
                print("Please login first!\n")
                continue
            user = logged_in_user
            assert user is not None
            task = input("Task ID (0 = back): ").strip()
            if is_back(task):
                continue
            try:
                task_id = int(task)
            except ValueError:
                print("Invalid ID.")
                continue
            delete_task(task_id, user['id'])

        elif choice == "5":
            if not logged_in_user:
                print("Please login first!\n")
                continue
            user = logged_in_user
            assert user is not None
            task = input("Task ID (0 = back): ").strip()
            if is_back(task):
                continue
            try:
                task_id = int(task)
            except ValueError:
                print("Invalid ID.")
                continue

            new_title = input("New title (empty = unchanged): ").strip() or None
            new_category_name = input("New category name (empty = unchanged): ").strip()
            new_category = get_or_create_category(new_category_name) if new_category_name else None
            new_description = input("New description (empty = unchanged): ").strip() or None
            new_due_date = input_date_or_empty("New due date")
            if new_due_date == "BACK":
                continue

            update_task(task_id, user['id'], new_title, new_category,
                        new_description, new_due_date)

        elif choice == "6":
            name = input("Category name: ").strip()
            if name == "":
                continue
            add_category(name)

        elif choice == "7":
            list_categories()

        elif choice == "8":
            logged_in_user = login_user()
            if logged_in_user:
                print(f"Logged in as {logged_in_user['alias']}.\n")

        elif choice == "9":
            logged_in_user = None
            print("Logged out.\n")

        elif choice == "10":
            alias = input("New Alias: ").strip()
            if is_back(alias):
                continue
            pw = input("New Password: ").strip()
            if is_back(pw):
                continue
            register_user(alias, pw)

        elif choice == "11":
            profile_menu()
            continue

        elif choice == "0":
            print("Goodbye!")
            break

        # Admin-Menü-Aktionen (nur wenn Admin und A/B/C gewählt)
        elif logged_in_user and logged_in_user['is_admin'] and choice.upper() in ("A", "B", "C"):
            if choice.upper() == "A":
                admin_show_users()
            elif choice.upper() == "B":
                uid = input("User ID to unlock (0 = back): ").strip()
                if is_back(uid):
                    continue
                try:
                    admin_unlock_user(int(uid))
                except ValueError:
                    print("Invalid ID.")
                    continue
            elif choice.upper() == "C":
                uid = input("User ID to reset password (0 = back): ").strip()
                if is_back(uid):
                    continue
                try:
                    uid_int = int(uid)
                except ValueError:
                    print("Invalid ID.")
                    continue
                new_pw = input("New password: ").strip()
                admin_reset_password(uid_int, new_pw)
            continue

        else:
            print("Please enter a valid option.\n")

## Start des Programms ##
if __name__ == "__main__":
    init_db()  # DB + Tabelle anlegen (falls noch nicht vorhanden)
    main_menu()  # Menü starten
