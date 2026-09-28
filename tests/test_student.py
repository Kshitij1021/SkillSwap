"""Tests for skillswap/student.py (Student class, file load/save, id generation)."""

import os
import sys

# lets a test file also be run directly (e.g. the "Run Python File" button in VS Code):
# the project root is added to the path so `import skillswap` works from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
import tempfile
import unittest

from skillswap.student import (
    Student, load_all_students, save_all_students,
    find_student_by_id, find_student_by_email, generate_new_student_id,
)


class TestStudentSkills(unittest.TestCase):
    def setUp(self):
        self.s = Student("S001", "Asha", "asha@x.com", "pass1")

    def test_new_student_has_empty_lists(self):
        self.assertEqual(self.s.teaching_skills, [])
        self.assertEqual(self.s.learning_skills, [])

    def test_lists_are_not_shared_between_students(self):
        other = Student("S002", "Ravi", "ravi@x.com", "pass2")
        self.s.add_teaching_skill("Python")
        self.assertEqual(other.teaching_skills, [])

    def test_add_teaching_skill_uses_title_case(self):
        self.assertTrue(self.s.add_teaching_skill("  python  "))
        self.assertEqual(self.s.teaching_skills, ["Python"])

    def test_add_duplicate_teaching_skill_is_rejected(self):
        self.s.add_teaching_skill("Python")
        self.assertFalse(self.s.add_teaching_skill("PYTHON"))
        self.assertEqual(len(self.s.teaching_skills), 1)

    def test_add_and_duplicate_learning_skill(self):
        self.assertTrue(self.s.add_learning_skill("guitar"))
        self.assertFalse(self.s.add_learning_skill("Guitar"))
        self.assertEqual(self.s.learning_skills, ["Guitar"])

    def test_remove_teaching_skill(self):
        self.s.add_teaching_skill("Python")
        self.assertTrue(self.s.remove_teaching_skill("python"))
        self.assertEqual(self.s.teaching_skills, [])

    def test_remove_missing_skill_returns_false(self):
        self.assertFalse(self.s.remove_teaching_skill("Chess"))
        self.assertFalse(self.s.remove_learning_skill("Chess"))

    def test_remove_learning_skill(self):
        self.s.add_learning_skill("Chess")
        self.assertTrue(self.s.remove_learning_skill("chess"))
        self.assertEqual(self.s.learning_skills, [])


class TestStudentRating(unittest.TestCase):
    def test_average_is_zero_with_no_ratings(self):
        self.assertEqual(Student("S001", "A", "a@x.com", "pw12").average_rating(), 0.0)

    def test_average_rating_is_rounded(self):
        s = Student("S001", "A", "a@x.com", "pw12", rating_total=10, rating_count=3)
        self.assertEqual(s.average_rating(), 3.33)


class TestStudentFileFormat(unittest.TestCase):
    def test_to_line_uses_dash_for_empty_lists(self):
        s = Student("S001", "Asha", "asha@x.com", "pass1")
        self.assertEqual(s.to_line(), "S001|Asha|asha@x.com|pass1|-|-|0|0")

    def test_round_trip_keeps_all_fields(self):
        s = Student("S007", "Ravi", "r@x.com", "pw12", ["Python", "Excel"],
                    ["Guitar"], 9, 2)
        copy = Student.from_line(s.to_line())
        self.assertEqual(copy.student_id, "S007")
        self.assertEqual(copy.name, "Ravi")
        self.assertEqual(copy.email, "r@x.com")
        self.assertEqual(copy.password, "pw12")
        self.assertEqual(copy.teaching_skills, ["Python", "Excel"])
        self.assertEqual(copy.learning_skills, ["Guitar"])
        self.assertEqual(copy.rating_total, 9)
        self.assertEqual(copy.rating_count, 2)

    def test_dash_loads_as_empty_list(self):
        s = Student.from_line("S001|Asha|a@x.com|pw12|-|-|0|0")
        self.assertEqual(s.teaching_skills, [])
        self.assertEqual(s.learning_skills, [])

    def test_float_rating_total_is_accepted(self):
        s = Student.from_line("S001|Asha|a@x.com|pw12|-|-|12.0|3")
        self.assertEqual(s.rating_total, 12.0)

    def test_blank_comment_and_short_lines_are_skipped(self):
        self.assertIsNone(Student.from_line(""))
        self.assertIsNone(Student.from_line("   \n"))
        self.assertIsNone(Student.from_line("# a comment"))
        self.assertIsNone(Student.from_line("S001|Asha|a@x.com"))


class TestStudentFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "students.txt")

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(load_all_students(self.path), [])

    def test_save_then_load(self):
        students = [
            Student("S001", "Asha", "a@x.com", "pw12", ["Python"], ["Guitar"]),
            Student("S002", "Ravi", "r@x.com", "pw34"),
        ]
        save_all_students(self.path, students)
        loaded = load_all_students(self.path)
        self.assertEqual([s.student_id for s in loaded], ["S001", "S002"])
        self.assertEqual(loaded[0].teaching_skills, ["Python"])

    def test_bad_lines_do_not_stop_the_load(self):
        with open(self.path, "w") as f:
            f.write("S001|Asha|a@x.com|pw12|-|-|0|0\n")
            f.write("this line is broken\n")
            f.write("\n")
            f.write("S002|Ravi|r@x.com|pw34|-|-|0|0\n")
        self.assertEqual(len(load_all_students(self.path)), 2)


class TestStudentLookup(unittest.TestCase):
    def setUp(self):
        self.students = [
            Student("S001", "Asha", "Asha@X.com", "pw12"),
            Student("S002", "Ravi", "ravi@x.com", "pw34"),
        ]

    def test_find_by_id_ignores_case(self):
        self.assertEqual(find_student_by_id(self.students, "s002").name, "Ravi")

    def test_find_by_id_not_found(self):
        self.assertIsNone(find_student_by_id(self.students, "S999"))

    def test_find_by_email_ignores_case(self):
        self.assertEqual(find_student_by_email(self.students, "asha@x.COM").name, "Asha")

    def test_find_by_email_not_found(self):
        self.assertIsNone(find_student_by_email(self.students, "nobody@x.com"))


class TestStudentIdGeneration(unittest.TestCase):
    def test_first_id(self):
        self.assertEqual(generate_new_student_id([]), "S001")

    def test_next_id_is_highest_plus_one(self):
        students = [Student("S001", "A", "a@x.com", "pw12"),
                    Student("S005", "B", "b@x.com", "pw12")]
        self.assertEqual(generate_new_student_id(students), "S006")

    def test_ids_that_do_not_follow_the_pattern_are_ignored(self):
        students = [Student("S002", "A", "a@x.com", "pw12"),
                    Student("SX", "B", "b@x.com", "pw12")]
        self.assertEqual(generate_new_student_id(students), "S003")


if __name__ == "__main__":
    unittest.main()
