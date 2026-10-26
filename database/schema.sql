CREATE DATABASE IF NOT EXISTS college_attendance
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE college_attendance;

CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id VARCHAR(30) NOT NULL UNIQUE,
  name VARCHAR(120) NOT NULL,
  department VARCHAR(120) NOT NULL,
  academic_year VARCHAR(30) NOT NULL,
  INDEX ix_students_student_id (student_id)
);

CREATE TABLE IF NOT EXISTS courses (
  id INT AUTO_INCREMENT PRIMARY KEY,
  course_id VARCHAR(30) NOT NULL UNIQUE,
  course_name VARCHAR(160) NOT NULL,
  INDEX ix_courses_course_id (course_id)
);

CREATE TABLE IF NOT EXISTS attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  course_id INT NOT NULL,
  attendance_date DATE NOT NULL,
  status ENUM('Present', 'Absent') NOT NULL,
  CONSTRAINT fk_attendance_student FOREIGN KEY (student_id) REFERENCES students(id),
  CONSTRAINT fk_attendance_course FOREIGN KEY (course_id) REFERENCES courses(id),
  CONSTRAINT uq_attendance_day UNIQUE (student_id, course_id, attendance_date),
  INDEX ix_attendance_date (attendance_date)
);
