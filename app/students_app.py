"""
students_app.py
===============
COMP 3005 - Database Interaction with PostgreSQL and Application Programming

A small command-line application that connects to a PostgreSQL database and
performs CRUD (Create, Read, Update, Delete) operations on the `students` table.

Functions required by the assignment:
    getAllStudents()                                   -> READ
    addStudent(first_name, last_name, email, date)     -> CREATE
    updateStudentEmail(student_id, new_email)          -> UPDATE
    deleteStudent(student_id)                          -> DELETE

Connection settings are read from environment variables (with sensible
defaults) so no passwords need to be hard-coded in the source:
    DB_HOST (default: localhost)     DB_PORT (default: 5432)
    DB_NAME (default: students_db)   DB_USER (default: postgres)
    DB_PASSWORD (default: postgres)

Run:  python students_app.py
"""

import os
import sys
from datetime import date

import psycopg2
from psycopg2 import errors


# Connection parameters, overridable through environment variables.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "students_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}


def get_connection():
    """Open and return a new connection to the PostgreSQL database.

    Exits the program with a clear message if the database is unreachable
    (wrong password, server not running, database not created, etc.).
    """
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Could not connect to PostgreSQL: {e}")
        print("Check that the server is running and your DB_* settings are correct.")
        sys.exit(1)




def getAllStudents():
    """READ: Retrieve and display every record in the students table.

    Rows are ordered by student_id and printed as a formatted table.
    Returns the list of rows so the function can also be reused/tested.
    """
    query = """
        SELECT student_id, first_name, last_name, email, enrollment_date
        FROM students
        ORDER BY student_id;
    """
    # "with" blocks guarantee the cursor and connection are closed afterwards.
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    conn.close()

    # Pretty-print the results as an aligned table.
    if not rows:
        print("The students table is empty.")
        return rows

    header = f"{'ID':<4} {'First Name':<12} {'Last Name':<12} {'Email':<30} {'Enrolled':<10}"
    print(header)
    print("-" * len(header))
    for student_id, first, last, email, enrolled in rows:
        enrolled_str = enrolled.isoformat() if enrolled else "N/A"
        print(f"{student_id:<4} {first:<12} {last:<12} {email:<30} {enrolled_str:<10}")
    print(f"\n{len(rows)} record(s) found.")
    return rows


def addStudent(first_name, last_name, email, enrollment_date):
    """CREATE: Insert a new student record into the students table.

    A parameterized query (%s placeholders) is used so values are escaped by
    the driver, which prevents SQL injection. RETURNING gives back the
    auto-generated student_id. Returns the new id, or None on failure.
    """
    query = """
        INSERT INTO students (first_name, last_name, email, enrollment_date)
        VALUES (%s, %s, %s, %s)
        RETURNING student_id;
    """
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:  # commits on success, rolls back on error
            cur.execute(query, (first_name, last_name, email, enrollment_date))
            new_id = cur.fetchone()[0]
        print(f"[OK] Added {first_name} {last_name} with student_id = {new_id}.")
        return new_id
    except errors.UniqueViolation:
        # Triggered by the UNIQUE constraint on email.
        print(f"[ERROR] A student with email '{email}' already exists.")
    except errors.NotNullViolation:
        print("[ERROR] First name, last name and email are required.")
    except psycopg2.Error as e:
        print(f"[ERROR] Could not add student: {e.pgerror or e}")
    finally:
        conn.close()
    return None


def updateStudentEmail(student_id, new_email):
    """UPDATE: Change the email address of the student with the given id.

    Uses cursor.rowcount to detect when no student has that id.
    Returns True if a row was updated, otherwise False.
    """
    query = "UPDATE students SET email = %s WHERE student_id = %s;"
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(query, (new_email, student_id))
            updated = cur.rowcount
        if updated == 0:
            print(f"[WARN] No student found with student_id = {student_id}.")
            return False
        print(f"[OK] Email for student_id {student_id} updated to '{new_email}'.")
        return True
    except errors.UniqueViolation:
        print(f"[ERROR] Email '{new_email}' is already used by another student.")
    except psycopg2.Error as e:
        print(f"[ERROR] Could not update email: {e.pgerror or e}")
    finally:
        conn.close()
    return False


def deleteStudent(student_id):
    """DELETE: Remove the student record with the given id.

    Returns True if a row was deleted, otherwise False.
    """
    query = "DELETE FROM students WHERE student_id = %s;"
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(query, (student_id,))
            deleted = cur.rowcount
        if deleted == 0:
            print(f"[WARN] No student found with student_id = {student_id}.")
            return False
        print(f"[OK] Student with student_id {student_id} deleted.")
        return True
    except psycopg2.Error as e:
        print(f"[ERROR] Could not delete student: {e.pgerror or e}")
    finally:
        conn.close()
    return False



# Input helpers: validate user input before it reaches the database


def prompt_non_empty(label):
    """Keep asking until the user enters a non-blank value."""
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("  This field cannot be empty.")


def prompt_int(label):
    """Keep asking until the user enters a valid integer (e.g. a student_id)."""
    while True:
        value = input(f"{label}: ").strip()
        if value.isdigit():
            return int(value)
        print("  Please enter a positive whole number.")


def prompt_date(label):
    """Ask for a date in YYYY-MM-DD format. Blank input means 'no date' (NULL)."""
    while True:
        value = input(f"{label} (YYYY-MM-DD, blank for none): ").strip()
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            print("  Invalid date. Use the format YYYY-MM-DD, e.g. 2023-09-01.")



# Interactive menu: lets each function be called and demonstrated


MENU = """
========== Students Database ==========
 1. View all students      (getAllStudents)
 2. Add a student          (addStudent)
 3. Update a student email (updateStudentEmail)
 4. Delete a student       (deleteStudent)
 0. Exit
======================================="""


def main():
    """Show the menu in a loop and dispatch to the matching CRUD function."""
    print(f"Connected to database '{DB_CONFIG['dbname']}' on "
          f"{DB_CONFIG['host']}:{DB_CONFIG['port']} as '{DB_CONFIG['user']}'.")
    get_connection().close()  # fail fast if the database is unreachable

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            getAllStudents()
        elif choice == "2":
            addStudent(
                prompt_non_empty("First name"),
                prompt_non_empty("Last name"),
                prompt_non_empty("Email"),
                prompt_date("Enrollment date"),
            )
        elif choice == "3":
            updateStudentEmail(prompt_int("Student ID"), prompt_non_empty("New email"))
        elif choice == "4":
            deleteStudent(prompt_int("Student ID"))
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please choose 0-4.")



if __name__ == "__main__":
    main()
