"""Tests for skillswap/file_manager.py. The data paths are redirected to a temp folder
so the real data/ folder is never touched."""

import os
import tempfile
import unittest
from unittest import mock

from skillswap import file_manager


class TestSetupDataFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        folder = os.path.join(self.tmp.name, "data")
        self.paths = {
            "DATA_FOLDER": folder,
            "STUDENTS_FILE": os.path.join(folder, "students.txt"),
            "REQUESTS_FILE": os.path.join(folder, "requests.txt"),
            "SESSIONS_FILE": os.path.join(folder, "sessions.txt"),
            "SKILLS_FILE": os.path.join(folder, "skills.txt"),
        }
        patcher = mock.patch.multiple(file_manager, **self.paths)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_creates_folder_and_all_files(self):
        file_manager.setup_data_files()
        self.assertTrue(os.path.isdir(self.paths["DATA_FOLDER"]))
        for key in ["STUDENTS_FILE", "REQUESTS_FILE", "SESSIONS_FILE", "SKILLS_FILE"]:
            self.assertTrue(os.path.isfile(self.paths[key]), key)

    def test_starter_skills_are_written(self):
        file_manager.setup_data_files()
        with open(self.paths["SKILLS_FILE"]) as f:
            lines = [line.strip() for line in f if line.strip()]
        self.assertEqual(len(lines), 8)
        self.assertIn("Python|Programming", lines)

    def test_other_files_start_empty(self):
        file_manager.setup_data_files()
        for key in ["STUDENTS_FILE", "REQUESTS_FILE", "SESSIONS_FILE"]:
            self.assertEqual(os.path.getsize(self.paths[key]), 0, key)

    def test_second_run_does_not_overwrite_existing_data(self):
        file_manager.setup_data_files()
        with open(self.paths["SKILLS_FILE"], "a") as f:
            f.write("Chess Tactics|Games\n")
        with open(self.paths["STUDENTS_FILE"], "w") as f:
            f.write("S001|Asha|a@x.com|pw12|-|-|0|0\n")

        file_manager.setup_data_files()

        with open(self.paths["SKILLS_FILE"]) as f:
            self.assertIn("Chess Tactics|Games", f.read())
        with open(self.paths["STUDENTS_FILE"]) as f:
            self.assertIn("S001|Asha", f.read())


class TestPaths(unittest.TestCase):
    def test_data_folder_is_inside_the_project_root(self):
        self.assertEqual(os.path.dirname(file_manager.DATA_FOLDER),
                         file_manager.PROJECT_ROOT)
        self.assertTrue(os.path.isfile(os.path.join(file_manager.PROJECT_ROOT, "main.py")))

    def test_file_paths_are_inside_the_data_folder(self):
        for path in [file_manager.STUDENTS_FILE, file_manager.REQUESTS_FILE,
                     file_manager.SESSIONS_FILE, file_manager.SKILLS_FILE]:
            self.assertEqual(os.path.dirname(path), file_manager.DATA_FOLDER)


if __name__ == "__main__":
    unittest.main()
