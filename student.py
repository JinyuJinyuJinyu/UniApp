"""student.py

Student Name: Hang Wang
Student ID: 14734281
"""

# Student model. Holds the basic details plus the list of subjects
# the student is currently enrolled in. Max 4 subjects per student.

import re
import random
from subject import Subject


class Student:

    MAX_SUBJECTS = 4

    # firstname.lastname@university.com
    _EMAIL_PATTERN = re.compile(r"^[a-zA-Z]+\.[a-zA-Z]+@university\.com$")

    # One uppercase letter, then at least 5 more letters, then 3+ digits.
    # That makes the minimum length 9 characters. The brief's example
    # "Hello123" only has 5 letters so it's intentionally rejected,
    # while "Helloworld123" passes.
    _PASSWORD_PATTERN = re.compile(r"^[A-Z][a-zA-Z]{5,}\d{3,}$")

    def __init__(
        self,
        name:       str,
        email:      str,
        password:   str,
        student_id: str = None,
        subjects:   list = None,
    ):
        if student_id is None:
            self.id = self._generate_student_id()
        else:
            self.id = student_id
        self.name     = name
        self.email    = email
        self.password = password
        if subjects is None:
            self.subjects = []
        else:
            self.subjects = subjects

    @staticmethod
    def _generate_student_id() -> str:
        # 6-digit ID, zero padded.
        return str(random.randint(1, 999_999)).zfill(6)

    @classmethod
    def validate_email_pattern(cls, email: str) -> bool:
        return bool(cls._EMAIL_PATTERN.match(email))

    @classmethod
    def validate_password_pattern(cls, password: str) -> bool:
        return bool(cls._PASSWORD_PATTERN.match(password))

    def check_login_credential(self, email: str, password: str) -> bool:
        # Email comparison is case-insensitive, password has to be exact.
        return (
            self.email.lower() == email.lower()
            and self.password == password
        )

    def enrol(self) -> Subject | None:
        # Returns the new subject, or None if the student is already at the cap.
        if len(self.subjects) >= self.MAX_SUBJECTS:
            return None
        subject = Subject()
        self.subjects.append(subject)
        return subject

    def remove_subject(self, subject_id: str) -> bool:
        for i, subj in enumerate(self.subjects):
            if subj.id == subject_id:
                self.subjects.pop(i)
                return True
        return False

    @property
    def average_mark(self) -> float:
        # Recalculated every time so it always reflects the current subjects.
        if not self.subjects:
            return 0.0
        return sum(s.mark for s in self.subjects) / len(self.subjects)

    @property
    def overall_grade(self) -> str:
        return Subject.calculate_grade(self.average_mark)

    @property
    def is_pass(self) -> bool:
        return self.average_mark >= 50

    def change_password(self, new_password: str) -> bool:
        # Only update if the new password follows the rules.
        if not self.validate_password_pattern(new_password):
            return False
        self.password = new_password
        return True

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

    def __str__(self) -> str:
        # e.g.  John Smith :: 673358 --> Email: john.smith@university.com
        return f"{self.name} :: {self.id} --> Email: {self.email}"

    def short_repr(self) -> str:
        # Used by the admin views, e.g.
        #   John Smith :: 673358 --> GRADE:  C - MARK: 68.25
        grade_str = str(self.overall_grade).rjust(2)
        mark_str  = f"{self.average_mark:.2f}"
        return (
            f"{self.name} :: {self.id} --> "
            + "GRADE: " + grade_str + " - MARK: " + mark_str
        )
