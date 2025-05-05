from flask import Flask
import flask_login
from app.data.users import User


def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    from app.endpoints.ping import ping_bp
    from app.endpoints.flight import flight_api

    app.register_blueprint(flight_api)
    app.register_blueprint(ping_bp)

    return app
