"""Tests for skillswap/skill.py (Skill class and the master skill list)."""

import os
import tempfile
import unittest

from skillswap.skill import Skill, load_all_skills, add_new_skill_to_master


class TestSkill(unittest.TestCase):
    def test_name_and_category_are_title_cased(self):
        s = Skill("  public speaking ", " soft skills ")
        self.assertEqual(s.name, "Public Speaking")
        self.assertEqual(s.category, "Soft Skills")

    def test_default_category_is_general(self):
        self.assertEqual(Skill("Chess").category, "General")
        self.assertEqual(Skill("Chess", "").category, "General")

    def test_str(self):
        self.assertEqual(str(Skill("Python", "Programming")), "Python (Programming)")

    def test_to_line(self):
        self.assertEqual(Skill("Python", "Programming").to_line(), "Python|Programming")

    def test_from_line(self):
        s = Skill.from_line("Guitar|Music")
        self.assertEqual((s.name, s.category), ("Guitar", "Music"))

    def test_from_line_without_category_uses_general(self):
        self.assertEqual(Skill.from_line("Chess").category, "General")

    def test_from_line_skips_blank_and_comment(self):
        self.assertIsNone(Skill.from_line(""))
        self.assertIsNone(Skill.from_line("# note"))


class TestMasterSkillList(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "skills.txt")

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(load_all_skills(self.path), [])

    def test_add_new_skill_creates_and_appends(self):
        self.assertTrue(add_new_skill_to_master(self.path, "python", "programming"))
        self.assertTrue(add_new_skill_to_master(self.path, "guitar", "music"))
        names = [s.name for s in load_all_skills(self.path)]
        self.assertEqual(names, ["Python", "Guitar"])

    def test_duplicate_ignoring_case_is_rejected(self):
        add_new_skill_to_master(self.path, "Python", "Programming")
        self.assertFalse(add_new_skill_to_master(self.path, "  PYTHON ", "Other"))
        self.assertEqual(len(load_all_skills(self.path)), 1)

    def test_existing_skills_are_kept_when_adding(self):
        with open(self.path, "w") as f:
            f.write("Chess|Games\n")
        add_new_skill_to_master(self.path, "Excel", "Office Tools")
        names = [s.name for s in load_all_skills(self.path)]
        self.assertEqual(names, ["Chess", "Excel"])


if __name__ == "__main__":
    unittest.main()
