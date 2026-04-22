# CLIUniApp & GUIUniApp – University Enrolment System
## Assessment 1 – Part 2 | University of Technology Sydney, FEIT

---

## Project Structure

```
UniApp/
├── CLIUniApp.py      – Command-line entry point
├── GUIUniApp.py      – Graphical UI entry point
├── student.py        – Student model (registration, pattern validation, enrolment)
├── subject.py        – Subject model (ID, mark, grade generation)
├── admin.py          – Admin model (student management operations)
├── database.py       – Data-access layer (students.data CRUD)
├── test_uniapp.py    – Automated test suite (39 tests)
├── students.data     – Persistent data file (auto-created on first run)
└── README.md         – This file
```

---

## Requirements

- Python 3.10 or higher
- `tkinter` – included with standard Python (required for GUIUniApp only)
- No third-party packages required

---

## Running the Applications

### CLIUniApp (Command-Line)

```bash
python CLIUniApp.py
```

Top-level menu:
```
[1] Student subsystem
[2] Admin subsystem
[3] Exit
```

#### Student subsystem
- **Register** – enter name, email (`firstname.lastname@university.com`) and a password
- **Login** – credentials checked via `Student.check_login_credential(email, pwd)`
  - Enrol in a new subject (auto-generated Subject ID, random mark 25–100, grade)
  - Remove an enrolled subject by ID
  - View all enrolled subjects with marks and grades
  - Change password

#### Admin subsystem
- Login with password: **`admin`** – checked via `Admin.check_login_credential(pwd)`
- View all registered students
- Group students by grade (HD / D / C / P / Z)
- Categorise students into PASS / FAIL
- Remove a student by ID
- Clear all student data (with confirmation)

### GUIUniApp (Graphical UI)

```bash
python GUIUniApp.py
```

The **Login Window** is the main window. Enter a registered student's email and password.

> Registration is only available via CLIUniApp — register first, then log in via GUIUniApp.

After login, the **Enrolment Window** opens, showing:
- Student details (name, ID, email)
- Enrolments table (Subject ID, Mark, Grade)
- **Enrol** – adds a new subject (blocked with warning if already at 4)
- **Remove** – removes the selected subject after confirmation
- **Logout** – returns to the Login Window

---

## API — Method Names (match Part 1 class diagram)

| Class | Method | Purpose |
|---|---|---|
| Student | `validate_email_pattern(email)` | Static. Checks `firstname.lastname@university.com` pattern |
| Student | `validate_password_pattern(pwd)` | Static. Checks uppercase-start / ≥5 letters / ≥3 digits |
| Student | `check_login_credential(email, pwd)` | Verifies email + password against stored credentials |
| Student | `enrol()` / `remove_subject(id)` / `view_subjects()` | Enrolment operations |
| Student | `change_password(new_pwd)` | Password update (with pattern validation) |
| Admin   | `check_login_credential(pwd)` | Static. Admin uses password only, no email |
| Admin   | `view_all_students()` / `group_by_grade()` / `group_by_pass_fail()` | Admin queries |
| Admin   | `remove_student(id)` / `clear_student_data()` | Admin mutations |

Python naming uses `snake_case`; the class diagram uses `camelCase`. These map directly:
- `validateEmailPattern` ↔ `validate_email_pattern`
- `validatePasswordPattern` ↔ `validate_password_pattern`
- `checkLoginCredential` ↔ `check_login_credential`

---

## Validation Rules

### Email
Must match `firstname.lastname@university.com`
- ✔ `john.smith@university.com`
- ✘ `johnsmith@university.com`
- ✘ `john.smith@university`

### Password
All three conditions must be satisfied:
1. Starts with an uppercase letter
2. Contains at least 5 letters in total
3. Ends with 3 or more digits

- ✔ `David123` (D + avid = 5 letters, 123 = 3 digits)
- ✘ `david123` (no leading uppercase)
- ✘ `Dav12345` (only 3 letters)

### Student ID
- Random integer 1 – 999,999, zero-padded to 6 digits (e.g. `002340`)

### Subject ID
- Random integer 1 – 999, zero-padded to 3 digits (e.g. `042`)

### Subject Mark
- Random integer in range 25 – 100

### Grade Scale (UTS)
| Mark range | Grade |
|-----------|-------|
| ≥ 85      | HD    |
| 75 – 84   | D     |
| 65 – 74   | C     |
| 50 – 64   | P     |
| < 50      | Z     |

---

## Data Storage

All data is stored in `students.data` as pipe-delimited plain text.

**Format per line:**
```
studentId|name|email|password|subjectId:mark:grade,subjectId:mark:grade,...
```

**Example:**
```
002340|John Smith|john.smith@university.com|David123|042:87:HD,019:63:P
```

---

## Exception Handling

### CLIUniApp
- Invalid email or password pattern → error message, operation aborted
- Duplicate email on registration → error message
- Login with wrong credentials → error message (via `check_login_credential`)
- Enrolment attempt beyond 4 subjects → warning message
- Remove non-existent subject ID → error message

### GUIUniApp
- Empty login fields → `showwarning` ("Missing or Invalid Information")
- Invalid email/password pattern → `showwarning` ("Missing or Invalid Information")
- Invalid credentials → `showerror` ("Login Failed")
- Enrolment attempt beyond 4 subjects → `showwarning` ("Enrolment Limit Reached")
- Remove without selection → `showinfo` ("No Selection")

---

## Running Tests

```bash
python test_uniapp.py
```

39 unit tests covering: Subject generation & grading, Student pattern validation,
credential checking, enrolment limits, password changes, serialisation,
Database CRUD, and all Admin operations.

---

## Design Alignment with Part 1

| Part 1 Class | Implemented In |
|---|---|
| Student    | `student.py`   |
| Subject    | `subject.py`   |
| Admin      | `admin.py`     |
| Database   | `database.py`  |
| CLIUniApp  | `CLIUniApp.py` |
| GUIUniApp  | `GUIUniApp.py` |
