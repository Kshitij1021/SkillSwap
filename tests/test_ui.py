"""Tests for skillswap/ui.py (only the parts that print text)."""

import contextlib
import io
import unittest

from skillswap import ui


def capture(function, *args):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        function(*args)
    return buffer.getvalue()


class TestShorten(unittest.TestCase):
    def test_short_text_is_unchanged(self):
        self.assertEqual(ui.shorten("Python"), "Python")

    def test_long_text_is_cut_with_dots(self):
        result = ui.shorten("x" * 100)
        self.assertEqual(len(result), ui.MAX_CELL)
        self.assertTrue(result.endswith("..."))

    def test_non_strings_are_converted(self):
        self.assertEqual(ui.shorten(4.5), "4.5")


class TestMessages(unittest.TestCase):
    def test_message_prefixes(self):
        self.assertEqual(capture(ui.show_message, "hi"), ">> hi\n")
        self.assertEqual(capture(ui.show_success, "done"), "[OK] done\n")
        self.assertEqual(capture(ui.show_error, "bad"), "[!!] bad\n")


class TestMenuAndTitle(unittest.TestCase):
    def test_title_is_centred_between_borders(self):
        lines = capture(ui.show_title, "HELLO").splitlines()
        self.assertEqual(lines[0], "=" * ui.WIDTH)
        self.assertEqual(lines[1].strip(), "HELLO")
        self.assertEqual(len(lines[1]), ui.WIDTH)

    def test_menu_numbers_start_at_one(self):
        out = capture(ui.show_menu, "MENU", ["First", "Second"])
        self.assertIn("[1]  First", out)
        self.assertIn("[2]  Second", out)
        self.assertNotIn("[0]", out)


class TestTable(unittest.TestCase):
    def test_all_lines_have_the_same_width(self):
        out = capture(ui.show_table, ["ID", "Name"],
                      [["S001", "Asha"], ["S002", "A much longer name here"]])
        lines = out.splitlines()
        self.assertEqual(len(set(len(line) for line in lines)), 1)
        self.assertEqual(len(lines), 6)  # border, heading, border, 2 rows, border

    def test_long_cells_are_shortened(self):
        out = capture(ui.show_table, ["Skills"], [["y" * 100]])
        self.assertIn("...", out)
        self.assertNotIn("y" * 50, out)

    def test_empty_table_still_prints_headings(self):
        out = capture(ui.show_table, ["ID", "Name"], [])
        self.assertIn("ID", out)
        self.assertEqual(len(out.splitlines()), 4)


if __name__ == "__main__":
    unittest.main()
