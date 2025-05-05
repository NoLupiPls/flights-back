from flask import request, jsonify, Blueprint
from app.data.flights import Flight
from app.data import db_session
import uuid
from flask_login import login_user, LoginManager, login_required, logout_user, current_user

flight_api = Blueprint('flight_api', __name__)


@login_required
@flight_api.route('/add_flight', methods=['POST'])
def create_flight():
    def fill_missing_fields(data: dict) -> dict:
        required_fields = [
            'name', 'company', 'dt_from', 'dt_to', 'duration', 'distance',
            'ap_from', 'ap_to', 'passengers', 'pilot',
            'plane', 'terminal', 'gate', 'dt_register', 'dt_boarding', 'user_id'
        ]

        # Создаем копию исходного словаря, чтобы не изменять оригинал
        result = data.copy()

        # Добавляем отсутствующие поля со значением None
        for field in required_fields:
            if field not in result:
                result[field] = None

        return result

    db_session.global_init('db/flights_db.db')
    req_data = request.get_json()

    data = fill_missing_fields(req_data)

    new_flight = Flight(
        uuid=str(uuid.uuid4()),
        name=data["name"],
        company=data["company"],
        dt_from=data["dt_from"],
        dt_to=data["dt_to"],
        duration=data["duration"],
        distance=data["distance"],
        ap_from=data["ap_from"],
        ap_to=data["ap_to"],
        passengers=data["passengers"],
        pilot=data["pilot"],
        plane=data["plane"],
        terminal=data["terminal"],
        gate=data["gate"],
        dt_register=data["dt_register"],
        dt_boarding=data["dt_boarding"],
    )
    db_sess = db_session.create_session()
    current_user.my_flights.append(new_flight)
    db_sess.merge(current_user)
    db_sess.add(new_flight)
    db_sess.commit()

    return jsonify(new_flight.to_dict()), 201


@flight_api.route('/get_flights', methods=['GET'])
def get_flights():
    db_session.global_init('db/flights_db.db')
    db_sess = db_session.create_session()
    flights_db_req = db_sess.query(Flight).all()
    return jsonify([flight.to_dict() for flight in flights_db_req]), 200
