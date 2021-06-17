import pathlib
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# init config
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))

from app.settings.config import get_app_settings  # isort:skip

config = get_app_settings()

context_config = context.config

fileConfig(context_config.config_file_name)

target_metadata = None

context_config.set_main_option("sqlalchemy.url", str(config.DATABASE_URL))


def run_migrations_online() -> None:
    connectable = engine_from_config(
        context_config.get_section(context_config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
