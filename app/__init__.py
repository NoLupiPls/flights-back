from flask import Flask


def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='../')

    from app.endpoints.ping import ping_bp
    from app.endpoints.login import login_bp
    from app.endpoints.register import register_bp
    from app.endpoints.flight import flight_api
    from app.endpoints.account_verification import verify_api
    from app.endpoints.index import index

    app.register_blueprint(index)
    app.register_blueprint(ping_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(flight_api)
    app.register_blueprint(verify_api)

    return app
