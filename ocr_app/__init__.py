"""Flask application factory."""

import detectlanguage
from flask import Flask

from .config import Config
from .extensions import login_manager
from .models import User
from .utils.database import init_database


def create_app(config_object=Config):
    """Create and configure a Flask app instance."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_object)

    init_database(app)
    _configure_login_manager(app)
    _register_blueprints(app)

    detectlanguage.configuration.api_key = app.config.get("DETECT_LANGUAGE_API_KEY")

    return app


def _configure_login_manager(app):
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)


def _register_blueprints(app):
    from .blueprints.auth import auth
    from .blueprints.main import main
    from .blueprints.uploads import uploads_bp

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(uploads_bp)
