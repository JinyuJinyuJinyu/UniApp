"""CLIUniApp.py

Student Name: Sai Som Seng
Student ID: 25724218
"""

# Entry point for the CLI version. Most of the actual work lives in
# the controllers, this file just wires them together and shows the
# top-level menu.
#
# Run with:  python CLIUniApp.py

import sys
from database           import Database
from student_controller import StudentController
from admin_controller   import AdminController
from cli_view           import banner, divider, prompt, warn


# One shared database instance for both controllers.
DB = Database("students.data")

student_controller = StudentController(DB)
admin_controller   = AdminController(DB)


def run_main_menu():
    while True:
        banner("CLIUNIAPP - UNIVERSITY ENROLMENT SYSTEM")
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
            warn("Invalid option. Please enter 1-3.")


if __name__ == "__main__":
    try:
        run_main_menu()
    except (KeyboardInterrupt, EOFError):
        # Treat Ctrl+C / EOF as a normal exit instead of a stack trace.
        print("\n  Goodbye!\n")
        sys.exit(0)
