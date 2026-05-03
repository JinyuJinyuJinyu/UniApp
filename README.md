# CLIUniApp & GUIUniApp – University Enrolment System

**Assessment 1 – Part 2** | University of Technology Sydney, FEIT
*Software Engineering Practice*

---

## Architecture (MVC)

This project follows the **Model–View–Controller** pattern recommended in
Section 3 of the assignment brief:

```
UniApp/
│
├── Models (pure data + rules — no I/O)
│   ├── student.py         – Student: data, validation patterns, derived props
│   ├── subject.py         – Subject: id/mark/grade auto-generation
│   └── database.py        – Database: students.data persistence (JSON)
│
├── Controllers (services + system menus)
│   ├── student_controller.py   – register, login, drives student subsystem menu
│   ├── subject_controller.py   – enrol, remove, list, change password,
│   │                              drives subject enrolment menu
│   └── admin_controller.py     – view all, group, partition, remove, clear,
│                                  drives admin subsystem menu
│
├── View
│   └── cli_view.py        – banner, prompt, info/warn/error/success helpers
│
├── Entry points
│   ├── CLIUniApp.py       – wires controllers, dispatches main menu
│   └── GUIUniApp.py       – tkinter UI; uses controllers (no direct DB calls)
│
├── Helpers
│   ├── populate_data.py   – seed students.data with sample students
│   └── test_uniapp.py     – 33 tests covering models + controllers
│
└── README.md
```

### Why two layers of methods on each Controller?

Each controller exposes:

| Layer | Methods | Used by |
|---|---|---|
| **Service** (pure) | `register()`, `login()`, `enrol()`, `group_by_grade()`, … | CLI menus, GUI windows, **and tests** |
| **Menu** (CLI flow) | `run_student_subsystem()`, `run_subject_menu()`, `run_admin_subsystem()` | only `CLIUniApp.py` |

This keeps the spec recommendation ("controllers contain system menus") while
letting GUIUniApp and the test suite reuse the exact same business logic
without duplicating it.

---

## Requirements

- **Python 3.10 or higher** (uses `X | Y` union types)
- **tkinter** (standard library; on Linux: `sudo apt install python3-tk`)
- No third-party packages

---

## Running

### CLIUniApp

```bash
python CLIUniApp.py
```

```
════════════════════════════════════════════════════════════
  CLIUNIAPP – UNIVERSITY ENROLMENT SYSTEM
════════════════════════════════════════════════════════════
  [1] Student subsystem
  [2] Admin subsystem
  [3] Exit
────────────────────────────────────────────────────────────
  Select option:
```

**Student subsystem**
- Register → enter email, password, name (with format validation)
- Login → enter credentials → enters Subject Enrolment menu
- From Subject Enrolment menu: Enrol, Remove, View, Change Password, Logout

**Admin subsystem** (password: `admin`)
- View all students
- Group students by grade (per OVERALL grade — each student appears once)
- Categorise PASS / FAIL (based on AVERAGE mark ≥ 50)
- Remove a student
- Clear all student data

### GUIUniApp

```bash
python GUIUniApp.py
```

Four distinct windows (per the GUIUniApp marking scheme):

1. **Login Window** *(main)* — calls `StudentController.login()`
2. **Enrolment Window** — calls `SubjectController.enrol()`
3. **Subject Window** — table of enrolled subjects with marks & grades
4. **Exception Window** — modal dialog for empty fields, invalid format,
   incorrect credentials, enrolment limit

> Use `python populate_data.py` first to seed `students.data` with valid sample
> accounts, then use one of the printed credentials to log in.

### populate_data.py (helper)

```bash
python populate_data.py             # 15 students
python populate_data.py 30          # 30 students
python populate_data.py 20 --append # add 20 without wiping the file
```

### Tests

```bash
python test_uniapp.py
```

33 tests across:
- **Models** — Subject grade boundaries, Student validation regex, derived properties
- **StudentController** — register / login: success, bad email, bad password, duplicate, unregistered
- **SubjectController** — enrol / remove / list / change password (incl. enrolment limit, unpadded ID, persistence)
- **AdminController** — login credential, group_by_grade (overall grade, no duplicates), partition_pass_fail (average rule), remove, clear

---

## Specification Notes (compliance highlights)

These behaviours match the **Assessment 1 – Part 2** brief and sample I/O:

### Email pattern
`firstname.lastname@university.com`

### Password pattern
1. Starts with **one uppercase letter**
2. Followed by **5 or more letters**
3. Ends with **3 or more digits**

| Input | Result |
|---|---|
| `Helloworld123` | ✔ valid |
| `Newworld123` | ✔ valid |
| `Hello123` | ✘ invalid (only 5 letters) |
| `helloworld123` | ✘ invalid (no uppercase) |

### Student ID — random 6-digit, 1–999,999, zero-padded
### Subject ID — random 3-digit, 1–999, zero-padded
### Subject mark — random integer 25–100
### UTS Grade Scale
| Mark range | Grade |
|---|---|
| ≥ 85 | HD |
| 75 – 84 | D |
| 65 – 74 | C |
| 50 – 64 | P |
| < 50 | Z |

### Pass / Fail rule (admin partition)
A student PASSES if the **average mark** of all enrolled subjects is **≥ 50**.
Students with no enrolments are excluded from both PASS and FAIL.

### Group by Grade (admin)
Each student is placed under their **overall grade** (derived from average mark).
Every student appears once.

### Maximum subjects: 4

---

## Data Storage

`students.data` is a UTF-8 JSON file:

```json
[
  {
    "id": "622001",
    "name": "Harper Johnson",
    "email": "harper.johnson@university.com",
    "password": "Helloworld123",
    "subjects": [
      { "id": "302", "mark": 89, "grade": "HD" }
    ]
  }
]
```

All reads and writes go through `Database` — no other class touches the file
directly. Controllers ask the Database to read/write models; the View layer
never sees the file at all.

---

## How to extend

- **Add a new student-side feature** → add a service method to
  `SubjectController` (or `StudentController`), then route the CLI menu choice
  in its `run_*_menu()` method, and optionally add a button + handler in
  `GUIUniApp.py` that calls the same service method.
- **Add a new admin operation** → add a service method to `AdminController`,
  route a new menu option in `_run_admin_menu`.
- **Add a new view layer** (e.g. a web UI) → import the controllers and call
  the service methods directly. The CLI menu code stays untouched.
