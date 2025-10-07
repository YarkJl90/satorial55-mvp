import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/satorial55"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "satorial_dev_secret"
