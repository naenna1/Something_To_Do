from datetime import datetime
from db import get_conn, DB_PATH

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