"""populate_data.py

Student Name: Hang Wang
Student ID: 14734281
"""

# Quick script to fill students.data with sample records so the admin
# views and grade groupings have something to show.
#
# Examples:
#     python populate_data.py              -> 15 students (default)
#     python populate_data.py 30           -> 30 students
#     python populate_data.py 20 --append  -> add 20 to the existing data
#
# Generated accounts follow the same email/password rules as the
# normal register flow, so they can be logged into directly.

import argparse
import random
import sys

from student  import Student
from subject  import Subject
from database import Database


# Just a pool of names to mix and match.
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
    # Builds something the Student password regex will accept:
    # uppercase letter, 5-8 lowercase letters, then 3-4 digits.
    letters  = "abcdefghijklmnopqrstuvwxyz"
    body_len = random.randint(5, 8)
    body     = "".join(random.choices(letters, k=body_len))
    digits   = "".join(random.choices("0123456789", k=random.randint(3, 4)))
    return random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + body + digits


def make_student(used_emails: set, used_ids: set) -> Student:
    # Keep rolling names until we get an email that isn't already taken.
    while True:
        first = random.choice(FIRST_NAMES)
        last  = random.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}@university.com"
        if email not in used_emails:
            used_emails.add(email)
            break

    # Same trick for the student ID.
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

    # Give the student somewhere between 0 and 4 unique subjects.
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
    if seed is not None:
        random.seed(seed)

    db = Database("students.data")

    used_emails: set = set()
    used_ids:    set = set()

    existing: list = []
    if append:
        # Don't reuse emails/IDs that are already in the file.
        existing = db.read_all_students()
        for s in existing:
            used_emails.add(s.email.lower())
            used_ids.add(s.id)

    new_students = []
    for _ in range(count):
        new_students.append(make_student(used_emails, used_ids))

    if append:
        db.write_all_students(existing + new_students)
    else:
        db.write_all_students(new_students)

    print(f"✔  Wrote {len(new_students)} new student(s) to {db.filename}")
    if append and existing:
        print(f"   (kept {len(existing)} existing record(s), total {len(existing) + len(new_students)})")

    # Show a couple of the new accounts so you don't have to crack
    # open the file just to test logging in.
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
