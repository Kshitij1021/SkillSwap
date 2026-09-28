"""Tests for skillswap/validators.py, including the input loops (input() is mocked)."""

import os
import sys

# lets a test file also be run directly (e.g. the "Run Python File" button in VS Code):
# the project root is added to the path so `import skillswap` works from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import contextlib
import io
import unittest
from unittest import mock

from skillswap import validators


def ask(function, inputs, *args, **kwargs):
    """Run an input-loop function with fake typed input; return (result, printed text)."""
    buffer = io.StringIO()
    with mock.patch("builtins.input", side_effect=inputs), \
            contextlib.redirect_stdout(buffer):
        result = function(*args, **kwargs)
    return result, buffer.getvalue()


class TestEmail(unittest.TestCase):
    def test_valid_emails(self):
        for email in ["a@x.com", "  a@x.com  ", "first.last@college.edu.in"]:
            self.assertTrue(validators.is_valid_email(email), email)

    def test_invalid_emails(self):
        for email in ["", "plain", "no-at.com", "a@b", "@x.com", "a@", "a@@x.com"]:
            self.assertFalse(validators.is_valid_email(email), email)


class TestNameAndPassword(unittest.TestCase):
    def test_name(self):
        self.assertTrue(validators.is_valid_name("Al"))
        self.assertFalse(validators.is_valid_name("A"))
        self.assertFalse(validators.is_valid_name("   "))

    def test_password_length(self):
        self.assertTrue(validators.is_valid_password("abcd"))
        self.assertFalse(validators.is_valid_password("abc"))
        self.assertFalse(validators.is_valid_password(""))


class TestDate(unittest.TestCase):
    def test_valid_dates(self):
        self.assertTrue(validators.is_valid_date("25-12-2026"))
        self.assertTrue(validators.is_valid_date(" 29-02-2028 "))  # leap year

    def test_impossible_dates(self):
        self.assertFalse(validators.is_valid_date("31-02-2026"))
        self.assertFalse(validators.is_valid_date("29-02-2027"))  # not a leap year
        self.assertFalse(validators.is_valid_date("32-01-2026"))
        self.assertFalse(validators.is_valid_date("10-13-2026"))

    def test_wrong_format(self):
        for text in ["2026-12-25", "25/12/2026", "tomorrow", ""]:
            self.assertFalse(validators.is_valid_date(text), text)


class TestGetIntInput(unittest.TestCase):
    def test_accepts_a_number(self):
        result, _ = ask(validators.get_int_input, ["3"], "Pick: ")
        self.assertEqual(result, 3)

    def test_letters_and_blank_are_rejected_until_a_number_comes(self):
        result, out = ask(validators.get_int_input, ["abc", "", "7"], "Pick: ")
        self.assertEqual(result, 7)
        self.assertEqual(out.count("Please enter a valid number."), 2)

    def test_range_is_enforced(self):
        result, out = ask(validators.get_int_input, ["0", "11", "5"], "Pick: ", 1, 10)
        self.assertEqual(result, 5)
        self.assertIn("not less than 1", out)
        self.assertIn("not more than 10", out)

    def test_boundaries_are_allowed(self):
        self.assertEqual(ask(validators.get_int_input, ["1"], "P: ", 1, 5)[0], 1)
        self.assertEqual(ask(validators.get_int_input, ["5"], "P: ", 1, 5)[0], 5)


class TestGetNonEmptyInput(unittest.TestCase):
    def test_returns_stripped_text(self):
        result, _ = ask(validators.get_non_empty_input, ["  hello  "], "Text: ")
        self.assertEqual(result, "hello")

    def test_blank_is_rejected(self):
        result, out = ask(validators.get_non_empty_input, ["", "   ", "ok"], "Text: ")
        self.assertEqual(result, "ok")
        self.assertEqual(out.count("cannot be empty"), 2)

    def test_pipe_is_rejected(self):
        result, out = ask(validators.get_non_empty_input, ["a|b", "ab"], "Text: ")
        self.assertEqual(result, "ab")
        self.assertIn("| symbol is not allowed", out)


if __name__ == "__main__":
    unittest.main()
