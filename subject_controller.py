"""
subject_controller.py – Controller for subject enrolment operations
===================================================================
Coordinates Subject lifecycle for a logged-in Student:
  * enrol in a new subject (auto-generated, max 4)
  * remove a subject by ID
  * list current enrolments

Service methods (pure) are reusable by both CLI and GUI.
Menu methods (run_subject_menu) drive the CLI-only loop.
"""

from student  import Student
from subject  import Subject
from database import Database
from cli_view import (banner, divider, prompt, info, warn, error, success)


class SubjectController:

    def __init__(self, db: Database):
        self._db = db

    # ═════════════════════════════════════════════════════════════════════════
    #  SERVICE METHODS — pure, reusable
    # ═════════════════════════════════════════════════════════════════════════

    def enrol(self, student: Student) -> Subject | None:
        """
        Enrol the student in a new auto-generated subject.

        Returns the new Subject, or None if MAX_SUBJECTS already reached.
        Persists the change.
        """
        subject = student.enrol()
        if subject is None:
            return None
        self._db.save_student(student)
        return subject

    def remove(self, student: Student, subject_id: str) -> bool:
        """
        Remove a subject by ID. Accepts both 3-digit ('042') and trimmed ('42').
        Returns True if removed, False if not found.
        """
        sid = subject_id.strip().zfill(3)
        if not student.remove_subject(sid):
            return False
        self._db.save_student(student)
        return True

    def list_subjects(self, student: Student) -> list:
        """Return the current list of enrolled subjects (refreshed from DB)."""
        fresh = self._db.find_by_email(student.email)
        if fresh is not None:
            student.subjects = fresh.subjects
        return student.subjects

    def change_password(self, student: Student, new_password: str) -> bool:
        """
        Update the student's password (with pattern validation) and persist.
        Returns True on success.
        """
        if not student.change_password(new_password):
            return False
        self._db.save_student(student)
        return True

    # ═════════════════════════════════════════════════════════════════════════
    #  CLI MENU
    # ═════════════════════════════════════════════════════════════════════════

    def run_subject_menu(self, student: Student) -> None:
        """Subject Enrolment menu — runs until logout."""
        while True:
            banner(f"STUDENT MENU  –  {student.name}  (ID: {student.id})")
            print("  [1] Enrol in a subject")
            print("  [2] Remove a subject")
            print("  [3] View enrolled subjects")
            print("  [4] Change password")
            print("  [5] Logout")
            divider()

            choice = prompt("Select option")

            if   choice == "1": self._cli_enrol(student)
            elif choice == "2": self._cli_remove(student)
            elif choice == "3": self._cli_view(student)
            elif choice == "4": self._cli_change_password(student)
            elif choice == "5":
                info("Logged out.")
                return
            else:
                warn("Invalid option. Please enter 1–5.")

    # ── CLI flow handlers (use service methods) ───────────────────────────────

    def _cli_enrol(self, student: Student) -> None:
        if len(student.subjects) >= Student.MAX_SUBJECTS:
            warn(f"Students are allowed to enrol in {Student.MAX_SUBJECTS} subjects only.")
            return

        subject = self.enrol(student)
        success(f"Enrolling in Subject-{int(subject.id)}")
        print(f"     {subject}")
        print(
            f"     You are now enrolled in {len(student.subjects)} out of "
            f"{Student.MAX_SUBJECTS} subjects"
        )

    def _cli_remove(self, student: Student) -> None:
        subjects = self.list_subjects(student)
        if not subjects:
            warn("You have no enrolled subjects to remove.")
            return

        print()
        print("  Your current subjects:")
        for subj in subjects:
            print(f"     {subj}")

        raw = prompt("Enter Subject ID to remove")
        if not raw:
            return

        if not self.remove(student, raw):
            error(f"Subject ID '{raw}' not found in your enrolment list.")
            return

        success(f"Droping Subject-{int(raw.zfill(3))}")
        print(
            f"     You are now enrolled in {len(student.subjects)} out of "
            f"{Student.MAX_SUBJECTS} subjects"
        )

    def _cli_view(self, student: Student) -> None:
        subjects = self.list_subjects(student)

        banner("YOUR ENROLMENTS")
        print(f"  Student: {student.name}  (ID: {student.id})\n")
        print(f"  Showing {len(subjects)} subjects")

        if not subjects:
            info("You have no enrolled subjects.")
        else:
            for subj in subjects:
                print(f"     {subj}")
            divider()
            print(
                f"  Total: {len(subjects)} / {Student.MAX_SUBJECTS}  |  "
                f"Average: {student.average_mark:.2f}  |  "
                f"Overall: {student.overall_grade}"
            )

    def _cli_change_password(self, student: Student) -> None:
        banner("CHANGE PASSWORD")
        print("  Updating Password")
        print("  Rules: uppercase start · 5+ letters · 3+ digits at end")

        new_password = prompt("New password")
        if not Student.validate_password_pattern(new_password):
            error(
                "Invalid password. It must start with an uppercase letter, "
                "contain 5 or more letters, and end with 3 or more digits."
            )
            return

        # Confirm — loop on mismatch
        while True:
            confirm = prompt("Confirm password")
            if confirm == new_password:
                break
            error("Password does not match - try again")

        self.change_password(student, new_password)
        success("Password updated successfully.")
