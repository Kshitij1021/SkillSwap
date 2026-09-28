"""Tests for skillswap/exchange_request.py."""

import os
import sys

# lets a test file also be run directly (e.g. the "Run Python File" button in VS Code):
# the project root is added to the path so `import skillswap` works from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import os
import tempfile
import unittest

from skillswap.exchange_request import (
    ExchangeRequest, load_all_requests, save_all_requests, generate_new_request_id,
)


def make_request(request_id="R001"):
    return ExchangeRequest(request_id, "S001", "S002", "Guitar", "Python")


class TestExchangeRequest(unittest.TestCase):
    def test_new_request_is_pending_and_dated_today(self):
        r = make_request()
        self.assertEqual(r.status, "Pending")
        self.assertEqual(r.date_created, datetime.date.today().isoformat())

    def test_accept(self):
        r = make_request()
        r.accept()
        self.assertEqual(r.status, "Accepted")

    def test_reject(self):
        r = make_request()
        r.reject()
        self.assertEqual(r.status, "Rejected")

    def test_round_trip(self):
        r = ExchangeRequest("R004", "S001", "S002", "Guitar", "Python",
                            "Accepted", "2026-01-15")
        copy = ExchangeRequest.from_line(r.to_line())
        self.assertEqual(r.to_line(), copy.to_line())
        self.assertEqual(copy.status, "Accepted")
        self.assertEqual(copy.date_created, "2026-01-15")

    def test_to_line_format(self):
        r = ExchangeRequest("R001", "S001", "S002", "Guitar", "Python",
                            "Pending", "2026-01-15")
        self.assertEqual(r.to_line(), "R001|S001|S002|Guitar|Python|Pending|2026-01-15")

    def test_blank_comment_and_incomplete_lines_are_skipped(self):
        self.assertIsNone(ExchangeRequest.from_line(""))
        self.assertIsNone(ExchangeRequest.from_line("# note"))
        self.assertIsNone(ExchangeRequest.from_line("R001|S001|S002"))


class TestRequestFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "requests.txt")

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(load_all_requests(self.path), [])

    def test_save_then_load(self):
        r1, r2 = make_request("R001"), make_request("R002")
        r2.accept()
        save_all_requests(self.path, [r1, r2])
        loaded = load_all_requests(self.path)
        self.assertEqual([r.request_id for r in loaded], ["R001", "R002"])
        self.assertEqual(loaded[1].status, "Accepted")


class TestRequestIdGeneration(unittest.TestCase):
    def test_first_id(self):
        self.assertEqual(generate_new_request_id([]), "R001")

    def test_next_id_is_highest_plus_one(self):
        self.assertEqual(
            generate_new_request_id([make_request("R001"), make_request("R009")]),
            "R010")

    def test_bad_ids_are_ignored(self):
        self.assertEqual(
            generate_new_request_id([make_request("R002"), make_request("Rxx")]),
            "R003")


if __name__ == "__main__":
    unittest.main()
