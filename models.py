from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, nullable=False)
    bot = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
