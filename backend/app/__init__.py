from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensiones
    db.init_app(app)
    CORS(app)
    JWTManager(app)

    @app.route("/")
    def index():
        return {"message": "Satorial55 conectado a base de datos PostgreSQL ✅"}

    return app
