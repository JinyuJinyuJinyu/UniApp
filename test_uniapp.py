"""
test_uniapp.py – Automated test suite for CLIUniApp / GUIUniApp
===============================================================
Run with:  python test_uniapp.py
"""

import sys, os, unittest, tempfile, shutil

sys.path.insert(0, os.path.dirname(__file__))

from subject  import Subject
from student  import Student
from admin    import Admin
from database import Database


class TestSubject(unittest.TestCase):
    """Tests for the Subject model."""

    def test_auto_generation(self):
        subj = Subject()
        self.assertTrue(1 <= int(subj.id) <= 999)
        self.assertEqual(len(subj.id), 3)
        self.assertTrue(25 <= subj.mark <= 100)
        self.assertIn(subj.grade, ("Z","P","C","D","HD"))

    def test_grade_boundaries(self):
        cases = [
            (25, "Z"), (49, "Z"),
            (50, "P"), (64, "P"),
            (65, "C"), (74, "C"),
            (75, "D"), (84, "D"),
            (85, "HD"),(100,"HD"),
        ]
        for mark, expected in cases:
            with self.subTest(mark=mark):
                subj = Subject(subject_id="001", mark=mark)
                self.assertEqual(subj.grade, expected)

    def test_calculate_grade_static(self):
        self.assertEqual(Subject.calculate_grade(90), "HD")
        self.assertEqual(Subject.calculate_grade(74), "C")

    def test_serialise_roundtrip(self):
        subj = Subject(subject_id="042", mark=87)
        self.assertEqual(subj.to_string(), "042:87:HD")
        subj2 = Subject.from_string("042:87:HD")
        self.assertEqual(subj2.id, "042")
        self.assertEqual(subj2.mark, 87)
        self.assertEqual(subj2.grade, "HD")


class TestStudentValidation(unittest.TestCase):
    """Tests for Student.validate_email_pattern / validate_password_pattern."""

    def test_valid_emails(self):
        for email in [
            "john.smith@university.com",
            "a.b@university.com",
            "JOHN.SMITH@university.com",
        ]:
            with self.subTest(email=email):
                self.assertTrue(Student.validate_email_pattern(email))

    def test_invalid_emails(self):
        for email in [
            "johnsmith@university.com",      # no dot separator
            "john.smith@university",          # wrong domain
            "john.smith@gmail.com",           # wrong domain
            "@university.com",
            "john.smith@university.com.au",   # extra TLD
            "john@university.com",            # no dot in name
        ]:
            with self.subTest(email=email):
                self.assertFalse(Student.validate_email_pattern(email))

    def test_valid_passwords(self):
        for pwd in ["David123", "HelloWorld999", "Abcde12345"]:
            with self.subTest(pwd=pwd):
                self.assertTrue(Student.validate_password_pattern(pwd))

    def test_invalid_passwords(self):
        for pwd in [
            "david123",     # no uppercase start
            "Dav123",       # only 3 letters
            "David12",      # only 2 digits
            "David",        # no digits
            "1David123",    # starts with digit
            "",
        ]:
            with self.subTest(pwd=pwd):
                self.assertFalse(Student.validate_password_pattern(pwd))


class TestStudentCheckLoginCredential(unittest.TestCase):
    """Tests for Student.check_login_credential()."""

    def setUp(self):
        self.student = Student(
            name="Jane Doe",
            email="jane.doe@university.com",
            password="Hello123",
        )

    def test_correct_credentials(self):
        self.assertTrue(
            self.student.check_login_credential(
                "jane.doe@university.com", "Hello123")
        )

    def test_wrong_password(self):
        self.assertFalse(
            self.student.check_login_credential(
                "jane.doe@university.com", "Wrong123")
        )

    def test_wrong_email(self):
        self.assertFalse(
            self.student.check_login_credential(
                "other.person@university.com", "Hello123")
        )

    def test_email_case_insensitive(self):
        """Email comparison should be case-insensitive, password exact."""
        self.assertTrue(
            self.student.check_login_credential(
                "JANE.DOE@university.com", "Hello123")
        )

    def test_password_case_sensitive(self):
        """Password comparison must be exact."""
        self.assertFalse(
            self.student.check_login_credential(
                "jane.doe@university.com", "hello123")
        )


class TestStudentEnrolment(unittest.TestCase):
    """Tests for enrolment logic on a Student instance."""

    def _make_student(self):
        return Student(
            name="Test User",
            email="test.user@university.com",
            password="David123",
        )

    def test_enrol_up_to_max(self):
        student = self._make_student()
        for _ in range(Student.MAX_SUBJECTS):
            self.assertIsNotNone(student.enrol())
        self.assertEqual(len(student.subjects), Student.MAX_SUBJECTS)

    def test_enrol_beyond_max_returns_none(self):
        student = self._make_student()
        for _ in range(Student.MAX_SUBJECTS):
            student.enrol()
        self.assertIsNone(student.enrol())  # 5th – must fail
        self.assertEqual(len(student.subjects), Student.MAX_SUBJECTS)

    def test_remove_subject(self):
        student = self._make_student()
        subj = student.enrol()
        self.assertTrue(student.remove_subject(subj.id))
        self.assertEqual(len(student.subjects), 0)

    def test_remove_nonexistent(self):
        student = self._make_student()
        self.assertFalse(student.remove_subject("999"))

    def test_change_password_valid(self):
        student = self._make_student()
        self.assertTrue(student.change_password("Newpass456"))
        self.assertEqual(student.password, "Newpass456")

    def test_change_password_invalid(self):
        student = self._make_student()
        self.assertFalse(student.change_password("weak"))
        self.assertEqual(student.password, "David123")

    def test_student_id_zero_padded(self):
        student = self._make_student()
        self.assertEqual(len(student.id), 6)

    def test_serialise_roundtrip(self):
        student = self._make_student()
        student.enrol()
        line = student.to_string()
        student2 = Student.from_string(line)
        self.assertEqual(student.id, student2.id)
        self.assertEqual(student.name, student2.name)
        self.assertEqual(student.email, student2.email)
        self.assertEqual(student.password, student2.password)
        self.assertEqual(len(student.subjects), len(student2.subjects))


class TestDatabase(unittest.TestCase):
    """Tests for the Database class using a temporary file."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "test_students.data")
        self.db      = Database(self.db_path)
        self.student = Student(
            name="Jane Doe",
            email="jane.doe@university.com",
            password="Hello123",
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_save_and_read(self):
        self.db.save_student(self.student)
        students = self.db.read_all_students()
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].email, "jane.doe@university.com")

    def test_find_by_email(self):
        self.db.save_student(self.student)
        found = self.db.find_by_email("jane.doe@university.com")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Jane Doe")

    def test_find_by_email_not_found(self):
        self.assertIsNone(self.db.find_by_email("no.one@university.com"))

    def test_update_existing_student(self):
        self.db.save_student(self.student)
        self.student.change_password("Updated999")
        self.db.save_student(self.student)
        students = self.db.read_all_students()
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].password, "Updated999")

    def test_delete_student(self):
        self.db.save_student(self.student)
        self.assertTrue(self.db.delete_student(self.student.id))
        self.assertEqual(len(self.db.read_all_students()), 0)

    def test_delete_nonexistent(self):
        self.assertFalse(self.db.delete_student("000000"))

    def test_clear_all(self):
        self.db.save_student(self.student)
        self.assertTrue(self.db.clear_all())
        self.assertEqual(len(self.db.read_all_students()), 0)

    def test_email_exists(self):
        self.db.save_student(self.student)
        self.assertTrue(self.db.email_exists("jane.doe@university.com"))
        self.assertFalse(self.db.email_exists("no.one@university.com"))

    def test_subjects_persisted(self):
        self.student.enrol()
        self.student.enrol()
        self.db.save_student(self.student)
        loaded = self.db.find_by_email(self.student.email)
        self.assertEqual(len(loaded.subjects), 2)


class TestAdmin(unittest.TestCase):
    """Tests for Admin operations."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        db_path      = os.path.join(self.tmp_dir, "students.data")
        self.db      = Database(db_path)
        self.admin   = Admin(self.db)

        for name, email, pwd, mark in [
            ("Alice A", "alice.a@university.com", "Alice123", 90),  # HD
            ("Bob B",   "bob.b@university.com",   "Bobby123", 45),  # Z (FAIL)
            ("Carol C", "carol.c@university.com", "Carol123", 70),  # C (PASS)
        ]:
            s = Student(name=name, email=email, password=pwd)
            s.subjects = [Subject(subject_id="001", mark=mark)]
            self.db.save_student(s)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_check_login_credential_correct(self):
        self.assertTrue(Admin.check_login_credential("admin"))

    def test_check_login_credential_wrong(self):
        self.assertFalse(Admin.check_login_credential("wrong"))

    def test_view_all_students(self):
        students = self.admin.view_all_students()
        self.assertEqual(len(students), 3)

    def test_group_by_grade(self):
        groups = self.admin.group_by_grade()
        self.assertEqual(len(groups["HD"]), 1)
        self.assertEqual(len(groups["Z"]),  1)
        self.assertEqual(len(groups["C"]),  1)
        self.assertEqual(len(groups["P"]),  0)
        self.assertEqual(len(groups["D"]),  0)

    def test_group_by_pass_fail(self):
        groups = self.admin.group_by_pass_fail()
        self.assertEqual(len(groups["PASS"]), 2)  # Alice + Carol
        self.assertEqual(len(groups["FAIL"]), 1)  # Bob

    def test_remove_student(self):
        students = self.db.read_all_students()
        bob_id = next(s.id for s in students if s.name == "Bob B")
        self.assertTrue(self.admin.remove_student(bob_id))
        self.assertEqual(len(self.db.read_all_students()), 2)

    def test_clear_student_data(self):
        self.assertTrue(self.admin.clear_student_data())
        self.assertEqual(len(self.db.read_all_students()), 0)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in [TestSubject, TestStudentValidation,
                TestStudentCheckLoginCredential, TestStudentEnrolment,
                TestDatabase, TestAdmin]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
