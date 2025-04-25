from flask import Flask
from flask_cors import CORS
from app.config.config import Config
from app.routes.fortune_routes import fortune_bp
from app.utils.db import DatabaseManager
from app.utils.logger import log_info

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize CORS
    CORS(app, origins=Config.CORS_ORIGINS)

    # Initialize database connection pool
    DatabaseManager.initialize()

    # Register blueprints
    app.register_blueprint(fortune_bp)

    # Log application startup
    log_info("Application started", {
        "debug_mode": app.debug,
        "deploy_mode": Config.DEPLOY_MODE
    })

    return app 