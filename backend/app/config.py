import os
class Config:
    # Use DATABASE_URL if set; otherwise fall back to a local SQLite file (backend/satorial55.db)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///satorial55.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
