-- PostgreSQL initialization script
-- Safe to re-run: uses IF NOT EXISTS; never drops existing data.

CREATE TABLE IF NOT EXISTS students (
  id            SERIAL PRIMARY KEY,
  student_id    VARCHAR(30)  NOT NULL UNIQUE,
  name          VARCHAR(120) NOT NULL,
  department    VARCHAR(120) NOT NULL,
  academic_year VARCHAR(30)  NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_students_student_id ON students (student_id);

CREATE TABLE IF NOT EXISTS courses (
  id          SERIAL PRIMARY KEY,
  course_id   VARCHAR(30)  NOT NULL UNIQUE,
  course_name VARCHAR(160) NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_courses_course_id ON courses (course_id);

CREATE TABLE IF NOT EXISTS attendance (
  id              SERIAL PRIMARY KEY,
  student_id      INT  NOT NULL REFERENCES students(id),
  course_id       INT  NOT NULL REFERENCES courses(id),
  attendance_date DATE NOT NULL,
  status          VARCHAR(10) NOT NULL CHECK (status IN ('Present', 'Absent')),
  CONSTRAINT uq_attendance_day UNIQUE (student_id, course_id, attendance_date)
);
CREATE INDEX IF NOT EXISTS ix_attendance_date     ON attendance (attendance_date);
CREATE INDEX IF NOT EXISTS ix_attendance_student  ON attendance (student_id);
CREATE INDEX IF NOT EXISTS ix_attendance_course   ON attendance (course_id);
