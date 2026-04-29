"""
student.py – Student model for CLIUniApp / GUIUniApp
=====================================================
Handles registration data, pattern validation, enrolment logic and
password management for a single student.

Public methods are named to match the Part 1 UML class diagram:
  - validateEmailPattern   → validate_email_pattern
  - validatePasswordPattern → validate_password_pattern
  - checkLoginCredential   → check_login_credential
"""

import re
import random
from subject import Subject


class Student:
    """
    Represents a registered university student.

    Attributes
    ----------
    id       : str            – unique 6-digit zero-padded ID (e.g. "002340")
    name     : str            – full name supplied at registration
    email    : str            – validated university email
    password : str            – validated password
    subjects : list[Subject]  – enrolled subjects; maximum 4
    """

    MAX_SUBJECTS = 4

    #email & password patterns

    # firstname.lastname@university.com
    _EMAIL_PATTERN    = re.compile(r"^[a-zA-Z]+\.[a-zA-Z]+@university\.com$")

    # Starts with ONE uppercase letter, then >=4 more letters (total >=5 letters),
    # then >=3 digits, nothing else.
    _PASSWORD_PATTERN = re.compile(r"^[A-Z][a-zA-Z]{4,}\d{3,}$")

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

    #ID generation

    @staticmethod
    def _generate_student_id() -> str:
        """Generate a random 6-digit zero-padded student ID."""
        return str(random.randint(1, 999_999)).zfill(6)

    #pattern validation

    @classmethod
    def validate_email_pattern(cls, email: str) -> bool:
        """
        Return True if email matches firstname.lastname@university.com.

        Examples
        --------
        >>> Student.validate_email_pattern("john.smith@university.com")
        True
        >>> Student.validate_email_pattern("john.smith@university")
        False
        >>> Student.validate_email_pattern("johnsmith@university.com")
        False
        """
        return bool(cls._EMAIL_PATTERN.match(email))

    @classmethod
    def validate_password_pattern(cls, password: str) -> bool:
        """
        Return True if the password satisfies all three criteria:
          (i)   Starts with an uppercase letter
          (ii)  Contains at least 5 letters in total
          (iii) Followed by 3 or more digits

        Examples
        --------
        >>> Student.validate_password_pattern("David123")
        True
        >>> Student.validate_password_pattern("david123")
        False
        >>> Student.validate_password_pattern("Dav123")
        False
        """
        return bool(cls._PASSWORD_PATTERN.match(password))

    #credential checking

    def check_login_credential(self, email: str, password: str) -> bool:
        """
        Verify that the supplied email and password match this student's
        stored credentials.

        Returns True on match, False otherwise.
        Email comparison is case-insensitive; password comparison is exact.
        """
        return (
            self.email.lower() == email.lower()
            and self.password == password
        )

    #enrolment operations

    def enrol(self) -> Subject | None:
        """
        Add a new auto-generated Subject to the student's enrolment list.

        Returns
        -------
        Subject  – the newly created subject, or
        None     – if the student is already enrolled in MAX_SUBJECTS subjects.
        """
        if len(self.subjects) >= self.MAX_SUBJECTS:
            return None
        subject = Subject()
        self.subjects.append(subject)
        return subject

    def remove_subject(self, subject_id: str) -> bool:
        """
        Remove the subject with the given ID from the enrolment list.

        Returns True if a matching subject was found and removed, False otherwise.
        """
        for i, subj in enumerate(self.subjects):
            if subj.id == subject_id:
                self.subjects.pop(i)
                return True
        return False

    def view_subjects(self) -> list:
        """Return the current list of enrolled Subject objects."""
        return list(self.subjects)

    #account management

    def change_password(self, new_password: str) -> bool:
        """
        Update the stored password if new_password passes pattern validation.

        Returns True on success, False if the new password is invalid.
        """
        if not self.validate_password_pattern(new_password):
            return False
        self.password = new_password
        return True

    #serialisation helpers

    def to_string(self) -> str:
        """
        Serialise to a single pipe-delimited line:
          id|name|email|password|subj1,subj2,...
        """
        subjects_str = ",".join(s.to_string() for s in self.subjects)
        return f"{self.id}|{self.name}|{self.email}|{self.password}|{subjects_str}"

    @classmethod
    def from_string(cls, line: str) -> "Student":
        """Deserialise from a line produced by to_string()."""
        parts    = line.strip().split("|")
        sid      = parts[0]
        name     = parts[1]
        email    = parts[2]
        password = parts[3]
        subjects_str = parts[4] if len(parts) > 4 else ""
        subjects = (
            [Subject.from_string(t) for t in subjects_str.split(",") if t]
            if subjects_str else []
        )
        return cls(
            name=name,
            email=email,
            password=password,
            student_id=sid,
            subjects=subjects,
        )

    #display helpers

    def __str__(self) -> str:
        return (
            f"ID: {self.id}  |  "
            f"Name: {self.name:<20}  |  "
            f"Email: {self.email}"
        )

    def display_subjects(self) -> None:
        """Print a formatted list of the student's enrolled subjects."""
        if not self.subjects:
            print("  [No subjects enrolled]")
            return
        for subj in self.subjects:
            print(f"  {subj}")
