# MeWe

MeWe is a Telegram Mini App for discovering and organizing student activities at Far Eastern Federal University (FEFU). Students can find events, register for them, and manage events they organize without leaving Telegram.

## Features

- Create events with a category, location, date, duration, participant limit, and description
- Search upcoming events by title, description, and location
- Filter events by one or more categories
- View event details and current registration counts
- Register for events or cancel a registration
- Delete an event as its organizer, before it starts
- View created events and joined events separately on **My events**, with past events in collapsible lists
- Authenticate through Telegram Web App `initData`; no separate password is needed
- Edit the profile description and view other users' profiles
- Choose a light, dark, or Telegram-matching theme; the choice syncs across devices through Telegram CloudStorage

## Tech stack

- **Backend:** Python 3.12, Flask, Pydantic, SQLAlchemy 2.0 typed models (via Flask-SQLAlchemy), Alembic, Gunicorn
- **Database:** MySQL 8.4
- **Bot:** `python-telegram-bot`
- **Frontend:** Jinja2 templates, vanilla JavaScript ES modules, and CSS; no build step
- **Quality:** pytest on a real MySQL database, pyright in strict mode, ruff
- **Infrastructure:** Docker Compose, GitLab CI/CD, `uv` for dependency management

## Architecture

The backend is split into layers; each layer depends only on the one below it:

```text
routes/        HTTP: parse the request, call a service, serialize the response
  ↓
services/      business rules and transactions (commit); know nothing about HTTP
  ↓
repositories/  database queries only: select() statements, no rules, no commit
  ↓
models.py      SQLAlchemy 2.0 models with Mapped[...] types
```

- **Validation at the boundary.** A route parses the JSON body into a Pydantic schema (`schemas/`) with strict types, length limits, and timezone-aware dates, and passes the typed object to a service. Rules that need the clock or the database (the event starts in the future, the category exists, the creation cooldown) live in services.
- **Errors.** Client errors are subclasses of `AppError` (`ValidationError` → 400, `ConflictError` → 409, and so on). API requests get `{"error": "message"}`; HTML pages get an error page.
- **Authentication.** The Mini App sends Telegram `initData`; the backend verifies its HMAC-SHA256 signature with the bot token and its age, then creates a session.
- **Concurrency.** Registration locks the event row with `SELECT ... FOR UPDATE`, so two users cannot take the last place at the same time.
- **Time.** All dates are stored and processed in UTC through a custom column type that rejects naive datetimes; the client formats dates for the user's timezone.
- **Request origin.** The session cookie must be `SameSite=None` inside Telegram, so state-changing API requests are accepted only from `APP_ORIGIN`.

## Application layout

```text
├── bot.py                 # Telegram /start command and Mini App menu button
├── run.py                 # Flask web server entry point
├── docker-compose.yml     # web, bot, and MySQL services
├── .gitlab-ci.yml         # CI checks and deployment
├── migrations/            # Alembic migrations
├── tests/                 # pytest suite (needs a MySQL test database)
└── src/app/
    ├── models.py          # Category, Event, User, and Participant models
    ├── db_types.py        # UTC datetime column type
    ├── exceptions.py      # AppError hierarchy mapped to HTTP status codes
    ├── routes/            # API endpoints, HTML pages, and the health check
    ├── services/          # Business rules and Telegram initData verification
    ├── repositories/      # Database queries
    ├── schemas/           # Pydantic request schemas
    ├── serializers/       # API response serialization
    ├── templates/         # Jinja2 pages
    └── static/            # JavaScript, styles, and icons
```

## Configuration

Create a `.env` file in the repository root. Do not commit it or share its secret values.

```dotenv
# Required
BOT_TOKEN=replace_with_telegram_bot_token
WEBAPP_URL=https://your-public-host/
APP_ORIGIN=https://your-public-host
SECRET_KEY=replace_with_a_long_random_secret
DB_PASSWORD=replace_with_database_user_password
DB_ROOT_PASSWORD=replace_with_database_root_password

# Optional; defaults shown
PORT=8000
WEB_BIND=127.0.0.1
FLASK_DEBUG=false
```

`WEBAPP_URL` is the public HTTPS URL opened by Telegram. `APP_ORIGIN` must be the exact origin of that page (scheme and host, with no path); the backend checks it for state-changing API requests. Flask session cookies are secure and partitioned, so the Mini App must be served over HTTPS.

Docker Compose builds `DATABASE_URL` for the web and bot containers from `DB_PASSWORD` and the Compose database service. When running the app outside Docker, `DATABASE_URL` is required and must point to a reachable MySQL database, for example:

```text
mysql+pymysql://mewe:password@localhost/mewe_app
```

The database name and non-secret MySQL user are set by `docker-compose.yml`. `WEB_BIND` controls the host-side address to which the web port is published; keep the default loopback binding when a local reverse proxy provides public HTTPS.

## Run with Docker Compose

Requirements: Docker Engine with the Compose plugin, and a Telegram bot configured to use the same public Mini App URL.

```bash
docker compose build
docker compose run --rm web alembic upgrade head
docker compose up -d
```

The web and bot services wait for MySQL's health check, and the web container reports its own health through `/api/health`. The web app runs under Gunicorn with two workers. `PORT` sets both the port Gunicorn listens on inside the container and the published host port. `WEB_BIND` sets the host address; by default, Compose publishes the app only on `127.0.0.1:8000`, ready for a local HTTPS reverse proxy. `FLASK_DEBUG` applies to the local `run.py` server and does not enable debug mode in the Gunicorn deployment. To inspect service output:

```bash
docker compose logs -f web bot
```

Stop the services with `docker compose down`. The MySQL data volume is preserved; add `-v` only if you intentionally want to remove the database data.

## Run locally

Requirements: Python 3.12, `uv`, a reachable MySQL database, and a publicly accessible HTTPS URL for Telegram Mini App authentication and cookies.

Set the required variables in `.env` (including `DATABASE_URL`), then run:

```bash
uv sync
uv run alembic upgrade head
uv run python run.py
```

The web server defaults to `http://0.0.0.0:8000`; `PORT` changes the port. For Telegram end-to-end use, put it behind HTTPS at `WEBAPP_URL` and set `APP_ORIGIN` to that public origin. Run the bot in a separate terminal:

```bash
uv run python bot.py
```

## Main pages and API

HTML pages:

- `/` — upcoming events, search, multi-category filters, and event details
- `/my_events` — events the current user organizes and events they have joined
- `/profile` — the current user's profile, editable description, and theme switcher
- `/{id}/profile` — another user's public profile

The JSON API is under `/api`. Successful responses are unwrapped JSON objects; deleting an event returns `204 No Content`. Errors use `{"error": "message"}`; a validation error names the field, for example `{"error": "title: String should have at least 1 character"}`. Protected endpoints use the Flask session cookie.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check that the app and its database respond; used by the Compose healthcheck |
| `POST` | `/api/sessions` | Validate Telegram `initData` and create a session |
| `GET` | `/api/events` | Search and filter upcoming events; repeat `category` for multiple IDs; paginate with `page` and `per_page` (default 15, max 100) |
| `POST` | `/api/events` | Create an event |
| `GET` | `/api/events/{id}/participants/me` | Get the current user's participation status |
| `PUT` / `DELETE` | `/api/events/{id}/participants/me` | Register for an event or cancel registration; both are idempotent and return the new `registered_count` |
| `DELETE` | `/api/events/{id}` | Delete an event as its organizer |
| `GET` | `/api/users/me/events` | List events organized by the current user |
| `GET` | `/api/users/me/participations` | List events joined by the current user, including past events |
| `PATCH` | `/api/users/me` | Update the profile description |

State-changing API requests must come from the configured `APP_ORIGIN`. The browser sends the same-origin session cookie automatically.

## Tests

Tests use pytest and a real MySQL database: row locks and the UTC column type behave differently on SQLite. The schema is built by the Alembic migrations, and tables are truncated after every test.

```bash
docker run -d --name mewe-test-db -p 127.0.0.1:3307:3306 \
  -e MYSQL_ROOT_PASSWORD=test -e MYSQL_DATABASE=mewe_test mysql:8.4.11
uv run pytest
```

Set `TEST_DATABASE_URL` to use another database; its name must end with `_test`, so the suite can never truncate a real database.

The suite covers:

- Telegram `initData` verification: a valid signature, tampered data, a signature from another bot, expired and future `auth_date`, and malformed user data
- sessions: first login creates a user, a repeat login updates it, forged data is rejected
- events: creation, validation errors, the creation cooldown, deletion rules, search with escaped `LIKE` wildcards, and hiding started events
- participation: joining, leaving, idempotency, a full event, the organizer's own event, and events that have already started
- API protection: requests without a session and from a foreign `Origin`
- profile updates, the health check, and rendering of the HTML pages

## Development checks

Run before committing; CI runs the same checks:

```bash
uvx ruff check src tests
uv run pyright
uv run pytest
```

`pyright` checks `src` and `bot.py` in strict mode and `tests` in standard mode.

## CI/CD

GitLab CI runs three jobs on every merge request and push to `main`:

- **lint:** `ruff`
- **typecheck:** `pyright`
- **test:** on a temporary MySQL service container, checks that migrations have a single head, runs `upgrade` → `downgrade base` → `upgrade`, runs `alembic check` to catch model changes without a migration, and then runs the pytest suite

A push to `main` deploys to the server only after CI passes, and the deploy checks out the exact commit that passed. It backs up the database with `mysqldump` (the last 10 dumps are kept) before applying migrations. Docker image versions are pinned, so CI and the server run the same MySQL.

The deploy job needs `SSH_HOST`, `SSH_USER`, `SSH_PORT` and `SSH_PRIVATE_KEY` (of the File type) in the project's CI/CD variables, protected so they are only exposed to `main`. The server's `origin` must point to the GitLab repository.

## Database migrations

Apply migrations with `alembic upgrade head`. In Docker, use `docker compose run --rm web alembic upgrade head`. Migration history is in `migrations/versions/`.

## Author

Lev Fedorenko — [GitHub](https://github.com/kassinione)
