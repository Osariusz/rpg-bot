from datetime import datetime
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

class EndTurnORM(Base):
    __tablename__ = 'end_turn'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)

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

def get_statistic_raw_data(server_id: int, statistic: str, only_before_last_turn: bool = False) -> list:
    value_sum = func.sum(StatisticChangeORM.value).label("total_value")

    # Get the last EndTurnORM date
    last_turn_date = session.query(func.max(EndTurnORM.date)).scalar()

    sort_behavior = session.query(StatisticORM.sort_behavior).where(StatisticORM.name == statistic).scalar()
    info = StatisticShowInfo(sort_behavior)

    # Query statistics
    query = session.query(
            StatisticChangeORM.user_name, 
            value_sum,
            UserORM.country
        ).join(UserORM, UserORM.name == StatisticChangeORM.user_name).filter(
        (StatisticChangeORM.server_id == server_id) & 
        (StatisticChangeORM.statistic == statistic)
    )

    # Apply the date filter based on the argument
    if last_turn_date and only_before_last_turn:
        query = query.filter(StatisticChangeORM.date < last_turn_date)

    query = query.group_by(StatisticChangeORM.user_name)

    # Apply sorting
    for sort_priority in info.sort_priorities:
        if sort_priority == StatisticsShowInfoSortType.NATION:
            query = query.order_by(UserORM.country)
        if sort_priority == StatisticsShowInfoSortType.VALUE:
            query = query.order_by(value_sum.desc())

    return query.all() if last_turn_date or not only_before_last_turn else []

def end_turn_with_max_adjustment(server_id: int):
    # First, add an end turn entry
    add_end_turn()

    # Query for all statistic configurations that have a max_name defined for this server
    stat_configs = session.query(StatisticORM).filter(
        StatisticORM.server_id == server_id,
        StatisticORM.max_name.isnot(None)
    ).all()

    # Get all users in the given server
    users = get_users(server_id)

    # For each statistic that has a maximum counterpart, adjust every user's current total.
    for stat_config in stat_configs:
        base_stat = stat_config.name
        max_stat = stat_config.max_name

        for user in users:
            # Get the current total for the base statistic for this user
            current_value = session.query(func.sum(StatisticChangeORM.value)).filter(
                StatisticChangeORM.user_name == user.name,
                StatisticChangeORM.statistic == base_stat,
                StatisticChangeORM.server_id == server_id
            ).scalar() or 0

            # Get the current total for the corresponding max statistic for this user
            max_value = session.query(func.sum(StatisticChangeORM.value)).filter(
                StatisticChangeORM.user_name == user.name,
                StatisticChangeORM.statistic == max_stat,
                StatisticChangeORM.server_id == server_id
            ).scalar() or 0

            # Calculate the adjustment needed (max - current)
            adjustment = max_value - current_value

            # Only add a change if there is a non-zero difference
            if adjustment:
                new_change = StatisticChangeORM(
                    user_name=user.name,
                    statistic=base_stat,
                    value=adjustment,
                    date=datetime.utcnow(),
                    comment="Auto adjustment to max",
                    server_id=server_id
                )
                session.add(new_change)

    session.commit()

def add_end_turn():
    """Adds a new EndTurnORM entry with the current timestamp."""
    session.add(EndTurnORM(date=datetime.utcnow()))
    session.commit()

def get_turn_dates() -> list:
    """
    Retrieves all the dates of finished turns.
    Returns:
        A list of datetime objects representing each turn finish.
    """
    # Query for the dates and order by date.
    results = session.query(EndTurnORM.date).order_by(EndTurnORM.date).all()
    # Each result is a tuple; extract the first element.
    return [record[0] for record in results]

def delete_end_turn_by_day(day: datetime):
    """Deletes all EndTurnORM entries for the specified date."""
    session.query(EndTurnORM).filter(func.date(EndTurnORM.date) == day.date()).delete()
    session.commit()

def get_statistic_data(server_id: int, statistic: str):
    result = get_statistic_raw_data(server_id, statistic)

    statistic_config: StatisticChangeORM | None = session.query(StatisticORM).filter(StatisticORM.name == statistic).one_or_none()
    
    if statistic_config and statistic_config.max_name:
        max_statistic_name = statistic_config.max_name
        max_statistic_result = get_statistic_raw_data(server_id, max_statistic_name)

        # Create a dictionary for quick lookup
        max_stat_dict = {name: stat for name, stat, *_ in max_statistic_result}

        # Create new tuples with the additional value
        result = tuple((*statistic_tuple, max_stat_dict.get(statistic_tuple[0], 0)) for statistic_tuple in result)

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
