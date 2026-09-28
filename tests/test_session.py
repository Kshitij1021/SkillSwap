"""Tests for skillswap/session.py."""

import os
import sys

# lets a test file also be run directly (e.g. the "Run Python File" button in VS Code):
# the project root is added to the path so `import skillswap` works from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import os
import tempfile
import unittest

from skillswap.session import (
    Session, load_all_sessions, save_all_sessions, generate_new_session_id,
)


def make_session(session_id="SE001"):
    return Session(session_id, "R001", "S001", "S002", "Python", "25-12-2026")


class TestSession(unittest.TestCase):
    def test_defaults(self):
        s = make_session()
        self.assertEqual(s.status, "Scheduled")
        self.assertEqual(s.rating, 0)
        self.assertEqual(s.comment, "-")

    def test_default_date_is_today(self):
        s = Session("SE001", "R001", "S001", "S002", "Python")
        self.assertEqual(s.session_date, datetime.date.today().isoformat())

    def test_mark_completed(self):
        s = make_session()
        s.mark_completed()
        self.assertEqual(s.status, "Completed")

    def test_add_feedback(self):
        s = make_session()
        s.add_feedback(4, "Very clear")
        self.assertEqual((s.rating, s.comment), (4, "Very clear"))

    def test_empty_comment_becomes_dash(self):
        s = make_session()
        s.add_feedback(5, "")
        self.assertEqual(s.comment, "-")

    def test_to_line_format(self):
        self.assertEqual(make_session().to_line(),
                         "SE001|R001|S001|S002|Python|25-12-2026|Scheduled|0|-")

    def test_round_trip(self):
        s = make_session()
        s.mark_completed()
        s.add_feedback(5, "Great")
        copy = Session.from_line(s.to_line())
        self.assertEqual(copy.to_line(), s.to_line())
        self.assertEqual(copy.rating, 5)
        self.assertIsInstance(copy.rating, int)

    def test_rating_written_as_float_still_loads(self):
        s = Session.from_line("SE001|R001|S001|S002|Python|25-12-2026|Completed|4.0|ok")
        self.assertEqual(s.rating, 4)

    def test_blank_comment_and_incomplete_lines_are_skipped(self):
        self.assertIsNone(Session.from_line(""))
        self.assertIsNone(Session.from_line("# note"))
        self.assertIsNone(Session.from_line("SE001|R001|S001"))


class TestSessionFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "sessions.txt")

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(load_all_sessions(self.path), [])

    def test_save_then_load(self):
        a, b = make_session("SE001"), make_session("SE002")
        b.mark_completed()
        save_all_sessions(self.path, [a, b])
        loaded = load_all_sessions(self.path)
        self.assertEqual([s.session_id for s in loaded], ["SE001", "SE002"])
        self.assertEqual(loaded[1].status, "Completed")


class TestSessionIdGeneration(unittest.TestCase):
    def test_first_id(self):
        self.assertEqual(generate_new_session_id([]), "SE001")

    def test_next_id_is_highest_plus_one(self):
        self.assertEqual(
            generate_new_session_id([make_session("SE001"), make_session("SE012")]),
            "SE013")

    def test_bad_ids_are_ignored(self):
        self.assertEqual(
            generate_new_session_id([make_session("SE004"), make_session("SExx")]),
            "SE005")


if __name__ == "__main__":
    unittest.main()
