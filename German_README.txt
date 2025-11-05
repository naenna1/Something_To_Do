========================================
        Something To-Do
   Multi-User Task Management System
========================================

📌 DEUTSCH – Bedienungsanleitung

========================================

🚀 Was ist „Something To-Do“?
----------------------------------------
Eine mehrbenutzerfähige Aufgabenverwaltung für Familien oder Teams.
Jeder Nutzer hat seine eigenen Aufgaben und seinen eigenen Login.
Admins können Benutzer verwalten und Konten entsperren.

🧩 Voraussetzungen
----------------------------------------
• Python 3.x installiert
• Benötigte Module:
    - sqlite3 (Standardbibliothek)
    - bcrypt   (für Passwort-Hashing → Installation: pip install bcrypt)

📦 Projektdateien:
----------------------------------------
• main.py              → Startet das Programm
• db.py                → Datenbank & Tabellen
• auth.py              → Login / Registrierung / Benutzerstatus
• tasks.py             → Aufgabenfunktionen
• categories.py        → Kategorienfunktionen
• admin.py             → Admin-Verwaltung
• profile.py           → Benutzerprofil
• utils.py             → Hilfsfunktionen (Eingaben/Datum)

🛠️ Start des Programms:
----------------------------------------
Windows:
> python main.py

Mac/Linux:
$ python3 main.py

🔐 Benutzerverwaltung
----------------------------------------
• Jeder Benutzer meldet sich mit Alias + Passwort an
• 3 Fehlversuche → Konto gesperrt
• Administrator kann entsperren

👥 Rollen:
----------------------------------------
Benutzer: Kann eigene Aufgaben verwalten  
Admin: Kann zusätzlich Benutzerdaten verwalten

✅ Funktionen im Hauptmenü
----------------------------------------
1 – Aufgabe erstellen  
2 – Aufgaben anzeigen  
3 – Aufgabe als erledigt markieren  
4 – Aufgabe löschen  
5 – Aufgabe bearbeiten  
6 – Kategorie erstellen  
7 – Kategorien anzeigen  
8 – Login / Benutzer wechseln  
9 – Logout  
10 – Benutzer registrieren  
11 – Profilmenü (Alias/Passwort ändern)

👑 Admin-Menü (nur für Admins)
----------------------------------------
A – Benutzerliste anzeigen  
B – Konto entsperren  
C – Passwort eines Benutzers zurücksetzen  

✅ Profil-Menü
----------------------------------------
• Eigenes Profil anzeigen
• Alias ändern
• Passwort ändern