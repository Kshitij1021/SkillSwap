"""
exchange_request.py

An ExchangeRequest is created when one student asks another for a skill swap. It starts as "Pending" and becomes "Accepted" or "Rejected" once the receiver responds.

One request per line in data/requests.txt:
request_id|sender_id|receiver_id|skill_offered|skill_wanted|status|date_created
"""

import datetime


class ExchangeRequest:
    def __init__(self, request_id, sender_id, receiver_id, skill_offered,
                 skill_wanted, status="Pending", date_created=None):
        self.request_id = request_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.skill_offered = skill_offered
        self.skill_wanted = skill_wanted
        self.status = status
        # a new request gets today's date (YYYY-MM-DD); loaded ones keep their own
        if date_created is None:
            self.date_created = datetime.date.today().isoformat()
        else:
            self.date_created = date_created

    def accept(self):
        self.status = "Accepted"

    def reject(self):
        self.status = "Rejected"

    def to_line(self):
        return f"{self.request_id}|{self.sender_id}|{self.receiver_id}|{self.skill_offered}|{self.skill_wanted}|{self.status}|{self.date_created}"

    @staticmethod
    def from_line(line):
        line = line.strip()
        if line == "" or line.startswith("#"):
            return None
        parts = line.split("|")
        # skip incomplete lines
        if len(parts) < 7:
            return None
        return ExchangeRequest(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6])


def load_all_requests(filepath):
    requests_list = []
    try:
        file = open(filepath, "r")
        lines = file.readlines()
        file.close()
        for line in lines:
            req = ExchangeRequest.from_line(line)
            if req is not None:
                requests_list.append(req)
    # no file yet just means no requests yet
    except FileNotFoundError:
        requests_list = []
    return requests_list


def save_all_requests(filepath, requests_list):
    file = open(filepath, "w")
    for r in requests_list:
        file.write(r.to_line() + "\n")
    file.close()


def generate_new_request_id(requests_list):
    if len(requests_list) == 0:
        return "R001"

    last_num = 0
    for r in requests_list:
        try:
            # [1:] drops the leading 'R'
            num = int(r.request_id[1:])
            if num > last_num:
                last_num = num
        except ValueError:
            pass

    return "R" + str(last_num + 1).zfill(3)