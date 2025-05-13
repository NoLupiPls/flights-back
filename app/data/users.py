import sqlalchemy
from app.data.db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    # Изменить определение uuid с Integer на String
    uuid = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    verified = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    premium = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    friends = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    my_flights = orm.relationship("Flight", back_populates='user')
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    verification_code = sqlalchemy.Column(sqlalchemy.String(4), nullable=True)
    verification_code_expires = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pfp_route = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    # Добавьте этот метод
    def get_id(self):
        """Переопределение метода для Flask-Login, чтобы использовать uuid вместо id"""
        return str(self.uuid)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)