"""
database.py – Data-access layer for CLIUniApp / GUIUniApp
=========================================================
Centralises all reading and writing of students.data (JSON format).

Per the assignment spec:
  - check that students.data exists; create it if it doesn't
  - read and write Student objects from/to students.data
  - clear all objects from students.data
"""

import json
import os
from student import Student


class Database:

    def __init__(self, filename: str = "students.data"):
        self.filename = filename
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Ensure students.data exists; create it as an empty JSON array if not."""
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump([], f)

    # ── read ──────────────────────────────────────────────────────────────────

    def read_all_students(self) -> list:
        """Return all Student objects stored in students.data."""
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
        """Return the Student whose email matches (case-insensitive), or None."""
        for student in self.read_all_students():
            if student.email.lower() == email.lower():
                return student
        return None

    def find_by_name(self, name: str) -> Student | None:
        """Return the first Student whose full name matches (case-insensitive), or None."""
        for student in self.read_all_students():
            if student.name.lower() == name.lower():
                return student
        return None

    def find_by_id(self, student_id: str) -> Student | None:
        for student in self.read_all_students():
            if student.id == student_id:
                return student
        return None

    # ── write ─────────────────────────────────────────────────────────────────

    def write_all_students(self, students: list) -> None:
        """Single write path — overwrites students.data with provided list."""
        with open(self.filename, "w") as f:
            json.dump([s.to_dict() for s in students], f, indent=2)

    def save_student(self, student: Student) -> None:
        """
        Persist a student. If a student with the same ID exists they are
        replaced; otherwise the student is appended.
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
        """Remove the student with the given ID. Returns True if found."""
        students = self.read_all_students()
        filtered = [s for s in students if s.id != student_id]
        if len(filtered) == len(students):
            return False
        self.write_all_students(filtered)
        return True

    def clear_all(self) -> bool:
        """Empty the students.data file."""
        try:
            with open(self.filename, "w") as f:
                json.dump([], f)
            return True
        except IOError:
            return False

    # ── query helpers ─────────────────────────────────────────────────────────

    def email_exists(self, email: str) -> bool:
        return self.find_by_email(email) is not None
