"""
admin.py – Admin model for CLIUniApp
=====================================
Admins are pre-existing university staff. No registration is required.
All admin operations retrieve data from the shared students.data file
via the Database layer.

Note: per the Part 1 class diagram, Admin authenticates with a single
shared password (no email) via check_login_credential(pwd).
"""

from database import Database


# Fixed admin password – admins do not register
_ADMIN_PASSWORD = "admin"


class Admin:
    """
    Provides all student-management operations available to admin users.

    Parameters
    ----------
    db : Database – shared Database instance
    """

    def __init__(self, db: Database):
        self._db = db

    # ── credential checking ───────────────────────────────────────────────────

    @staticmethod
    def check_login_credential(password: str) -> bool:
        """
        Verify the supplied password against the fixed admin credential.

        Returns True if the password matches, False otherwise.
        Admin uses only a password (no email) because the admin subsystem
        has no registration flow.
        """
        return password == _ADMIN_PASSWORD

    # ── read operations ───────────────────────────────────────────────────────

    def view_all_students(self) -> list:
        """Return all registered students from students.data."""
        return self._db.read_all_students()

    def group_by_grade(self) -> dict:
        """
        Organise students by grade.

        Returns
        -------
        dict – keys are grade strings (HD/D/C/P/Z), values are lists of
               Student objects that have at least one subject with that grade.
               A student may appear in multiple groups if they have subjects
               with different grades.
        """
        groups: dict[str, list] = {"HD": [], "D": [], "C": [], "P": [], "Z": []}
        for student in self._db.read_all_students():
            seen_grades: set[str] = set()
            for subj in student.subjects:
                if subj.grade not in seen_grades:
                    groups[subj.grade].append(student)
                    seen_grades.add(subj.grade)
        return groups

    def group_by_pass_fail(self) -> dict:
        """
        Categorise students into PASS / FAIL based on their subject marks.

        A student is PASS if ALL their subjects have mark >= 50,
        FAIL if ANY subject has mark < 50.
        Students with no enrolments are excluded from both groups.

        Returns
        -------
        dict – {"PASS": [...], "FAIL": [...]}
        """
        result: dict[str, list] = {"PASS": [], "FAIL": []}
        for student in self._db.read_all_students():
            if not student.subjects:
                continue
            if all(s.mark >= 50 for s in student.subjects):
                result["PASS"].append(student)
            else:
                result["FAIL"].append(student)
        return result

    # ── write operations ──────────────────────────────────────────────────────

    def remove_student(self, student_id: str) -> bool:
        """
        Delete the student with the given ID from students.data.
        Returns True if the student was found and removed.
        """
        return self._db.delete_student(student_id)

    def clear_student_data(self) -> bool:
        """
        Wipe all student records from students.data.
        Returns True on success.
        """
        return self._db.clear_all()
