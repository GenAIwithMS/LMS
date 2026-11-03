-- Make username and email unique for students, teachers and admins.
--
-- Why this file is needed: db.create_all() only creates tables that do not
-- exist yet. It never changes an existing table, so the new unique=True rules
-- in the models only reach an existing database when you run this file.
-- A brand new database gets the rules automatically.
--
-- How to run (MySQL):
--   mysql -u <user> -p <database_name> < backend/migrations/add_unique_username_email.sql
--
-- Step 1 shows existing duplicates. If any rows come back, fix them first
-- (change the username or email of the extra account), because MySQL refuses
-- to add a unique rule while duplicates exist.
-- Note: the app also checks emails and usernames across all three tables
-- (an email used by a teacher cannot be used by a student). The database rules
-- below only work inside each table, so also check the last query.


-- Step 1: find duplicates -----------------------------------------------------

SELECT 'students' AS table_name, 'username' AS field, username AS value, COUNT(*) AS times
FROM students GROUP BY username HAVING COUNT(*) > 1
UNION ALL
SELECT 'students', 'email', email, COUNT(*) FROM students GROUP BY email HAVING COUNT(*) > 1
UNION ALL
SELECT 'teachers', 'username', username, COUNT(*) FROM teachers GROUP BY username HAVING COUNT(*) > 1
UNION ALL
SELECT 'teachers', 'email', email, COUNT(*) FROM teachers GROUP BY email HAVING COUNT(*) > 1
UNION ALL
SELECT 'admin', 'username', username, COUNT(*) FROM admin GROUP BY username HAVING COUNT(*) > 1
UNION ALL
SELECT 'admin', 'email', email, COUNT(*) FROM admin GROUP BY email HAVING COUNT(*) > 1;

-- Emails used in more than one table (login would pick the wrong account)
SELECT email, COUNT(*) AS times FROM (
    SELECT email FROM admin
    UNION ALL
    SELECT email FROM teachers
    UNION ALL
    SELECT email FROM students
) AS all_emails
GROUP BY email HAVING COUNT(*) > 1;


-- Step 2: add the unique rules --------------------------------------------------

ALTER TABLE students ADD CONSTRAINT uq_students_username UNIQUE (username);
ALTER TABLE students ADD CONSTRAINT uq_students_email UNIQUE (email);

ALTER TABLE teachers ADD CONSTRAINT uq_teachers_username UNIQUE (username);
ALTER TABLE teachers ADD CONSTRAINT uq_teachers_email UNIQUE (email);

ALTER TABLE admin ADD CONSTRAINT uq_admin_username UNIQUE (username);
ALTER TABLE admin ADD CONSTRAINT uq_admin_email UNIQUE (email);
