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

## Docker Compose

Docker Compose runs the frontend, FastAPI backend, and MySQL database as separate services. It uses the named `mysql_data` volume for persistence, and the backend connects to MySQL at the Compose service name `db`.

Create the root environment file and replace the placeholder passwords:

```powershell
Copy-Item .env.example .env
```

Build and start the stack:

```powershell
docker compose config
docker compose build
docker compose up -d
docker compose ps
```

Open `http://localhost`. The frontend proxies `/api/...` requests to the backend's existing root-level routes, so no API routes were changed. The API health check is available at `http://localhost/api/health`.

The SQL file is run only when MySQL initializes an empty data directory. Existing data in the named volume is preserved. Do not use `docker compose down -v` unless you intentionally want to delete that Docker volume. To migrate an existing local database, export it first with `mysqldump`, then restore the dump into the container with `docker compose exec -T db mysql ...`; do not overwrite or drop data without a verified backup.

## Deploying to Ubuntu EC2

1. Create an Ubuntu EC2 instance and allow inbound TCP 22 only from your IP, and TCP 80 from the internet. Add TCP 443 later when HTTPS is configured. Do not open TCP 3306.
2. Install Docker Engine and the Compose plugin by following Docker's official Ubuntu instructions: <https://docs.docker.com/engine/install/ubuntu/>. Add your user to the `docker` group if desired, then reconnect to the SSH session.
3. Clone or securely copy this project to the instance, for example with `git clone` or `scp`.
4. In the project root, run `cp .env.example .env`, edit it with strong unique passwords, and set `FRONTEND_ORIGINS=http://YOUR_EC2_PUBLIC_IP`.
5. Start and verify the application:

```bash
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 db backend frontend
```

6. Browse to `http://YOUR_EC2_PUBLIC_IP`. Back up the database regularly with `docker compose exec -T db mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" college_attendance > backup.sql`, storing the backup outside the server. Keep the Compose volume on persistent disk and never expose MySQL publicly.
