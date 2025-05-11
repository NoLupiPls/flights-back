import datetime
import sqlalchemy
from sqlalchemy import orm

from app.data.db_session import SqlAlchemyBase

categories = orm.relationship("Category",
                              secondary="association",
                              backref="flights")


class Flight(SqlAlchemyBase):
    __tablename__ = 'flights'

    uuid = sqlalchemy.Column(sqlalchemy.String, primary_key=True) # id
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

    def to_dict(self):
        """Преобразует объект Flight в словарь для JSON-сериализации"""
        return {
            'uuid': self.uuid,
            'name': self.name,
            'company': self.company,
            'dt_from': self.dt_from.isoformat() if self.dt_from else None,
            'dt_to': self.dt_to.isoformat() if self.dt_to else None,
            'duration': self.duration,
            'distance': self.distance,
            'ap_from': self.ap_from,
            'ap_to': self.ap_to,
            'passengers': self.passengers,
            'pilot': self.pilot,
            'plane': self.plane, 
            'terminal': self.terminal,
            'gate': self.gate,
            'dt_register': self.dt_register.isoformat() if self.dt_register else None,
            'dt_boarding': self.dt_boarding.isoformat() if self.dt_boarding else None
        }
    