# SkillSwap - Peer to Peer Skill Exchange

## About the project
SkillSwap is a terminal based Python program where college students trade skills instead of paying for lessons. For example, if you know Guitar and want to learn Python, you can look for a student who teaches Python and offer to teach them Guitar in return.

I made this for the Vityarthi "Build Your Own Project" assignment. It uses functions, modules, lists and OOP (classes).

## Features
- Register and login
- Profile: add or remove skills you can teach and skills you want to learn
- Find students who teach a skill you want to learn
- Send, accept and reject exchange requests
- Schedule a session for an accepted request
- Mark a session as completed and give a rating out of 5 with a short comment
- Data is saved in plain `.txt` files, so no database is needed

## What I used
- Python 3 (only the standard library, nothing to install)
- Plain text files for storing data

## Files
```
SkillSwap/
├── main.py                   # start here (runs skillswap/app.py)
├── skillswap/                # the application package
│   ├── __init__.py
│   ├── app.py                # all the menus and program flow
│   ├── student.py            # Student class + load/save students
│   ├── skill.py              # Skill class + master skill list
│   ├── exchange_request.py   # ExchangeRequest class + load/save requests
│   ├── session.py            # Session class + load/save sessions
│   ├── validators.py         # checks user input
│   ├── file_manager.py       # creates the data folder and files
│   └── ui.py                 # titles, menus and tables for the terminal
├── tests/                    # automated unit tests (unittest)
│   ├── test_student.py
│   ├── test_skill.py
│   ├── test_exchange_request.py
│   ├── test_session.py
│   ├── test_validators.py
│   ├── test_file_manager.py
│   ├── test_ui.py
│   └── test_app_flow.py      # end to end: register -> match -> request -> session -> rating
├── README.md
├── statement.md
└── data/                     # made automatically on the first run (not committed)
    ├── students.txt
    ├── requests.txt
    ├── sessions.txt
    └── skills.txt
```

## How to install and run
Nothing to install. You only need Python 3.8 or newer (the standard library is enough).
Run these commands from the project folder (the one that contains `main.py`):
```
python main.py
```
The `data/` folder is created next to `main.py` on the first run.

## How to test

### Automated tests
The unit tests use Python's built-in `unittest`, so nothing extra is needed. From the project folder run:
```
python -m unittest discover -v
```
They use temporary files, so your real `data/` folder is never changed. What is covered:

| Test file | What it checks |
|---|---|
| `test_student.py` | skills add/remove, ratings, file format, load/save, id generation |
| `test_skill.py` | Skill class, master list, duplicate skills |
| `test_exchange_request.py` | Pending/Accepted/Rejected, file format, id generation |
| `test_session.py` | scheduling data, feedback, file format, id generation |
| `test_validators.py` | email, name, password, date, number and text input loops |
| `test_file_manager.py` | data folder and files are created, existing data is not overwritten |
| `test_ui.py` | messages, menus and table layout |
| `test_app_flow.py` | full workflow with fake keyboard input (register, login, match, request, accept, schedule, rate) |

### Manual test
1. Run the program and register two students with different emails (call them A and B).
2. Login as A, open "My Profile", add a teaching skill (for example Guitar) and a learning skill (for example Python), then logout.
3. Login as B and add Python as a teaching skill, then logout.
4. Login as A again and open "Find Skill Match". B should show up for Python.
5. Use "Send Exchange Request" to send a request to B. Logout, login as B and accept it from "View Incoming Requests".
6. Either student can now use "Schedule a Session". After that, open "My Sessions & Feedback" to mark it completed and leave a rating.

## Things that do not work perfectly yet
- Passwords are saved as plain text in `students.txt`. This is fine for a class project but not safe for real use.
- A skill name with a comma in it (like "Data Structures, Algorithms") gets split into two skills when the file is loaded again, because skills are saved separated by commas.
- A session has only one rating slot, so only the first person who rates is saved.
- The program does not check the session date against today's date, so a session can be marked completed before it happens.
- A session saves only one skill, even though a swap goes both ways.
- Dates are not saved in one format everywhere (some are DD-MM-YYYY and some are YYYY-MM-DD).

## Future improvements
- Fix the problems listed above
- Search by skill category
- A simple GUI with Tkinter
- Hide the password while typing and store it in a safer way

## What I learned
- How to split a project into several files (modules) instead of writing everything in one file.
- How to use classes to represent real things like a student, a request and a session.
- How to store data in text files: every object becomes one line, and the fields are separated by a `|` symbol.
- Why input checking matters, because users type blank things, letters instead of numbers, or wrong dates.
- That text files are simple but limited, since the whole file has to be rewritten every time something changes.