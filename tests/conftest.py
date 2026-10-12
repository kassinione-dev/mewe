import itertools
import os
import time
from datetime import UTC, datetime, timedelta
from urllib.parse import urlsplit

import pytest
import sqlalchemy as sa

# Окружение задаём до импорта приложения: load_dotenv() в src/app не перезаписывает
# уже заданные переменные, поэтому .env с настоящей БД тестам не достанется.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "mysql+pymysql://root:test@127.0.0.1:3307/mewe_test",
)
APP_ORIGIN = "https://mewe.test"

if not urlsplit(TEST_DATABASE_URL).path.endswith("_test"):
    raise RuntimeError("TEST_DATABASE_URL must point to a database whose name ends with _test")

os.environ.update(
    DATABASE_URL=TEST_DATABASE_URL,
    BOT_TOKEN="123456:test-token",
    APP_ORIGIN=APP_ORIGIN,
    SECRET_KEY="test-secret",
)

from alembic import command
from alembic.config import Config

from src.app import create_app
from src.app.extensions import db
from src.app.models import Category, Event, User

DB_WAIT_SECONDS = 60


def _wait_for_db(url: str) -> None:
    engine = sa.create_engine(url)
    deadline = time.monotonic() + DB_WAIT_SECONDS

    try:
        while True:
            try:
                with engine.connect():
                    return
            except sa.exc.OperationalError:
                if time.monotonic() > deadline:
                    raise
                time.sleep(1)
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def app():
    _wait_for_db(TEST_DATABASE_URL)
    # Схему строят миграции, а не db.create_all(): так она совпадает с серверной
    command.upgrade(Config("alembic.ini"), "head")

    return create_app()


@pytest.fixture(autouse=True)
def _clean_db(app):
    yield

    with app.app_context():
        tables = [table.name for table in db.metadata.sorted_tables]
        db.session.execute(sa.text("SET FOREIGN_KEY_CHECKS = 0"))
        for table in tables:
            db.session.execute(sa.text(f"TRUNCATE TABLE `{table}`"))
        db.session.execute(sa.text("SET FOREIGN_KEY_CHECKS = 1"))
        db.session.commit()


@pytest.fixture
def client(app):
    """Клиент от имени Mini App: HTTPS (cookie сессии Secure) и правильный Origin."""
    client = app.test_client()
    client.environ_base.update({"wsgi.url_scheme": "https", "HTTP_ORIGIN": APP_ORIGIN})

    return client


@pytest.fixture
def login(client):
    def _login(user_id: int) -> None:
        with client.session_transaction() as session:
            session["user_id"] = user_id

    return _login


_telegram_ids = itertools.count(1000)


@pytest.fixture
def make_user(app):
    def _make_user(first_name: str = "Test") -> int:
        with app.app_context():
            user = User(telegram_id=next(_telegram_ids), first_name=first_name)  # pyright: ignore[reportCallIssue]
            db.session.add(user)
            db.session.commit()

            return user.id

    return _make_user


@pytest.fixture
def make_category(app):
    def _make_category(name: str = "Спорт") -> int:
        with app.app_context():
            category = Category(name=name, icon="sports_soccer")  # pyright: ignore[reportCallIssue]
            db.session.add(category)
            db.session.commit()

            return category.id

    return _make_category


@pytest.fixture
def make_event(app):
    """Пишет событие прямо в БД, в обход валидации — так можно создать и прошедшее."""

    def _make_event(
        creator_id: int,
        starts_in: timedelta = timedelta(days=1),
        max_participants: int = 10,
    ) -> int:
        with app.app_context():
            event = Event(
                creator_id=creator_id,  # pyright: ignore[reportCallIssue]
                title="Футбол",  # pyright: ignore[reportCallIssue]
                description="Игра во дворе",  # pyright: ignore[reportCallIssue]
                location="Корпус A",  # pyright: ignore[reportCallIssue]
                max_participants=max_participants,  # pyright: ignore[reportCallIssue]
                event_date=datetime.now(UTC) + starts_in,  # pyright: ignore[reportCallIssue]
                duration_minutes=60,  # pyright: ignore[reportCallIssue]
            )
            db.session.add(event)
            db.session.commit()

            return event.id

    return _make_event


@pytest.fixture
def reschedule_event(app):
    """Сдвигает начало события: так событие, на которое уже записались, становится прошедшим."""

    def _reschedule_event(event_id: int, starts_in: timedelta) -> None:
        with app.app_context():
            event = db.session.get(Event, event_id)
            assert event is not None
            event.event_date = datetime.now(UTC) + starts_in
            db.session.commit()

    return _reschedule_event


@pytest.fixture
def query(app):
    """Выполняет запрос к БД в отдельном контексте — чтобы проверять, что реально записано."""

    def _query(statement):
        with app.app_context():
            return db.session.scalar(statement)

    return _query
