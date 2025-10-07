import os
class Config:
    # Usa DATABASE_URL si existe; si no, SQLite local (archivo en /workspaces/satorial55-mvp/backend)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///satorial55.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
