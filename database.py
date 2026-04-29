"""
database.py – Data-access layer for CLIUniApp / GUIUniApp
=========================================================
All reading and writing of students.data is centralised here.
The file format is a JSON array of student objects:

  [
    {"id": "...", "name": "...", "email": "...", "password": "...",
     "subjects": [{"id": "...", "mark": 87, "grade": "HD"}, ...]},
    ...
  ]

An empty file (or "[]") means no students.
"""

import json
import os
from student import Student


class Database:
    """
    Provides CRUD operations for the students.data flat file.

    Parameters
    ----------
    filename : str – path to the data file (default: "students.data")
    """

    def __init__(self, filename: str = "students.data"):
        self.filename = filename
        # Ensure the file exists and contains a valid empty JSON array
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump([], f)

    # ── read ──────────────────────────────────────────────────────────────────

    def read_all_students(self) -> list:
        """
        Load and return all Student objects from the data file.
        Returns an empty list if the file is empty or does not exist.
        """
        try:
            with open(self.filename, "r") as f:
                content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        return [Student.from_dict(d) for d in data]

    def find_by_email(self, email: str) -> Student | None:
        """
        Return the Student whose email matches (case-insensitive), or None.
        """
        for student in self.read_all_students():
            if student.email.lower() == email.lower():
                return student
        return None

    def find_by_id(self, student_id: str) -> Student | None:
        """Return the Student with the given ID, or None."""
        for student in self.read_all_students():
            if student.id == student_id:
                return student
        return None

    # ── write ─────────────────────────────────────────────────────────────────

    def write_all_students(self, students: list) -> None:
        """
        Overwrite students.data with the provided list of Student objects.
        This is the single write path – all mutation goes through here.
        """
        with open(self.filename, "w") as f:
            json.dump([s.to_dict() for s in students], f, indent=2)

    def save_student(self, student: Student) -> None:
        """
        Persist a student. If a student with the same ID already exists,
        they are replaced; otherwise the new student is appended.
        """
        students = self.read_all_students()
        for i, s in enumerate(students):
            if s.id == student.id:
                students[i] = student
                self.write_all_students(students)
                return
        students.append(student)
        self.write_all_students(students)

    # ── delete ────────────────────────────────────────────────────────────────

    def delete_student(self, student_id: str) -> bool:
        """
        Remove the student with the given ID from the data file.
        Returns True if found and deleted, False otherwise.
        """
        students = self.read_all_students()
        filtered = [s for s in students if s.id != student_id]
        if len(filtered) == len(students):
            return False
        self.write_all_students(filtered)
        return True

    def clear_all(self) -> bool:
        """Empty the students.data file. Returns True on success."""
        try:
            with open(self.filename, "w") as f:
                json.dump([], f)
            return True
        except IOError:
            return False

    # ── query helpers ─────────────────────────────────────────────────────────

    def email_exists(self, email: str) -> bool:
        """Return True if an account with this email is already registered."""
        return self.find_by_email(email) is not None
