# Kategorie anlegen

def add_category(name, description=""):
    if not name.strip():
        raise ValueError("Category name cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO category (name, description)
        VALUES (?, ?)
    """, (name.strip(), description.strip()))

    con.commit()
    con.close()
    print(f"Category '{name}' has been created.")


# Kategorien anzeigen/auflisten

def list_categories():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name, description FROM categories ORDER BY id")

# .fetchall gibt Liste von Tupeln zurück
    rows = cursor.fetchall()
    connection.close()

# Wenn keine Kategorien gefunden wurden
    if not rows:
        print("No categories found.")
    else:
        print("Categories list:")


# Kategorie löschen

def delete_category(category_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    connection.commit()
    connection.close()

    print(f"Category with ID {category_id} has been deleted.")