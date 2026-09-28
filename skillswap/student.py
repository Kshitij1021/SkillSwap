"""
student.py

The Student class plus the functions that load and save students in data/students.txt.

One student per line, fields separated by "|":
student_id|name|email|password|teaching_skills|learning_skills|rating_total|rating_count

Inside the two skill fields the skills are comma separated, and "-" means the list is empty. Ratings are kept as a running total and a count, so the average can be worked out without storing every single rating.
"""


class Student:
    def __init__(self, student_id, name, email, password, teaching_skills=None,
                 learning_skills=None, rating_total=0, rating_count=0):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.password = password

        # None as the default instead of [] because a list default is created once
        # and would then be shared by every Student object
        if teaching_skills is None:
            self.teaching_skills = []
        else:
            self.teaching_skills = teaching_skills

        if learning_skills is None:
            self.learning_skills = []
        else:
            self.learning_skills = learning_skills

        self.rating_total = rating_total
        self.rating_count = rating_count

    def average_rating(self):
        # nobody has rated this student yet (also avoids dividing by zero)
        if self.rating_count == 0:
            return 0.0
        return round(self.rating_total / self.rating_count, 2)

    def add_teaching_skill(self, skill_name):
        # .title() so 'python' and 'PYTHON' are stored the same way and the
        # duplicate check below works
        skill_name = skill_name.strip().title()
        if skill_name not in self.teaching_skills:
            self.teaching_skills.append(skill_name)
            return True
        return False

    def add_learning_skill(self, skill_name):
        skill_name = skill_name.strip().title()
        if skill_name not in self.learning_skills:
            self.learning_skills.append(skill_name)
            return True
        return False

    def remove_teaching_skill(self, skill_name):
        skill_name = skill_name.strip().title()
        if skill_name in self.teaching_skills:
            self.teaching_skills.remove(skill_name)
            return True
        return False

    def remove_learning_skill(self, skill_name):
        skill_name = skill_name.strip().title()
        if skill_name in self.learning_skills:
            self.learning_skills.remove(skill_name)
            return True
        return False

    def show_profile(self):
        print("-------------------------------------")
        print("Student ID    :", self.student_id)
        print("Name          :", self.name)
        print("Email         :", self.email)
        print("Can Teach     :", ", ".join(self.teaching_skills) if self.teaching_skills else "None yet")
        print("Wants to Learn:", ", ".join(self.learning_skills) if self.learning_skills else "None yet")
        print("Rating        :", self.average_rating(), "/ 5  (", self.rating_count, "ratings)")
        print("-------------------------------------")

    def to_line(self):
        # '-' stands in for an empty list so the field is never blank in the file
        teach_str = ",".join(self.teaching_skills) if self.teaching_skills else "-"
        learn_str = ",".join(self.learning_skills) if self.learning_skills else "-"
        return f"{self.student_id}|{self.name}|{self.email}|{self.password}|{teach_str}|{learn_str}|{self.rating_total}|{self.rating_count}"

    @staticmethod
    def from_line(line):
        # blank lines and lines starting with # are ignored
        line = line.strip()
        if line == "" or line.startswith("#"):
            return None

        parts = line.split("|")
        # a line with missing fields is skipped instead of crashing the whole load
        if len(parts) < 8:
            return None

        student_id = parts[0]
        name = parts[1]
        email = parts[2]
        password = parts[3]
        teach_str = parts[4]
        learn_str = parts[5]
        # float() so a value like 12.0, written back after an earlier load and save,
        # still reads fine
        rating_total = float(parts[6])
        rating_count = int(parts[7])

        # turn the '-' placeholder back into an empty list
        teaching_skills = [] if teach_str in ("-", "") else teach_str.split(",")
        learning_skills = [] if learn_str in ("-", "") else learn_str.split(",")

        return Student(student_id, name, email, password, teaching_skills,
                        learning_skills, rating_total, rating_count)


def load_all_students(filepath):
    students_list = []
    try:
        file = open(filepath, "r")
        lines = file.readlines()
        file.close()
        for line in lines:
            student_obj = Student.from_line(line)
            if student_obj is not None:
                students_list.append(student_obj)
    # no file yet just means no students yet
    except FileNotFoundError:
        students_list = []
    return students_list


def save_all_students(filepath, students_list):
    file = open(filepath, "w")
    for s in students_list:
        file.write(s.to_line() + "\n")
    file.close()


def find_student_by_id(students_list, student_id):
    for s in students_list:
        # compared in upper case so 's001' still finds 'S001'
        if s.student_id.upper() == student_id.upper():
            return s
    return None


def find_student_by_email(students_list, email):
    for s in students_list:
        # compared in lower case so A@x.com and a@x.com count as the same account
        if s.email.lower() == email.lower():
            return s
    return None


def generate_new_student_id(students_list):
    # ids look like S001, S002, ... The new id is the highest number in use + 1
    # (not the number of students), so an id is never handed out twice.
    if len(students_list) == 0:
        return "S001"

    last_num = 0
    for s in students_list:
        try:
            # [1:] drops the leading 'S'; ids that don't follow S### are skipped below
            num = int(s.student_id[1:])
            if num > last_num:
                last_num = num
        except ValueError:
            pass

    return "S" + str(last_num + 1).zfill(3)