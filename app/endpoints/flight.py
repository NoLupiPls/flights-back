from flask import Flask, request, jsonify
from app.data.flights import Flight
from app.data import db_session
from app.data.users import User
import uuid
from flask_login import login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init('../db/flights_db.db')

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@login_required
@app.route('/post', methods=['POST'])
def create_flight():
    data = request.get_json()

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


@app.route('/get_flights', methods=['GET'])
def get_flights():
    db_sess = db_session.create_session()
    flights = db_sess.query(Flight).all()
    return jsonify([flight.to_dict() for flight in flights]), 200

app.run()