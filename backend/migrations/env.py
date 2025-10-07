from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys

# --- Ajustar rutas para importar backend.app correctamente ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import create_app, db  # Importar app y db desde tu paquete Flask

# --- Crear la app y empujar el contexto ---
app = create_app()
app.app_context().push()

# --- Configuración principal ---
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Tomar la URL desde la app Flask
db_url = app.config.get("SQLALCHEMY_DATABASE_URI")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# Asignar metadatos (esto es lo que Alembic usa para autogenerar migraciones)
target_metadata = db.metadata

# --- Modo offline ---
def run_migrations_offline():
    """Ejecutar migraciones sin conexión."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# --- Modo online ---
def run_migrations_online():
    """Ejecutar migraciones con conexión."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# --- Ejecución ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
