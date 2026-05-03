"""
subject.py – Subject model for CLIUniApp / GUIUniApp
=====================================================
Each Subject is auto-generated at enrolment time.

Spec compliance (Assessment 1 – Part 2):
  - id    : random 3-digit number, 1–999
  - mark  : random integer in [25, 100]
  - grade : derived from mark via the UTS scale

Display format matches the sample I/O exactly:
  [ Subject::541 -- mark = 55 -- grade =   P ]
"""

import random


class Subject:

    # UTS grading scale: ordered from highest threshold to lowest
    GRADE_MAP = [
        (85, "HD"),
        (75, "D"),
        (65, "C"),
        (50, "P"),
        (0,  "Z"),
    ]

    def __init__(self, subject_id: str = None, mark: int = None):
        """
        Create a Subject.

        With no arguments → all fields are auto-generated.
        With arguments    → the supplied values are used (used when loading from file).
        """
        self.id    = subject_id if subject_id is not None else self._generate_subject_id()
        self.mark  = mark       if mark       is not None else self._generate_mark()
        self.grade = self.calculate_grade(self.mark)

    # ── generation ────────────────────────────────────────────────────────────

    @staticmethod
    def _generate_subject_id() -> str:
        """Return a random 3-digit zero-padded subject ID (e.g. '042')."""
        return str(random.randint(1, 999)).zfill(3)

    @staticmethod
    def _generate_mark() -> int:
        """Return a random integer mark in the inclusive range [25, 100]."""
        return random.randint(25, 100)

    # ── grade calculation ─────────────────────────────────────────────────────

    @classmethod
    def calculate_grade(cls, mark: float) -> str:
        """
        Apply UTS grading scale:
          mark < 50          → Z (Fail)
          50 <= mark < 65    → P (Pass)
          65 <= mark < 75    → C (Credit)
          75 <= mark < 85    → D (Distinction)
          mark >= 85         → HD (High Distinction)
        """
        for threshold, grade in cls.GRADE_MAP:
            if mark >= threshold:
                return grade
        return "Z"

    # ── serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {"id": self.id, "mark": self.mark, "grade": self.grade}

    @classmethod
    def from_dict(cls, data: dict) -> "Subject":
        return cls(subject_id=data["id"], mark=int(data["mark"]))

    # ── display ───────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        # Matches sample I/O exactly:
        #   [ Subject::541 -- mark = 55 -- grade =   P ]
        return f"[ Subject::{self.id} -- mark = {self.mark} -- grade = {self.grade:>3} ]"
