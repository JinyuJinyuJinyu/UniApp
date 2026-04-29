"""
subject.py – Subject model for CLIUniApp / GUIUniApp
=====================================================
Each Subject is auto-generated at enrolment time.
"""

import random


class Subject:
    """
    Represents a single enrolled subject.

    Attributes
    ----------
    id    : str  – unique 3-digit zero-padded subject ID (e.g. "042")
    mark  : int  – random mark in [25, 100]
    grade : str  – letter grade derived from mark
    """

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

        If called with no arguments (normal enrolment) all fields are
        auto-generated. If called with arguments (loading from file) the
        supplied values are used instead.
        """
        self.id    = subject_id if subject_id is not None else self._generate_subject_id()
        self.mark  = mark       if mark       is not None else self._generate_mark()
        self.grade = self.calculate_grade(self.mark)

    # ── generation helpers ────────────────────────────────────────────────────

    @staticmethod
    def _generate_subject_id() -> str:
        """Return a random 3-digit zero-padded subject ID."""
        return str(random.randint(1, 999)).zfill(3)

    @staticmethod
    def _generate_mark() -> int:
        """Return a random integer mark in the inclusive range [25, 100]."""
        return random.randint(25, 100)

    # ── grade calculation ─────────────────────────────────────────────────────

    @classmethod
    def calculate_grade(cls, mark: int) -> str:
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

    # ── serialisation helpers ─────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serialise to a JSON-friendly dict for storage in students.data."""
        return {"id": self.id, "mark": self.mark, "grade": self.grade}

    @classmethod
    def from_dict(cls, data: dict) -> "Subject":
        """Deserialise from a dict produced by to_dict()."""
        return cls(subject_id=data["id"], mark=int(data["mark"]))

    # ── display ───────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        return (
            f"Subject ID: {self.id}  |  "
            f"Mark: {self.mark:>3}  |  "
            f"Grade: {self.grade}"
        )
