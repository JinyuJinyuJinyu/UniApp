"""admin_controller.py 

Student Name: Sai Som Seng
Student ID: 25724218"""


"""
admin_controller.py - Controller for admin operations
======================================================
Admins do not register; they authenticate against a fixed shared password.

Service methods (pure) are reusable by both CLI and GUI.
Menu methods drive the CLI-only loop.

Spec-correct rules:
  * Group by grade : student is placed under their OVERALL grade (computed
                     from average mark). Each student appears exactly once.
                     Students with no enrolments are excluded.
  * PASS / FAIL    : student is in PASS if average_mark >= 50, else FAIL.
                     Students with no enrolled subjects are excluded.
"""

from database import Database
from cli_view import (banner, divider, prompt, info, warn, error, success)


# Fixed admin password - admins do not register
_ADMIN_PASSWORD = "admin"


class AdminController:

    def __init__(self, db: Database):
        self._db = db

    # ═════════════════════════════════════════════════════════════════════════
    #  ADMIN PASSWORD CHECK
    # ═════════════════════════════════════════════════════════════════════════

    #Verify the supplied password against the fixed admin credential. Admin uses only a password (no email).
    @staticmethod
    def check_login_credential(password):
        if password == _ADMIN_PASSWORD:
            return True
        else:
            return False

    # ═════════════════════════════════════════════════════════════════════════
    #  ADMIN FUNCTIONS
    # ═════════════════════════════════════════════════════════════════════════

    #Return all students from "students.data"
    def view_all_students(self):
        return self._db.read_all_students()

    # ═════════════════════════════════════════════════════════════════════════
    #  Grouping by Overall Grade
    # ═════════════════════════════════════════════════════════════════════════

    #Group students by their OVERALL grade
    #Each student appears under exactly one grade key (HD/D/C/P/Z)
    #Students with no enrolments are NOT included

    def group_by_grade(self):
        groups = {"HD": [], 
                    "D": [], 
                    "C": [], 
                    "P": [], 
                    "Z": []}
        for student in self._db.read_all_students():
            if not student.subjects:
                continue

            grade = student.overall_grade

            if grade == "HD":
                groups["HD"].append(student)
            elif grade == "D":
                groups["D"].append(student)
            elif grade == "C":
                groups["C"].append(student)
            elif grade == "P":
                groups["P"].append(student)
            else:
                groups["Z"].append(student)
        
        non_empty_groups = {}

        for grade in groups:
            if len(groups[grade]) > 0:
                non_empty_groups[grade] = groups[grade]
        return non_empty_groups
    
    # ═════════════════════════════════════════════════════════════════════════
    #  Grouping by PASS OR FAIL
    # ═════════════════════════════════════════════════════════════════════════

    #Separating students into PASS / FAIL based on AVERAGE mark >= 50
    #Students with no enrolments are NOT included
    def group_by_pass_fail(self):
        result = {"PASS": [], 
                                   "FAIL": []}
        for student in self._db.read_all_students():
            if not student.subjects:
                continue
            if student.average_mark >= 50:
                result["PASS"].append(student)
            else:
                result["FAIL"].append(student)
        return result
    
    # ═════════════════════════════════════════════════════════════════════════
    #  Deleting Student/s
    # ═════════════════════════════════════════════════════════════════════════

    #Delete the student with the given ID. Returns True if found
    def remove_student(self, student_id):
        return self._db.delete_student(student_id)

    # ═════════════════════════════════════════════════════════════════════════
    #  Clearing Students
    # ═════════════════════════════════════════════════════════════════════════

    #Wipe the entire students.data file
    def clear_student_data(self):
        return self._db.clear_all()

    # ═════════════════════════════════════════════════════════════════════════
    #  CLI Admin MENU Screen
    # ═════════════════════════════════════════════════════════════════════════

    #Authenticate then enter the admin operations menu
    def run_admin_subsystem(self):
        if not self._cli_login():
            return
        self._run_admin_menu()

    # ═════════════════════════════════════════════════════════════════════════
    #  Admin Login and Systems
    # ═════════════════════════════════════════════════════════════════════════

    #Returns True if admin credentials are correct
    def _cli_login(self):
        banner("ADMIN LOGIN")
        password = prompt("Admin password")
        if not self.check_login_credential(password):
            error("Incorrect admin password.")
            return False
        success("Admin access granted.")
        return True

    #Admin operations menu
    def _run_admin_menu(self):
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

            if   choice == "1": 
                self._cli_view_all()
            elif choice == "2": 
                self._cli_group_by_grade()
            elif choice == "3": 
                self._cli_partition_pass_fail()
            elif choice == "4": 
                self._cli_remove_student()
            elif choice == "5": 
                self._cli_clear_data()
            elif choice == "6":
                info("Admin logged out.")
                return
            else:
                warn("Invalid option. Please enter 1-6.")

    # ═════════════════════════════════════════════════════════════════════════
    #  CLI functions
    # ═════════════════════════════════════════════════════════════════════════

    def _cli_view_all(self):
        banner("ALL REGISTERED STUDENTS")
        students = self.view_all_students()
        if not students:
            info("< Nothing to Display >")
            return

        for student in students:
            print(f"  {student}")
            if student.subjects:
                for subj in student.subjects:
                    print(f"       └─ {subj}")
        divider()
        print(f"  Total students: {len(students)}")

    def _cli_group_by_grade(self):
        banner("STUDENTS GROUPED BY GRADE")
        groups = self.group_by_grade()
        if not groups:
            info("< Nothing to Display >")
            return

        for grade in ["HD", "D", "C", "P", "Z"]:
            students = groups.get(grade, [])
            print(f"\n  Grade {grade}  ({len(students)} student(s))")
            divider()
            if not students:
                print("    —")
            else:
                for s in students:
                    print(f"    {s.short_repr()}")

    def _cli_partition_pass_fail(self):
        banner("STUDENTS BY PASS / FAIL")
        parts = self.group_by_pass_fail()
        for category in ["PASS", "FAIL"]:
            students = parts[category]
            print(f"\n  {category}  ({len(students)} student(s))")
            divider()
            if not students:
                print("    —")
            else:
                for s in students:
                    print(f"    {s.short_repr()}")

    def _cli_remove_student(self):
        student_id = prompt("Enter Student ID to remove")
        if not student_id:
            return
        if self.remove_student(student_id):
            success(f"Student {student_id} has been removed.")
        else:
            error(f"Student ID '{student_id}' not found.")

    def _cli_clear_data(self):
        banner("CLEAR ALL STUDENT DATA")
        warn("This will permanently delete ALL student records!")
        confirm = prompt("Are you sure you want to clear the database? (Y)ES/(N)O")
        if confirm.lower() in ("y", "yes"):
            self.clear_student_data()
            success("Students data cleared.")
        else:
            info("Clear operation cancelled.")
