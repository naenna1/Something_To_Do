import sqlite3
from datetime import datetime

DB_PATH = "todo.db"

# Datenbank initialisieren
def init_db(db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # Kategorie-Tabelle
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    """)

    # Aufgaben-Tabelle mit Foreign Key
    cur.execute("""
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            creation_date TEXT NOT NULL,
            completed INTEGER NOT NULL CHECK (completed IN (0,1)),
            due_date TEXT,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL
        )
    """)

    con.commit()
    con.close()

# Kategorie erstellen
def add_category(name, description=""):
    if not name.strip():
        raise ValueError(f"'category' cannot be empty.")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        INSERT INTO category (name, description)
        VALUES (?, ?)
    """, (name.strip(), description.strip()))

    con.commit()
    con.close()
    print(f"'category' '{name}' wurde erstellt.")

# Kategorien anzeigen/auflisten
def list_categories():
    con = sqlite3.connect(DB_PATH)
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
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Prüfen, ob Aufgaben diese Kategorie nutzen
    cur.execute("SELECT COUNT(*) FROM task WHERE category_id = ?", (category_id,))
    count = cur.fetchone()[0]

    if count > 0:
        con.close()
        print(f"Category cannot be deleted! There are still {count} tasks associated with it.")
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
    except:
        raise ValueError(f"{field_name} must be in the format YYYY-MM-DD (2025-11-03).")

# Aufgabe erstellen
def create_task(title, category_id, description, creation_date, completed, due_date, db_path=DB_PATH):
    if title is None or str(title).strip() == "":
        raise ValueError(f"'title' cannot be empty.")
    title = title.strip()

    if category_id is not None:
        try:
            category_id = int(category_id)
        except:
            raise ValueError(f"'category_id' must be a number or None.")

    try:
        datetime.strptime(creation_date, "%Y-%m-%d")
    except Exception:
        raise ValueError(f"'creation_date' must be in the format YYYY-MM-DD.")

    if due_date is not None:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except Exception:
            raise ValueError(f"'due_date' must be in the format YYYY-MM-DD or None.")

    if completed in (True, False):
        completed_val = 1 if completed else 0
    else:
        try:
            completed_val = int(completed)
        except:
            raise ValueError(f"'completed' must be 0/1 or True/False.")
        if completed_val not in (0, 1):
            raise ValueError("'completed' must be 0 or 1.")

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute("""
            INSERT INTO task (title, description, creation_date, completed, due_date, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, creation_date, completed_val, due_date, category_id))
        con.commit()
    finally:
        con.close()

# Aufgabenliste anzeigen lassen
def list_tasks(db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""
        SELECT id, title, category_id, description, creation_date, completed, due_date
        FROM task
        ORDER BY completed ASC, COALESCE(due_date, '9999-12-31') ASC, id ASC
    """)
    rows = cur.fetchall()
    con.close()

    if len(rows) == 0:
        print("\nNo tasks found.\n")
        return

    print("\n=== Tasks ===")
    for r in rows:
        task_id = r[0]
        title = r[1]
        category_id = r[2]
        description = r[3]
        creation_date = r[4]
        completed = r[5]
        due_date = r[6]
        status = "✔️ Completed" if completed == 1 else "⭕ Open"
        line = f"{task_id}: {title} [Category-ID: {category_id}] - {status} (Created: {creation_date})"
        if due_date:
            line += f" | Due: {due_date}"
        print(line)
        if description:
            print("   Description:", description)
    print()

# Aufgaben löschen
def delete_task(task_id, db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("DELETE FROM task WHERE id = ?", (task_id,))
    con.commit()
    changed = cur.rowcount
    con.close()
    if changed == 0:
        print("No task found with this ID.")
    else:
        print("Task deleted.")

# Erledigt Status anpassen
def complete_task(task_id, db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("UPDATE task SET completed = 1 WHERE id = ?", (task_id,))
    con.commit()
    con.close()
    print("Task marked as completed.")

# Aufgaben aktualisieren
def update_task(task_id, title=None, category_id=None, description=None, due_date=None, db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Felder auswählen, die aktualisiert werden sollen
    updates = []
    values = []

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
        values.append(due_date)

    if not updates:
        print("No changes applied.")
        con.close()
        return

    values.append(task_id)  # ID ans Ende
    sql = f"UPDATE task SET {', '.join(updates)} WHERE id = ?"

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
    val = input(prompt + " (YYYY-MM-DD or empty): ").strip()
    if val == "":
        return None
    try:
        datetime.strptime(val, "%Y-%m-%d")
        return val
    except:
        print("Please enter the date in the format YYYY-MM-DD.")
        return input_date_or_empty(prompt)

def input_completed(prompt="Completed? (0/1 oder true/false) "):
    val = input(prompt).strip().lower()
    if val in ("1", "true", "ja", "y"):
        return 1
    if val in ("0", "false", "nein", "n", ""):
        return 0
    print("Please enter 0/1 or true/false.")
    return input_completed(prompt)

## MENÜ ##
def main_menu():
    while True:
        print("===== TO-DO =====")
        print("1) Create task")
        print("2) Show tasks")
        print("3) Mark task as completed")
        print("4) Delete task")
        print("5) Update task")
        print("6) Create category")
        print("7) Show categories")
        print("0) Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            try:
                title = input_nonempty("Title: ")
                category_id = input("Category-ID (or empty): ").strip()
                if category_id == "":
                    category_id = None
                else:
                    category_id = int(category_id)

                description = input("Description (optional): ").strip()
                creation_date = input_date_or_empty("Created on")
                if creation_date is None:
                    creation_date = datetime.now().strftime("%Y-%m-%d")
                completed = input_completed()
                due_date = input_date_or_empty("Due on")

                create_task(title, category_id, description, creation_date, completed, due_date)
                print("Task saved.\n")
            except Exception as e:
                print("Error:", e, "\n")

        elif choice == "2":
            list_tasks()

        elif choice == "3":
            try:
                task_id = int(input_nonempty("Task-ID: "))
                complete_task(task_id)
                print()
            except Exception as e:
                print("Error:", e, "\n")

        elif choice == "4":
            try:
                task_id = int(input_nonempty("Task-ID: "))
                delete_task(task_id)
                print()
            except Exception as e:
                print("Error:", e, "\n")

        elif choice == "5":
            try:
                task_id = int(input_nonempty("Task-ID: "))
                print(
                    "Only change what you want to change. Leave blank = stays as it is..")

                new_title = input("New title (empty = unchanged): ").strip()
                if new_title == "":
                    new_title = None

                new_category = input(
                    "New Category-ID (empty = unchanged): ").strip()
                if new_category == "":
                    new_category = None
                else:
                    new_category = int(new_category)

                new_description = input(
                    "New description (empty = unchanged): ").strip()
                if new_description == "":
                    new_description = None

                new_due_date = input_date_or_empty("New due-date:")
                update_task(task_id, new_title, new_category, new_description,
                            new_due_date)
            except Exception as e:
                print("Error:", e, "\n")

        elif choice == "6":
            try:
                name = input_nonempty("Category name: ")
                description = input("Description (optional): ").strip()
                add_category(name, description)
            except Exception as e:
                print("Error:", e, "\n")

        elif choice == "7":
            list_categories()

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Please enter 0–6.\n")

## Start des Programms ##
if __name__ == "__main__":
    init_db()     # DB + Tabelle anlegen (falls noch nicht vorhanden)
    main_menu()   # Menü starten