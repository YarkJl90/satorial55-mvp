import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Base de datos SQLite para desarrollo
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'satorial55.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "satorial_dev_secret"
