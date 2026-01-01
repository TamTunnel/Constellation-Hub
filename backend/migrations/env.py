"""
Alembic migrations environment configuration.

This module is responsible for running Alembic in either
'offline' mode (generating SQL scripts) or 'online' mode
(connecting to database and running migrations directly).
"""
import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models to register them with Base.metadata
from common.models.user import Base as UserBase, UserORM

# Import service models
try:
    from core_orbits_app.models import Base as CoreOrbitsBase
except ImportError:
    CoreOrbitsBase = None

try:
    from routing_app.models import Base as RoutingBase
except ImportError:
    RoutingBase = None

try:
    from ground_scheduler_app.models import Base as GroundSchedulerBase
except ImportError:
    GroundSchedulerBase = None

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata from all models
# We use UserBase as the primary, models will be registered there
target_metadata = UserBase.metadata

# Override sqlalchemy.url from environment variable
def get_database_url():
    """Get database URL from environment, with async driver."""
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql://constellation:constellation@localhost:5432/constellation_hub"
    )
    # Ensure we use asyncpg driver
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with a database connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
