from enum import Enum, IntEnum
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, func, select

from globe.globe_message import GlobeMessage
from db.db import Base, engine, session

class UserORM(Base):
    __tablename__ = 'user'

    name = Column(String, primary_key=True)
    server_id = Column(Integer)
    country = Column(String)
    
class StatisticORM(Base):
    __tablename__ = 'statistic'

    name = Column(String, primary_key=True)
    type = Column(String)
    max_name = Column(String, ForeignKey("statistic.name"), nullable=True)
    server_id = Column(Integer)
    sort_behavior = Column(Integer)

class StatisticChangeORM(Base):
    __tablename__ = 'statistic_change'

    id = Column(Integer, primary_key=True)
    user_name = Column(String, ForeignKey("user.name"))
    statistic = Column(String, ForeignKey("statistic.name"))
    value = Column(Integer)
    date = Column(DateTime)
    comment = Column(String)
    server_id = Column(Integer)

def save_to_db(user: UserORM | StatisticORM | StatisticChangeORM):
    session.add(user)
    session.commit()

class StatisticsShowInfoSortTypeBehaviour(IntEnum):
    NATIONAL = 0,
    PLAYER = 1

class StatisticsShowInfoSortType(IntEnum):
    NATION = 0,
    VALUE = 1

class StatisticShowInfo():

    def __init__(self, sort_behavior: StatisticsShowInfoSortTypeBehaviour = StatisticsShowInfoSortTypeBehaviour.NATIONAL):
        if(sort_behavior == StatisticsShowInfoSortTypeBehaviour.NATIONAL.value):
            self.sort_priorities = [StatisticsShowInfoSortType.NATION, StatisticsShowInfoSortType.VALUE]
        elif(sort_behavior == StatisticsShowInfoSortTypeBehaviour.PLAYER.value):
            self.sort_priorities = [StatisticsShowInfoSortType.VALUE]
        else:
            self.sort_priorities = []

def get_statistic_sum(server_id: int, statistic: str):
    value_sum = func.sum(StatisticChangeORM.value).label("total_value")
    sort_behavior = session.query(
                StatisticORM.sort_behavior
            ).where(StatisticORM.name == statistic).scalar()
    info = StatisticShowInfo(sort_behavior)

    #TODO: show users without changes as 0 
    #TODO: add max value in (brackets)
    result = session.query(
            StatisticChangeORM.user_name, 
            value_sum,
            UserORM.country
        ).join(UserORM, UserORM.name == StatisticChangeORM.user_name).filter(
        (StatisticChangeORM.server_id == server_id) & 
        (StatisticChangeORM.statistic == statistic)
    ).group_by(StatisticChangeORM.user_name)

    for sort_priority in info.sort_priorities:
        if(sort_priority == StatisticsShowInfoSortType.NATION):
            result = result.order_by(UserORM.country)
        if(sort_priority == StatisticsShowInfoSortType.VALUE):
            result = result.order_by(value_sum.desc())

    result = result.all()

    return result

def get_statistic_user(statistic: String, user_name: String):
    messages = session.query(StatisticChangeORM).execute(select(StatisticChangeORM).where(StatisticChangeORM.user_name == user_name)).all()
    return messages

def get_users(server_id: int) -> list[UserORM]:
    return session.query(UserORM).filter_by(server_id=server_id).all()

def update_user_country(name: str, new_country: str) -> None:
    user = session.query(UserORM).filter_by(name=name).first()
    if user:
        user.country = new_country
        session.commit()
    else:
        raise ValueError("User not found")

def get_statistics(server_id: int) -> list[StatisticORM]:
    return session.query(StatisticORM).filter_by(server_id=server_id).all()
