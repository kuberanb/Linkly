
import asyncio
from pathlib import Path

from logging.config import fileConfig

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.db.base import Base

# Import all models so their tables are registered
from app.models import User, URL, URLCLICK


config = context.config


class MigrationSettings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
    )

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Migrations need only the database URL, not the application's JWT settings.
config.set_main_option(
    "sqlalchemy.url",
    MigrationSettings().DATABASE_URL.replace("%", "%%")
)


# Tell Alembic about our SQLAlchemy models
target_metadata = Base.metadata


def run_migrations_offline():

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool
    )

    async with connectable.connect() as connection:

        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():

    asyncio.run(run_async_migrations())


if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()
