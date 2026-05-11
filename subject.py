"""subject.py

Student Name: Hang Wang
Student ID: 14734281
"""

# Subject model used by both the CLI and GUI versions.
# Whenever a student enrols, a new Subject is created with a random
# ID and mark, and the grade is worked out from the mark.

import random


class Subject:

    # Grade thresholds in order from highest to lowest.
    GRADE_MAP = [
        (85, "HD"),
        (75, "D"),
        (65, "C"),
        (50, "P"),
        (0,  "Z"),
    ]

    def __init__(self, subject_id: str = None, mark: int = None):
        # If no values are passed in, just generate them.
        # The args are mostly for loading subjects back from the file.
        if subject_id is None:
            self.id = self._generate_subject_id()
        else:
            self.id = subject_id
        if mark is None:
            self.mark = self._generate_mark()
        else:
            self.mark = mark

        self.grade = self.calculate_grade(self.mark)

    @staticmethod
    def _generate_subject_id() -> str:
        # 3-digit ID padded with zeros, e.g. "042".
        return str(random.randint(1, 999)).zfill(3)

    @staticmethod
    def _generate_mark() -> int:
        return random.randint(25, 100)

    @classmethod
    def calculate_grade(cls, mark: float) -> str:
        # Walks the list from the top down and returns the first grade that fits.
        for threshold, grade in cls.GRADE_MAP:
            if mark >= threshold:
                return grade
        return "Z"

    def to_dict(self) -> dict:
        return {"id": self.id, "mark": self.mark, "grade": self.grade}

    @classmethod
    def from_dict(cls, data: dict) -> "Subject":
        return cls(subject_id=data["id"], mark=int(data["mark"]))

    def __str__(self) -> str:
        # Format taken from the sample output in the assignment brief.
        return f"[ Subject::{self.id} -- mark = {self.mark} -- grade = {self.grade:>3} ]"
