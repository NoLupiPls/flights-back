import sqlalchemy
from app.data.db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

pfp_directory = 'static/uploads/user_pfp/'


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    uuid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    premium = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    friends = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    my_flights = orm.relationship("Flight", back_populates='user')
    pfp = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
