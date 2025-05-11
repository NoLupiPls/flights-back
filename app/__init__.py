import os
from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_cors import CORS  # Добавляем импорт CORS


# Загружаем переменные окружения
load_dotenv()


def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='../')

    # Настраиваем CORS для всего приложения
    CORS(app, resources={r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }})

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing_only')

    # Инициализация Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login_bp.login'  # Указываем путь для перенаправления
    login_manager.login_message = "Пожалуйста, войдите в систему для доступа к этой странице."
    login_manager.login_message_category = "info"

    # Загружаем пользователя
    from app.data.users import User
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.data import db_session
        db_path = os.path.join(os.path.dirname(__file__), 'db', 'flights_db.db')
        db_session.global_init(db_path)
        db_sess = db_session.create_session()
        return db_sess.query(User).filter(User.uuid == user_id).first()

    # Регистрируем blueprints
    from app.endpoints.ping import ping_bp
    from app.endpoints.login import login_bp
    from app.endpoints.register import register_bp
    from app.endpoints.flight import flight_api
    from app.endpoints.account_verification import verify_api
    from app.endpoints.profile import profile_api  # Добавлен импорт для API профиля

    app.register_blueprint(ping_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(flight_api)
    app.register_blueprint(verify_api)
    app.register_blueprint(profile_api)  # Регистрируем API для работы с профилем

    return app
