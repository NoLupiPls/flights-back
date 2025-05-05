from flask import Flask


def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    from app.endpoints.ping import ping_bp
    app.register_blueprint(ping_bp)

    return app
