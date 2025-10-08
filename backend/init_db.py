

from app import create_app
from app.db import db
from alembic import command
from alembic.config import Config as AlembicConfig
import os
from pathlib import Path

def upgrade_database() -> None:
    app = create_app()
    with app.app_context():
        # Importar modelos dentro del contexto para asegurar el registro correcto
        from app import models
        alembic_cfg = AlembicConfig(str(Path(__file__).with_name("alembic.ini")))
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        command.upgrade(alembic_cfg, "head")
        print("Alembic upgrade complete.")
        db.create_all()
        # Aquí puedes cargar datos seed si lo deseas
        # db.session.add(...)
        # db.session.commit()



if __name__ == '__main__':
    upgrade_database()
    print("✅ Base de datos inicializada correctamente.")
