import os
from pathlib import Path
import discord

from db.db import Base, session
from sqlalchemy import Column, Integer

class GlobeDedicatedChannelORM(Base):
    __tablename__ = 'globe_dedicated_channels'

    id = Column(Integer, primary_key=True)

def add_globe_dedicated_channel(channel_id: int):
    existing_channel = session.query(GlobeDedicatedChannelORM).filter_by(id=channel_id).first()
    
    if not existing_channel:
        orm_instance = GlobeDedicatedChannelORM(id=channel_id)
        session.add(orm_instance)
        session.commit()
    else:
        raise IndexError(f"Channel with ID {channel_id} already exists")


def remove_globe_dedicated_channel(channel_id: int):
    channel = session.query(GlobeDedicatedChannelORM).filter_by(id=channel_id).first()

    if channel:
        session.delete(channel)
        session.commit()
    else:
        raise IndexError(f"Channel with ID {channel_id} doesn't exist")

def get_all_globe_dedicated_channels():
    channels = session.query(GlobeDedicatedChannelORM).all()
    return channels