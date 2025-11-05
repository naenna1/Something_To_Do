import sqlite3
import pandas as pd
import bcrypt

conn = sqlite3.connect('todo_test.db')
cursor = conn.cursor()

# welcome
def welcome():
    while True:
        print("\n=== Welcome to ToDo System ===")
        print("1️ - Login")
        print("2️ - Register")

        choice = input("Please choose: ").strip()

        if choice == "1":
            alias = input("Alias: ").strip()
            pw = input("Password: ").strip()
            user = login(alias, pw)
            if user:
                main_menu(user)

        elif choice == "2":
            first = input("First name: ").strip()
            last = input("Last name: ").strip()
            alias = input("Alias: ").strip()
            pw = input("Password: ").strip()
            register_user(first, last, alias, pw)

        else:
            print("Invalid option!")


# user register
def register_user(first_name, last_name, alias, plain_password, is_admin=False):
    cursor.execute("SELECT alias FROM users WHERE alias=?", (alias,))
    if cursor.fetchone():
        print(f'{alias} exists already!')
        return
    hashed_pw = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("""
        INSERT INTO users (first_name, last_name, alias, password, is_admin)
        VALUES (?, ?, ?, ?, ?)
    """, (first_name, last_name, alias, hashed_pw, is_admin))
    conn.commit()
    print(f'{alias} has been registered successfully!')

# login, with password check and freeze by 3 wrong tries
def login(alias, plain_password):
    cursor.execute("""
        SELECT user_id, password, failed_attempts, freezed, is_admin
        FROM users WHERE alias=?
    """, (alias,))
    user = cursor.fetchone()

    if not user:
        print(f'{alias} does not exist!')
        return False

    user_id, stored_hash, failed_attempts, freezed, is_admin = user

    if freezed:
        print('This account is blocked! Please contact admin!')
        return False

    if bcrypt.checkpw(plain_password.encode('utf-8'), stored_hash.encode('utf-8')):
        cursor.execute("UPDATE users SET failed_attempts=0 WHERE user_id=?", (user_id,))
        conn.commit()
        print(f'Welcome back, {alias}!')

        return {
            "user_id": user_id,
            "alias": alias,
            "is_admin": bool(is_admin),
        }
    else:
        failed_attempts += 1
        if failed_attempts >= 3:
            cursor.execute("UPDATE users SET freezed=1, failed_attempts=? WHERE user_id=?", (failed_attempts, user_id))
            print(f'You have given incorrect password for three times. The account of {alias} has been blocked!')
        else:
            cursor.execute("UPDATE users SET failed_attempts=? WHERE user_id=?", (failed_attempts, user_id))
            print(f'Wrong password! You have (3 - {failed_attempts}) times left!')
        conn.commit()
        return False

# main menu
def main_menu(user):
    if not user:
        print('Login Failed!')
        return

    print(f"\n Welcome back, {user['alias']}!")

    while True:
        print('\n Main menu')
        print('1 - personal information\n')
        print('2️ - my todos\n')
        if user['is_admin']:
            print('️3 - user management\n')
        print('0️ - logout\n')

        choice = input('Please choose your option:').strip()

        if choice == "1":
            show_profile(user)
        elif choice == "2":
            show_todos(user)
        elif choice == "3" and user["is_admin"]:
            user_management()
        elif choice == "0":
            print('Logout successful! See you next time!')
            break
        else:
            print('Invalid input!')

#show own profile
def show_profile(user):
    print("\n Your information:")
    for k, v in user.items():
        print(f"{k}: {v}")
    while True:
        print('\nFunctions:')
        print('1 - change my information\n')
        print('2 - delete my account\n')
        print('0 - exit\n')
        choice = input('Please choose your option:').strip()

        if choice == "1":
            change_information(user)
        elif choice == "2":
            delete_account(user)
            break
        elif choice == "0":
            break
        else:
            print('Invalid input!')

# change own information
def change_information(user):
    print('\nChange my information:')
    print('\n1 - change my name')
    print('\n2 - change my password')
    print('\n0 - exit')
    choice = input('Please choose your option:').strip()

    if choice == '1':
        new_first = input('Your first name:').strip()
        new_last = input('Your last name').strip()

        if new_first or new_last:
            cursor.execute("""
                UPDATE users
                SET first_name = COALESCE(NULLIF(?, ''), first_name),
                    last_name  = COALESCE(NULLIF(?, ''), last_name)
                WHERE user_id = ?
            """, (new_first, new_last, user["user_id"]))
            conn.commit()
            print('Your information has been updated successfully!')
        else:
            print('No changes were taken!')


    elif choice == '2':
        new_pw = input('Your new password:').strip()
        confirm_pw = input('Your new passord again:').strip()
        if new_pw != confirm_pw:
            print('Passwords are not identical!')
            return

        hashed_pw = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE users SET password=? WHERE user_id=?", (hashed_pw, user["user_id"]))
        conn.commit()
        print('Your password has been updated successfully!')

    elif choice == '0':
        return

    else:
        print('Invalid input!')

# delete own account
def delete_account(user):
    alias = user["alias"]
    confirmation = input(f'\nType: "{alias} confirms to delete." to confirm.\n')

    if confirmation != f'{alias} confirms to delete.':
        print('Pattern does not match! Deletion was cancelled!')
        return False

    cursor.execute("DELETE FROM users WHERE user_id=?", (user["user_id"],))
    conn.commit()

    print(f"{alias}'s account has been deleted!")
    return True

# show to-do-list
def show_todos(user):
    cursor.execute("SELECT * FROM todos WHERE user_id=?", (user["user_id"],))
    rows = cursor.fetchall()

    if not rows:
        print("You have no tasks currently!")
    else:
        print("\nYour tasks:")
        for row in rows:
            print(row)

# admin function, which allows admin to show users, reset their passwords and freeze/defreeze their account
def user_management(user):
    while True:
        print('\nUser management:')
        print('\n1 - show all users')
        print('\n2 - reset password')
        print('\n3 -  freeze / defreeze user')
        print('\n0 - exit\n')

        choice = input('Please choose your option:').strip()

        if choice == "1":
            show_users()
        elif choice == "2":
            reset_password()
        elif choice == "3":
            account_freeze()
        elif choice == "0":
            break
        else:
            print('Invalid input!')

# show users
def show_users():
    cursor.execute("""
        SELECT user_id, first_name, last_name, alias, is_admin, freezed, failed_attempts, created_at
        FROM users ORDER BY user_id
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(row)

# reset password for non-admin user
def reset_password():
    try:
        target_id = int(input('Please enter the user id:').strip())
    except ValueError:
        print('Invalid input!')
        return

    new_pw = input('Please enter new password').strip()
    if not new_pw:
        print('Password is empty!')
        return

    confirm_pw = input('Your new passord again:').strip()
    if new_pw != confirm_pw:
        print('Passwords are not identical!')
        return


    hashed_pw = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("UPDATE users SET password=?, failed_attempts=0, freezed=0 WHERE user_id=? AND is_admin=0",
                   (hashed_pw, target_id))
    if cursor.rowcount:
        conn.commit()
        print(f' The password of User {target_id} has been updated!')
    else:
        print('You can not reset password of ohter administrator!')

# freeze/defreeze accounts
def account_freeze():
    try:
        target_id = int(input('Please enter the user id:').strip())
    except ValueError:
        print('Invalid input!')
        return

    cursor.execute("SELECT alias, freezed FROM users WHERE user_id=?", (target_id,))
    row = cursor.fetchone()
    if not row:
        print('Id does not exist!')
        return


    if freezed:
        new_state = 0
        action = 'defreezed'
    else:
        new_state = 1
        action = 'freezed'

    cursor.execute("UPDATE users SET freezed=?, failed_attempts=0 WHERE user_id=?", (new_state, target_id))
    conn.commit()
    print(f' User {alias} is now {action}')

if __name__ == "__main__":
    welcome()
