import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest
from datetime import datetime, timedelta
from app.data import db_session
import uuid
from app.data.users import User
from werkzeug.security import generate_password_hash
import re


register_bp = Blueprint('register_bp', __name__)


@register_bp.route('/register', methods=['POST'])
def register():
    """
    Регистрация нового пользователя.
    Должен принимать данные в форме .json файла
    """
    req_data = request.get_json()
    
    # Проверка наличия обязательных полей
    if not req_data or 'name' not in req_data or 'email' not in req_data or 'password' not in req_data:
        return jsonify({
            'error': 'Missing required fields: name, email, and password are required'
        }), 400
    
    # Валидация email адреса
    email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    if not email_pattern.match(req_data['email']):
        return jsonify({
            'error': 'Invalid email format'
        }), 400
    
    # Проверка длины пароля
    if len(req_data['password']) < 6:
        return jsonify({
            'error': 'Password must be at least 6 characters long'
        }), 400

    # Создаем абсолютный путь к базе данных
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_dir = os.path.join(base_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'flights_db.db')
    
    # Инициализируем соединение с БД
    db_session.global_init(db_path)
    db_sess = db_session.create_session()
    
    # Проверка, не существует ли пользователя с таким email
    existing_user = db_sess.query(User).filter(User.email == req_data['email']).first()
    if existing_user:
        return jsonify({
            'error': 'User with this email already exists'
        }), 409

    # Создание пользователя
    user = User()
    user.uuid = str(uuid.uuid4())
    user.name = req_data['name']
    user.email = req_data['email']
    user.set_password(req_data['password'])
    user.verified = False  # Добавлено обязательное поле
    
    # Автоматически устанавливаем значения по умолчанию
    user.premium = False  # Без премиума
    user.friends = ""     # Строка вместо списка, т.к. поле определено как строковое
    user.verification_code = None
    user.verification_code_expires = None

    db_sess.add(user)
    db_sess.commit()

    return jsonify({
        'message': 'User registered successfully',
        'uuid': user.uuid
    }), 201
