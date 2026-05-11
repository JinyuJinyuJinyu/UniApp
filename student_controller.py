"""Student_controller.py

Student Name: Sai Som Seng
Student ID: 25724218
"""

# Handles student registration and login. Once a student is logged
# in, this hands off to SubjectController for the per-student menu.

from student            import Student
from database           import Database
from subject_controller import SubjectController
from cli_view           import (banner, divider, prompt, info, warn, error, success)


# Error codes returned by register()/login(). The CLI and GUI both
# check these so each can show its own messages.
ERR_BAD_EMAIL_FORMAT    = "BAD_EMAIL_FORMAT"
ERR_BAD_PASSWORD_FORMAT = "BAD_PASSWORD_FORMAT"
ERR_DUPLICATE           = "DUPLICATE"
ERR_NOT_FOUND           = "NOT_FOUND"


class StudentController:

    def __init__(self, db: Database):
        self._db = db
        self._subject_controller = SubjectController(db)

    def register(self, name, email, password):
        if not Student.validate_email_pattern(email):
            return None, ERR_BAD_EMAIL_FORMAT
        if not Student.validate_password_pattern(password):
            return None, ERR_BAD_PASSWORD_FORMAT
        if self._db.email_exists(email):
            return None, ERR_DUPLICATE

        student = Student(name=name, email=email, password=password)
        self._db.save_student(student)
        return student, None

    def login(self, email, password):
        if not Student.validate_email_pattern(email):
            return None, ERR_BAD_EMAIL_FORMAT
        if not Student.validate_password_pattern(password):
            return None, ERR_BAD_PASSWORD_FORMAT

        candidate = self._db.find_by_email(email)
        if candidate is None or not candidate.check_login_credential(email, password):
            return None, ERR_NOT_FOUND

        return candidate, None

    # CLI-only menu below.

    def run_student_subsystem(self):
        while True:
            banner("STUDENT SUBSYSTEM")
            print("  [1] Register")
            print("  [2] Login")
            print("  [3] Back to main menu")
            divider()

            choice = prompt("Select option")

            if   choice == "1":
                self._cli_register()
            elif choice == "2":
                student = self._cli_login()
                if student is not None:
                    self._subject_controller.run_subject_menu(student)
            elif choice == "3":
                return
            else:
                warn("Invalid option. Please enter 1-3.")

    def _cli_register(self):
        # Order: email -> password -> format checks -> duplicate check -> name -> save.
        banner("STUDENT REGISTRATION")

        email = prompt("Email (e.g. john.smith@university.com)")
        if not Student.validate_email_pattern(email):
            error("Invalid email. Must be in the format firstname.lastname@university.com")
            return

        print()
        print("  Password rules:")
        print("    • Starts with an uppercase letter")
        print("    • Followed by 5 or more letters")
        print("    • Ends with 3 or more digits")
        print("    Example: Helloworld123")
        password = prompt("Password")
        if not Student.validate_password_pattern(password):
            error(
                "Invalid password. It must start with an uppercase letter, "
                "contain 5 or more letters, and end with 3 or more digits."
            )
            return

        info("email and password formats acceptable")

        existing = self._db.find_by_email(email)
        if existing is not None:
            error(f"Student {existing.name} already exists.")
            return

        # Only ask for the name once everything else has passed.
        name = prompt("Full name")
        if not name:
            error("Name cannot be empty.")
            return

        student, err = self.register(name=name, email=email, password=password)
        # Shouldn't actually trigger since we already checked everything,
        # but it's cheap insurance.
        if err is not None:
            error(f"Registration failed: {err}")
            return

        divider()
        success(f"Enrolling Student {name}")
        success(f"Registration successful! Your student ID is: {student.id}")

    def _cli_login(self):
        banner("STUDENT LOGIN")

        email    = prompt("Email")
        password = prompt("Password")

        student, err = self.login(email, password)
        if err == ERR_BAD_EMAIL_FORMAT:
            error("Invalid email format.")
            return None
        if err == ERR_BAD_PASSWORD_FORMAT:
            error("Invalid password format.")
            return None
        if err == ERR_NOT_FOUND:
            error("Student does not exist.")
            return None

        info("email and password formats acceptable")
        success(f"Welcome back, {student.name}!")
        return student
