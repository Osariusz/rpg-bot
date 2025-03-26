import os
from pathlib import Path
import discord

from db.db import Base, session
from sqlalchemy import Column, Integer

class MessageThreadhannelORM(Base):
    __tablename__ = 'message_thread_channels'

    id = Column(Integer, primary_key=True)
    ping_id = Column(Integer)

def add_message_thread_channel(channel_id: int):
    existing_channel = session.query(MessageThreadhannelORM).filter_by(id=channel_id).first()
    
    if not existing_channel:
        orm_instance = MessageThreadhannelORM(id=channel_id)
        session.add(orm_instance)
        session.commit()
    else:
        raise IndexError(f"Channel with ID {channel_id} already exists")

def remove_message_thread_channel(channel_id: int):
    channel = session.query(MessageThreadhannelORM).filter_by(id=channel_id).first()

    if channel:
        session.delete(channel)
        session.commit()
    else:
        raise IndexError(f"Channel with ID {channel_id} doesn't exist")

def get_message_thread_channel(channel_id: int) -> MessageThreadhannelORM:
    channel = session.query(MessageThreadhannelORM).filter_by(id=channel_id).first()
    return channel

def get_all_message_thread_channels() -> list[MessageThreadhannelORM]:
    channels = session.query(MessageThreadhannelORM).all()
    return channels