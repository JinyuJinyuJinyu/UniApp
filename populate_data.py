"""
populate_data.py – Seed students.data with sample records
=========================================================
Generates a configurable number of valid Student records (with random
subjects) and writes them to students.data via the Database class.

Run with:
    python populate_data.py              # default: 15 students
    python populate_data.py 30           # 30 students
    python populate_data.py 20 --append  # add 20 without wiping existing data

Every generated account satisfies the Student email and password patterns,
so the seeded data is usable for login, admin views, and grade grouping.
"""

import argparse
import random
import sys

from student  import Student
from subject  import Subject
from database import Database


# ── sample name pool ────────────────────────────────────────────────────────
FIRST_NAMES = [
    "David",  "Sarah",  "Liam",    "Emma",   "Noah",   "Olivia",
    "James",  "Ava",    "Lucas",   "Mia",    "Ethan",  "Isabella",
    "Oliver", "Sophia", "William", "Amelia", "Mason",  "Charlotte",
    "Logan",  "Harper", "Jackson", "Evelyn", "Aiden",  "Abigail",
]

LAST_NAMES = [
    "Smith",   "Johnson", "Williams", "Brown",    "Jones",    "Garcia",
    "Miller",  "Davis",   "Rodriguez","Martinez", "Hernandez","Lopez",
    "Wilson",  "Anderson","Thomas",   "Taylor",   "Moore",    "Jackson",
    "Martin",  "Lee",     "Perez",    "Thompson", "White",    "Harris",
]


def random_password() -> str:
    """
    Build a password that passes Student.validate_password_pattern:
      - starts with an uppercase letter
      - at least 5 letters total
      - ends with 3+ digits
    """
    letters = "abcdefghijklmnopqrstuvwxyz"
    body_len = random.randint(4, 7)                       # -> 5..8 letters total
    body     = "".join(random.choices(letters, k=body_len))
    digits   = "".join(random.choices("0123456789", k=random.randint(3, 4)))
    return random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + body + digits


def make_student(used_emails: set, used_ids: set) -> Student:
    """Create a single Student with a unique email, ID, and 0–4 subjects."""
    while True:
        first = random.choice(FIRST_NAMES)
        last  = random.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}@university.com"
        if email not in used_emails:
            used_emails.add(email)
            break

    while True:
        sid = str(random.randint(1, 999_999)).zfill(6)
        if sid not in used_ids:
            used_ids.add(sid)
            break

    student = Student(
        name       = f"{first} {last}",
        email      = email,
        password   = random_password(),
        student_id = sid,
        subjects   = [],
    )

    # Give each student 0–4 unique subjects
    subject_count = random.randint(0, Student.MAX_SUBJECTS)
    used_subject_ids: set = set()
    for _ in range(subject_count):
        while True:
            subj = Subject()
            if subj.id not in used_subject_ids:
                used_subject_ids.add(subj.id)
                student.subjects.append(subj)
                break

    return student


def populate(count: int, append: bool, seed: int | None) -> None:
    """Generate `count` students and write them to students.data."""
    if seed is not None:
        random.seed(seed)

    db = Database("students.data")

    used_emails: set = set()
    used_ids:    set = set()

    existing: list = []
    if append:
        existing = db.read_all_students()
        used_emails.update(s.email.lower() for s in existing)
        used_ids.update(s.id for s in existing)

    new_students = [make_student(used_emails, used_ids) for _ in range(count)]

    if append:
        db.write_all_students(existing + new_students)
    else:
        db.write_all_students(new_students)

    print(f"✔  Wrote {len(new_students)} new student(s) to {db.filename}")
    if append and existing:
        print(f"   (kept {len(existing)} existing record(s), total {len(existing) + len(new_students)})")

    print("\nSample credentials you can use to log in:")
    for s in new_students[:3]:
        print(f"  • {s.email:<40}  password: {s.password}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate students.data with sample records.")
    parser.add_argument("count",  nargs="?", type=int, default=15,
                        help="Number of students to generate (default: 15)")
    parser.add_argument("--append", action="store_true",
                        help="Keep existing records and append new ones")
    parser.add_argument("--seed", type=int, default=None,
                        help="Optional RNG seed for reproducible output")
    args = parser.parse_args()

    if args.count <= 0:
        print("count must be a positive integer", file=sys.stderr)
        sys.exit(1)

    populate(args.count, args.append, args.seed)


if __name__ == "__main__":
    main()
