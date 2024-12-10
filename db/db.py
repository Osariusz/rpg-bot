from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///example.db', echo=True)  # SQLite database
Session = sessionmaker(bind=engine)
session = Session()