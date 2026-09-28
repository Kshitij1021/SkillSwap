"""
session.py

A Session is created for the actual meetup once a request has been accepted. Either student can later mark it completed and leave a rating (1-5) and a short comment.

One session per line in data/sessions.txt:
session_id|request_id|sender_id|receiver_id|skill|session_date|status|rating|comment

A rating of 0 means no feedback has been given yet.
"""

import datetime


class Session:
    def __init__(self, session_id, request_id, sender_id, receiver_id, skill,
                 session_date=None, status="Scheduled", rating=0, comment="-"):
        self.session_id = session_id
        self.request_id = request_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.skill = skill
        # default is today in YYYY-MM-DD. Note: main.py passes the date the user typed
        # (DD-MM-YYYY), so both formats can end up in sessions.txt.
        if session_date is None:
            self.session_date = datetime.date.today().isoformat()
        else:
            self.session_date = session_date
        self.status = status
        self.rating = rating
        self.comment = comment

    def mark_completed(self):
        self.status = "Completed"

    def add_feedback(self, rating, comment):
        # there is only one rating slot per session, so only one student's feedback
        # gets stored
        self.rating = rating
        # '-' keeps the field non-empty in the file
        self.comment = comment if comment else "-"

    def to_line(self):
        return f"{self.session_id}|{self.request_id}|{self.sender_id}|{self.receiver_id}|{self.skill}|{self.session_date}|{self.status}|{self.rating}|{self.comment}"

    @staticmethod
    def from_line(line):
        line = line.strip()
        if line == "" or line.startswith("#"):
            return None
        parts = line.split("|")
        if len(parts) < 9:
            return None
        # rating goes through float() first because int('4.0') on its own would fail
        return Session(parts[0], parts[1], parts[2], parts[3], parts[4],
                        parts[5], parts[6], int(float(parts[7])), parts[8])


def load_all_sessions(filepath):
    sessions_list = []
    try:
        file = open(filepath, "r")
        lines = file.readlines()
        file.close()
        for line in lines:
            sess = Session.from_line(line)
            if sess is not None:
                sessions_list.append(sess)
    # no file yet just means no sessions yet
    except FileNotFoundError:
        sessions_list = []
    return sessions_list


def save_all_sessions(filepath, sessions_list):
    file = open(filepath, "w")
    for s in sessions_list:
        file.write(s.to_line() + "\n")
    file.close()


def generate_new_session_id(sessions_list):
    if len(sessions_list) == 0:
        return "SE001"

    last_num = 0
    for s in sessions_list:
        try:
            # [2:] drops the leading 'SE'
            num = int(s.session_id[2:])
            if num > last_num:
                last_num = num
        except ValueError:
            pass

    return "SE" + str(last_num + 1).zfill(3)