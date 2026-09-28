"""
skill.py

The Skill class and the master skill list in data/skills.txt. The master list exists so students can see what is already on SkillSwap and pick from it, which keeps spellings consistent and makes matching easier.
"""


class Skill:
    def __init__(self, name, category="General"):
        # Title Case so 'python' and 'Python' can't both end up in the master list
        self.name = name.strip().title()
        if category:
            self.category = category.strip().title()
        else:
            self.category = "General"

    def __str__(self):
        return self.name + " (" + self.category + ")"

    def to_line(self):
        return self.name + "|" + self.category

    @staticmethod
    def from_line(line):
        line = line.strip()
        if line == "" or line.startswith("#"):
            return None
        parts = line.split("|")
        # a line with no category still loads, under General
        if len(parts) < 2:
            return Skill(parts[0], "General")
        return Skill(parts[0], parts[1])


def load_all_skills(filepath):
    # one Skill object per line; a missing file just gives an empty list
    skills_list = []
    try:
        file = open(filepath, "r")
        lines = file.readlines()
        file.close()
        for line in lines:
            skill_obj = Skill.from_line(line)
            if skill_obj is not None:
                skills_list.append(skill_obj)
    except FileNotFoundError:
        skills_list = []
    return skills_list


def add_new_skill_to_master(filepath, name, category):
    # lower case comparison stops duplicates like 'Python' and 'python'.
    # Returns False if the skill was already there.
    existing = load_all_skills(filepath)
    for s in existing:
        if s.name.lower() == name.strip().lower():
            return False

    # 'a' appends, so the skills already in the file are kept
    file = open(filepath, "a")
    new_skill = Skill(name, category)
    file.write(new_skill.to_line() + "\n")
    file.close()
    return True