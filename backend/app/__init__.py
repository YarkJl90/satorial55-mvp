from flask import Flask
from backend.app.db import db
from flask_cors import CORS


def create_app(config: dict | None = None):
    """Create and configure the Flask application.

    Args:
        config: Optional dictionary of configuration overrides (useful for tests).

    Returns:
        A configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    # Apply overrides (e.g. TESTING or SQLALCHEMY_DATABASE_URI)
    if config:
        app.config.update(config)

    db.init_app(app)
    CORS(app)

    # Register blueprints (import after init_app to avoid import cycles)
    from app.routes.catalog import catalog_bp
    app.register_blueprint(catalog_bp)
    from app.routes.procurement import procurement_bp
    app.register_blueprint(procurement_bp)

    return app
