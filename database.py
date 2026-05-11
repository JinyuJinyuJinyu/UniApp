"""database.py

Student Name: Hang Wang
Student ID: 14734281
"""

# All reads/writes to students.data go through this class.
# The file is just a JSON array of student dicts.

import json
import os
from student import Student


class Database:

    def __init__(self, filename: str = "students.data"):
        self.filename = filename
        self._ensure_file()

    def _ensure_file(self) -> None:
        # If the data file isn't there yet, drop in an empty list so the
        # rest of the code can assume it exists.
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump([], f)

    def read_all_students(self) -> list:
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
        # Case-insensitive lookup. Returns None if no match.
        for student in self.read_all_students():
            if student.email.lower() == email.lower():
                return student
        return None

    def write_all_students(self, students: list) -> None:
        # Everything writes through here so the format stays consistent.
        with open(self.filename, "w") as f:
            json.dump([s.to_dict() for s in students], f, indent=2)

    def save_student(self, student: Student) -> None:
        # Replace if an entry with the same ID is already there,
        # otherwise just tack it on the end.
        students = self.read_all_students()
        for i, s in enumerate(students):
            if s.id == student.id:
                students[i] = student
                self.write_all_students(students)
                return
        students.append(student)
        self.write_all_students(students)

    def delete_student(self, student_id: str) -> bool:
        students = self.read_all_students()
        filtered = [s for s in students if s.id != student_id]
        if len(filtered) == len(students):
            return False
        self.write_all_students(filtered)
        return True

    def clear_all(self) -> bool:
        try:
            with open(self.filename, "w") as f:
                json.dump([], f)
            return True
        except IOError:
            return False

    def email_exists(self, email: str) -> bool:
        return self.find_by_email(email) is not None
