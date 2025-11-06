from db import get_conn
from auth import hash_pw

def admin_show_users():
    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT id, alias, locked, failed_attempts, is_admin FROM users ORDER BY id")
    rows = cur.fetchall()
    con.close()

    print("\n=== Users ===")
    for r in rows:
        status = []
        if r[4]: status.append("ADMIN")
        if r[2]: status.append("LOCKED")
        status_txt = " | ".join(status) if status else "-"
        print(f"{r[0]} | {r[1]} | {status_txt} | Fails: {r[3]}")
    print()

def admin_unlock_user(user_id):
    con= get_conn()
    cur = con.cursor()
    cur.execute("UPDATE users SET locked = 0, failed_attempts = 0 WHERE id = ?", (user_id,))
    con.commit()
    print("✅ User unlocked!")
    con.close()

def admin_reset_password(user_id, new_password):
    con= get_conn()
    cur = con.cursor()
    cur.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                (hash_pw(new_password), user_id))
    con.commit()
    print("✅ Password updated!")
    con.close()

def admin_handle_choice(choice):
    if choice.upper() == "A":
        admin_show_users()

    elif choice.upper() == "B":
        uid = input("User ID to unlock (0 = back): ").strip()
        if uid == "0": return
        try:
            admin_unlock_user(int(uid))
        except ValueError:
            print("Invalid ID.")

    elif choice.upper() == "C":
        uid = input("User ID to reset password (0 = back): ").strip()
        if uid == "0": return
        try:
            uid = int(uid)
        except ValueError:
            print("Invalid ID.")
            return
        new_pw = input("New password: ").strip()
        admin_reset_password(uid, new_pw)