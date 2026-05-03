"""
CLIUniApp.py – Command-Line University Application (entry point)
=================================================================
Run with:   python CLIUniApp.py

This module is a thin entry point. All business logic lives in:
  - Models      : student.py, subject.py, database.py
  - Controllers : student_controller.py, subject_controller.py, admin_controller.py
  - View        : cli_view.py

CLIUniApp simply instantiates the database, instantiates the top-level
controllers, and routes between them based on the user's menu choice.
"""

import sys
from database           import Database
from student_controller import StudentController
from admin_controller   import AdminController
from cli_view           import banner, divider, prompt, warn


# ── shared application instances ──────────────────────────────────────────────
DB                 = Database("students.data")
student_controller = StudentController(DB)
admin_controller   = AdminController(DB)


def run_main_menu() -> None:
    """Top-level University System menu — dispatches to controllers."""
    while True:
        banner("CLIUNIAPP – UNIVERSITY ENROLMENT SYSTEM")
        print("  [1] Student subsystem")
        print("  [2] Admin subsystem")
        print("  [3] Exit")
        divider()

        choice = prompt("Select option")

        if choice == "1":
            student_controller.run_student_subsystem()
        elif choice == "2":
            admin_controller.run_admin_subsystem()
        elif choice == "3":
            print("\n  Goodbye!\n")
            sys.exit(0)
        else:
            warn("Invalid option. Please enter 1–3.")


if __name__ == "__main__":
    try:
        run_main_menu()
    except (KeyboardInterrupt, EOFError):
        print("\n  Goodbye!\n")
        sys.exit(0)
