from db import get_conn, DB_PATH
from auth import logged_in_user, check_pw, hash_pw
from utils import is_back

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
