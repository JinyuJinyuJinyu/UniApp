"""
GUIUniApp.py – Graphical University Enrolment Application
=========================================================
Per the assignment marking scheme, GUIUniApp provides FOUR distinct windows:

  1. Login Window       – main window; reads students.data via StudentController
  2. Enrolment Window   – action panel: enrol new subjects (max 4)
  3. Subject Window     – list of enrolled subjects with marks & grades
  4. Exception Window   – modal dialog for format errors and overflow

The GUI is a pure View layer — all data operations go through the
StudentController and SubjectController service methods. tkinter widgets
never touch the Database directly.

Run with:
    python GUIUniApp.py
"""

import tkinter as tk
from tkinter import ttk
from student            import Student
from database           import Database
from student_controller import (
    StudentController,
    ERR_BAD_EMAIL_FORMAT,
    ERR_BAD_PASSWORD_FORMAT,
    ERR_NOT_FOUND,
)
from subject_controller import SubjectController


# ── shared controllers (one Database, shared by both controllers) ────────────
DB                  = Database("students.data")
student_controller  = StudentController(DB)
subject_controller  = SubjectController(DB)

# ── colour palette ────────────────────────────────────────────────────────────
C_BG        = "#F0F4F8"
C_PRIMARY   = "#1F5C99"
C_SECONDARY = "#2980B9"
C_ACCENT    = "#27AE60"
C_DANGER    = "#E74C3C"
C_TEXT      = "#2C3E50"
C_LIGHT     = "#ECF0F1"
C_WHITE     = "#FFFFFF"
C_BORDER    = "#BDC3C7"

FONT_TITLE = ("Arial", 20, "bold")
FONT_SUB   = ("Arial", 12, "bold")
FONT_BODY  = ("Arial", 11)
FONT_SMALL = ("Arial", 9)
FONT_LABEL = ("Arial", 11, "bold")


# ═══════════════════════════════════════════════════════════════════════════════
#  WINDOW 4 — EXCEPTION WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class ExceptionWindow(tk.Toplevel):
    """
    Custom modal exception/notification window.

    Used for all error and warning notifications:
      - empty login fields
      - invalid email or password format
      - incorrect credentials
      - enrolment limit reached
    """

    def __init__(self, parent, title: str, message: str, kind: str = "error"):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=C_BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        ww, wh = 460, 220
        x = parent.winfo_rootx() + (parent.winfo_width()  - ww) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - wh) // 2
        self.geometry(f"{ww}x{wh}+{max(x,0)}+{max(y,0)}")

        header_color = {
            "error":   C_DANGER,
            "warning": "#E67E22",
            "info":    C_PRIMARY,
        }.get(kind, C_DANGER)
        tk.Frame(self, bg=header_color, height=8).pack(fill="x")

        icon = {"error": "✘", "warning": "⚠", "info": "ⓘ"}.get(kind, "✘")
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(body, text=icon, font=("Arial", 36, "bold"),
                 fg=header_color, bg=C_BG).pack(side="left", padx=(0, 16))
        right = tk.Frame(body, bg=C_BG)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text=title, font=FONT_TITLE, fg=C_TEXT,
                 bg=C_BG, anchor="w").pack(fill="x")
        tk.Label(right, text=message, font=FONT_BODY, fg=C_TEXT,
                 bg=C_BG, anchor="w", justify="left",
                 wraplength=320).pack(fill="x", pady=(8, 0))

        btn_frame = tk.Frame(self, bg=C_BG)
        btn_frame.pack(fill="x", padx=24, pady=(0, 18))
        tk.Button(
            btn_frame, text="OK", command=self.destroy,
            bg=header_color, fg=C_WHITE, font=("Arial", 11, "bold"),
            relief="flat", cursor="hand2", padx=24, pady=6,
            activebackground=C_SECONDARY, activeforeground=C_WHITE,
        ).pack(side="right")

        self.bind("<Return>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy())
        self.wait_window(self)


# ═══════════════════════════════════════════════════════════════════════════════
#  WINDOW 1 — LOGIN WINDOW (main)
# ═══════════════════════════════════════════════════════════════════════════════

class LoginWindow:
    """Main window — authenticates via StudentController.login()."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self._build_ui()

    def _build_ui(self):
        self.root.title("GUIUniApp – Student Login")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        ww, wh = 480, 560
        self.root.geometry(f"{ww}x{wh}")
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - ww) // 2
        y = (self.root.winfo_screenheight() - wh) // 2
        self.root.geometry(f"{ww}x{wh}+{x}+{y}")

        # Header
        header = tk.Frame(self.root, bg=C_PRIMARY, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🎓  GUIUniApp",
                 font=("Arial", 22, "bold"), fg=C_WHITE,
                 bg=C_PRIMARY).pack(pady=(18, 2))
        tk.Label(header, text="University Enrolment System",
                 font=FONT_SMALL, fg="#BDC3C7",
                 bg=C_PRIMARY).pack()

        # Card
        card = tk.Frame(self.root, bg=C_WHITE, relief="groove", bd=1)
        card.pack(padx=40, pady=30, fill="both", expand=True)

        tk.Label(card, text="Student Login", font=FONT_TITLE,
                 fg=C_PRIMARY, bg=C_WHITE).pack(anchor="w", padx=40, pady=(30, 20))

        tk.Label(card, text="Email", font=FONT_LABEL, fg=C_TEXT,
                 bg=C_WHITE, anchor="w").pack(fill="x", padx=40)
        self.email_entry = tk.Entry(card, font=FONT_BODY, relief="solid",
                                    bd=1, bg=C_WHITE, fg=C_TEXT,
                                    insertbackground=C_TEXT)
        self.email_entry.pack(fill="x", padx=40, pady=(4, 16), ipady=4)

        tk.Label(card, text="Password", font=FONT_LABEL, fg=C_TEXT,
                 bg=C_WHITE, anchor="w").pack(fill="x", padx=40)
        self.pass_entry = tk.Entry(card, show="●", font=FONT_BODY, relief="solid",
                                   bd=1, bg=C_WHITE, fg=C_TEXT,
                                   insertbackground=C_TEXT)
        self.pass_entry.pack(fill="x", padx=40, pady=(4, 24), ipady=4)

        tk.Button(
            card, text="Login", command=self._handle_login,
            bg=C_PRIMARY, fg=C_WHITE, font=FONT_BODY,
            relief="flat", cursor="hand2", pady=8,
            activebackground=C_SECONDARY, activeforeground=C_WHITE,
        ).pack(fill="x", padx=40, pady=(0, 12))

        tk.Frame(card, bg=C_BORDER, height=1).pack(fill="x", padx=40, pady=8)
        tk.Label(card,
                 text="Note: Registration is available via CLIUniApp.",
                 font=FONT_SMALL, fg="#95A5A6", bg=C_WHITE,
                 wraplength=360).pack(anchor="w", padx=40, pady=(8, 30))

        self.root.bind("<Return>", lambda e: self._handle_login())

    def _handle_login(self):
        """Authenticate via the controller and react to its result."""
        email    = self.email_entry.get().strip()
        password = self.pass_entry.get().strip()

        # GUI-specific concern: empty fields
        if not email or not password:
            ExceptionWindow(self.root, "Missing Information",
                            "Please enter both your email and password.",
                            kind="warning")
            return

        # Delegate to controller
        student, err = student_controller.login(email, password)

        if err == ERR_BAD_EMAIL_FORMAT:
            ExceptionWindow(self.root, "Invalid Email",
                            "Email must be in the form\n"
                            "firstname.lastname@university.com",
                            kind="warning")
            return
        if err == ERR_BAD_PASSWORD_FORMAT:
            ExceptionWindow(self.root, "Invalid Password",
                            "Password must start with an uppercase letter, "
                            "contain 5 or more letters, and end with 3 or more digits.",
                            kind="warning")
            return
        if err == ERR_NOT_FOUND:
            ExceptionWindow(self.root, "Login Failed",
                            "Student does not exist or credentials are incorrect.",
                            kind="error")
            return

        # success — open enrolment window
        self.root.withdraw()
        top = tk.Toplevel(self.root)
        EnrolmentWindow(top, student, on_close=self._on_close)

    def _on_close(self):
        """Restore the Login Window when a child window closes."""
        self.root.deiconify()
        self.pass_entry.delete(0, "end")


# ═══════════════════════════════════════════════════════════════════════════════
#  WINDOW 2 — ENROLMENT WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class EnrolmentWindow:
    """Action panel: enrol new subjects via SubjectController.enrol()."""

    def __init__(self, root: tk.Toplevel, student: Student, on_close=None):
        self.root     = root
        self.student  = student
        self.on_close = on_close
        self._subject_win = None
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._logout)

    def _build_ui(self):
        self.root.title(f"GUIUniApp – Enrolment  |  {self.student.name}")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        ww, wh = 580, 480
        self.root.geometry(f"{ww}x{wh}")
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - ww) // 2
        y = (self.root.winfo_screenheight() - wh) // 2
        self.root.geometry(f"{ww}x{wh}+{x}+{y}")

        # Header
        header = tk.Frame(self.root, bg=C_PRIMARY, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        info = tk.Frame(header, bg=C_PRIMARY)
        info.pack(side="left", padx=20, pady=10)

        tk.Label(info, text=f"Welcome, {self.student.name}",
                 font=("Arial", 15, "bold"), fg=C_WHITE,
                 bg=C_PRIMARY).pack(anchor="w")
        tk.Label(info,
                 text=f"Student ID: {self.student.id} · {self.student.email}",
                 font=FONT_SMALL, fg="#BDC3C7", bg=C_PRIMARY).pack(anchor="w")

        tk.Button(header, text="Logout", command=self._logout,
                  bg="#C0392B", fg=C_WHITE, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", padx=14, pady=6,
                  activebackground="#A93226",
                  activeforeground=C_WHITE).pack(side="right", padx=20, pady=20)

        # Body
        body = tk.Frame(self.root, bg=C_BG)
        body.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(body, text="Enrol in a New Subject",
                 font=FONT_TITLE, fg=C_PRIMARY, bg=C_BG,
                 anchor="w").pack(fill="x", pady=(0, 8))

        tk.Label(body,
                 text=("Each enrolment auto-generates a Subject ID, a random "
                       "mark (25–100), and the corresponding grade.\n"
                       "You may enrol in up to 4 subjects per semester."),
                 font=FONT_BODY, fg=C_TEXT, bg=C_BG,
                 wraplength=520, justify="left").pack(anchor="w", pady=(0, 20))

        counter_frame = tk.Frame(body, bg=C_LIGHT, height=44)
        counter_frame.pack(fill="x", pady=(0, 20))
        counter_frame.pack_propagate(False)
        self.counter_var = tk.StringVar(value="")
        tk.Label(counter_frame, textvariable=self.counter_var,
                 font=("Arial", 12, "bold"), fg=C_TEXT,
                 bg=C_LIGHT).pack(side="left", padx=20, pady=8)

        btns = tk.Frame(body, bg=C_BG)
        btns.pack(fill="x")

        tk.Button(btns, text="➕  Enrol in Subject", command=self._handle_enrol,
                  bg=C_ACCENT, fg=C_WHITE, font=FONT_BODY, relief="flat",
                  cursor="hand2", padx=20, pady=12, width=22,
                  activebackground="#1E8449",
                  activeforeground=C_WHITE).pack(side="left", padx=(0, 12))

        tk.Button(btns, text="📋  View My Subjects",
                  command=self._open_subject_window,
                  bg=C_PRIMARY, fg=C_WHITE, font=FONT_BODY, relief="flat",
                  cursor="hand2", padx=20, pady=12, width=22,
                  activebackground=C_SECONDARY,
                  activeforeground=C_WHITE).pack(side="left")

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(self.root, textvariable=self.status_var,
                 font=FONT_SMALL, fg="#7F8C8D", bg=C_LIGHT,
                 anchor="w", padx=12, pady=5).pack(fill="x", side="bottom")

        self._refresh()

    def _refresh(self):
        """Re-read student via the controller so UI shows persisted state."""
        subjects = subject_controller.list_subjects(self.student)
        count = len(subjects)
        self.counter_var.set(
            f"Subjects enrolled: {count} / {Student.MAX_SUBJECTS}"
        )

    def _handle_enrol(self):
        """Try to enrol via SubjectController.enrol()."""
        subject = subject_controller.enrol(self.student)
        if subject is None:
            ExceptionWindow(
                self.root,
                "Enrolment Limit Reached",
                f"Students are allowed to enrol in {Student.MAX_SUBJECTS} subjects only.",
                kind="warning",
            )
            self.status_var.set("⚠  Enrolment blocked – maximum subjects reached.")
            return

        self._refresh()
        self.status_var.set(
            f"✔  Enrolled in Subject {subject.id}  |  "
            f"Mark: {subject.mark}  |  Grade: {subject.grade}"
        )

        if self._subject_win is not None and self._subject_win.is_open():
            self._subject_win.refresh(self.student)

    def _open_subject_window(self):
        if self._subject_win is not None and self._subject_win.is_open():
            self._subject_win.focus()
            return
        sub_root = tk.Toplevel(self.root)
        self._subject_win = SubjectWindow(sub_root, self.student)

    def _logout(self):
        if self._subject_win is not None and self._subject_win.is_open():
            self._subject_win.close()
        self.root.destroy()
        if self.on_close:
            self.on_close()


# ═══════════════════════════════════════════════════════════════════════════════
#  WINDOW 3 — SUBJECT WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class SubjectWindow:
    """Lists enrolled subjects with their marks and grades."""

    def __init__(self, root: tk.Toplevel, student: Student):
        self.root    = root
        self.student = student
        self._open   = True
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def is_open(self) -> bool: return self._open

    def focus(self) -> None:
        if self._open:
            self.root.lift()
            self.root.focus_force()

    def close(self) -> None:
        self._open = False
        try: self.root.destroy()
        except tk.TclError: pass

    def refresh(self, student: Student) -> None:
        if not self._open: return
        self.student = student
        self._populate_tree()

    def _build_ui(self):
        self.root.title(f"GUIUniApp – Subjects  |  {self.student.name}")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        ww, wh = 560, 480
        self.root.geometry(f"{ww}x{wh}")

        header = tk.Frame(self.root, bg=C_PRIMARY, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Enrolled Subjects",
                 font=("Arial", 16, "bold"), fg=C_WHITE,
                 bg=C_PRIMARY).pack(side="left", padx=20, pady=20)
        self.summary_var = tk.StringVar(value="")
        tk.Label(header, textvariable=self.summary_var,
                 font=FONT_SMALL, fg="#BDC3C7",
                 bg=C_PRIMARY).pack(side="right", padx=20, pady=24)

        body = tk.Frame(self.root, bg=C_BG)
        body.pack(fill="both", expand=True, padx=20, pady=15)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Subj.Treeview",
            background=C_WHITE, foreground=C_TEXT, rowheight=32,
            fieldbackground=C_WHITE, font=FONT_BODY, bordercolor=C_BORDER)
        style.configure("Subj.Treeview.Heading",
            background=C_PRIMARY, foreground=C_WHITE,
            font=("Arial", 10, "bold"), relief="flat")
        style.map("Subj.Treeview", background=[("selected", C_SECONDARY)])

        cols = ("Subject ID", "Mark", "Grade")
        self.tree = ttk.Treeview(body, columns=cols, show="headings",
                                 style="Subj.Treeview", height=10)
        for col, w in zip(cols, [180, 180, 180]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        scroll = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        actions = tk.Frame(self.root, bg=C_BG)
        actions.pack(fill="x", padx=20, pady=(0, 18))
        tk.Button(actions, text="🗑  Remove Selected", command=self._handle_remove,
                  bg=C_DANGER, fg=C_WHITE, font=FONT_BODY, relief="flat",
                  cursor="hand2", padx=20, pady=8,
                  activebackground="#A93226",
                  activeforeground=C_WHITE).pack(side="left")
        tk.Button(actions, text="Close", command=self.close,
                  bg=C_LIGHT, fg=C_TEXT, font=FONT_BODY, relief="flat",
                  cursor="hand2", padx=20, pady=8).pack(side="right")

        self._populate_tree()

    def _populate_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for subj in self.student.subjects:
            self.tree.insert("", "end", iid=subj.id,
                             values=(subj.id, subj.mark, subj.grade))
        avg   = self.student.average_mark
        grade = self.student.overall_grade if self.student.subjects else "—"
        self.summary_var.set(
            f"{len(self.student.subjects)} / {Student.MAX_SUBJECTS}   |   "
            f"Avg: {avg:.2f}   |   Overall grade: {grade}"
        )

    def _handle_remove(self):
        sel = self.tree.selection()
        if not sel:
            ExceptionWindow(self.root, "No Selection",
                            "Select a subject in the list, then click Remove.",
                            kind="info")
            return
        sid = sel[0]
        if subject_controller.remove(self.student, sid):
            self._populate_tree()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def show_login_window() -> None:
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    show_login_window()
