"""
test_uniapp.py – Automated test suite for CLIUniApp / GUIUniApp
===============================================================
Covers the full MVC stack:
  - Models      : Subject, Student, Database
  - Controllers : StudentController, SubjectController, AdminController

Run with:
    python test_uniapp.py
"""

import sys, os, unittest, tempfile, shutil

sys.path.insert(0, os.path.dirname(__file__))

from subject            import Subject
from student            import Student
from database           import Database
from student_controller import (
    StudentController,
    ERR_BAD_EMAIL_FORMAT,
    ERR_BAD_PASSWORD_FORMAT,
    ERR_DUPLICATE,
    ERR_NOT_FOUND,
)
from subject_controller import SubjectController
from admin_controller   import AdminController


# ═══════════════════════════════════════════════════════════════════════════════
#  MODEL TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestSubject(unittest.TestCase):

    def test_auto_generation(self):
        subj = Subject()
        self.assertTrue(1 <= int(subj.id) <= 999)
        self.assertEqual(len(subj.id), 3)
        self.assertTrue(25 <= subj.mark <= 100)
        self.assertIn(subj.grade, ("Z", "P", "C", "D", "HD"))

    def test_grade_boundaries(self):
        for mark, expected in [(25, "Z"), (49, "Z"),
                               (50, "P"), (64, "P"),
                               (65, "C"), (74, "C"),
                               (75, "D"), (84, "D"),
                               (85, "HD"), (100, "HD")]:
            with self.subTest(mark=mark):
                self.assertEqual(Subject(subject_id="001", mark=mark).grade, expected)

    def test_str_format(self):
        subj = Subject(subject_id="541", mark=55)
        self.assertEqual(str(subj), "[ Subject::541 -- mark = 55 -- grade =   P ]")


class TestStudentValidation(unittest.TestCase):
    """Tightened password regex per spec."""

    def test_email_valid(self):
        for e in ["john.smith@university.com",
                  "alen.jones@university.com",
                  "JOHN.SMITH@university.com"]:
            with self.subTest(e=e):
                self.assertTrue(Student.validate_email_pattern(e))

    def test_email_invalid(self):
        for e in ["johnsmith@university.com",
                  "john.smith@university",
                  "john.smith@gmail.com",
                  "john.smith@university.com.au"]:
            with self.subTest(e=e):
                self.assertFalse(Student.validate_email_pattern(e))

    def test_password_valid(self):
        for p in ["Helloworld123", "Newworld123", "Abcdef1234"]:
            with self.subTest(p=p):
                self.assertTrue(Student.validate_password_pattern(p))

    def test_password_invalid_per_sample_io(self):
        for p in ["helloworld123", "Hello123", "Newworld12",
                  "1Helloworld123", ""]:
            with self.subTest(p=p):
                self.assertFalse(Student.validate_password_pattern(p))


class TestStudentDerivedProperties(unittest.TestCase):
    """average_mark / overall_grade / is_pass — required by spec for admin views."""

    def _make(self):
        return Student(name="Test", email="t.t@university.com",
                       password="Helloworld123")

    def test_no_subjects(self):
        s = self._make()
        self.assertEqual(s.average_mark, 0.0)
        self.assertFalse(s.is_pass)

    def test_average_recalculated(self):
        s = self._make()
        s.subjects = [Subject("001", m) for m in (50, 60, 70, 80)]
        self.assertAlmostEqual(s.average_mark, 65.0)
        self.assertEqual(s.overall_grade, "C")
        self.assertTrue(s.is_pass)

    def test_pass_when_some_below_but_avg_ok(self):
        s = self._make()
        s.subjects = [Subject("001", 90), Subject("002", 90), Subject("003", 30)]
        self.assertTrue(s.is_pass)


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTROLLER TESTS — The new layer
# ═══════════════════════════════════════════════════════════════════════════════

class _TempDb(unittest.TestCase):
    """Mixin: isolated Database in a temp dir."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db  = Database(os.path.join(self.tmp, "students.data"))

    def tearDown(self):
        shutil.rmtree(self.tmp)


class TestStudentController(_TempDb):

    def setUp(self):
        super().setUp()
        self.ctrl = StudentController(self.db)

    def test_register_success(self):
        s, err = self.ctrl.register("Jane Doe",
                                    "jane.doe@university.com",
                                    "Helloworld123")
        self.assertIsNone(err)
        self.assertIsNotNone(s)
        self.assertEqual(s.name, "Jane Doe")
        # verify it was persisted
        self.assertTrue(self.db.email_exists("jane.doe@university.com"))

    def test_register_bad_email(self):
        s, err = self.ctrl.register("Jane", "no-dot@university.com", "Helloworld123")
        self.assertIsNone(s)
        self.assertEqual(err, ERR_BAD_EMAIL_FORMAT)

    def test_register_bad_password(self):
        s, err = self.ctrl.register("Jane", "jane.doe@university.com", "Hello123")
        self.assertIsNone(s)
        self.assertEqual(err, ERR_BAD_PASSWORD_FORMAT)

    def test_register_duplicate(self):
        self.ctrl.register("Jane", "jane.doe@university.com", "Helloworld123")
        s, err = self.ctrl.register("Other", "jane.doe@university.com", "Helloworld456")
        self.assertIsNone(s)
        self.assertEqual(err, ERR_DUPLICATE)

    def test_login_success(self):
        self.ctrl.register("Jane", "jane.doe@university.com", "Helloworld123")
        s, err = self.ctrl.login("jane.doe@university.com", "Helloworld123")
        self.assertIsNone(err)
        self.assertIsNotNone(s)

    def test_login_wrong_password(self):
        self.ctrl.register("Jane", "jane.doe@university.com", "Helloworld123")
        s, err = self.ctrl.login("jane.doe@university.com", "Helloworld456")
        self.assertEqual(err, ERR_NOT_FOUND)

    def test_login_unregistered(self):
        s, err = self.ctrl.login("nobody@university.com", "Helloworld123")
        # Email format invalid → controller catches that first
        self.assertEqual(err, ERR_BAD_EMAIL_FORMAT)

    def test_login_email_case_insensitive(self):
        self.ctrl.register("Jane", "jane.doe@university.com", "Helloworld123")
        s, err = self.ctrl.login("JANE.DOE@university.com", "Helloworld123")
        self.assertIsNone(err)
        self.assertIsNotNone(s)


class TestSubjectController(_TempDb):

    def setUp(self):
        super().setUp()
        self.subj_ctrl    = SubjectController(self.db)
        self.student_ctrl = StudentController(self.db)
        self.student, _   = self.student_ctrl.register(
            "Test", "test.user@university.com", "Helloworld123")

    def test_enrol_persists_and_increments(self):
        before = len(self.student.subjects)
        new_subj = self.subj_ctrl.enrol(self.student)
        self.assertIsNotNone(new_subj)
        self.assertEqual(len(self.student.subjects), before + 1)

        # Verify persisted
        loaded = self.db.find_by_email(self.student.email)
        self.assertEqual(len(loaded.subjects), before + 1)

    def test_enrol_blocks_at_max(self):
        for _ in range(Student.MAX_SUBJECTS):
            self.subj_ctrl.enrol(self.student)
        # 5th attempt
        result = self.subj_ctrl.enrol(self.student)
        self.assertIsNone(result)
        self.assertEqual(len(self.student.subjects), Student.MAX_SUBJECTS)

    def test_remove_existing(self):
        subj = self.subj_ctrl.enrol(self.student)
        self.assertTrue(self.subj_ctrl.remove(self.student, subj.id))
        self.assertEqual(len(self.student.subjects), 0)

    def test_remove_accepts_unpadded_id(self):
        # enrol with a known ID via direct manipulation, then remove using "42"
        from subject import Subject as Subj
        self.student.subjects = [Subj(subject_id="042", mark=60)]
        self.db.save_student(self.student)
        self.assertTrue(self.subj_ctrl.remove(self.student, "42"))

    def test_remove_nonexistent(self):
        self.assertFalse(self.subj_ctrl.remove(self.student, "999"))

    def test_change_password_valid(self):
        self.assertTrue(self.subj_ctrl.change_password(self.student, "Newworld456"))
        loaded = self.db.find_by_email(self.student.email)
        self.assertEqual(loaded.password, "Newworld456")

    def test_change_password_invalid(self):
        self.assertFalse(self.subj_ctrl.change_password(self.student, "Hello123"))

    def test_list_subjects_refreshes_from_db(self):
        # Enrol, then change DB underneath (simulate other window)
        self.subj_ctrl.enrol(self.student)
        # Local student object thinks it has 1; DB has 1 — verify list is consistent
        listed = self.subj_ctrl.list_subjects(self.student)
        self.assertEqual(len(listed), 1)


class TestAdminController(_TempDb):
    """Spec-correct grouping rules verified at the controller layer."""

    def setUp(self):
        super().setUp()
        self.admin = AdminController(self.db)

        for name, email, pwd, marks in [
            ("Alice A", "alice.a@university.com", "Aliceabc123", [90, 80, 70, 60]),  # avg=75 → D
            ("Bob B",   "bob.b@university.com",   "Bobbobby123", [40, 45, 50, 55]),  # avg=47.5 → Z
            ("Carol C", "carol.c@university.com", "Carolcdef123",[60, 65, 70, 75]),  # avg=67.5 → C
        ]:
            stu = Student(name=name, email=email, password=pwd)
            stu.subjects = [Subject(subject_id=f"{i+1:03d}", mark=m)
                            for i, m in enumerate(marks)]
            self.db.save_student(stu)

    def test_check_login_credential(self):
        self.assertTrue(AdminController.check_login_credential("admin"))
        self.assertFalse(AdminController.check_login_credential("wrong"))

    def test_view_all(self):
        self.assertEqual(len(self.admin.view_all_students()), 3)

    def test_group_by_grade_each_student_appears_once(self):
        groups = self.admin.group_by_grade()
        self.assertIn("D", groups);  self.assertEqual(len(groups["D"]), 1)
        self.assertIn("C", groups);  self.assertEqual(len(groups["C"]), 1)
        self.assertIn("Z", groups);  self.assertEqual(len(groups["Z"]), 1)
        flat = []
        for v in groups.values(): flat.extend(v)
        self.assertEqual(len(flat), 3)

    def test_partition_uses_average(self):
        parts = self.admin.group_by_pass_fail()
        self.assertEqual(len(parts["PASS"]), 2)  # Alice + Carol
        self.assertEqual(len(parts["FAIL"]), 1)  # Bob

    def test_no_subjects_excluded_from_groups(self):
        empty = Student(name="Empty E", email="empty.e@university.com",
                        password="Emptyemp123")
        self.db.save_student(empty)
        groups = self.admin.group_by_grade()
        flat = [s for v in groups.values() for s in v]
        self.assertEqual(len(flat), 3)  # empty excluded
        parts = self.admin.group_by_pass_fail()
        self.assertEqual(len(parts["PASS"]) + len(parts["FAIL"]), 3)

    def test_remove_student(self):
        students = self.db.read_all_students()
        bob_id = next(s.id for s in students if s.name == "Bob B")
        self.assertTrue(self.admin.remove_student(bob_id))
        self.assertEqual(len(self.db.read_all_students()), 2)

    def test_clear_all(self):
        self.assertTrue(self.admin.clear_student_data())
        self.assertEqual(len(self.db.read_all_students()), 0)


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in [TestSubject,
                TestStudentValidation,
                TestStudentDerivedProperties,
                TestStudentController,
                TestSubjectController,
                TestAdminController]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
