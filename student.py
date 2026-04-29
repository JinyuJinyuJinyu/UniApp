"""
student.py – Student model for CLIUniApp / GUIUniApp
=====================================================
Spec compliance (Assessment 1 – Part 2):
  - id       : 6-digit random ID, 000001–999999
  - name     : full name
  - email    : firstname.lastname@university.com
  - password : starts with uppercase, ≥5 letters AFTER the uppercase, ≥3 digits
  - subjects : list of Subject; max 4
  - average_mark : average mark of all enrolled subjects (re-computed on enrol)
  - overall_grade: grade derived from the average mark
  - A student PASSES if average_mark >= 50

Display format (matches sample I/O):
  John Smith :: 673358 --> Email: john.smith@university.com
"""

import re
import random
from subject import Subject


class Student:

    MAX_SUBJECTS = 4

    # ── patterns ──────────────────────────────────────────────────────────────

    # firstname.lastname@university.com
    _EMAIL_PATTERN = re.compile(r"^[a-zA-Z]+\.[a-zA-Z]+@university\.com$")

    # Password: starts with ONE uppercase, then >=5 more letters,
    # then >=3 digits. So minimum length is 1 + 5 + 3 = 9 characters.
    # This makes "Hello123" (5 letters) INVALID — matching the assignment sample I/O,
    # while "Helloworld123" (10 letters) is VALID.
    _PASSWORD_PATTERN = re.compile(r"^[A-Z][a-zA-Z]{5,}\d{3,}$")

    def __init__(
        self,
        name:       str,
        email:      str,
        password:   str,
        student_id: str = None,
        subjects:   list = None,
    ):
        self.id       = student_id if student_id else self._generate_student_id()
        self.name     = name
        self.email    = email
        self.password = password
        self.subjects = subjects if subjects is not None else []

    # ── ID generation ─────────────────────────────────────────────────────────

    @staticmethod
    def _generate_student_id() -> str:
        """Generate a random 6-digit zero-padded student ID."""
        return str(random.randint(1, 999_999)).zfill(6)

    # ── pattern validation ────────────────────────────────────────────────────

    @classmethod
    def validate_email_pattern(cls, email: str) -> bool:
        return bool(cls._EMAIL_PATTERN.match(email))

    @classmethod
    def validate_password_pattern(cls, password: str) -> bool:
        return bool(cls._PASSWORD_PATTERN.match(password))

    # ── credential checking ───────────────────────────────────────────────────

    def check_login_credential(self, email: str, password: str) -> bool:
        """Verify supplied credentials. Email is case-insensitive, password exact."""
        return (
            self.email.lower() == email.lower()
            and self.password == password
        )

    # ── enrolment operations ──────────────────────────────────────────────────

    def enrol(self) -> Subject | None:
        """
        Add a new auto-generated Subject. Returns the new Subject, or None
        if MAX_SUBJECTS already reached.
        The student's average_mark is automatically recalculated.
        """
        if len(self.subjects) >= self.MAX_SUBJECTS:
            return None
        subject = Subject()
        self.subjects.append(subject)
        return subject

    def remove_subject(self, subject_id: str) -> bool:
        """Remove subject by ID. Returns True if found and removed."""
        for i, subj in enumerate(self.subjects):
            if subj.id == subject_id:
                self.subjects.pop(i)
                return True
        return False

    # ── derived properties ────────────────────────────────────────────────────

    @property
    def average_mark(self) -> float:
        """
        Average mark of all enrolled subjects, recomputed every access.
        Returns 0.0 if no subjects are enrolled.
        """
        if not self.subjects:
            return 0.0
        return sum(s.mark for s in self.subjects) / len(self.subjects)

    @property
    def overall_grade(self) -> str:
        """Grade derived from the average mark via the UTS scale."""
        return Subject.calculate_grade(self.average_mark)

    @property
    def is_pass(self) -> bool:
        """A student passes if the average mark is >= 50."""
        return self.average_mark >= 50

    # ── account management ────────────────────────────────────────────────────

    def change_password(self, new_password: str) -> bool:
        """Update password if it satisfies the pattern."""
        if not self.validate_password_pattern(new_password):
            return False
        self.password = new_password
        return True

    # ── serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id":       self.id,
            "name":     self.name,
            "email":    self.email,
            "password": self.password,
            "subjects": [s.to_dict() for s in self.subjects],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        subjects = [Subject.from_dict(s) for s in data.get("subjects", [])]
        return cls(
            name=data["name"],
            email=data["email"],
            password=data["password"],
            student_id=data["id"],
            subjects=subjects,
        )

    # ── display helpers (match sample I/O exactly) ────────────────────────────

    def __str__(self) -> str:
        # Sample format:  John Smith :: 673358 --> Email: john.smith@university.com
        return f"{self.name} :: {self.id} --> Email: {self.email}"

    def short_repr(self) -> str:
        # Used in admin grouping/partition output:
        #   John Smith :: 673358 --> GRADE:  C - MARK: 68.25
        return (
            f"{self.name} :: {self.id} --> "
            f"GRADE: {self.overall_grade:>2} - MARK: {self.average_mark:.2f}"
        )
