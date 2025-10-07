from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    from .config import Config
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app)
    JWTManager(app)

    with app.app_context():
        from . import models  # noqa

    @app.get("/")
    def health():
        return {"message": "Satorial55 conectado a base de datos ✅"}

    return app
