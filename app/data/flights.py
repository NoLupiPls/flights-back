import datetime
import sqlalchemy
from sqlalchemy import orm

from app.data.db_session import SqlAlchemyBase

categories = orm.relationship("Category",
                              secondary="association",
                              backref="news")


class Flight(SqlAlchemyBase):
    __tablename__ = 'flights'

    uuid = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True) # id

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True) # имя рейса

    company  = sqlalchemy.Column(sqlalchemy.String, nullable=True) # название компании перевозчика

    dt_from = sqlalchemy.Column(sqlalchemy.DateTime) # дата и время вылета

    dt_to = sqlalchemy.Column(sqlalchemy.DateTime) # дата и время прилёта

    duration = sqlalchemy.Column(sqlalchemy.Integer) # длительность (в минутах)

    distance = sqlalchemy.Column(sqlalchemy.Integer) # дистанция (км)

    ap_from = sqlalchemy.Column(sqlalchemy.String, nullable=True) # аэропорт (вылет)

    ap_to = sqlalchemy.Column(sqlalchemy.String, nullable=True) # аэропорт (прилёт)

    passengers = sqlalchemy.Column(sqlalchemy.Integer, nullable=True) # кол-во пассажиров

    pilot = sqlalchemy.Column(sqlalchemy.String, nullable=True) # Пилот (Иванов И. И.)

    plane = sqlalchemy.Column(sqlalchemy.String, nullable=True) # имя самолёта

    terminal = sqlalchemy.Column(sqlalchemy.String, nullable=True) # Название терминала вылета

    gate = sqlalchemy.Column(sqlalchemy.Integer) # номер выхода

    dt_register = sqlalchemy.Column(sqlalchemy.DateTime) # дата и время начала регистрации

    dt_boarding = sqlalchemy.Column(sqlalchemy.DateTime) # дата и время начала посадки

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.uuid"))

    user = orm.relationship('User')
