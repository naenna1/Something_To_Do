from datetime import datetime
from db import get_conn, DB_PATH


# ----------------------------
# Create
# ----------------------------
def create_task(title, category_id, description, creation_date, completed,
                due_date, user_id, db_path=DB_PATH):
    """Erstellt eine Aufgabe für einen User."""
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
        cur.execute(
            """
            INSERT INTO task (title, description, creation_date, completed, due_date, category_id, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (title, description, creation_date, completed_val, due_date, category_id, user_id),
        )
        con.commit()
    finally:
        con.close()


# ----------------------------
# Read (CLI Ausgabe)
# ----------------------------
def list_tasks(user_id, db_path=DB_PATH, is_admin=False):
    """
    Gibt Aufgaben auf der Konsole aus.
    - Normale User sehen nur eigene Tasks.
    - Admins sehen alle Tasks.
    """
    con = get_conn(db_path)
    cur = con.cursor()

    if is_admin:
        cur.execute(
            """
            SELECT task.id,
                   task.title,
                   category.name,
                   task.description,
                   task.creation_date,
                   task.completed,
                   task.due_date
            FROM task
            LEFT JOIN category ON task.category_id = category.id
            ORDER BY task.completed,
                     COALESCE(task.due_date, '9999-12-31'),
                     task.id
            """
        )
    else:
        cur.execute(
            """
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
                     COALESCE(task.due_date, '9999-12-31'),
                     task.id
            """,
            (user_id,),
        )

    rows = cur.fetchall()
    con.close()

    if not rows:
        print("\nNo tasks found.\n")
        return

    print("\n=== Task List ===")
    for (task_id, title, category_name, description, creation_date, completed, due_date) in rows:
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


# ----------------------------
# Delete
# ----------------------------
def delete_task(task_id, user_id, db_path=DB_PATH, is_admin=False):
    """
    Löscht eine Aufgabe.
    - Normale User: nur eigene Tasks.
    - Admins: beliebige Task-ID.
    """
    con = get_conn(db_path)
    cur = con.cursor()

    if is_admin:
        cur.execute("DELETE FROM task WHERE id = ?", (task_id,))
    else:
        # Besitz prüfen und löschen
        cur.execute("DELETE FROM task WHERE id = ? AND user_id = ?", (task_id, user_id))

    con.commit()
    deleted = cur.rowcount
    con.close()

    if deleted == 0 and not is_admin:
        print("You cannot delete tasks that are not yours.")
    elif deleted == 0:
        print("Task not found.")
    else:
        print("Task deleted.")


# ----------------------------
# Complete
# ----------------------------
def complete_task(task_id, user_id, db_path=DB_PATH, is_admin=False):
    """
    Markiert eine Aufgabe als erledigt.
    - Normale User: nur eigene Tasks.
    - Admins: beliebige Task-ID.
    """
    con = get_conn(db_path)
    cur = con.cursor()

    if is_admin:
        cur.execute("UPDATE task SET completed = 1 WHERE id = ?", (task_id,))
    else:
        cur.execute("UPDATE task SET completed = 1 WHERE id = ? AND user_id = ?", (task_id, user_id))

    con.commit()
    updated = cur.rowcount
    con.close()

    if updated == 0 and not is_admin:
        print("Task not found or not owned by you.")
    elif updated == 0:
        print("Task not found.")
    else:
        print("Task marked as completed.")


# ----------------------------
# Update
# ----------------------------
def update_task(task_id, user_id, title=None, category_id=None, description=None, due_date=None,
                db_path=DB_PATH, is_admin=False):
    """
    Aktualisiert Felder einer Aufgabe.
    - Normale User: nur eigene Tasks.
    - Admins: beliebige Task-ID.
    """
    con = get_conn(db_path)
    cur = con.cursor()

    # Besitzerprüfung nur für Nicht-Admins
    if not is_admin:
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
        values.append((description or "").strip())

    if due_date is not None:
        # validieren
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

    # WHERE-Bedingung abhängig von Admin/Nutzer
    if is_admin:
        sql = f"UPDATE task SET {', '.join(updates)} WHERE id = ?"
        values.append(task_id)
    else:
        sql = f"UPDATE task SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
        values.extend([task_id, user_id])

    cur.execute(sql, values)
    con.commit()
    con.close()
    print(f"Task {task_id} has been updated.")


# ----------------------------
# Read for GUI
# ----------------------------
def get_tasks(user_id, db_path=DB_PATH, is_admin=False):
    """
    Liefert Task-Zeilen für die GUI:
    (task.id, task.title, category.name, task.description, task.creation_date, task.completed, task.due_date, owner_alias)
    Admin: sieht alle Tasks (inkl. owner_alias); bei normalen Usern ist owner_alias ihr eigener Alias.
    """
    con = get_conn(db_path)
    cur = con.cursor()

    if is_admin:
        cur.execute(
            """
            SELECT task.id,
                   task.title,
                   category.name,
                   task.description,
                   task.creation_date,
                   task.completed,
                   task.due_date,
                   users.alias AS owner_alias
            FROM task
            LEFT JOIN category ON task.category_id = category.id
            LEFT JOIN users    ON task.user_id     = users.id
            ORDER BY task.completed,
                     COALESCE(task.due_date, '9999-12-31'),
                     task.id
            """
        )
    else:
        cur.execute(
            """
            SELECT task.id,
                   task.title,
                   category.name,
                   task.description,
                   task.creation_date,
                   task.completed,
                   task.due_date,
                   users.alias AS owner_alias
            FROM task
            LEFT JOIN category ON task.category_id = category.id
            LEFT JOIN users    ON task.user_id     = users.id
            WHERE task.user_id = ?
            ORDER BY task.completed,
                     COALESCE(task.due_date, '9999-12-31'),
                     task.id
            """,
            (user_id,),
        )

    rows = cur.fetchall()
    con.close()
    return rows
