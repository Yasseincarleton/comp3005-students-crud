-- =============================================================================
-- 01_create_database.sql
-- Purpose : Creates the PostgreSQL database used by the Students CRUD app.
-- Run as  : a superuser (e.g. postgres), connected to the default "postgres" DB.
--           In pgAdmin: right-click "Databases" > Query Tool, paste, and run.
-- =============================================================================

-- Remove any old copy so the script can be re-run cleanly during testing.
-- (Disconnect from "students_db" in pgAdmin before running this.)
DROP DATABASE IF EXISTS students_db;

-- Create a fresh database to hold the "students" table.
CREATE DATABASE students_db;
