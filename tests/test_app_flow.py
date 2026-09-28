"""End to end tests of the menu functions in skillswap/app.py.

The keyboard is faked with mock.patch on input(), and the four data files are pointed
at a temp folder. The steps follow the manual test in README.md:
register A and B -> add skills -> match -> request -> accept -> schedule -> rate.
"""

import os
import sys

# lets a test file also be run directly (e.g. the "Run Python File" button in VS Code):
# the project root is added to the path so `import skillswap` works from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from skillswap import app
from skillswap import student as student_module
from skillswap import exchange_request as request_module
from skillswap import session as session_module


def run(function, inputs=()):
    """Call a menu function with fake typed input. Returns (return value, printed text)."""
    buffer = io.StringIO()
    with mock.patch("builtins.input", side_effect=list(inputs)), \
            contextlib.redirect_stdout(buffer):
        result = function()
    return result, buffer.getvalue()


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for name in ["STUDENTS_FILE", "REQUESTS_FILE", "SESSIONS_FILE", "SKILLS_FILE"]:
            path = os.path.join(self.tmp.name, name.lower().replace("_file", ".txt"))
            patcher = mock.patch.object(app, name, path)
            patcher.start()
            self.addCleanup(patcher.stop)
        app.current_user = None
        self.addCleanup(setattr, app, "current_user", None)

    # helpers
    def register(self, name, email, password="pass1234"):
        return run(app.register_new_student, [name, email, password])

    def login(self, email, password="pass1234"):
        result, _ = run(app.login_student, [email, password])
        return result

    def set_skills(self, teaches, learns):
        """Give the logged in student skills and save them, like the profile menu does."""
        for skill in teaches:
            app.current_user.add_teaching_skill(skill)
        for skill in learns:
            app.current_user.add_learning_skill(skill)
        students = student_module.load_all_students(app.STUDENTS_FILE)
        app.update_student_in_file(students)

    def students(self):
        return student_module.load_all_students(app.STUDENTS_FILE)

    def requests(self):
        return request_module.load_all_requests(app.REQUESTS_FILE)

    def sessions(self):
        return session_module.load_all_sessions(app.SESSIONS_FILE)

    def two_students_with_skills(self):
        """A teaches Guitar and wants Python; B teaches Python and wants Guitar."""
        self.register("Alice Roy", "alice@x.com")
        self.register("Bob Das", "bob@x.com")
        self.login("alice@x.com")
        self.set_skills(["guitar"], ["python"])
        self.login("bob@x.com")
        self.set_skills(["python"], ["guitar"])


class TestHelpers(AppTestCase):
    def test_join_skills(self):
        self.assertEqual(app.join_skills([]), "None yet")
        self.assertEqual(app.join_skills(["Python", "Guitar"]), "Python, Guitar")

    def test_has_skill_ignores_case_and_spaces(self):
        self.assertTrue(app.has_skill(["Python"], "  python "))
        self.assertFalse(app.has_skill(["Python"], "Guitar"))
        self.assertFalse(app.has_skill([], "Python"))


class TestRegisterAndLogin(AppTestCase):
    def test_register_saves_student_with_next_id(self):
        _, out = self.register("Alice Roy", "alice@x.com")
        self.assertIn("Registration successful", out)
        self.assertIn("S001", out)
        self.register("Bob Das", "bob@x.com")
        self.assertEqual([s.student_id for s in self.students()], ["S001", "S002"])

    def test_register_retries_on_bad_input(self):
        inputs = ["A", "Alice Roy", "not-an-email", "alice@x.com", "abc", "pass1234"]
        _, out = run(app.register_new_student, inputs)
        self.assertIn("Name looks too short", out)
        self.assertIn("email does not look correct", out)
        self.assertIn("Password too short", out)
        self.assertEqual(len(self.students()), 1)

    def test_duplicate_email_is_rejected_ignoring_case(self):
        self.register("Alice Roy", "alice@x.com")
        _, out = run(app.register_new_student, ["Alice Two", "ALICE@x.com"])
        self.assertIn("already exists", out)
        self.assertEqual(len(self.students()), 1)

    def test_login_success_sets_current_user(self):
        self.register("Alice Roy", "alice@x.com")
        self.assertTrue(self.login("alice@x.com"))
        self.assertEqual(app.current_user.name, "Alice Roy")

    def test_login_wrong_password(self):
        self.register("Alice Roy", "alice@x.com")
        result, out = run(app.login_student, ["alice@x.com", "wrong"])
        self.assertFalse(result)
        self.assertIn("Wrong password", out)
        self.assertIsNone(app.current_user)

    def test_login_unknown_email(self):
        result, out = run(app.login_student, ["ghost@x.com", "pass1234"])
        self.assertFalse(result)
        self.assertIn("No account found", out)

    def test_logout_clears_current_user(self):
        self.register("Alice Roy", "alice@x.com")
        self.login("alice@x.com")
        run(app.logout_student)
        self.assertIsNone(app.current_user)


class TestMatching(AppTestCase):
    def test_match_is_found(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        _, out = run(app.find_matches)
        self.assertIn("Bob Das", out)
        self.assertIn("Python", out)

    def test_own_profile_is_not_a_match(self):
        self.register("Alice Roy", "alice@x.com")
        self.login("alice@x.com")
        self.set_skills(["python"], ["python"])
        _, out = run(app.find_matches)
        self.assertIn("No matches found", out)

    def test_no_learning_skill_gives_a_hint(self):
        self.register("Alice Roy", "alice@x.com")
        self.login("alice@x.com")
        _, out = run(app.find_matches)
        self.assertIn("not added any skill you want to learn", out)

    def test_browse_lists_everyone_and_marks_me(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        _, out = run(app.browse_all_students)
        self.assertIn("Alice Roy (you)", out)
        self.assertIn("Bob Das", out)
        self.assertIn("Total users: 2", out)


class TestSendRequest(AppTestCase):
    def test_send_request_saves_pending_request(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        _, out = run(app.send_exchange_request, ["S002", "python", "guitar"])
        self.assertIn("Request sent", out)
        request = self.requests()[0]
        self.assertEqual((request.sender_id, request.receiver_id), ("S001", "S002"))
        self.assertEqual((request.skill_wanted, request.skill_offered), ("Python", "Guitar"))
        self.assertEqual(request.status, "Pending")

    def test_unknown_student_id(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        _, out = run(app.send_exchange_request, ["S999"])
        self.assertIn("No student found", out)
        self.assertEqual(self.requests(), [])

    def test_cannot_request_yourself(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        _, out = run(app.send_exchange_request, ["S001"])
        self.assertIn("cannot send a request to yourself", out)

    def test_needs_a_teaching_skill_to_offer(self):
        self.two_students_with_skills()
        self.register("Cara Sen", "cara@x.com")
        self.login("cara@x.com")
        _, out = run(app.send_exchange_request, ["S002"])
        self.assertIn("not listed any teaching skill", out)

    def test_wanted_skill_must_be_taught_by_receiver(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        _, out = run(app.send_exchange_request, ["S002", "chess"])
        self.assertIn("does not teach this skill", out)
        self.assertEqual(self.requests(), [])

    def test_offered_skill_must_be_in_my_list(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        _, out = run(app.send_exchange_request, ["S002", "python", "chess"])
        self.assertIn("not in your teaching list", out)
        self.assertEqual(self.requests(), [])


class TestIncomingRequests(AppTestCase):
    def send_request(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        run(app.send_exchange_request, ["S002", "python", "guitar"])

    def test_receiver_can_accept(self):
        self.send_request()
        self.login("bob@x.com")
        _, out = run(app.view_incoming_requests, ["R001", "a"])
        self.assertIn("Request accepted", out)
        self.assertEqual(self.requests()[0].status, "Accepted")

    def test_receiver_can_reject(self):
        self.send_request()
        self.login("bob@x.com")
        _, out = run(app.view_incoming_requests, ["R001", "R"])
        self.assertIn("Request rejected", out)
        self.assertEqual(self.requests()[0].status, "Rejected")

    def test_invalid_decision_changes_nothing(self):
        self.send_request()
        self.login("bob@x.com")
        _, out = run(app.view_incoming_requests, ["R001", "x"])
        self.assertIn("Invalid option", out)
        self.assertEqual(self.requests()[0].status, "Pending")

    def test_handled_requests_disappear_from_incoming(self):
        self.send_request()
        self.login("bob@x.com")
        run(app.view_incoming_requests, ["R001", "R"])
        _, out = run(app.view_incoming_requests)
        self.assertIn("No pending requests", out)

    def test_sender_does_not_see_it_as_incoming(self):
        self.send_request()
        self.login("alice@x.com")
        _, out = run(app.view_incoming_requests)
        self.assertIn("No pending requests", out)

    def test_sent_requests_show_status(self):
        self.send_request()
        _, out = run(app.view_my_sent_requests)
        self.assertIn("R001", out)
        self.assertIn("Pending", out)

    def test_no_sent_requests_message(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        _, out = run(app.view_my_sent_requests)
        self.assertIn("not sent any requests", out)


class TestSessionsAndFeedback(AppTestCase):
    def accepted_request(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        run(app.send_exchange_request, ["S002", "python", "guitar"])
        self.login("bob@x.com")
        run(app.view_incoming_requests, ["R001", "A"])

    def test_cannot_schedule_without_accepted_request(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        _, out = run(app.schedule_session)
        self.assertIn("no accepted requests", out)

    def test_schedule_session(self):
        self.accepted_request()
        _, out = run(app.schedule_session, ["R001", "25-12-2026"])
        self.assertIn("Session scheduled", out)
        session = self.sessions()[0]
        self.assertEqual(session.session_id, "SE001")
        self.assertEqual(session.request_id, "R001")
        self.assertEqual(session.skill, "Python")
        self.assertEqual(session.session_date, "25-12-2026")
        self.assertEqual(session.status, "Scheduled")

    def test_invalid_date_is_asked_again(self):
        self.accepted_request()
        _, out = run(app.schedule_session, ["R001", "31-02-2026", "tomorrow", "25-12-2026"])
        self.assertEqual(out.count("not a valid date"), 2)
        self.assertEqual(len(self.sessions()), 1)

    def test_unknown_request_id(self):
        self.accepted_request()
        _, out = run(app.schedule_session, ["R777"])
        self.assertIn("Invalid Request ID", out)
        self.assertEqual(self.sessions(), [])

    def test_complete_and_rate(self):
        self.accepted_request()
        run(app.schedule_session, ["R001", "25-12-2026"])
        self.login("alice@x.com")
        _, out = run(app.view_my_sessions, ["SE001", "y", "5", "Great teacher"])
        self.assertIn("marked as completed", out)
        self.assertIn("Thanks for your feedback", out)

        session = self.sessions()[0]
        self.assertEqual((session.status, session.rating, session.comment),
                         ("Completed", 5, "Great teacher"))

        # the rating goes to the OTHER student (Bob), never to the one who gave it
        alice, bob = self.students()
        self.assertEqual((bob.rating_total, bob.rating_count), (5, 1))
        self.assertEqual((alice.rating_total, alice.rating_count), (0, 0))

    def test_rating_out_of_range_is_asked_again(self):
        self.accepted_request()
        run(app.schedule_session, ["R001", "25-12-2026"])
        self.login("alice@x.com")
        _, out = run(app.view_my_sessions, ["SE001", "y", "9", "0", "4", "ok"])
        self.assertIn("not more than 5", out)
        self.assertIn("not less than 1", out)
        self.assertEqual(self.sessions()[0].rating, 4)

    def test_complete_without_feedback(self):
        self.accepted_request()
        run(app.schedule_session, ["R001", "25-12-2026"])
        self.login("alice@x.com")
        run(app.view_my_sessions, ["SE001", "n"])
        session = self.sessions()[0]
        self.assertEqual((session.status, session.rating), ("Completed", 0))
        self.assertEqual(self.students()[1].rating_count, 0)

    def test_unknown_session_id(self):
        self.accepted_request()
        run(app.schedule_session, ["R001", "25-12-2026"])
        _, out = run(app.view_my_sessions, ["SE999"])
        self.assertIn("Session not found", out)

    def test_no_sessions_message(self):
        self.two_students_with_skills()
        self.login("alice@x.com")
        _, out = run(app.view_my_sessions)
        self.assertIn("No sessions yet", out)

    def test_outsider_does_not_see_the_session(self):
        self.accepted_request()
        run(app.schedule_session, ["R001", "25-12-2026"])
        self.register("Cara Sen", "cara@x.com")
        self.login("cara@x.com")
        _, out = run(app.view_my_sessions)
        self.assertIn("No sessions yet", out)


if __name__ == "__main__":
    unittest.main()
