"""Utility script to apply the latest Alembic migrations."""
import os
from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig


def upgrade_database() -> None:
    """Apply migrations up to the latest revision."""
    alembic_cfg = AlembicConfig(str(Path(__file__).with_name("alembic.ini")))

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(alembic_cfg, "head")
    print("Alembic upgrade complete.")


if __name__ == '__main__':
    upgrade_database()
    print("✅ Base de datos inicializada correctamente.")
