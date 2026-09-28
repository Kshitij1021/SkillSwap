"""
ui.py

Everything that controls how the terminal app looks: titles, menus, tables and status messages. main.py only calls these functions, so a change in appearance only needs edits here.
"""

import os

WIDTH = 64          # characters per line for titles, menus and borders
MAX_CELL = 28       # longest text shown in a table cell before it is cut


def clear_screen():
    # os.name is 'nt' on Windows (cls); Linux and Mac use clear
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def show_title(title):
    print("=" * WIDTH)
    print(title.center(WIDTH))
    print("=" * WIDTH)


def show_menu(title, options):
    # options are numbered from 1 so the numbers match what the user types
    print()
    show_title(title)
    number = 1
    for option in options:
        print("  [" + str(number) + "]  " + option)
        number = number + 1
    print("-" * WIDTH)


def show_message(text):
    print(">> " + text)


def show_success(text):
    print("[OK] " + text)


def show_error(text):
    print("[!!] " + text)


def pause():
    input("\nPress Enter to continue...")


def shorten(value):
    # long values are cut with '...' so one long skill list can't make the table
    # wider than the screen
    text = str(value)
    if len(text) > MAX_CELL:
        text = text[:MAX_CELL - 3] + "..."
    return text


def show_table(headings, rows):
    # headings: the column names; rows: a list of lists, one inner list per row

    # each column is as wide as its longest cell (after shortening) or its heading
    widths = []
    for heading in headings:
        widths.append(len(heading))

    for row in rows:
        for i in range(len(row)):
            cell = shorten(row[i])
            if len(cell) > widths[i]:
                widths[i] = len(cell)

    # border line like +-----+-------+ (the +2 is one space on each side of the text)
    line = "+"
    for w in widths:
        line = line + "-" * (w + 2) + "+"

    # heading row between two borders
    print(line)
    heading_row = "|"
    for i in range(len(headings)):
        heading_row = heading_row + " " + headings[i].ljust(widths[i]) + " |"
    print(heading_row)
    print(line)

    # data rows; ljust pads each cell so the | signs line up
    for row in rows:
        row_text = "|"
        for i in range(len(row)):
            row_text = row_text + " " + shorten(row[i]).ljust(widths[i]) + " |"
        print(row_text)
    print(line)