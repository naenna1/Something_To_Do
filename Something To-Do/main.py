from datetime import datetime
from db import init_db
from auth import login_user, register_user, get_logged_in_user, logout_user
from admin import admin_handle_choice
from tasks import create_task, list_tasks, delete_task, complete_task, update_task
from categories import add_category, get_or_create_category, list_categories
from profile import profile_menu
from utils import input_nonempty, input_date_or_empty, is_back


def main_menu():
    while True:
        user = get_logged_in_user()
        print("\n===== SOMETHING TO-DO =====")
        print("Logged in as:", user['alias'] if user else "Nobody")

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

        # Admin-Menü (nur sichtbar für Admins)
        if user and user.get('is_admin'):
            print("\n--- Admin Menu ---")
            print("A) Show user list")
            print("B) Unlock account")
            print("C) Reset user password")

        print("0) Exit")

        choice = input("Choice: ").strip()

        # Aktionen 1–5 und 11 nur mit Login
        if choice in ["1", "2", "3", "4", "5", "11"] and not user:
            print("Please login first!\n")
            continue

        # Für Bequemlichkeit: Flag einmal berechnen
        is_admin = bool(user.get('is_admin')) if user else False

        if choice == "1":
            # Create task
            try:
                title = input_nonempty("Title (0 = back): ")
                if is_back(title):
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

                create_task(
                    title=title,
                    category_id=category_id,
                    description=description,
                    creation_date=creation_date,
                    completed=completed,
                    due_date=due_date,
                    user_id=user['id'],
                )
                print("Task saved!\n")
            except ValueError as e:
                print("Error:", e)

        elif choice == "2":
            # Show tasks (Admin sieht alle)
            list_tasks(user['id'], is_admin=is_admin)

        elif choice == "3":
            # Mark completed
            task = input("Task ID (0 = back): ").strip()
            if is_back(task):
                continue
            try:
                task_id = int(task)
            except ValueError:
                print("Invalid ID.")
                continue
            complete_task(task_id, user['id'], is_admin=is_admin)

        elif choice == "4":
            # Delete task
            task = input("Task ID (0 = back): ").strip()
            if is_back(task):
                continue
            try:
                task_id = int(task)
            except ValueError:
                print("Invalid ID.")
                continue
            delete_task(task_id, user['id'], is_admin=is_admin)

        elif choice == "5":
            # Update task
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
            if new_category_name:
                new_category = get_or_create_category(new_category_name)
            else:
                new_category = None  # None = Kategorie NICHT ändern

            new_description = input("New description (empty = unchanged): ").strip() or None
            new_due_date = input_date_or_empty("New due date")
            if new_due_date == "BACK":
                continue

            update_task(
                task_id,
                user['id'],
                new_title,
                new_category,
                new_description,
                new_due_date,
                is_admin=is_admin
            )

        elif choice == "6":
            # Create category
            name = input("Category name (0 = back): ").strip()
            if is_back(name) or name == "":
                continue
            add_category(name)

        elif choice == "7":
            # Show categories
            list_categories()

        elif choice == "8":
            # Login
            _ = login_user()
            user = get_logged_in_user()
            if user:
                print(f"Logged in as {user['alias']}.\n")
            continue

        elif choice == "9":
            # Logout
            logout_user()
            print("Logged out.\n")

        elif choice == "10":
            # Register
            alias = input("New Alias (0 = back): ").strip()
            if is_back(alias):
                continue
            pw = input("New Password (0 = back): ").strip()
            if is_back(pw):
                continue
            register_user(alias, pw)

        elif choice == "11":
            # Profile submenu
            user = get_logged_in_user()
            if not user:
                print("Please login first!\n")
                continue
            profile_menu()
            continue

        # Admin actions (A/B/C)
        elif (user := get_logged_in_user()) and user.get('is_admin') and choice.upper() in ("A", "B", "C"):
            admin_handle_choice(choice)
            continue

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Please enter a valid option.\n")


if __name__ == "__main__":
    init_db()
    main_menu()
