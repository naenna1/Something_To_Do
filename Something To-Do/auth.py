import sqlite3
import bcrypt
from db import DB_PATH

# interner Login-Status NUR hier halten
_logged_in_user = None  # Dict wie {"id": 1, "alias": "Max", "is_admin": 0}

def get_logged_in_user():
# Gibt den aktuell eingeloggten Benutzer (dict) oder None zurück.
    return _logged_in_user

def set_logged_in_user(user_or_none):
# Setzt den aktuell eingeloggten Benutzer (dict) oder None.
    global _logged_in_user
    _logged_in_user = user_or_none

def logout_user():
# Loggt den aktuellen Benutzer aus.
    set_logged_in_user(None)

# Passwort-Helfer
def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_pw(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

# Registrierung
def register_user(alias: str, password: str, db_path=DB_PATH):
    if not alias.strip():
        print("Alias cannot be empty.")
        return
    if not password:
        print("Password cannot be empty.")
        return
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM users WHERE alias = ?", (alias.strip(),))
    if cur.fetchone():
        print("Alias already exists.")
        con.close()
        return
    cur.execute(
        "INSERT INTO users (alias, password_hash) VALUES (?, ?)",
        (alias.strip(), hash_pw(password))
    )
    con.commit()
    con.close()
    print(f"User '{alias}' registered.")

# Login mit Menü (Sign in / Register / Exit)
def login_user(db_path=DB_PATH):
    while True:
        print("\n=== Login ===")
        print("1) Sign in")
        print("2) Register")
        print("0) Exit")
        choice = input("Choice: ").strip()

        if choice == "0":
            return None  # kein Login-Versuch / zurück

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

            con = sqlite3.connect(db_path)
            cur = con.cursor()
            cur.execute("""
                SELECT id, password_hash, failed_attempts, locked, is_admin
                FROM users WHERE alias = ?
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
                cur.execute("UPDATE users SET failed_attempts = 0 WHERE id = ?", (uid,))
                con.commit()
                con.close()
                user_dict = {"id": uid, "alias": alias, "is_admin": int(is_admin)}
                set_logged_in_user(user_dict)
                print(f"Welcome, {alias}!")
                return user_dict
            else:
                fails += 1
                if fails >= 3:
                    cur.execute("UPDATE users SET locked = 1, failed_attempts = ? WHERE id = ?", (fails, uid))
                    print("Too many failed attempts. Account is now locked.")
                else:
                    cur.execute("UPDATE users SET failed_attempts = ? WHERE id = ?", (fails, uid))
                    print(f"Wrong password. Attempts left: {3 - fails}")
                con.commit()
                con.close()
                continue

        else:
            print("Please choose 0–2.")

#------------------------------------------
# GUI-Login
def authenticate(alias: str, password: str, db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""
        SELECT id, password_hash, failed_attempts, locked, is_admin
        FROM users WHERE alias = ?
    """, (alias,))
    row = cur.fetchone()

    if not row:
        con.close()
        return None

    uid, pw_hash, fails, locked, is_admin = row

    if locked:
        con.close()
        return None

    if check_pw(password, pw_hash):
        # Login zählt als Erfolg → Fehlversuche zurücksetzen
        cur.execute("UPDATE users SET failed_attempts = 0 WHERE id = ?", (uid,))
        con.commit()
        con.close()
        user = {"id": uid, "alias": alias, "is_admin": int(is_admin)}
        set_logged_in_user(user)
        return user
    else:
        fails += 1
        if fails >= 3:
            cur.execute("UPDATE users SET locked = 1, failed_attempts = ? WHERE id = ?", (fails, uid))
        else:
            cur.execute("UPDATE users SET failed_attempts = ? WHERE id = ?", (fails, uid))
        con.commit()
        con.close()
        return None