# College Attendance Management System

A simple React + FastAPI + MySQL application for managing students, courses, and daily attendance. This workspace contains application code only; Docker and deployment are intentionally out of scope.

## Prerequisites

- Python 3.10+
- Node.js 18+
- A locally installed MySQL server

## Local MySQL setup

Create a dedicated database account (use a password appropriate for your machine) and grant it access to the application database:

```sql
CREATE USER 'attendance_user'@'localhost' IDENTIFIED BY 'change_me';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX
  ON college_attendance.* TO 'attendance_user'@'localhost';
FLUSH PRIVILEGES;
```

Run `database/schema.sql` with an administrative MySQL account to create the database and tables. The script uses `IF NOT EXISTS` and does not delete existing records.

## Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env with your local MySQL credentials
uvicorn app.main:app --reload --port 8000
```

Required backend variables are `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `FRONTEND_ORIGINS`. The API creates missing tables on startup, but running the reviewed SQL script is recommended for a repeatable initial setup.

## Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

`VITE_API_BASE_URL` points to the FastAPI server and is safe to expose in the browser because it is not a secret.

## API endpoints

- `GET /health`
- `GET /students`, `POST /students`, `GET /students/{id}`
- `GET /courses`, `POST /courses`
- `GET /attendance?student_id=&course_id=&attendance_date=`
- `POST /attendance`
- `GET /attendance/student/{student_id}`
- `GET /dashboard?selected_date=`

FastAPI's interactive documentation is available at `http://localhost:8000/docs`.

## Project structure

```text
backend/app/       FastAPI settings, database, models, schemas, and routes
database/schema.sql Safe, non-destructive MySQL initialization script
frontend/src/      React UI and API client
```

## Validation and limitations

Student and course identifiers are unique. Attendance is unique per student, course, and date. The app has no authentication or role-based access control; it is intended for local development and should not be exposed publicly without adding those controls.

## Docker Integration Handover for Jeyashankar

Docker files have not been created. When containerizing later:

1. Change `DB_HOST` from `localhost` to the MySQL service name in the Compose environment, and provide the container's database credentials through environment variables.
2. Change `VITE_API_BASE_URL` to the reachable FastAPI URL before building the frontend.
3. Use `database/schema.sql` or the existing SQLAlchemy table initialization against the new database; do not delete existing data.
4. Ensure the backend starts only after MySQL accepts connections, or add an external health-check/retry policy. The current engine uses `pool_pre_ping`.
5. Configure `FRONTEND_ORIGINS` for the deployed frontend origin.

No Docker, Docker Compose, server deployment, firewall, or system MySQL configuration was changed.
