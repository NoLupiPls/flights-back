from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest
from datetime import datetime, timedelta
from app.data import db_session
import uuid
from app.data.users import User

register_bp = Blueprint('register_bp', __name__)


@register_bp.route('/register', methods=['POST'])
def register():
    """

        Должен принимать данные в форме .json файла

        """

    def fill_missing_fields(data: dict) -> dict:
        required_fields = [
            'name', 'premium', 'friends', 'my_flights', 'email', 'verification_code',
            'verification_code_expires']

        # Создаем копию исходного словаря, чтобы не изменять оригинал
        result = data.copy()

        # Добавляем отсутствующие поля со значением None
        for field in required_fields:
            if field not in result:
                result[field] = None
        return result


    req_data = request.get_json()

    data = fill_missing_fields(req_data)

    # Создание пользователя
    user = User()
    user.uuid = str(uuid.uuid4())
    user.name = data['name']
    user.premium = data['premium']
    user.friends = data['friends']
    if not data["my_flights"]:
        user.my_flights = []
    else:
        user.my_flights = data['my_flights']
    user.email = None,
    user.verification_code = None,
    user.verification_code_expires = None


    db_session.global_init('db/flights_db.db')
    db_sess = db_session.create_session()
    db_sess.add(user)

    return jsonify({
        'message': 'User registered successfully',
    }), 201

