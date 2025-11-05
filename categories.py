from db import get_conn, DB_PATH

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
