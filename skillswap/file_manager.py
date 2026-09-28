"""
file_manager.py

Creates the data folder and the .txt files if they don't exist yet, and keeps the file paths in one place so the other modules import them instead of retyping the strings.
"""

import os

# project root = the folder that contains the skillswap/ package. Anchoring data/ there
# means it is the same folder no matter which directory the program is started from.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(PROJECT_ROOT, "data")

STUDENTS_FILE = os.path.join(DATA_FOLDER, "students.txt")
REQUESTS_FILE = os.path.join(DATA_FOLDER, "requests.txt")
SESSIONS_FILE = os.path.join(DATA_FOLDER, "sessions.txt")
SKILLS_FILE = os.path.join(DATA_FOLDER, "skills.txt")


def setup_data_files():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    # empty files are enough for these three; the load functions handle no lines
    for filepath in [STUDENTS_FILE, REQUESTS_FILE, SESSIONS_FILE]:
        if not os.path.exists(filepath):
            f = open(filepath, "w")
            f.close()

    if not os.path.exists(SKILLS_FILE):
        f = open(SKILLS_FILE, "w")
        # only written when skills.txt doesn't exist yet, so skills students add later
        # are never overwritten. The starter list gives new users something to pick from.
        starter_skills = [
            "Python|Programming",
            "Guitar|Music",
            "Public Speaking|Soft Skills",
            "Photoshop|Design",
            "Cooking|Lifestyle",
            "Excel|Office Tools",
            "Chess|Games",
            "Sketching|Art",
        ]
        for line in starter_skills:
            f.write(line + "\n")
        f.close()