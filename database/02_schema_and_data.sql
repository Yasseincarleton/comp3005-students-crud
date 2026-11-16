-- =============================================================================
-- 02_schema_and_data.sql
-- Purpose : Creates the "students" table exactly as specified in the
--           assignment schema and populates it with the initial data set.
-- Run in  : the "students_db" database (created by 01_create_database.sql).
-- =============================================================================

-- Drop the table if it already exists so the script is safely re-runnable.
DROP TABLE IF EXISTS students;

-- -----------------------------------------------------------------------------
-- Table: students
--   student_id      : SERIAL creates an auto-incrementing INTEGER backed by a
--                     sequence; PRIMARY KEY makes it unique and NOT NULL.
--   first_name      : TEXT, required (NOT NULL).
--   last_name       : TEXT, required (NOT NULL).
--   email           : TEXT, required (NOT NULL) and UNIQUE, so two students
--                     can never share the same email address.
--   enrollment_date : DATE, optional (nullable, as the schema gives no
--                     constraint for this column).
-- -----------------------------------------------------------------------------
CREATE TABLE students (
    student_id      SERIAL PRIMARY KEY,
    first_name      TEXT   NOT NULL,
    last_name       TEXT   NOT NULL,
    email           TEXT   NOT NULL UNIQUE,
    enrollment_date DATE
);

-- -----------------------------------------------------------------------------
-- Initial data (provided by the assignment).
-- student_id is omitted so PostgreSQL generates it automatically (1, 2, 3).
-- -----------------------------------------------------------------------------
INSERT INTO students (first_name, last_name, email, enrollment_date) VALUES
('John', 'Doe',   'john.doe@example.com',   '2023-09-01'),
('Jane', 'Smith', 'jane.smith@example.com', '2023-09-01'),
('Jim',  'Beam',  'jim.beam@example.com',   '2023-09-02');

-- Verify the setup: should return the three rows above with IDs 1-3.
SELECT * FROM students ORDER BY student_id;
