# Something To-Do – Aufgabenverwaltung mit CLI, GUI und Admin-Panel

Eine Python-basierte Todo-Anwendung mit benutzerabhängiger Aufgabenverwaltung, Kategorisierung und Admin-Funktionen. Läuft lokal mit SQLite-Datenbank.

## Features

- **Dual-Interface**: CLI (Kommandozeile) und GUI (Tkinter)
- **Benutzerverwaltung**: Registrierung, Login, Profilmanagement
- **Authentifizierung**: Passwort-Hashing mit Argon2
- **Aufgabenverwaltung**: Erstellen, anzeigen, aktualisieren, löschen, als erledigt markieren
- **Kategorien**: Tasks mit Kategorien organisieren
- **Admin-Panel**: Benutzerlisten, Account-Sperrung, Passwort-Reset
- **SQLite-Datenbank**: Lokale persistente Speicherung

## Installation

### Voraussetzungen
- Python 3.8+
- pip

### Setup

```bash
# Repository klonen oder extrahieren
cd "Something To-Do"

# Virtual Environment (optional, empfohlen)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# Core-Abhängigkeiten installieren
pip install argon2-cffi
```

> **Hinweis**: Die `requirements.txt` enthält viele Jupyter/Entwicklungs-Dependencies. Für die Anwendung selbst brauchst du nur `argon2-cffi` für Passwort-Hashing. Die Standard-Library (sqlite3, tkinter) ist already enthalten.

## Verwendung

### CLI-Modus

```bash
python main.py
```

Zeigt interaktives Menü mit folgenden Optionen:

**Benutzer-Funktionen:**
- `1`: Neue Aufgabe erstellen
- `2`: Aufgaben anzeigen (gefiltert nach angemeldetem Nutzer)
- `3`: Aufgabe als erledigt markieren
- `4`: Aufgabe löschen
- `5`: Aufgabe aktualisieren
- `6`: Neue Kategorie erstellen
- `7`: Kategorien anzeigen
- `8`: Login / Nutzer wechseln
- `9`: Logout
- `10`: Neuen Nutzer registrieren
- `11`: Profil (Passwort ändern, Account löschen)

**Admin-Funktionen** (für Administratoren):
- `A`: Benutzerliste anzeigen
- `B`: Account entsperren
- `C`: Passwort zurücksetzen

### GUI-Modus

```bash
python gui.py
```

Öffnet eine grafische Oberfläche mit:
- Login/Registrierung
- Task-Verwaltung (CRUD)
- Kategorie-Verwaltung
- Profil-Einstellungen
- Admin-Tools (falls Admin)

## Projektstruktur

```
Something To-Do/
├── main.py              # CLI-Entry Point, Hauptmenü
├── gui.py               # GUI mit Tkinter
├── auth.py              # Authentifizierung & Passwort-Hashing
├── tasks.py             # Task-CRUD-Operationen
├── categories.py        # Kategorie-Management
├── profile.py           # Benutzer-Profil & -Einstellungen
├── admin.py             # Admin-Funktionen
├── db.py                # Datenbankinitialisierung
├── utils.py             # Hilfsfunktionen
├── todo.db              # SQLite-Datenbank (wird auto-erstellt)
├── requirements.txt     # Dependencies
├── app.ico              # Taskbar-Icon für GUI
├── logo.png             # App-Logo
├── CLI_Anleitung_GER.txt
├── GUI_Anleitung_GER.txt
├── CLI_Instructions_EN.txt
└── GUI_Instructions_EN.txt
```

### Module im Detail

**main.py** (200 Z.)
- Interaktives CLI-Menü
- Routing zu Funktionen basierend auf Benutzer-Input
- Session-Management (Login/Logout)

**gui.py** (785 Z.)
- Tkinter-basierte Benutzeroberfläche
- Tabs/Screens für verschiedene Funktionen
- Direkter Dialog statt Kommandozeile

**auth.py** (162 Z.)
- Registrierung mit Passwort-Hashing (Argon2)
- Login & Session-Management
- Passwort-Validierung

**tasks.py** (307 Z.)
- CRUD für Aufgaben (Create, Read, Update, Delete)
- Filterung nach Benutzer
- Status-Management (pending, completed)

**categories.py** (97 Z.)
- Kategorie-Erstellung & -Verwaltung
- Zuordnung zu Tasks

**profile.py** (183 Z.)
- Passwort ändern
- Account löschen
- Profil-Informationen

**admin.py** (57 Z.)
- Benutzerverwaltung
- Account-Sperrung
- Passwort-Reset

**db.py** (82 Z.)
- SQLite-Datenbankinitialisierung
- Tabellen-Schema (users, tasks, categories)

## Datenbank-Schema

```sql
-- users: Benutzerkonten
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    alias TEXT,
    is_admin BOOLEAN,
    is_locked BOOLEAN
);

-- tasks: Aufgaben pro Benutzer
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    description TEXT,
    category_id INTEGER,
    due_date TEXT,
    is_completed BOOLEAN
);

-- categories: Aufgaben-Kategorien
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT UNIQUE
);
```

## Authentifizierung & Sicherheit

- **Passwort-Hashing**: Argon2 (kryptographisch stark)
- **Session**: Globals halten den aktuell angemeldeten Nutzer
- **Admin-Flag**: Nur Admins sehen Admin-Optionen
- **Account-Sperrung**: Admins können Accounts sperren (Login-Block)

## Sprache

- CLI & GUI: Menüs in Deutsch
- Anleitung: Deutsch (`*_GER.txt`) und English (`*_EN.txt`)

## Beispiel-Workflow (CLI)

```
===== SOMETHING TO-DO =====
Logged in as: Nobody

--- Main Menu ---
10) Register new user
   → Username: anna
   → Password: ***
   → Alias: Anna
   → registered successfully!

8) Login / Switch user
   → Username: anna
   → Password: ***
   → logged in as Anna!

1) Create task
   → Title: "Projekt abschließen"
   → Description: "README schreiben"
   → Category: "Arbeit"
   → Due date (YYYY-MM-DD): 2025-12-31
   → Task created!

2) Show tasks
   ID | Title | Category | Due | Completed
   1  | Projekt abschließen | Arbeit | 2025-12-31 | ✗

3) Mark task as completed
   → Task ID: 1
   → Marked as completed!
```

## Testing & Entwicklung

Keine automatisierten Tests included. Für Entwicklung:
- `.idea/` = PyCharm-Metadaten (kann gelöscht werden)
- `.venv/` = Virtual Environment (kann regeneriert werden)

## Lizenz

MIT (oder deine Lizenz hier)

## Notizen für CV/Portfolio

**Technische Highlights:**
- Datenbankdesign (relationale Struktur mit Foreign Keys)
- OOP-Struktur (separate Module für Concerns)
- Benutzerauth mit starkem Hashing
- Dual-Interface (CLI + GUI)
- Admin-Rollen & -Funktionen

**Lerneffekt:**
- SQLite & Datenbankabfragen
- Tkinter GUI-Programmierung
- Authentifizierung & Sicherheit (Argon2)
- Menü-gesteuerte CLI-Anwendungen
- Modularisierung & Code-Organisation

---

**Kontakt / Issues**: GitHub Issues oder Pull Requests willkommen!
