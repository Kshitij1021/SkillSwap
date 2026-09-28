"""
validators.py

Input checks used by main.py. Each function either returns True/False or keeps asking until the input is usable, so the menu code never has to handle bad input itself.
"""

import datetime


# basic sanity check only: exactly one '@' and a '.' somewhere. It does not
# check that the dot comes after the '@', and it can't tell if the address is real.
def is_valid_email(email):
    email = email.strip()
    if "@" not in email or "." not in email:
        return False
    if email.count("@") != 1:
        return False
    if email.startswith("@") or email.endswith("@"):
        return False
    return True


def is_valid_name(name):
    return len(name.strip()) >= 2


# length only. Passwords are saved as plain text (see student.py), so this is
# a class-project check and not real security.
def is_valid_password(password):
    return len(password) >= 4


def is_valid_date(text):
    # strptime rejects impossible dates like 31-02-2026, which a simple split on '-'
    # would let through. Format is DD-MM-YYYY.
    try:
        datetime.datetime.strptime(text.strip(), "%d-%m-%Y")
        return True
    except ValueError:
        return False


def get_int_input(prompt, min_val=None, max_val=None):
    # int('') and int('abc') both raise ValueError, so one except covers blank
    # input and letters. Loops until the number is inside the allowed range.
    while True:
        raw = input(prompt)
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if min_val is not None and value < min_val:
            print("Please enter a number not less than", min_val)
            continue

        if max_val is not None and value > max_val:
            print("Please enter a number not more than", max_val)
            continue

        return value


def get_non_empty_input(prompt):
    # '|' separates the fields in our .txt files, so one typed into a name would
    # push every later field out of place. Commas are NOT blocked here, but skills
    # are stored comma-separated, so a comma inside a skill name splits it on reload.
    while True:
        value = input(prompt).strip()
        if value == "":
            print("This field cannot be empty, please try again.")
            continue
        if "|" in value:
            print("The | symbol is not allowed, please try again.")
            continue
        return value