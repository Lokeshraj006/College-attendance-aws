# Docker Deployment - College Attendance App

This application runs three Docker Compose services:

| Service | Technology | Exposure |
|---|---|---|
| `frontend` | React, Vite, NGINX | Host port 80 |
| `backend` | FastAPI, Uvicorn | Internal port 8000 |
| `db` | MySQL 8.4 | Internal port 3306 |

NGINX serves the React application and proxies browser requests from `/api/...` to the backend's existing root-level routes. MySQL is not published to the host or internet.

## Local startup

```powershell
Copy-Item .env.example .env
# Edit .env and replace both placeholder passwords

docker compose config
docker compose up -d --build
docker compose ps
```

Open `http://localhost`. Verify the API with `http://localhost/api/health`.

## Configuration

The backend receives `DB_HOST=db`, `DB_PORT=3306`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` from Compose. The backend uses SQLAlchemy with `mysql+pymysql`. The root `.env` is ignored by Git; commit only `.env.example` with safe placeholders.

## Persistence and initialization

The named `mysql_data` volume preserves records across ordinary restarts and container recreation. `database/schema.sql` is mounted read-only and runs only when MySQL initializes an empty data directory. It uses non-destructive `IF NOT EXISTS` statements.

Do not use `docker compose down -v` unless you intentionally want to delete the database volume. Before migrating an existing laptop database, create a backup with `mysqldump`, then restore it into the container after verifying the backup.

## EC2 deployment

1. Use an Ubuntu EC2 instance and install Docker Engine plus the Compose plugin using Docker's official Ubuntu instructions: <https://docs.docker.com/engine/install/ubuntu/>.
2. Allow TCP 22 only from your IP and TCP 80 from the internet. Add TCP 443 only when HTTPS is configured. Do not allow TCP 3306 or 8000.
3. Clone or copy this project to the server.
4. Create and securely edit the production environment file:

```bash
cp .env.example .env
nano .env
```

Set strong unique values for `DB_PASSWORD` and `MYSQL_ROOT_PASSWORD`, and set `FRONTEND_ORIGINS` to the public frontend origin.

5. Start and inspect the services:

```bash
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 db backend frontend
curl http://localhost/api/health
```

Browse to `http://YOUR_EC2_PUBLIC_IP`. Keep MySQL private and back up the database regularly, storing backups outside the EC2 host.

## Useful commands

```bash
docker compose logs -f
docker compose restart backend
docker compose up -d --build frontend backend
```
