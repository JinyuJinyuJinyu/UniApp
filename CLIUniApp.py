"""
CLIUniApp.py – Command-Line University Application
===================================================
Entry point for the interactive CLI system.

Run with:
    python CLIUniApp.py

Two subsystems are available:
  1. Student  – register, login, enrol, manage subjects & password
  2. Admin    – view, organise and manage all student records
"""

import os
import sys
from student  import Student
from admin    import Admin
from database import Database

# ── shared database instance ──────────────────────────────────────────────────
DB = Database("students.data")


# ═══════════════════════════════════════════════════════════════════════════════
#  DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def clear():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def banner(title: str) -> None:
    """Print a formatted section banner."""
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


def divider() -> None:
    print("─" * 60)


def prompt(text: str) -> str:
    """Thin wrapper around input() that strips whitespace."""
    return input(f"  {text}: ").strip()


def info(msg: str)    -> None: print(f"  ✔  {msg}")
def warn(msg: str)    -> None: print(f"  ⚠  {msg}")
def error(msg: str)   -> None: print(f"  ✘  {msg}")
def success(msg: str) -> None: print(f"  ✔  {msg}")


# ═══════════════════════════════════════════════════════════════════════════════
#  STUDENT SUBSYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

def student_register() -> None:
    """
    Guide a new student through the registration process.
    Validates email and password patterns, then saves the new account.
    """
    banner("STUDENT REGISTRATION")

    name = prompt("Full name")
    if not name:
        error("Name cannot be empty.")
        return

    # ── email pattern validation ──
    email = prompt("Email (e.g. john.smith@university.com)")
    if not Student.validate_email_pattern(email):
        error(
            "Invalid email. Must be in the format firstname.lastname@university.com"
        )
        return

    if DB.email_exists(email):
        error("An account with this email already exists.")
        return

    # ── password pattern validation ──
    print()
    print("  Password rules:")
    print("    • Starts with an uppercase letter")
    print("    • Contains at least 5 letters in total")
    print("    • Ends with 3 or more digits")
    print("    Example: David123")
    password = prompt("Password")
    if not Student.validate_password_pattern(password):
        error(
            "Invalid password. It must start with an uppercase letter, "
            "contain at least 5 letters, and end with 3 or more digits."
        )
        return

    # ── create and save ──
    student = Student(name=name, email=email, password=password)
    DB.save_student(student)

    divider()
    success(f"Registration successful!  Your student ID is: {student.id}")


def student_login() -> Student | None:
    """
    Authenticate an existing student via check_login_credential().

    Returns the authenticated Student object on success, None on failure.
    """
    banner("STUDENT LOGIN")

    email    = prompt("Email")
    password = prompt("Password")

    # Pattern-check before looking up (per assignment specification)
    if not Student.validate_email_pattern(email):
        error("Invalid email format.")
        return None

    if not Student.validate_password_pattern(password):
        error("Invalid password format.")
        return None

    # Look up the candidate student
    student = DB.find_by_email(email)

    # Verify credentials via the Student method named in the class diagram
    if student is None or not student.check_login_credential(email, password):
        error("Invalid email or password.")
        return None

    success(f"Welcome back, {student.name}!")
    return student


def student_enrol(student: Student) -> None:
    """Enrol the student in a new auto-generated subject."""
    subject = student.enrol()
    if subject is None:
        warn(
            f"Enrolment limit reached. "
            f"You cannot enrol in more than {Student.MAX_SUBJECTS} subjects."
        )
    else:
        DB.save_student(student)
        success(f"Enrolled in new subject!")
        print(f"     {subject}")


def student_remove(student: Student) -> None:
    """Prompt for a subject ID and remove it from the student's enrolment list."""
    if not student.subjects:
        warn("You have no enrolled subjects to remove.")
        return

    print()
    print("  Your current subjects:")
    for subj in student.subjects:
        print(f"     {subj}")

    subject_id = prompt("Enter Subject ID to remove")
    if student.remove_subject(subject_id):
        DB.save_student(student)
        success(f"Subject {subject_id} has been removed.")
    else:
        error(f"Subject ID '{subject_id}' not found in your enrolment list.")


def student_view(student: Student) -> None:
    """Display the student's current enrolment list."""
    banner("YOUR ENROLMENTS")
    print(f"  Student: {student.name}  (ID: {student.id})\n")
    if not student.subjects:
        info("You have no enrolled subjects.")
    else:
        for subj in student.subjects:
            print(f"     {subj}")
    divider()
    print(f"  Total subjects enrolled: {len(student.subjects)} / {Student.MAX_SUBJECTS}")


def student_change_password(student: Student) -> None:
    """Prompt for a new password and update the student's account."""
    banner("CHANGE PASSWORD")
    print("  Password rules: uppercase start · ≥5 letters · ≥3 digits at end")
    new_password = prompt("New password")

    if student.change_password(new_password):
        DB.save_student(student)
        success("Password updated successfully.")
    else:
        error(
            "Invalid password. "
            "It must start with an uppercase letter, contain at least 5 letters, "
            "and end with 3 or more digits."
        )


def show_student_menu(student: Student) -> None:
    """
    Display and handle the student operations menu.
    Loops until the student chooses to logout.
    """
    while True:
        banner(f"STUDENT MENU  –  {student.name}  (ID: {student.id})")
        print("  [1] Enrol in a subject")
        print("  [2] Remove a subject")
        print("  [3] View enrolled subjects")
        print("  [4] Change password")
        print("  [5] Logout")
        divider()

        choice = prompt("Select option")

        if   choice == "1": student_enrol(student)
        elif choice == "2": student_remove(student)
        elif choice == "3": student_view(student)
        elif choice == "4": student_change_password(student)
        elif choice == "5":
            info("Logged out.")
            break
        else:
            warn("Invalid option. Please enter 1–5.")


def run_student_subsystem() -> None:
    """
    Top-level student subsystem menu.
    Offers Register and Login before entering the student menu.
    """
    while True:
        banner("STUDENT SUBSYSTEM")
        print("  [1] Register")
        print("  [2] Login")
        print("  [3] Back to main menu")
        divider()

        choice = prompt("Select option")

        if choice == "1":
            student_register()
        elif choice == "2":
            student = student_login()
            if student is not None:
                show_student_menu(student)
        elif choice == "3":
            break
        else:
            warn("Invalid option. Please enter 1–3.")


# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN SUBSYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

def admin_view_all(admin: Admin) -> None:
    """Display all registered students."""
    banner("ALL REGISTERED STUDENTS")
    students = admin.view_all_students()
    if not students:
        info("No students registered.")
        return

    for student in students:
        print(f"  {student}")
        if student.subjects:
            for subj in student.subjects:
                print(f"       └─ {subj}")
    divider()
    print(f"  Total students: {len(students)}")


def admin_group_by_grade(admin: Admin) -> None:
    """Display students grouped by subject grade."""
    banner("STUDENTS GROUPED BY GRADE")
    groups = admin.group_by_grade()
    for grade in ["HD", "D", "C", "P", "Z"]:
        students = groups[grade]
        print(f"\n  Grade {grade}  ({len(students)} student(s))")
        divider()
        if not students:
            print("    —")
        else:
            for s in students:
                print(f"    {s}")
                for subj in s.subjects:
                    if subj.grade == grade:
                        print(f"         └─ {subj}")


def admin_group_by_pass_fail(admin: Admin) -> None:
    """Categorise students by PASS / FAIL."""
    banner("STUDENTS BY PASS / FAIL")
    groups = admin.group_by_pass_fail()
    for category in ["PASS", "FAIL"]:
        students = groups[category]
        print(f"\n  {category}  ({len(students)} student(s))")
        divider()
        if not students:
            print("    —")
        else:
            for s in students:
                print(f"    {s}")
                for subj in s.subjects:
                    mark_label = "PASS" if subj.mark >= 50 else "FAIL"
                    print(f"         └─ {subj}  [{mark_label}]")


def admin_remove_student(admin: Admin) -> None:
    """Prompt for a student ID and remove that student."""
    student_id = prompt("Enter Student ID to remove")
    if admin.remove_student(student_id):
        success(f"Student {student_id} has been removed.")
    else:
        error(f"Student ID '{student_id}' not found.")


def admin_clear_data(admin: Admin) -> None:
    """Confirm and clear all student data."""
    banner("CLEAR ALL STUDENT DATA")
    warn("This will permanently delete ALL student records!")
    confirm = prompt("Type 'YES' to confirm")
    if confirm == "YES":
        admin.clear_student_data()
        success("All student data has been cleared.")
    else:
        info("Clear operation cancelled.")


def admin_login() -> Admin | None:
    """
    Authenticate the admin via Admin.check_login_credential().
    Returns an Admin instance on success, None on failure.
    """
    banner("ADMIN LOGIN")
    password = prompt("Admin password")

    if not Admin.check_login_credential(password):
        error("Incorrect admin password.")
        return None

    success("Admin access granted.")
    return Admin(DB)


def show_admin_menu(admin: Admin) -> None:
    """
    Display and handle the admin operations menu.
    Loops until the admin chooses to logout.
    """
    while True:
        banner("ADMIN MENU")
        print("  [1] View all students")
        print("  [2] Group students by grade")
        print("  [3] Categorise students (PASS / FAIL)")
        print("  [4] Remove a student")
        print("  [5] Clear all student data")
        print("  [6] Logout")
        divider()

        choice = prompt("Select option")

        if   choice == "1": admin_view_all(admin)
        elif choice == "2": admin_group_by_grade(admin)
        elif choice == "3": admin_group_by_pass_fail(admin)
        elif choice == "4": admin_remove_student(admin)
        elif choice == "5": admin_clear_data(admin)
        elif choice == "6":
            info("Admin logged out.")
            break
        else:
            warn("Invalid option. Please enter 1–6.")


def run_admin_subsystem() -> None:
    """Authenticate then enter the admin menu."""
    admin = admin_login()
    if admin is not None:
        show_admin_menu(admin)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def run() -> None:
    """Start CLIUniApp and display the top-level menu."""
    while True:
        banner("CLIUNIAPP – UNIVERSITY ENROLMENT SYSTEM")
        print("  [1] Student subsystem")
        print("  [2] Admin subsystem")
        print("  [3] Exit")
        divider()

        choice = prompt("Select option")

        if   choice == "1": run_student_subsystem()
        elif choice == "2": run_admin_subsystem()
        elif choice == "3":
            print("\n  Goodbye!\n")
            sys.exit(0)
        else:
            warn("Invalid option. Please enter 1–3.")


if __name__ == "__main__":
    run()
