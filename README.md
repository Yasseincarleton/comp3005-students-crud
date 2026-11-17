# COMP 3005 – Students CRUD Application (PostgreSQL + Python)

A command-line Python application that connects to a PostgreSQL database and performs
**CRUD** (Create, Read, Update, Delete) operations on a `students` table.

**Author:** Yassein Kndeel — Carleton University, COMP 3005 Database Systems

**Repository:** https://github.com/Yasseincarleton/comp3005-students-crud

> A sample run of every function, with the resulting database state, is included in the
> [Demonstration](#demonstration-sample-run) section below.

---

## Repository Structure

```
comp3005-students-crud/
├── README.md                     # This file: setup, run steps, function explanations
├── .gitignore
├── database/
│   ├── 01_create_database.sql    # Creates the students_db database
│   └── 02_schema_and_data.sql    # Creates the students table + inserts initial data
└── app/
    ├── students_app.py           # Python application with the 4 CRUD functions + menu
    └── requirements.txt          # Python dependency (psycopg2)
```

---

## Prerequisites

| Tool | Version used | Purpose |
|------|--------------|---------|
| PostgreSQL | 16 (any 12+ works) | Database server |
| pgAdmin 4 | latest | GUI to run scripts and view table changes |
| Python | 3.9+ | Runs the application |
| psycopg2 | 2.9+ | PostgreSQL driver for Python |

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Yasseincarleton/comp3005-students-crud.git
cd comp3005-students-crud
```

### 2. Create the database and table

**Option A — pgAdmin (GUI)**

1. Open pgAdmin and connect to your PostgreSQL server.
2. Right-click **Databases → Query Tool** (on the default `postgres` database), open
   `database/01_create_database.sql`, and run it (F5). Refresh **Databases** — `students_db` appears.
3. Right-click **students_db → Query Tool**, open `database/02_schema_and_data.sql`, and run it.
   The final `SELECT` shows the three initial students.

**Option B — psql (command line)**

```bash
psql -U postgres -d postgres    -f database/01_create_database.sql
psql -U postgres -d students_db -f database/02_schema_and_data.sql
```

### 3. Install the Python dependency

```bash
cd app
pip install -r requirements.txt
```

(Optional: create a virtual environment first with `python -m venv venv` and activate it.)

### 4. Configure the connection

The app reads its connection settings from environment variables. Defaults are shown below;
you usually only need to set `DB_PASSWORD` to your own PostgreSQL password.

| Variable | Default |
|----------|---------|
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `students_db` |
| `DB_USER` | `postgres` |
| `DB_PASSWORD` | `postgres` |

```bash
# macOS / Linux
export DB_PASSWORD=your_password

# Windows (PowerShell)
$env:DB_PASSWORD="your_password"
```

### 5. Run the application

Python is interpreted, so there is no separate compile step:

```bash
python students_app.py        # use python3 on macOS/Linux if needed
```

You will see a menu:

```
========== Students Database ==========
 1. View all students      (getAllStudents)
 2. Add a student          (addStudent)
 3. Update a student email (updateStudentEmail)
 4. Delete a student       (deleteStudent)
 0. Exit
=======================================
```

---

## Database Schema

```sql
CREATE TABLE students (
    student_id      SERIAL PRIMARY KEY,   -- auto-incrementing integer key
    first_name      TEXT   NOT NULL,
    last_name       TEXT   NOT NULL,
    email           TEXT   NOT NULL UNIQUE,
    enrollment_date DATE
);
```

- **`SERIAL PRIMARY KEY`** – PostgreSQL creates a sequence that generates `student_id` automatically.
- **`NOT NULL`** – first name, last name and email are required.
- **`UNIQUE`** on `email` – the database rejects duplicate emails.

Initial data: John Doe, Jane Smith and Jim Beam (IDs 1–3).

---

## Application Functions

| Function | Operation | SQL | Behaviour |
|----------|-----------|-----|-----------|
| `getAllStudents()` | Read | `SELECT … ORDER BY student_id` | Prints all students as a formatted table and returns the rows. |
| `addStudent(first_name, last_name, email, enrollment_date)` | Create | `INSERT … RETURNING student_id` | Inserts a student and prints the auto-generated ID. |
| `updateStudentEmail(student_id, new_email)` | Update | `UPDATE … SET email = %s WHERE student_id = %s` | Changes the student's email. Reports if the ID doesn't exist. |
| `deleteStudent(student_id)` | Delete | `DELETE … WHERE student_id = %s` | Removes the student. Reports if the ID doesn't exist. |

### Design notes

- **Parameterized queries** (`%s` placeholders) are used everywhere, so user input is never
  concatenated into SQL. This prevents SQL injection.
- **Transactions:** each write runs inside `with conn:`, which **commits** on success and
  **rolls back** automatically on error.
- **Error handling:**
  - Duplicate email → caught as `UniqueViolation` with a friendly message.
  - Non-existent `student_id` on update or delete → detected with `cursor.rowcount == 0`.
  - Invalid date format or a non-numeric ID → rejected by input validation before reaching the database.
  - Database unreachable → clear message and clean exit.
- **No hard-coded credentials:** connection details come from environment variables.

---

## Demonstration (Sample Run)

A full run that calls every function, starting from the initial data (menu output trimmed).

**1. `getAllStudents()`: initial data**
```
Choose an option: 1
ID   First Name   Last Name    Email                          Enrolled
------------------------------------------------------------------------
1    John         Doe          john.doe@example.com           2023-09-01
2    Jane         Smith        jane.smith@example.com         2023-09-01
3    Jim          Beam         jim.beam@example.com           2023-09-02

3 record(s) found.
```

**2. `addStudent()`**
```
Choose an option: 2
First name: Alice
Last name: Nguyen
Email: alice.nguyen@example.com
Enrollment date (YYYY-MM-DD, blank for none): 2024-01-15
[OK] Added Alice Nguyen with student_id = 4.
```

**3. `updateStudentEmail()`**
```
Choose an option: 3
Student ID: 4
New email: alice.n@example.com
[OK] Email for student_id 4 updated to 'alice.n@example.com'.
```

**4. `deleteStudent()`**
```
Choose an option: 4
Student ID: 2
[OK] Student with student_id 2 deleted.
```

**5. `getAllStudents()`: final state**
```
Choose an option: 1
ID   First Name   Last Name    Email                          Enrolled
------------------------------------------------------------------------
1    John         Doe          john.doe@example.com           2023-09-01
3    Jim          Beam         jim.beam@example.com           2023-09-02
4    Alice        Nguyen       alice.n@example.com            2024-01-15

3 record(s) found.
```

**Database state checked directly in PostgreSQL** (same query in the pgAdmin Query Tool):
```
students_db=# SELECT * FROM students ORDER BY student_id;
 student_id | first_name | last_name |        email         | enrollment_date
------------+------------+-----------+----------------------+-----------------
          1 | John       | Doe       | john.doe@example.com | 2023-09-01
          3 | Jim        | Beam      | jim.beam@example.com | 2023-09-02
          4 | Alice      | Nguyen    | alice.n@example.com  | 2024-01-15
(3 rows)
```
This shows the INSERT (Alice, ID 4, auto-generated), the UPDATE (Alice's new email) and the DELETE (Jane, ID 2)
were all committed to the database.

**Error handling examples**
```
Email: john.doe@example.com
[ERROR] A student with email 'john.doe@example.com' already exists.     # UNIQUE constraint

Student ID: 99
[WARN] No student found with student_id = 99.                         # non-existent ID

Enrollment date (YYYY-MM-DD, blank for none): baddate
  Invalid date. Use the format YYYY-MM-DD, e.g. 2023-09-01.           # input validation
```

To check the changes yourself, run `SELECT * FROM students ORDER BY student_id;` in the pgAdmin
Query Tool, or right-click the table and choose **View/Edit Data → All Rows**.
