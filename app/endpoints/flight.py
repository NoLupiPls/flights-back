import os
import uuid
from flask import Blueprint, request, jsonify
from app.data.flights import Flight
from app.data import db_session
from flask_login import login_required, current_user
from app.data.users import User
import datetime


flight_api = Blueprint('flight_api', __name__)


@flight_api.route('/add_flight', methods=['POST'])
@login_required
def create_flight():
    """
    Должен принимать данные в форме .json файла
    """
    if not current_user.verified:
        return jsonify({'error': 'Account is not verified'}), 401
    
    def fill_missing_fields(data: dict) -> dict:
        required_fields = [
            'name', 'company', 'dt_from', 'dt_to', 'duration', 'distance',
            'ap_from', 'ap_to', 'passengers', 'pilot',
            'plane', 'terminal', 'gate', 'dt_register', 'dt_boarding'
        ]

        # Создаем копию исходного словаря, чтобы не изменять оригинал
        result = data.copy()

        # Добавляем отсутствующие поля со значением None
        for field in required_fields:
            if field not in result:
                result[field] = None

        return result

    # Исправленный путь к файлу базы данных
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_dir = os.path.join(base_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)  # Создаем директорию, если она не существует
    db_path = os.path.join(db_dir, 'flights_db.db')
    
    db_session.global_init(db_path)
    req_data = request.get_json()

    data = fill_missing_fields(req_data)

    # Преобразуем строки дат в объекты datetime
    dt_from = datetime.datetime.fromisoformat(data["dt_from"]) if data["dt_from"] else None
    dt_to = datetime.datetime.fromisoformat(data["dt_to"]) if data["dt_to"] else None
    dt_register = datetime.datetime.fromisoformat(data["dt_register"]) if data["dt_register"] else None
    dt_boarding = datetime.datetime.fromisoformat(data["dt_boarding"]) if data["dt_boarding"] else None

    # Преобразуем gate в Integer, если он есть
    gate = int(data["gate"]) if data["gate"] and data["gate"] != '' else None

    # Создаем объект Flight с указанием uuid
    new_flight = Flight(
        uuid=str(uuid.uuid4()),  # Генерируем UUID вручную
        name=data["name"],
        company=data["company"],
        dt_from=dt_from,
        dt_to=dt_to,
        duration=data["duration"],
        distance=data["distance"],
        ap_from=data["ap_from"],
        ap_to=data["ap_to"],
        passengers=data["passengers"],
        pilot=data["pilot"],
        plane=data["plane"],
        terminal=data["terminal"],
        gate=gate,
        dt_register=dt_register,
        dt_boarding=dt_boarding,
    )
    db_sess = db_session.create_session()
    current_user.my_flights.append(new_flight)
    db_sess.merge(current_user)
    db_sess.commit()

    return jsonify(new_flight.to_dict()), 201


@flight_api.route('/get_flights', methods=['GET'])
def get_flights():
    # Создаем абсолютный путь к базе данных
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_dir = os.path.join(base_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)  # Создаем директорию, если она не существует
    db_path = os.path.join(db_dir, 'flights_db.db')
    
    db_session.global_init(db_path)
    db_sess = db_session.create_session()
    flights = db_sess.query(Flight).all()
    return jsonify([flight.to_dict() for flight in flights]), 200


@flight_api.route('/my_flights', methods=['GET'])
@login_required
def get_my_flights():
    """
    Возвращает список рейсов текущего пользователя.
    """
    # Инициализируем соединение с БД
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_dir = os.path.join(base_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'flights_db.db')
    db_session.global_init(db_path)
    
    # Получаем свежий объект пользователя
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.uuid == current_user.uuid).first()
    
    return jsonify([flight.to_dict() for flight in user.my_flights]), 200


@flight_api.route('/save_flight', methods=['POST'])
@login_required
def save_flight():
    """
    Добавляет существующий рейс в список рейсов пользователя.
    Требует uuid рейса в теле запроса.
    """
    if not current_user.verified:
        return jsonify({'error': 'Account is not verified'}), 401
    
    req_data = request.get_json()
    
    # Проверяем наличие uuid рейса в запросе
    if not req_data or 'flight_uuid' not in req_data:
        return jsonify({'error': 'Flight UUID is required'}), 400
        
    flight_uuid = req_data['flight_uuid']  # Не преобразуем в int, так как в модели это String
    
    # Инициализируем соединение с БД
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_dir = os.path.join(base_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'flights_db.db')
    db_session.global_init(db_path)
    db_sess = db_session.create_session()
    
    # Получаем текущего пользователя из этой же сессии
    user = db_sess.query(User).filter(User.uuid == current_user.uuid).first()
    
    # Находим рейс по UUID
    flight = db_sess.query(Flight).filter(Flight.uuid == flight_uuid).first()
    
    if not flight:
        return jsonify({'error': 'Flight not found'}), 404
    
    # Проверяем, не добавлен ли уже этот рейс пользователю
    if flight in user.my_flights:
        return jsonify({'message': 'Flight already in your list'}), 200
    
    # Добавляем рейс в список рейсов пользователя
    user.my_flights.append(flight)
    db_sess.commit()
    
    return jsonify({
        'success': True,
        'message': 'Flight added to your list successfully',
        'flight': flight.to_dict()
    }), 201


@flight_api.route('/flight/<string:flight_uuid>', methods=['GET'])
def get_flight(flight_uuid):
    """
    Получение информации о конкретном рейсе по его UUID.
    """
    # Инициализируем соединение с БД
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_dir = os.path.join(base_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'flights_db.db')
    db_session.global_init(db_path)
    db_sess = db_session.create_session()
    
    # Находим рейс по UUID
    flight = db_sess.query(Flight).filter(Flight.uuid == flight_uuid).first()
    
    if not flight:
        return jsonify({'error': 'Flight not found'}), 404
    
    return jsonify(flight.to_dict()), 200
