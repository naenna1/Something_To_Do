import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, font
from datetime import datetime
from auth import authenticate, get_logged_in_user, logout_user, hash_pw
from tasks import get_tasks, create_task, complete_task, delete_task, update_task
from categories import get_categories, add_category, delete_category, get_or_create_category
from db import init_db, get_conn
from PIL import Image, ImageTk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Einheitliche Schriftart definieren
        DEFAULT_FONT = ("Segoe UI", 10)
        CAPTION_FONT = ("Segoe UI SemiBold", 10)
        TITLE_FONT = ("Segoe UI SemiBold", 12)

        self.option_add("*Font", DEFAULT_FONT)
        self.option_add("*TLabel.Font", DEFAULT_FONT)
        self.option_add("*TButton.Font", DEFAULT_FONT)
        self.option_add("*TEntry.Font", DEFAULT_FONT)
        self.option_add("*TCombobox.Font", DEFAULT_FONT)
        self.option_add("*Text.Font", DEFAULT_FONT)

        # --- Dark Theme & Styles ---
        self.configure(bg="#121212")
        style = ttk.Style(self)
        style.theme_use("clam")

        # Grundfarben
        BG = "#121212"
        SURFACE = "#1e1e1e"
        FG = "#e8e8e8"
        ACCENT = "#4f8cff"  # Primärfarbe für Buttons

        # Widgets allgemein
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("TFrame", background=BG)
        style.configure("TButton", background=SURFACE, foreground=FG, borderwidth=0, padding=8)
        style.map("TButton",
                  background=[("active", "#2a2a2a")],
                  relief=[("pressed", "sunken"), ("!pressed", "flat")])

        # Primär-Button
        style.configure("Primary.TButton", background=ACCENT, foreground="white", padding=8)
        style.map("Primary.TButton", background=[("active", "#3b6fd1")])

        # Entry-Felder
        style.configure("TEntry", fieldbackground=SURFACE, foreground=FG, insertcolor=FG)

        # Scrollbars dunkel
        style.configure("Vertical.TScrollbar", background="#2a2a2a")
        style.map("Vertical.TScrollbar", background=[("active", "#3a3a3a")])
        style.configure("Horizontal.TScrollbar", background="#2a2a2a")
        style.map("Horizontal.TScrollbar", background=[("active", "#3a3a3a")])

        # Dunkle Combobox
        style.configure("Dark.TCombobox",
                        fieldbackground="#1e1e1e",
                        background="#1e1e1e",
                        foreground="#e8e8e8",
                        arrowcolor="#e8e8e8",
                        bordercolor="#1e1e1e")
        style.map("Dark.TCombobox",
                  fieldbackground=[("readonly", "#1e1e1e")],
                  foreground=[("readonly", "#e8e8e8")],
                  background=[("active", "#2a2a2a")])

        # Fenstericon (optional)
        try:
            self.iconbitmap("app.ico")
        except Exception:
            pass

        # Fenstergröße & Zentrierung
        self.title("Something To-Do")
        window_width = 900
        window_height = 620
        self.minsize(window_width, window_height)
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.winfo_screenheight() // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.user = None
        self.login_frame = LoginFrame(self, on_success=self.on_login_success)
        self.login_frame.pack(fill="both", expand=True)

    def on_login_success(self, user):
        self.user = user
        self.login_frame.pack_forget()
        self.tasks_frame = TasksFrame(self, user)
        self.tasks_frame.pack(fill="both", expand=True)


class LoginFrame(tk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, bg="#121212")
        self.on_success = on_success

        # Grid für Zentrierung
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Logo groß, mittig
        try:
            img = Image.open("logo.png")
            img = img.resize((240, 240))
            self._logo_img = ImageTk.PhotoImage(img)
            tk.Label(self, image=self._logo_img, bg="#121212").grid(row=0, column=0, columnspan=2, pady=(24, 12))
            offset = 1
        except Exception:
            offset = 0

        ttk.Label(self, text="Alias").grid(row=offset+0, column=0, sticky="e", padx=10, pady=8)
        ttk.Label(self, text="Password").grid(row=offset+1, column=0, sticky="e", padx=10, pady=8)

        self.alias_var = tk.StringVar()
        self.pw_var = tk.StringVar()

        ttk.Entry(self, textvariable=self.alias_var, width=24).grid(row=offset+0, column=1, sticky="w", padx=10)
        ttk.Entry(self, textvariable=self.pw_var, show="*", width=24).grid(row=offset+1, column=1, sticky="w", padx=10)

        # Button-Reihe: Login (Primary) + Create Account
        btnrow = ttk.Frame(self)
        btnrow.grid(row=offset+2, column=0, columnspan=2, pady=(18, 10))
        ttk.Button(btnrow, text="Login", style="Primary.TButton", command=self.try_login).pack(side="left", padx=6)
        ttk.Button(btnrow, text="Create account…", command=self.open_register).pack(side="left", padx=6)

    def try_login(self):
        alias = self.alias_var.get().strip()
        pw = self.pw_var.get()

        ok = authenticate(alias, pw)
        if ok:
            user = get_logged_in_user()
            if user:
                self.on_success(user)
                return
        messagebox.showerror("Login failed", "Alias oder Passwort falsch oder Account gesperrt.")

    def open_register(self):
        RegisterDialog(self, on_success=lambda: None)


class RegisterDialog(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Create Account")
        self.configure(bg="#121212")
        self.resizable(False, False)
        self.grab_set()
        self.on_success = on_success

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Alias").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        ttk.Label(frm, text="Password").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        ttk.Label(frm, text="Repeat").grid(row=2, column=0, sticky="e", padx=6, pady=6)

        self.alias = tk.StringVar()
        self.pw1 = tk.StringVar()
        self.pw2 = tk.StringVar()

        ttk.Entry(frm, textvariable=self.alias, width=28).grid(row=0, column=1, sticky="w", padx=6)
        ttk.Entry(frm, textvariable=self.pw1, show="*", width=28).grid(row=1, column=1, sticky="w", padx=6)
        ttk.Entry(frm, textvariable=self.pw2, show="*", width=28).grid(row=2, column=1, sticky="w", padx=6)

        row = ttk.Frame(frm)
        row.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(row, text="Cancel", command=self.destroy).pack(side="left", padx=6)
        ttk.Button(row, text="Create", style="Primary.TButton", command=self._create).pack(side="left", padx=6)

    def _create(self):
        alias = (self.alias.get() or "").strip()
        pw1 = self.pw1.get()
        pw2 = self.pw2.get()

        if not alias:
            messagebox.showwarning("Input", "Alias cannot be empty.")
            return
        if not pw1 or not pw2:
            messagebox.showwarning("Input", "Password cannot be empty.")
            return
        if pw1 != pw2:
            messagebox.showwarning("Input", "Passwords do not match.")
            return

        con = get_conn()
        cur = con.cursor()

        # Alias muss einzigartig sein
        cur.execute("SELECT 1 FROM users WHERE alias = ?", (alias,))
        if cur.fetchone():
            con.close()
            messagebox.showerror("Error", "Alias already exists.")
            return

        cur.execute("INSERT INTO users (alias, password_hash) VALUES (?, ?)", (alias, hash_pw(pw1)))
        con.commit()
        con.close()

        messagebox.showinfo("Success", f"User '{alias}' created. You can now login.")
        self.on_success()
        self.destroy()


class TasksFrame(tk.Frame):
    def __init__(self, master, user):
        super().__init__(master, bg="#121212")
        self.user = user

        # Header
        ttk.Label(self, text=f"Logged in as: {user['alias']}").pack(anchor="w", padx=8, pady=(8, 0))

        # Buttons
        btnbar = ttk.Frame(self)
        btnbar.pack(fill="x", padx=8, pady=8)

        ttk.Button(btnbar, text="Refresh", command=self.refresh).pack(side="left", padx=4)
        ttk.Button(btnbar, text="Create Task", command=self.open_create_dialog).pack(side="left", padx=4)
        ttk.Button(btnbar, text="Complete Task", command=self.complete_selected).pack(side="left", padx=4)
        ttk.Button(btnbar, text="Delete Task", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Button(btnbar, text="Edit Task…", command=self.open_task_editor).pack(side="left", padx=4)
        ttk.Button(btnbar, text="Categories…", command=self.open_categories).pack(side="left", padx=4)
        if self.user.get("is_admin"):
            ttk.Button(btnbar, text="Admin…", command=self.open_admin).pack(side="left", padx=4)
        ttk.Button(btnbar, text="Logout", command=self.do_logout).pack(side="right", padx=4)

        # Listbox + Scrollbar
        list_wrap = tk.Frame(self, bg="#121212")
        list_wrap.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.listbox = tk.Listbox(list_wrap, bg="#1e1e1e", fg="#e8e8e8",
                                  selectbackground="#3b6fd1", selectforeground="white",
                                  highlightthickness=0, borderwidth=0)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_wrap, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Doppelklick öffnet Editor
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_task_editor())

        self.refresh()

    # --- Helpers ---

    def refresh(self):
        self.listbox.delete(0, tk.END)
        rows = get_tasks(self.user['id'], is_admin=bool(self.user.get('is_admin')))
        if not rows:
            self.listbox.insert(tk.END, "No tasks found.")
            return
        for row in rows:
            # Kompatibel, falls alte Daten ohne owner_alias auftauchen
            if len(row) >= 8:
                task_id, title, cat_name, desc, created, completed, due, owner_alias = row
            else:
                task_id, title, cat_name, desc, created, completed, due = row
                owner_alias = None

            status = "✓" if completed == 1 else "•"
            cat_part = f"[{cat_name}] " if cat_name else ""
            owner_part = ""
            # Admin soll alle Owner sehen; optional: immer anzeigen -> entferne die if-Bedingung
            if owner_alias:
                if self.user.get("is_admin"):
                    owner_part = f" — @{owner_alias}"
                # Falls du es IMMER anzeigen willst, nutze stattdessen:
                # owner_part = f" — @{owner_alias}"

            due_part = f" | due: {due}" if due else ""
            self.listbox.insert(tk.END, f"{status} {task_id}: {cat_part}{title}{owner_part}{due_part}")


    def open_categories(self):
        CategoryManager(self)

    def open_admin(self):
        AdminUsersWindow(self)

    def _selected_task_id(self):
        """
        Liest die aktuell selektierte Zeile und extrahiert die Task-ID aus:
        '✓ 12: [Cat] Title | due: 2025-11-01'
        """
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Hinweis", "Bitte zuerst eine Aufgabe auswählen.")
            return None
        line = self.listbox.get(sel[0])
        try:
            after_status = line.split(" ", 1)[1]
            id_str = after_status.split(":", 1)[0]
            return int(id_str.strip())
        except Exception:
            messagebox.showerror("Fehler", "Konnte Task-ID nicht erkennen.")
            return None

    # --- Button actions ---

    def open_task_editor(self):
        tid = self._selected_task_id()
        if tid is None:
            return
        TaskEditor(self, self.user, tid)

    def complete_selected(self):
        tid = self._selected_task_id()
        if tid is None:
            return
        is_admin = bool(self.user.get('is_admin'))
        complete_task(tid, self.user['id'], is_admin=is_admin)
        self.refresh()

    def delete_selected(self):
        tid = self._selected_task_id()
        if tid is None:
            return
        if messagebox.askyesno("Delete", "Task wirklich löschen?"):
            is_admin = bool(self.user.get('is_admin'))
            delete_task(tid, self.user['id'], is_admin=is_admin)
            self.refresh()

    def open_create_dialog(self):
        CreateTaskDialog(self, self.user, on_created=self.refresh)

    def do_logout(self):
        logout_user()
        self.pack_forget()
        self.master.tasks_frame = None
        self.master.login_frame = LoginFrame(self.master, self.master.on_login_success)
        self.master.login_frame.pack(fill="both", expand=True)


class CategoryManager(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Manage Categories")
        self.geometry("460x380")
        self.resizable(False, False)
        self.configure(bg="#121212")

        # Liste
        self.listbox = tk.Listbox(self, bg="#1e1e1e", fg="#e8e8e8",
                                  selectbackground="#3b6fd1", selectforeground="white",
                                  highlightthickness=0, borderwidth=0)
        self.listbox.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        # Button-Leiste
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=(4, 8))

        ttk.Button(bar, text="Add…", command=self.add_category_dialog).pack(side="left", padx=4)
        ttk.Button(bar, text="Delete", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Button(bar, text="Refresh", command=self.refresh).pack(side="left", padx=4)
        ttk.Button(bar, text="Close", command=self.destroy).pack(side="right", padx=4)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        rows = get_categories()
        if not rows:
            self.listbox.insert(tk.END, "No categories found.")
            return
        for (cid, name) in rows:
            self.listbox.insert(tk.END, f"{cid}: {name}")

    def _selected_category_id(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        text = self.listbox.get(sel[0])
        try:
            cid = int(text.split(":")[0])
            return cid
        except Exception:
            return None

    def add_category_dialog(self):
        name = simpledialog.askstring("New Category", "Name:")
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("Input", "Name cannot be empty.")
            return

        desc = simpledialog.askstring("New Category", "Description (optional):")
        if desc is None:
            desc = ""
        try:
            add_category(name, desc or "")
            messagebox.showinfo("Success", f"Category '{name}' created.")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected(self):
        cid = self._selected_category_id()
        if cid is None:
            messagebox.showwarning("Delete", "Please select a category.")
            return
        if not messagebox.askyesno("Delete", f"Delete category ID {cid}? (only if unused)"):
            return
        try:
            delete_category(cid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.refresh()


class AdminUsersWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Admin – Users")
        self.geometry("560x420")
        self.resizable(False, False)
        self.configure(bg="#121212")

        self.listbox = tk.Listbox(self, font=("Consolas", 10),
                                  bg="#1e1e1e", fg="#e8e8e8",
                                  selectbackground="#3b6fd1", selectforeground="white",
                                  highlightthickness=0, borderwidth=0)
        self.listbox.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=(4, 8))

        ttk.Button(bar, text="Refresh", command=self.refresh).pack(side="left", padx=4)
        ttk.Button(bar, text="Unlock", command=self.unlock_selected).pack(side="left", padx=4)
        ttk.Button(bar, text="Reset PW…", command=self.reset_pw_selected).pack(side="left", padx=4)
        ttk.Button(bar, text="Toggle Admin", command=self.toggle_admin_selected).pack(side="left", padx=4)
        ttk.Button(bar, text="Close", command=self.destroy).pack(side="right", padx=4)

        self.refresh()

    # --- Helpers ---

    def _selected_user_id(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Bitte zuerst einen Benutzer auswählen.")
            return None
        line = self.listbox.get(sel[0])
        try:
            # Format: "ID | alias | ROLE | LOCK | Fails:n"
            uid = int(line.split("|", 1)[0].strip())
            return uid
        except Exception:
            messagebox.showerror("Fehler", "Konnte User-ID nicht erkennen.")
            return None

    def refresh(self):
        self.listbox.delete(0, tk.END)
        con = get_conn()
        cur = con.cursor()
        cur.execute("SELECT id, alias, is_admin, locked, failed_attempts FROM users ORDER BY id")
        rows = cur.fetchall()
        con.close()

        if not rows:
            self.listbox.insert(tk.END, "Keine Benutzer gefunden.")
            return

        for (uid, alias, is_admin, locked, fails) in rows:
            role = "ADMIN" if is_admin else "USER"
            lk = "LOCKED" if locked else "OK"
            self.listbox.insert(tk.END, f"{uid:>3} | {alias:<16} | {role:<5} | {lk:<6} | Fails:{fails}")

    # --- Actions ---

    def unlock_selected(self):
        uid = self._selected_user_id()
        if uid is None:
            return
        con = get_conn()
        cur = con.cursor()
        cur.execute("UPDATE users SET locked=0, failed_attempts=0 WHERE id=?", (uid,))
        con.commit()
        con.close()
        messagebox.showinfo("OK", "User entsperrt.")
        self.refresh()

    def reset_pw_selected(self):
        uid = self._selected_user_id()
        if uid is None:
            return
        new_pw = simpledialog.askstring("Reset Password", "Neues Passwort:", show="*")
        if new_pw is None or new_pw.strip() == "":
            return
        con = get_conn()
        cur = con.cursor()
        cur.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_pw(new_pw.strip()), uid))
        con.commit()
        con.close()
        messagebox.showinfo("OK", "Passwort aktualisiert.")
        self.refresh()

    def toggle_admin_selected(self):
        uid = self._selected_user_id()
        if uid is None:
            return
        con = get_conn()
        cur = con.cursor()
        cur.execute("SELECT is_admin FROM users WHERE id=?", (uid,))
        row = cur.fetchone()
        if not row:
            con.close()
            messagebox.showerror("Fehler", "User nicht gefunden.")
            return
        new_flag = 0 if int(row[0]) == 1 else 1
        cur.execute("UPDATE users SET is_admin=? WHERE id=?", (new_flag, uid))
        con.commit()
        con.close()
        messagebox.showinfo("OK", f"Admin-Recht {'gesetzt' if new_flag else 'entfernt'}.")
        self.refresh()


class CreateTaskDialog(tk.Toplevel):
    def __init__(self, master, user, on_created):
        super().__init__(master)
        self.user = user
        self.on_created = on_created
        self.title("Create Task")
        self.configure(bg="#121212")
        self.grab_set()

        # Grid-Konfig
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # --- Admin: Owner-Auswahl laden ---
        self.is_admin = bool(self.user.get("is_admin"))
        self.owner_choices = []   # [(alias, id)]
        self.owner_var = tk.StringVar()
        if self.is_admin:
            try:
                con = get_conn()
                cur = con.cursor()
                cur.execute("SELECT id, alias FROM users ORDER BY alias COLLATE NOCASE")
                rows = cur.fetchall()
            finally:
                con.close()
            self.owner_choices = [(alias, uid) for (uid, alias) in rows]
            # Default: aktueller User vorauswählen (falls vorhanden), sonst erster Eintrag
            default_alias = self.user.get("alias")
            default_alias = default_alias if any(a == default_alias for a, _ in self.owner_choices) else (self.owner_choices[0][0] if self.owner_choices else "")
            self.owner_var.set(default_alias)

        # Title
        ttk.Label(self, text="Title *").grid(row=0, column=0, sticky="w", padx=10, pady=(12, 6))
        self.title_var = tk.StringVar()
        tk.Entry(self, textvariable=self.title_var, width=44,
                 bg="#1e1e1e", fg="#e8e8e8",
                 insertbackground="#e8e8e8",
                 highlightthickness=0, borderwidth=0, relief="flat"
                 ).grid(row=0, column=1, sticky="ew", padx=10, pady=(12, 6))

        # Description
        ttk.Label(self, text="Description").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        self.desc_text = tk.Text(self, height=5,
                                 bg="#1e1e1e", fg="#e8e8e8",
                                 insertbackground="#e8e8e8",
                                 highlightthickness=0, borderwidth=0, relief="flat")
        self.desc_text.grid(row=1, column=1, sticky="nsew", padx=10, pady=6)

        row_idx = 2

        # Admin: Owner-Auswahl anzeigen
        if self.is_admin and self.owner_choices:
            ttk.Label(self, text="Owner").grid(row=row_idx, column=0, sticky="w", padx=10, pady=6)
            self.owner_combo = ttk.Combobox(self, values=[a for a, _ in self.owner_choices],
                                            textvariable=self.owner_var, state="readonly",
                                            width=42, style="Dark.TCombobox")
            self.owner_combo.grid(row=row_idx, column=1, sticky="w", padx=10, pady=6)
            row_idx += 1

        # Category
        ttk.Label(self, text="Category").grid(row=row_idx, column=0, sticky="w", padx=10, pady=6)
        cats = get_categories()  # [(id, name)]
        self.cat_choices = [("— none —", None)] + [(name, cid) for (cid, name) in cats]
        names_only = [name for (name, _cid) in self.cat_choices]
        self.cat_var = tk.StringVar(value=names_only[0])
        self.cat_combo = ttk.Combobox(self, values=names_only,
                                      textvariable=self.cat_var,
                                      state="readonly", width=42,
                                      style="Dark.TCombobox")
        self.cat_combo.grid(row=row_idx, column=1, sticky="w", padx=10, pady=6)
        row_idx += 1

        # New category (optional)
        ttk.Label(self, text="New category (optional)").grid(row=row_idx, column=0, sticky="w", padx=10, pady=6)
        self.new_cat_var = tk.StringVar()
        tk.Entry(self, textvariable=self.new_cat_var, width=44,
                 bg="#1e1e1e", fg="#e8e8e8",
                 insertbackground="#e8e8e8",
                 highlightthickness=0, borderwidth=0, relief="flat"
                 ).grid(row=row_idx, column=1, sticky="w", padx=10, pady=6)
        row_idx += 1

        # Due date
        ttk.Label(self, text="Due date (YYYY-MM-DD, optional)").grid(row=row_idx, column=0, sticky="w", padx=10, pady=6)
        self.due_var = tk.StringVar()
        tk.Entry(self, textvariable=self.due_var, width=22,
                 bg="#1e1e1e", fg="#e8e8e8",
                 insertbackground="#e8e8e8",
                 highlightthickness=0, borderwidth=0, relief="flat"
                 ).grid(row=row_idx, column=1, sticky="w", padx=10, pady=6)
        row_idx += 1

        # Buttons
        btns = ttk.Frame(self)
        btns.grid(row=row_idx, column=0, columnspan=2, pady=12, padx=10, sticky="e")
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right", padx=6)
        ttk.Button(btns, text="Create", style="Primary.TButton", command=self._create).pack(side="right", padx=6)

        # Description-Feld darf wachsen
        self.grid_rowconfigure(1, weight=1)

    def _validate_date(self, val):
        if not val:
            return None
        try:
            datetime.strptime(val, "%Y-%m-%d")
            return val
        except Exception:
            messagebox.showerror("Error", "Due date muss im Format YYYY-MM-DD sein.")
            return "INVALID"

    def _selected_category_id(self):
        chosen_name = self.cat_var.get()
        for (name, cid) in self.cat_choices:
            if name == chosen_name:
                return cid
        return None

    def _owner_user_id(self):
        """Liefert die Ziel-User-ID: bei Admin aus Combobox, sonst aktueller User."""
        if not self.is_admin or not self.owner_choices:
            return self.user['id']
        chosen_alias = self.owner_var.get()
        for alias, uid in self.owner_choices:
            if alias == chosen_alias:
                return uid
        return self.user['id']  # Fallback

    def _create(self):
        title = (self.title_var.get() or "").strip()
        if not title:
            messagebox.showerror("Error", "Title darf nicht leer sein.")
            return

        description = self.desc_text.get("1.0", "end").strip() or None

        # Kategorie: Dropdown oder neues Feld
        new_cat_name = (self.new_cat_var.get() or "").strip()
        if new_cat_name:
            category_id = get_or_create_category(new_cat_name)
        else:
            category_id = self._selected_category_id()

        due = self._validate_date((self.due_var.get() or "").strip())
        if due == "INVALID":
            return

        creation_date = datetime.now().strftime("%Y-%m-%d")
        completed = 0
        owner_user_id = self._owner_user_id()

        try:
            create_task(
                title=title,
                category_id=category_id,
                description=description,
                creation_date=creation_date,
                completed=completed,
                due_date=due,
                user_id=owner_user_id
            )
            owner_hint = f" for @{self.owner_var.get()}" if self.is_admin else ""
            messagebox.showinfo("Success", f"Task created{owner_hint}.")
            self.on_created()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))



class TaskEditor(tk.Toplevel):
    def __init__(self, master, user, task_id):
        super().__init__(master)
        self.user = user
        self.task_id = task_id

        self.title(f"Edit Task {task_id}")
        self.geometry("420x380")
        self.resizable(False, False)
        self.configure(bg="#121212")

        # === Daten laden (Admin darf alle sehen) ===
        rows = get_tasks(user['id'], is_admin=bool(user.get('is_admin')))
        task = next((r for r in rows if r[0] == task_id), None)

        if task is None:
            messagebox.showerror("Error", "Task not found.")
            self.destroy()
            return

        # (_id, title, cat, desc, created, completed, due, [owner_alias])
        if len(task) >= 8:
            (_id, title, cat, desc, created, completed, due, _owner) = task
        else:
            (_id, title, cat, desc, created, completed, due) = task

        self.initial_completed = int(completed)

        # === UI Felder ===
        ttk.Label(self, text="Title:").pack(anchor="w", padx=8, pady=(10, 0))
        self.title_var = tk.StringVar(value=title or "")
        ttk.Entry(self, textvariable=self.title_var).pack(fill="x", padx=8)

        ttk.Label(self, text="Description:").pack(anchor="w", padx=8, pady=(10, 0))
        self.desc_text = tk.Text(self, height=4, bg="#1e1e1e", fg="#e8e8e8",
                                 insertbackground="#e8e8e8", highlightthickness=0, borderwidth=0)
        self.desc_text.pack(fill="both", padx=8)
        if desc:
            self.desc_text.insert("1.0", desc)

        ttk.Label(self, text="Due date (YYYY-MM-DD):").pack(anchor="w", padx=8, pady=(10, 0))
        self.due_var = tk.StringVar(value=due if due else "")
        ttk.Entry(self, textvariable=self.due_var).pack(fill="x", padx=8)

        self.completed_var = tk.IntVar(value=self.initial_completed)
        tk.Checkbutton(self, text="Completed", variable=self.completed_var,
                       bg="#121212", fg="#e8e8e8", selectcolor="#121212").pack(anchor="w", padx=8, pady=(10, 0))

        # Buttons
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", padx=8, pady=10)
        ttk.Button(btn_bar, text="Save", style="Primary.TButton", command=self.save).pack(side="right", padx=8)
        ttk.Button(btn_bar, text="Cancel", command=self.destroy).pack(side="right", padx=8)

    def save(self):
        new_title = self.title_var.get().strip()
        if not new_title:
            messagebox.showwarning("Input", "Title cannot be empty.")
            return

        new_desc = self.desc_text.get("1.0", "end").strip()
        new_due = self.due_var.get().strip()
        new_due = new_due if new_due else None
        new_completed = int(self.completed_var.get())
        is_admin = bool(self.user.get('is_admin'))

        try:
            update_task(
                self.task_id,
                self.user['id'],
                title=new_title,
                description=new_desc,
                due_date=new_due,
                is_admin=is_admin
            )
            if self.initial_completed == 0 and new_completed == 1:
                complete_task(self.task_id, self.user['id'], is_admin=is_admin)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        messagebox.showinfo("Saved", "Task updated.")
        self.master.refresh()
        self.destroy()


if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()
