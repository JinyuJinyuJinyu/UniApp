"""
GUIUniApp.py – Graphical University Enrolment Application
=========================================================
A tkinter-based GUI for registered students to:
  • Log in to their account   (Login Window — main window)
  • View and manage their subject enrolments (max 4)

Run with:
    python GUIUniApp.py

Exception handling covers:
  • Empty login fields
  • Attempt to enrol in more than 4 subjects
"""

import tkinter as tk
from tkinter import ttk, messagebox
from student  import Student
from database import Database


# ── shared database instance ──────────────────────────────────────────────────
DB = Database("students.data")

# ── colour palette ─────────────────────────────────────────────────────────────
C_BG        = "#F0F4F8"
C_PRIMARY   = "#1F5C99"
C_SECONDARY = "#2980B9"
C_ACCENT    = "#27AE60"
C_DANGER    = "#E74C3C"
C_TEXT      = "#2C3E50"
C_LIGHT     = "#ECF0F1"
C_WHITE     = "#FFFFFF"
C_BORDER    = "#BDC3C7"

FONT_TITLE  = ("Arial", 20, "bold")
FONT_SUB    = ("Arial", 12, "bold")
FONT_BODY   = ("Arial", 11)
FONT_SMALL  = ("Arial", 9)
FONT_LABEL  = ("Arial", 11, "bold")


# ═══════════════════════════════════════════════════════════════════════════════
#  REUSABLE WIDGET HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def make_button(parent, text, command, bg=C_PRIMARY, fg=C_WHITE,
                font=FONT_BODY, padx=20, pady=8, width=None):
    """Create a styled flat button."""
    kwargs = dict(
        text=text, command=command, bg=bg, fg=fg, font=font,
        relief="flat", cursor="hand2", padx=padx, pady=pady,
        activebackground=C_SECONDARY, activeforeground=C_WHITE,
    )
    if width:
        kwargs["width"] = width
    return tk.Button(parent, **kwargs)


def make_entry(parent, show=None, width=30):
    """Create a styled entry field."""
    return tk.Entry(
        parent, show=show, width=width, font=FONT_BODY,
        relief="solid", bd=1, bg=C_WHITE, fg=C_TEXT,
        insertbackground=C_TEXT,
    )


def card_frame(parent, **kwargs):
    """A white card frame."""
    return tk.Frame(parent, bg=C_WHITE, relief="groove", bd=1, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
#  LOGIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class LoginWindow:
    """
    Main window of GUIUniApp.

    Presents email and password fields. On successful authentication
    (via Student.check_login_credential), the Enrolment Window opens.

    Exceptions handled
    ------------------
    • Either field is empty → warning dialog
    • Email or password fails pattern validation → warning dialog
    • Credentials do not match any record → error dialog
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self._build_ui()

    def _build_ui(self):
        self.root.title("GUIUniApp – Student Login")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        w, h = 480, 560
        self.root.geometry(f"{w}x{h}")
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # ── header bar ────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=C_PRIMARY, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="🎓  GUIUniApp",
            font=("Arial", 22, "bold"), fg=C_WHITE, bg=C_PRIMARY,
        ).pack(pady=(18, 2))
        tk.Label(
            header, text="University Enrolment System",
            font=FONT_SMALL, fg="#BDC3C7", bg=C_PRIMARY,
        ).pack()

        # ── card ──────────────────────────────────────────────────────────────
        card = card_frame(self.root, padx=40, pady=30)
        card.pack(padx=40, pady=30, fill="both", expand=True)

        tk.Label(
            card, text="Student Login", font=FONT_TITLE,
            fg=C_PRIMARY, bg=C_WHITE,
        ).pack(anchor="w", pady=(0, 20))

        tk.Label(card, text="Email", font=FONT_LABEL, fg=C_TEXT,
                 bg=C_WHITE, anchor="w").pack(fill="x")
        self.email_entry = make_entry(card, width=34)
        self.email_entry.pack(fill="x", pady=(4, 16))

        tk.Label(card, text="Password", font=FONT_LABEL, fg=C_TEXT,
                 bg=C_WHITE, anchor="w").pack(fill="x")
        self.pass_entry = make_entry(card, show="●", width=34)
        self.pass_entry.pack(fill="x", pady=(4, 24))

        make_button(card, "Login", self._handle_login,
                    bg=C_PRIMARY, width=32).pack(fill="x", pady=(0, 12))

        tk.Frame(card, bg=C_BORDER, height=1).pack(fill="x", pady=8)

        tk.Label(
            card,
            text="Note: Registration is available via CLIUniApp.",
            font=FONT_SMALL, fg="#95A5A6", bg=C_WHITE, wraplength=360,
        ).pack(anchor="w", pady=(8, 0))

        self.root.bind("<Return>", lambda e: self._handle_login())

    def _handle_login(self):
        """
        Validate inputs and authenticate the student using
        Student.check_login_credential.

        Exceptions handled
        ------------------
        ValueError  – empty fields OR pattern validation failure
        LookupError – no matching record or bad credentials
        """
        try:
            email    = self.email_entry.get().strip()
            password = self.pass_entry.get().strip()

            # ── exception: empty fields ──
            if not email or not password:
                raise ValueError("Please enter both your email and password.")

            # ── pattern validation ──
            if not Student.validate_email_pattern(email):
                raise ValueError(
                    "Invalid email format.\n\n"
                    "Expected: firstname.lastname@university.com"
                )

            if not Student.validate_password_pattern(password):
                raise ValueError(
                    "Invalid password format.\n\n"
                    "Password must start with an uppercase letter,\n"
                    "contain at least 5 letters, and end with 3 or more digits."
                )

            # ── lookup student ──
            student = DB.find_by_email(email)
            if student is None or not student.check_login_credential(email, password):
                raise LookupError("Invalid email or password. Please try again.")

            # ── success ──
            self._open_enrolment(student)

        except ValueError as exc:
            messagebox.showwarning("Missing or Invalid Information", str(exc),
                                   parent=self.root)
        except LookupError as exc:
            messagebox.showerror("Login Failed", str(exc), parent=self.root)

    def _open_enrolment(self, student: Student):
        """Open the Enrolment Window for the authenticated student."""
        self.root.withdraw()
        top = tk.Toplevel(self.root)
        EnrolmentWindow(top, student, on_close=self._on_enrolment_close)

    def _on_enrolment_close(self):
        """Called when the Enrolment Window closes; restore Login Window."""
        self.root.deiconify()
        self.pass_entry.delete(0, "end")


# ═══════════════════════════════════════════════════════════════════════════════
#  ENROLMENT WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class EnrolmentWindow:
    """
    Enrolment management window.

    Allows a logged-in student to:
      • View their current subject enrolments
      • Enrol in a new subject (up to 4 maximum)
      • Remove an enrolled subject
      • Logout (returns to Login Window)

    Exception handled
    -----------------
    • Enrolment attempt when already at 4 subjects → warning dialog
    """

    def __init__(self, root: tk.Toplevel, student: Student, on_close=None):
        self.root     = root
        self.student  = student
        self.on_close = on_close
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._logout)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self.root.title(f"GUIUniApp – Enrolment  |  {self.student.name}")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        w, h = 620, 620
        self.root.geometry(f"{w}x{h}")
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # ── header ────────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=C_PRIMARY, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        info_frame = tk.Frame(header, bg=C_PRIMARY)
        info_frame.pack(side="left", padx=20, pady=10)

        tk.Label(
            info_frame, text=f"Welcome,  {self.student.name}",
            font=("Arial", 15, "bold"), fg=C_WHITE, bg=C_PRIMARY,
        ).pack(anchor="w")
        tk.Label(
            info_frame,
            text=f"Student ID: {self.student.id}   |   Email: {self.student.email}",
            font=FONT_SMALL, fg="#BDC3C7", bg=C_PRIMARY,
        ).pack(anchor="w")

        make_button(
            header, "Logout", self._logout,
            bg="#C0392B", fg=C_WHITE,
            font=("Arial", 10, "bold"), padx=14, pady=6,
        ).pack(side="right", padx=20, pady=20)

        # ── subject count bar ─────────────────────────────────────────────────
        count_bar = tk.Frame(self.root, bg=C_LIGHT, height=36)
        count_bar.pack(fill="x")
        count_bar.pack_propagate(False)

        self.count_label = tk.Label(
            count_bar, text="",
            font=("Arial", 10, "bold"),
            bg=C_LIGHT, fg=C_TEXT,
        )
        self.count_label.pack(side="left", padx=20, pady=8)

        # ── subject list (Treeview) ───────────────────────────────────────────
        list_frame = tk.Frame(self.root, bg=C_BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(15, 0))

        tk.Label(
            list_frame, text="Enrolled Subjects",
            font=FONT_SUB, fg=C_PRIMARY, bg=C_BG,
        ).pack(anchor="w", pady=(0, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Enrol.Treeview",
            background=C_WHITE, foreground=C_TEXT, rowheight=32,
            fieldbackground=C_WHITE, font=FONT_BODY, bordercolor=C_BORDER,
        )
        style.configure(
            "Enrol.Treeview.Heading",
            background=C_PRIMARY, foreground=C_WHITE,
            font=("Arial", 10, "bold"), relief="flat",
        )
        style.map("Enrol.Treeview", background=[("selected", C_SECONDARY)])

        cols = ("Subject ID", "Mark", "Grade")
        self.tree = ttk.Treeview(
            list_frame, columns=cols, show="headings",
            style="Enrol.Treeview", height=8,
        )
        for col, w in zip(cols, [180, 180, 180]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        scroll = ttk.Scrollbar(list_frame, orient="vertical",
                               command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # ── action buttons ────────────────────────────────────────────────────
        btn_frame = tk.Frame(self.root, bg=C_BG)
        btn_frame.pack(fill="x", padx=20, pady=15)

        make_button(
            btn_frame, "➕  Enrol in Subject", self._handle_enrol,
            bg=C_ACCENT, width=22,
        ).pack(side="left", padx=(0, 10))

        make_button(
            btn_frame, "🗑  Remove Selected", self._handle_remove,
            bg=C_DANGER, width=20,
        ).pack(side="left")

        # ── status bar ────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(
            self.root, textvariable=self.status_var,
            font=FONT_SMALL, fg="#7F8C8D", bg=C_LIGHT,
            anchor="w", padx=12, pady=5,
        ).pack(fill="x", side="bottom")

        self._refresh()

    # ── data & display ────────────────────────────────────────────────────────

    def _refresh(self):
        """Reload student data from file and update all widgets."""
        updated = DB.find_by_email(self.student.email)
        if updated:
            self.student = updated

        for row in self.tree.get_children():
            self.tree.delete(row)

        for subj in self.student.subjects:
            self.tree.insert("", "end", iid=subj.id,
                             values=(subj.id, subj.mark, subj.grade))

        count = len(self.student.subjects)
        max_s = Student.MAX_SUBJECTS
        colour = C_DANGER if count >= max_s else C_PRIMARY
        self.count_label.config(
            text=f"Subjects enrolled: {count} / {max_s}",
            fg=colour,
        )

    # ── event handlers ────────────────────────────────────────────────────────

    def _handle_enrol(self):
        """
        Enrol the student in a new auto-generated subject.

        Exception handled
        -----------------
        RuntimeError – raised when already at MAX_SUBJECTS; displayed as
        a warning messagebox.
        """
        try:
            if len(self.student.subjects) >= Student.MAX_SUBJECTS:
                raise RuntimeError(
                    f"Enrolment limit reached.\n\n"
                    f"You cannot enrol in more than {Student.MAX_SUBJECTS} subjects "
                    f"per semester."
                )

            subject = self.student.enrol()
            if subject is None:
                raise RuntimeError(
                    f"Unable to enrol: maximum of {Student.MAX_SUBJECTS} subjects reached."
                )

            DB.save_student(self.student)
            self._refresh()
            self.status_var.set(
                f"✔  Enrolled in Subject {subject.id}  |  "
                f"Mark: {subject.mark}  |  Grade: {subject.grade}"
            )

        except RuntimeError as exc:
            messagebox.showwarning("Enrolment Limit Reached", str(exc),
                                   parent=self.root)
            self.status_var.set("⚠  Enrolment blocked – maximum subjects reached.")

    def _handle_remove(self):
        """Remove the subject currently selected in the Treeview."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(
                "No Selection",
                "Please select a subject from the list to remove.",
                parent=self.root,
            )
            return

        subject_id = selected[0]
        confirm = messagebox.askyesno(
            "Confirm Removal",
            f"Remove Subject {subject_id} from your enrolment list?",
            parent=self.root,
        )
        if confirm:
            self.student.remove_subject(subject_id)
            DB.save_student(self.student)
            self._refresh()
            self.status_var.set(f"✔  Subject {subject_id} removed.")

    def _logout(self):
        """Close the Enrolment Window and return to Login."""
        self.root.destroy()
        if self.on_close:
            self.on_close()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def show_login_window() -> None:
    """Create the Tk root and launch the Login Window."""
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    show_login_window()
