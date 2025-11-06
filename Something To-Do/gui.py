import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

from auth import authenticate, get_logged_in_user, logout_user
from tasks import get_tasks, create_task, complete_task, delete_task, update_task
from categories import get_categories, add_category, delete_category, get_or_create_category


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Something To-Do")
        self.geometry("640x520")
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
        super().__init__(master)
        self.on_success = on_success

        tk.Label(self, text="Alias").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        tk.Label(self, text="Password").grid(row=1, column=0, sticky="w", padx=8, pady=8)

        self.alias_var = tk.StringVar()
        self.pw_var = tk.StringVar()

        tk.Entry(self, textvariable=self.alias_var).grid(row=0, column=1, padx=8, pady=8)
        tk.Entry(self, textvariable=self.pw_var, show="*").grid(row=1, column=1, padx=8, pady=8)

        tk.Button(self, text="Login", command=self.try_login).grid(row=2, column=0, columnspan=2, pady=12)

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


class TasksFrame(tk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user

        # Header
        tk.Label(self, text=f"Logged in as: {user['alias']}", font=("Arial", 12, "bold")).pack(anchor="w", padx=8, pady=(8, 0))

        # Buttons
        btnbar = tk.Frame(self)
        btnbar.pack(fill="x", padx=8, pady=8)

        tk.Button(btnbar, text="Refresh", command=self.refresh).pack(side="left", padx=4)
        tk.Button(btnbar, text="Create Task", command=self.open_create_dialog).pack(side="left", padx=4)
        tk.Button(btnbar, text="Complete Task", command=self.complete_selected).pack(side="left", padx=4)
        tk.Button(btnbar, text="Delete Task", command=self.delete_selected).pack(side="left", padx=4)
        tk.Button(btnbar, text="Edit Task…", command=self.open_task_editor).pack(side="left", padx=4)
        tk.Button(btnbar, text="Categories…", command=self.open_categories).pack(side="left", padx=4)
        tk.Button(btnbar, text="Logout", command=self.do_logout).pack(side="right", padx=4)

        # Listbox + Scrollbar
        list_wrap = tk.Frame(self)
        list_wrap.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.listbox = tk.Listbox(list_wrap)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_wrap, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Doppelklick öffnet Editor
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_task_editor())

        self.refresh()

    # --- Helpers ---

    def refresh(self):
        self.listbox.delete(0, tk.END)
        rows = get_tasks(self.user['id'])
        if not rows:
            self.listbox.insert(tk.END, "No tasks found.")
            return
        for (task_id, title, cat_name, desc, created, completed, due) in rows:
            status = "✓" if completed == 1 else "•"
            cat_part = f"[{cat_name}] " if cat_name else ""
            due_part = f" | due: {due}" if due else ""
            self.listbox.insert(tk.END, f"{status} {task_id}: {cat_part}{title}{due_part}")

    def open_categories(self):
        CategoryManager(self)

    def _selected_task_id(self):
        """
        Liest die aktuell selektierte Zeile und extrahiert die Task-ID aus dem Muster:
        '✓ 12: [Cat] Title | due: 2025-11-01'
        """
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Hinweis", "Bitte zuerst eine Aufgabe auswählen.")
            return None
        line = self.listbox.get(sel[0])
        try:
            # schneide das führende Symbol ab und nimm Zahl vor dem ersten ':'
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
        complete_task(tid, self.user['id'])
        self.refresh()

    def delete_selected(self):
        tid = self._selected_task_id()
        if tid is None:
            return
        if messagebox.askyesno("Delete", "Task wirklich löschen?"):
            delete_task(tid, self.user['id'])
            self.refresh()

    def open_create_dialog(self):
        CreateTaskDialog(self, self.user, on_created=self.refresh)

    def do_logout(self):
        logout_user()
        self.pack_forget()  # TasksFrame verstecken
        self.master.tasks_frame = None
        # zurück zum LoginFrame
        self.master.login_frame = LoginFrame(self.master, self.master.on_login_success)
        self.master.login_frame.pack(fill="both", expand=True)


class CategoryManager(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Manage Categories")
        self.geometry("460x380")
        self.resizable(False, False)

        # Liste
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        # Button-Leiste
        bar = tk.Frame(self)
        bar.pack(fill="x", padx=8, pady=(4, 8))

        tk.Button(bar, text="Add…", command=self.add_category_dialog).pack(side="left", padx=4)
        tk.Button(bar, text="Delete", command=self.delete_selected).pack(side="left", padx=4)
        tk.Button(bar, text="Refresh", command=self.refresh).pack(side="left", padx=4)
        tk.Button(bar, text="Close", command=self.destroy).pack(side="right", padx=4)

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


class CreateTaskDialog(tk.Toplevel):
    def __init__(self, master, user, on_created):
        super().__init__(master)
        self.user = user
        self.on_created = on_created
        self.title("Create Task")
        self.grab_set()  # modaler Dialog

        # Title
        tk.Label(self, text="Title *").grid(row=0, column=0, sticky="w", padx=8, pady=(10, 4))
        self.title_var = tk.StringVar()
        tk.Entry(self, textvariable=self.title_var, width=40).grid(row=0, column=1, padx=8, pady=(10, 4))

        # Description
        tk.Label(self, text="Description").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.desc_var = tk.StringVar()
        tk.Entry(self, textvariable=self.desc_var, width=40).grid(row=1, column=1, padx=8, pady=4)

        # Category dropdown + optional neues Feld
        tk.Label(self, text="Category").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        cats = get_categories()
        self.cat_choices = [("— none —", None)] + [(name, cid) for (cid, name, *_rest) in cats]
        self.cat_var = tk.StringVar(value=self.cat_choices[0][0])

        names_only = [name for (name, _cid) in self.cat_choices]
        self.cat_menu = tk.OptionMenu(self, self.cat_var, *names_only)
        self.cat_menu.grid(row=2, column=1, sticky="w", padx=8, pady=4)

        # New category (optional)
        tk.Label(self, text="New category (optional)").grid(row=3, column=0, sticky="w", padx=8, pady=4)
        self.new_cat_var = tk.StringVar()
        tk.Entry(self, textvariable=self.new_cat_var, width=40).grid(row=3, column=1, padx=8, pady=4)

        # Due date
        tk.Label(self, text="Due date (YYYY-MM-DD, optional)").grid(row=4, column=0, sticky="w", padx=8, pady=4)
        self.due_var = tk.StringVar()
        tk.Entry(self, textvariable=self.due_var, width=20).grid(row=4, column=1, sticky="w", padx=8, pady=4)

        # Buttons
        btns = tk.Frame(self)
        btns.grid(row=5, column=0, columnspan=2, pady=12)
        tk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=6)
        tk.Button(btns, text="Create", command=self._create).pack(side="left", padx=6)

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

    def _create(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Title darf nicht leer sein.")
            return

        description = self.desc_var.get().strip() or None

        # Kategorie: entweder Dropdown, oder "New category" Feld
        new_cat_name = self.new_cat_var.get().strip()
        if new_cat_name:
            category_id = get_or_create_category(new_cat_name)
        else:
            category_id = self._selected_category_id()

        due = self._validate_date(self.due_var.get().strip())
        if due == "INVALID":
            return

        creation_date = datetime.now().strftime("%Y-%m-%d")
        completed = 0

        try:
            create_task(
                title=title,
                category_id=category_id,
                description=description,
                creation_date=creation_date,
                completed=completed,
                due_date=due,
                user_id=self.user['id']
            )
            messagebox.showinfo("Success", "Task created.")
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

        # === Daten laden ===
        rows = get_tasks(user['id'])
        task = next((r for r in rows if r[0] == task_id), None)

        if task is None:
            messagebox.showerror("Error", "Task not found.")
            self.destroy()
            return

        (_id, title, cat, desc, created, completed, due) = task
        self.initial_completed = int(completed)  # merken, um später zu wissen, ob wir "complete" setzen müssen

        # === UI Felder ===
        tk.Label(self, text="Title:").pack(anchor="w", padx=8, pady=(10, 0))
        self.title_var = tk.StringVar(value=title or "")
        tk.Entry(self, textvariable=self.title_var).pack(fill="x", padx=8)

        tk.Label(self, text="Description:").pack(anchor="w", padx=8, pady=(10, 0))
        self.desc_text = tk.Text(self, height=4)
        self.desc_text.pack(fill="both", padx=8)
        if desc:
            self.desc_text.insert("1.0", desc)

        tk.Label(self, text="Due date (YYYY-MM-DD):").pack(anchor="w", padx=8, pady=(10, 0))
        self.due_var = tk.StringVar(value=due if due else "")
        tk.Entry(self, textvariable=self.due_var).pack(fill="x", padx=8)

        self.completed_var = tk.IntVar(value=self.initial_completed)
        tk.Checkbutton(self, text="Completed", variable=self.completed_var).pack(anchor="w", padx=8, pady=(10, 0))

        # Buttons
        btn_bar = tk.Frame(self)
        btn_bar.pack(fill="x", padx=8, pady=10)
        tk.Button(btn_bar, text="Save", command=self.save).pack(side="right", padx=8)
        tk.Button(btn_bar, text="Cancel", command=self.destroy).pack(side="right", padx=8)

    def save(self):
        new_title = self.title_var.get().strip()
        if not new_title:
            messagebox.showwarning("Input", "Title cannot be empty.")
            return

        new_desc = self.desc_text.get("1.0", "end").strip()
        new_due = self.due_var.get().strip()
        new_due = new_due if new_due else None
        new_completed = int(self.completed_var.get())

        try:
            # 1) Felder (ohne completed) aktualisieren – deine update_task nimmt completed nicht an
            update_task(
                self.task_id,
                self.user['id'],
                title=new_title,
                description=new_desc,
                due_date=new_due
            )

            # 2) Wenn vorher offen (0) und jetzt gesetzt (1): als erledigt markieren
            if self.initial_completed == 0 and new_completed == 1:
                complete_task(self.task_id, self.user['id'])

        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        messagebox.showinfo("Saved", "Task updated.")
        self.master.refresh()
        self.destroy()


if __name__ == "__main__":
    # Starte nur die GUI (CLI bleibt unabhängig in main.py)
    app = App()
    app.mainloop()
