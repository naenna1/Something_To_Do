import sqlite3
from datetime import datetime

def create_task(title, category, description, creation_date, completed, due_date):
"""
Fügt eine Aufgabe in die Tabelle 'task' ein.
    - id:            int (eindeutig) – wenn ihr SQLite auto-ID wollt, könnt ihr ID auch NULL übergeben
    - title:         str (nicht leer)
    - category:      str (z. B. "Schule", "Uni", ...)
    - description:   str oder None
    - creation_date: 'YYYY-MM-DD'
    - completed:     0/1 oder True/False
    - due_date:      'YYYY-MM-DD' oder None
"""
if title is None or str(title).strip() == '':
    raise ValueError('\'title\' darf nicht leer sein.')
title = str(title).strip()
if category is None or str(category).strip() == '':
    raise ValueError('\'category\' darf nicht leer sein.')
category = str(category).strip()
try:
    datetime.strptime(creation_date, '%Y-%m-%d')
except Exception:
    raise ValueError('\'creation_date\' muss im Format YYYY-MM-DD sein.')
if due_date is not None:
    try:
        datetime.strptime(due_date, '%Y-%m-%d')
    except Exception:
        raise ValueError('\'due_date\' muss im Format YYYY-MM-DD sein oder None.')
if completed in (True, False):
    completed_val = 1 if completed else 0
else:
    try:
        completed_val = int(completed)
    except Exception:
        raise ValueError('\'completed\' muss 0/1 oder True/False sein')
    if completed_val not in (0, 1):
        raise ValueError('\'completed\' muss 0 oder 1 sein.')
con = sqlite3.connect(db_path)
cur = con.cursor()
try:
    cur.execute('''
    INSERT INTO task (title, category, description, creation_date, completed, due_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (id, title, category, description, creation_date, completed, due_date))
    con.commit()
finally:
    con.close()
