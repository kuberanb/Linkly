# Linkly

Linkly is a small FastAPI URL shortener. Users register and log in, create short links, list their links, and open a short link to redirect to its destination. PostgreSQL stores users and links. Redis caches destinations for 60 seconds.

## Run locally with Docker Compose

1. Copy `.env.example` to `.env` if you do not already have `.env`:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Set `POSTGRES_PASSWORD` and `JWT_SECRET` in `.env`. Use the same database password in the host `DATABASE_URL` line. To make a JWT secret:

   ```powershell
   py -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. Build and start the stack:

   ```powershell
   docker compose up --build -d
   docker compose ps -a
   Invoke-RestMethod http://127.0.0.1:8000/health
   ```

   `/health` should return `{"status":"healthy"}`. Compose also calls this endpoint in its API healthcheck. The `migrate` service runs `alembic upgrade head` and exits successfully before the API starts. If a migration fails, check `docker compose logs migrate`.

4. Open [Swagger UI](http://127.0.0.1:8000/docs). Register at `POST /api/auth/register`, log in at `POST /api/auth/login`, and use the returned Bearer token with Swagger's **Authorize** button. Create a link at `POST /api/urls`, then open `GET /api/urls/{short_code}`.

The host Python process uses `127.0.0.1:5433` for PostgreSQL. Containers use `db:5432` and `redis:6379` because Compose gives services network names. The API container receives those addresses through its `environment` settings. The `.env` file stays outside the Docker image and is ignored by Git.

## How the parts work

- The `Dockerfile` builds a Python image containing the application and its dependencies. Compose starts containers from that image.
- `db` stores users and links in a named volume. The volume keeps data when a container is recreated.
- `migrate` runs Alembic before `api` starts. Alembic records the current schema revision in `alembic_version`, so running the command again is safe.
- Opening a short link tries Redis first. The API still checks PostgreSQL to count the click and confirm the link is active and unexpired. On a cache miss, it stores the destination for 60 seconds if the link has no expiry. If Redis fails, the API logs a warning and continues using PostgreSQL.
- A database connection failure returns HTTP 503. Expected client mistakes, such as invalid input or a missing link, return 4xx responses.

## Run tests

Keep the Compose stack running. The tests call the API over HTTP, create a temporary user, and remove it afterward. They use only Python's standard test library.

```powershell
py -3.15 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

If you already have the project's virtual environment and dependencies installed, run only the last command. The tests cover authentication, validation, redirects, click counts, inactive and expired links, and Redis failure fallback.

## Useful commands

```powershell
docker compose logs --tail=50 api
docker compose run --rm migrate
docker compose down
```

`docker compose down` stops containers but keeps the PostgreSQL volume, so your data remains. A new database volume starts empty and the migration service creates its tables on the next `docker compose up`.

This Compose file is for local development. Before putting the API on the public internet, add HTTPS at the edge, rate limits for login and link creation, database backups, and monitoring.
