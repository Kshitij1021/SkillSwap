"""
app.py

SkillSwap - peer to peer skill exchange. All the menus live here. Start the app
by running main.py in the project root:

    python main.py

Students trade skills instead of paying for lessons. For example, someone who knows guitar and wants to learn Python gets matched with a student who can teach Python.
"""

from . import file_manager
from .file_manager import STUDENTS_FILE, REQUESTS_FILE, SESSIONS_FILE, SKILLS_FILE
from . import student as student_module
from . import exchange_request as request_module
from . import session as session_module
from . import skill as skill_module
from . import validators
from . import ui


# module level so every menu function can see who is logged in without passing
# it around; None means nobody is logged in
current_user = None


# helpers shared by several menus

def join_skills(skill_list):
    # ["Python", "Guitar"] -> "Python, Guitar", or "None yet" for an empty list
    if len(skill_list) == 0:
        return "None yet"
    return ", ".join(skill_list)


def has_skill(skill_list, name):
    # case-insensitive lookup, because what the user types won't always match the
    # case of what is stored
    for item in skill_list:
        if item.lower() == name.strip().lower():
            return True
    return False


def update_student_in_file(students):
    # students was loaded from the file before the edit, so put the edited
    # current_user back in by id, then rewrite the whole file (a .txt file can't be
    # changed one line at a time)
    for i in range(len(students)):
        if students[i].student_id == current_user.student_id:
            students[i] = current_user
            break
    student_module.save_all_students(STUDENTS_FILE, students)


# register / login / logout

def register_new_student():
    ui.show_title("NEW STUDENT REGISTRATION")
    students = student_module.load_all_students(STUDENTS_FILE)

    # get_non_empty_input already rejects blank text and '|'; the while loops
    # below add the length / format rules on top
    name = validators.get_non_empty_input("Enter your full name: ")
    while not validators.is_valid_name(name):
        ui.show_error("Name looks too short, try again.")
        name = validators.get_non_empty_input("Enter your full name: ")

    email = validators.get_non_empty_input("Enter your email: ")
    while not validators.is_valid_email(email):
        ui.show_error("That email does not look correct.")
        email = validators.get_non_empty_input("Enter your email: ")

    # one account per email, since login uses the email
    if student_module.find_student_by_email(students, email) is not None:
        ui.show_error("An account with this email already exists. Please login instead.")
        return

    password = validators.get_non_empty_input("Create a password (min 4 characters): ")
    while not validators.is_valid_password(password):
        ui.show_error("Password too short.")
        password = validators.get_non_empty_input("Create a password (min 4 characters): ")

    new_id = student_module.generate_new_student_id(students)
    new_student = student_module.Student(new_id, name, email, password)
    students.append(new_student)
    student_module.save_all_students(STUDENTS_FILE, students)

    ui.show_success("Registration successful! Your Student ID is " + new_id)
    ui.show_message("Please login now to start using SkillSwap.")


def login_student():
    global current_user
    ui.show_title("LOGIN")
    email = validators.get_non_empty_input("Email: ")
    # plain input(), so the password shows on screen while typing (getpass would
    # hide it)
    password = input("Password: ")

    # reloaded on every pass so the save at the bottom starts from what is
    # currently in the file
    students = student_module.load_all_students(STUDENTS_FILE)
    found = student_module.find_student_by_email(students, email)

    if found is None:
        ui.show_error("No account found with that email.")
        return False

    # plain text comparison; see the note in validators.py
    if found.password != password:
        ui.show_error("Wrong password.")
        return False

    current_user = found
    ui.show_success("Welcome back, " + current_user.name + "!")
    return True


def logout_student():
    global current_user
    ui.show_message("Logging out " + current_user.name + " ...")
    current_user = None


# profile

def show_master_skill_list():
    skills = skill_module.load_all_skills(SKILLS_FILE)
    print("\nSkills already on SkillSwap (pick one, or type a new one):")
    rows = []
    for s in skills:
        rows.append([s.name, s.category])
    ui.show_table(["Skill", "Category"], rows)


def manage_profile():
    while True:
        ui.clear_screen()
        ui.show_title("MY PROFILE")
        current_user.show_profile()
        ui.show_menu("PROFILE OPTIONS", [
            "Add a Teaching Skill",
            "Remove a Teaching Skill",
            "Add a Learning Skill",
            "Remove a Learning Skill",
            "Back to Main Menu",
        ])
        choice = validators.get_int_input("Enter choice: ", 1, 5)

        if choice == 5:
            break

        students = student_module.load_all_students(STUDENTS_FILE)

        if choice == 1:
            show_master_skill_list()
            skill_name = validators.get_non_empty_input("Skill you can teach: ")
            category = input("Category (press enter for General): ").strip()
            # new skills go into the shared master list first so other students see them
            skill_module.add_new_skill_to_master(SKILLS_FILE, skill_name, category)
            if current_user.add_teaching_skill(skill_name):
                ui.show_success(skill_name.title() + " added to your teaching skills.")
            else:
                ui.show_error("You already have this skill listed.")

        elif choice == 2:
            if len(current_user.teaching_skills) == 0:
                ui.show_error("You have no teaching skills to remove.")
            else:
                skill_name = validators.get_non_empty_input("Skill to remove: ")
                if current_user.remove_teaching_skill(skill_name):
                    ui.show_success("Removed.")
                else:
                    ui.show_error("That skill was not found in your list.")

        elif choice == 3:
            show_master_skill_list()
            skill_name = validators.get_non_empty_input("Skill you want to learn: ")
            category = input("Category (press enter for General): ").strip()
            skill_module.add_new_skill_to_master(SKILLS_FILE, skill_name, category)
            if current_user.add_learning_skill(skill_name):
                ui.show_success(skill_name.title() + " added to your learning list.")
            else:
                ui.show_error("You already want to learn this skill.")

        elif choice == 4:
            if len(current_user.learning_skills) == 0:
                ui.show_error("You have no learning skills to remove.")
            else:
                skill_name = validators.get_non_empty_input("Skill to remove: ")
                if current_user.remove_learning_skill(skill_name):
                    ui.show_success("Removed.")
                else:
                    ui.show_error("That skill was not found in your list.")

        # every option above changes current_user in memory; this writes it to disk
        update_student_in_file(students)
        ui.pause()


# browsing and matching

def browse_all_students():
    ui.show_title("ALL SKILLSWAP USERS")
    students = student_module.load_all_students(STUDENTS_FILE)

    if len(students) == 0:
        ui.show_message("No students have registered yet.")
        return

    rows = []
    for s in students:
        name = s.name
        if s.student_id == current_user.student_id:
            name = name + " (you)"
        rating = str(s.average_rating()) + " (" + str(s.rating_count) + ")"
        rows.append([s.student_id, name, join_skills(s.teaching_skills),
                     join_skills(s.learning_skills), rating])

    ui.show_table(["ID", "Name", "Teaches", "Wants to Learn", "Rating"], rows)
    print("Total users:", len(students))


def find_matches():
    ui.show_title("FIND A SKILL MATCH")
    students = student_module.load_all_students(STUDENTS_FILE)

    if len(current_user.learning_skills) == 0:
        ui.show_error("You have not added any skill you want to learn yet. Go to Profile first.")
        return

    matches = []  # each item is [student, skill they can teach me]

    for s in students:
        if s.student_id == current_user.student_id:
            continue
        # check every skill I want against every skill they teach (lower case, so
        # 'python' matches 'Python'). Someone who teaches two things I want is listed twice.
        for wanted_skill in current_user.learning_skills:
            for taught_skill in s.teaching_skills:
                if wanted_skill.lower() == taught_skill.lower():
                    matches.append([s, taught_skill])

    if len(matches) == 0:
        ui.show_message("No matches found right now. Try again later or add more skills.")
        return

    rows = []
    count = 1
    for pair in matches:
        matched_student = pair[0]
        matched_skill = pair[1]
        rows.append([count, matched_student.name, matched_student.student_id,
                     matched_skill, matched_student.average_rating()])
        count = count + 1

    print("Found", len(matches), "possible match(es):")
    ui.show_table(["No.", "Name", "ID", "Can Teach You", "Rating"], rows)
    ui.show_message("Use 'Send Exchange Request' from the main menu to contact them.")


# exchange requests

def send_exchange_request():
    ui.show_title("SEND EXCHANGE REQUEST")
    students = student_module.load_all_students(STUDENTS_FILE)

    receiver_id = validators.get_non_empty_input("Enter Student ID to request (e.g. S002): ")
    receiver = student_module.find_student_by_id(students, receiver_id)

    if receiver is None:
        ui.show_error("No student found with that ID.")
        return

    if receiver.student_id == current_user.student_id:
        ui.show_error("You cannot send a request to yourself!")
        return

    # a swap needs something to offer back, so a teaching skill is required
    if len(current_user.teaching_skills) == 0:
        ui.show_error("You have not listed any teaching skill yet. Add one first so you can offer something in return.")
        return

    print("They can teach:", join_skills(receiver.teaching_skills))
    skill_wanted = validators.get_non_empty_input("Which skill do you want to learn from them? ")
    if not has_skill(receiver.teaching_skills, skill_wanted):
        ui.show_error("That student does not teach this skill.")
        return

    print("Your teaching skills:", join_skills(current_user.teaching_skills))
    skill_offered = validators.get_non_empty_input("Which of your skills will you offer in exchange? ")
    if not has_skill(current_user.teaching_skills, skill_offered):
        ui.show_error("That skill is not in your teaching list.")
        return

    requests_list = request_module.load_all_requests(REQUESTS_FILE)
    new_id = request_module.generate_new_request_id(requests_list)
    # .title() so the saved names match how skills are stored in profiles
    new_request = request_module.ExchangeRequest(new_id, current_user.student_id,
                                                 receiver.student_id,
                                                 skill_offered.title(), skill_wanted.title())
    requests_list.append(new_request)
    request_module.save_all_requests(REQUESTS_FILE, requests_list)

    ui.show_success("Request sent! Request ID: " + new_id + " | Status: Pending")


def view_incoming_requests():
    ui.show_title("INCOMING REQUESTS")
    requests_list = request_module.load_all_requests(REQUESTS_FILE)
    students = student_module.load_all_students(STUDENTS_FILE)

    # only pending requests addressed to me; accepted or rejected ones are hidden
    incoming = []
    for r in requests_list:
        if r.receiver_id == current_user.student_id and r.status == "Pending":
            incoming.append(r)

    if len(incoming) == 0:
        ui.show_message("No pending requests for you right now.")
        return

    rows = []
    for r in incoming:
        sender = student_module.find_student_by_id(students, r.sender_id)
        if sender is None:
            sender_name = "Unknown"
        else:
            sender_name = sender.name
        rows.append([r.request_id, sender_name + " (" + r.sender_id + ")",
                     r.skill_offered, r.skill_wanted, r.date_created])

    ui.show_table(["Request ID", "From", "They Offer", "They Want", "Date"], rows)

    action = input("\nType a Request ID to Accept/Reject, or press enter to go back: ").strip()
    if action == "":
        return

    target = None
    for r in incoming:
        if r.request_id.upper() == action.upper():
            target = r
            break

    if target is None:
        ui.show_error("That Request ID was not in the list above.")
        return

    decision = input("Type A to Accept or R to Reject: ").strip().upper()

    # only A or R count; anything else leaves the request unchanged
    if decision == "A":
        target.accept()
    elif decision == "R":
        target.reject()
    else:
        ui.show_error("Invalid option, nothing changed.")
        return

    # replace the old copy of this request in the list, then rewrite the file
    for i in range(len(requests_list)):
        if requests_list[i].request_id == target.request_id:
            requests_list[i] = target
    request_module.save_all_requests(REQUESTS_FILE, requests_list)

    if decision == "A":
        ui.show_success("Request accepted! Now use 'Schedule a Session' to fix a date.")
    else:
        ui.show_success("Request rejected.")


def view_my_sent_requests():
    ui.show_title("MY SENT REQUESTS")
    requests_list = request_module.load_all_requests(REQUESTS_FILE)

    rows = []
    for r in requests_list:
        if r.sender_id == current_user.student_id:
            rows.append([r.request_id, r.receiver_id, r.skill_offered,
                         r.skill_wanted, r.status])

    if len(rows) == 0:
        ui.show_message("You have not sent any requests yet.")
        return

    ui.show_table(["Request ID", "To", "Offered", "Wanted", "Status"], rows)


# sessions and feedback

def schedule_session():
    ui.show_title("SCHEDULE A SESSION")
    requests_list = request_module.load_all_requests(REQUESTS_FILE)

    # accepted requests where I'm on either side, since both people can book
    accepted = []
    for r in requests_list:
        if r.status == "Accepted":
            if r.sender_id == current_user.student_id or r.receiver_id == current_user.student_id:
                accepted.append(r)

    if len(accepted) == 0:
        ui.show_message("You have no accepted requests to schedule yet.")
        return

    rows = []
    for r in accepted:
        if r.receiver_id == current_user.student_id:
            other = r.sender_id
        else:
            other = r.receiver_id
        rows.append([r.request_id, other, r.skill_wanted])
    ui.show_table(["Request ID", "With", "Skill"], rows)

    chosen_id = input("Enter the Request ID to schedule (or press enter to cancel): ").strip()
    if chosen_id == "":
        return

    chosen = None
    for r in accepted:
        if r.request_id.upper() == chosen_id.upper():
            chosen = r
            break

    if chosen is None:
        ui.show_error("Invalid Request ID.")
        return

    date_input = validators.get_non_empty_input("Enter session date (DD-MM-YYYY): ")
    while not validators.is_valid_date(date_input):
        ui.show_error("That is not a valid date. Example: 25-12-2026")
        date_input = validators.get_non_empty_input("Enter session date (DD-MM-YYYY): ")

    sessions_list = session_module.load_all_sessions(SESSIONS_FILE)
    new_id = session_module.generate_new_session_id(sessions_list)
    # only skill_wanted is saved, although an exchange goes both ways. The date is
    # kept as typed (DD-MM-YYYY) and is not compared with today.
    new_session = session_module.Session(new_id, chosen.request_id, chosen.sender_id,
                                         chosen.receiver_id, chosen.skill_wanted, date_input)
    sessions_list.append(new_session)
    session_module.save_all_sessions(SESSIONS_FILE, sessions_list)

    ui.show_success("Session scheduled! Session ID: " + new_id)


def view_my_sessions():
    ui.show_title("MY SESSIONS")
    sessions_list = session_module.load_all_sessions(SESSIONS_FILE)

    mine = []
    for s in sessions_list:
        if s.sender_id == current_user.student_id or s.receiver_id == current_user.student_id:
            mine.append(s)

    if len(mine) == 0:
        ui.show_message("No sessions yet.")
        return

    rows = []
    for s in mine:
        if s.rating == 0:
            rating_text = "-"
        else:
            rating_text = str(s.rating) + " / 5"
        rows.append([s.session_id, s.skill, s.session_date, s.status, rating_text])
    ui.show_table(["Session ID", "Skill", "Date", "Status", "Rating"], rows)

    session_id = input("\nEnter a Session ID to mark complete / give feedback, or press enter to go back: ").strip()
    if session_id == "":
        return

    target = None
    for s in mine:
        if s.session_id.upper() == session_id.upper():
            target = s
            break

    if target is None:
        ui.show_error("Session not found.")
        return

    # a session can be marked complete at any time; the date isn't checked
    if target.status != "Completed":
        target.mark_completed()
        ui.show_success("Session marked as completed.")

    # rating 0 means no feedback yet, since real ratings are 1-5
    if target.rating != 0:
        ui.show_message("Feedback was already given for this session.")
    else:
        give_feedback = input("Do you want to give feedback now? (y/n): ").strip().lower()
        if give_feedback == "y":
            rating = validators.get_int_input("Rate the session out of 5: ", 1, 5)
            comment = validators.get_non_empty_input("Leave a short comment: ")
            # limitation: a session has one rating slot, so only the first person to
            # rate is recorded
            target.add_feedback(rating, comment)

            # the rating goes on the OTHER student's profile, not our own
            students = student_module.load_all_students(STUDENTS_FILE)
            if target.sender_id == current_user.student_id:
                other_id = target.receiver_id
            else:
                other_id = target.sender_id
            other_student = student_module.find_student_by_id(students, other_id)
            if other_student is not None:
                other_student.rating_total = other_student.rating_total + rating
                other_student.rating_count = other_student.rating_count + 1
                student_module.save_all_students(STUDENTS_FILE, students)
            ui.show_success("Thanks for your feedback!")

    # write everything back; there is no update-in-place for .txt files
    for i in range(len(sessions_list)):
        if sessions_list[i].session_id == target.session_id:
            sessions_list[i] = target
    session_module.save_all_sessions(SESSIONS_FILE, sessions_list)


# menus

def logged_in_menu():
    while True:
        ui.clear_screen()
        ui.show_menu("SKILLSWAP MAIN MENU", [
            "My Profile",
            "Browse All Users",
            "Find Skill Match",
            "Send Exchange Request",
            "View Incoming Requests",
            "View My Sent Requests",
            "Schedule a Session",
            "My Sessions & Feedback",
            "Logout",
        ])
        print("Logged in as:", current_user.name, "(" + current_user.student_id + ")")
        choice = validators.get_int_input("Enter your choice: ", 1, 9)

        if choice == 9:
            logout_student()
            ui.pause()
            break

        if choice == 1:
            # the profile screen has its own loop and pause, so skip the shared pause below
            manage_profile()
            continue

        # every other option shows a screen and then waits for Enter
        ui.clear_screen()
        if choice == 2:
            browse_all_students()
        elif choice == 3:
            find_matches()
        elif choice == 4:
            send_exchange_request()
        elif choice == 5:
            view_incoming_requests()
        elif choice == 6:
            view_my_sent_requests()
        elif choice == 7:
            schedule_session()
        elif choice == 8:
            view_my_sessions()
        ui.pause()


def main():
    # make sure data/ and the .txt files exist before anything tries to read them
    file_manager.setup_data_files()

    while True:
        ui.clear_screen()
        print("*" * ui.WIDTH)
        print("WELCOME TO SKILLSWAP".center(ui.WIDTH))
        print("Peer to Peer Skill Exchange Platform".center(ui.WIDTH))
        print("*" * ui.WIDTH)
        ui.show_menu("START MENU", ["Register", "Login", "Exit"])
        choice = validators.get_int_input("Enter choice: ", 1, 3)

        if choice == 1:
            ui.clear_screen()
            register_new_student()
            ui.pause()
        elif choice == 2:
            ui.clear_screen()
            success = login_student()
            if success:
                ui.pause()
                logged_in_menu()
            else:
                ui.pause()
        else:
            print("\nThank you for using SkillSwap. Bye!")
            break
